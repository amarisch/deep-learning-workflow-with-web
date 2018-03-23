import os
import io
import subprocess
import sys
from contextlib import contextmanager
import traceback

from sshtunnel import SSHTunnelForwarder, HandlerSSHTunnelForwarderError

from helpers.resource_helper import ResourceHelper
from helpers.storage_helper import StorageHelper
from helpers.compute_helper import ComputeHelper

SCRIPTS_DIR = os.path.join(os.path.dirname(__file__), 'scripts')
tunneling_pid = -1

class VirtualMachineDeployer(object):
	""" Helper for deploying a virtual machine """
	def __init__(self, client_data, vm_name, resource_group, storage_account, username='azureadminuser', password='Azureadminpw1', location='westus'):
		self.vm_name = vm_name
		self.resources = ResourceHelper(client_data, location, resource_group)
		self.storage = StorageHelper(client_data, self.resources, storage_account)
		self.compute = ComputeHelper(client_data, self.resources, vm_name)

		self.username = username
		self.password = password
		self.fileshares = []


	def _format_proc_output(self, header, output):
		if output:
			print(
				header,
				'\n'.join([
					'    {}'.format(line)
					for line in output.decode('utf-8').split('\n')
				]),
				sep='\n',
				end='\n\n'
			)

	@contextmanager
	def cluster_ssh(self):
		"""Open a ssh connection to the cluster master as a subprocess."""
		try:
			cmd = ['sshpass', '-p', self.password, 'ssh', '-o', 'StrictHostKeyChecking=no', self.master_ssh_login()]
			print('Connecting to virtual maching:', ' '.join(cmd))
			proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
		except subprocess.CalledProcessError:
			print('Your SSH connection to the cluster was unsuccessful. '
				  'Try `ssh {}` to confirm that you can do so '
				  'without any prompts.'.format(self.master_ssh_login()))
			raise
		yield proc
		proc.terminate()

	def get_key_path(self):
		return os.path.join(os.environ['HOME'], '.ssh', 'id_rsa')

	def master_ssh_login(self):
		return '{}@{}'.format(
			self.username,
			self.public_ip()
		)

	def scp_to_master(self, local_path, remote_path):
		"""Utility function to copy a file to the cluster's master node."""
		address = self.master_ssh_login()
		try:
			subprocess.check_output([
				'sshpass',
				'-p',
				self.password,
				'scp',
				'-o', 
				'StrictHostKeyChecking=no',
				local_path,
				'{}:./{}'.format(address, remote_path)
			])
		except subprocess.CalledProcessError:
			traceback.print_exc()
			print('It looks like an scp command failed.')
			print('Make sure you can ssh into the server without prompts.')
			print('Please run the following command to try it:')
			print('ssh {}'.format(address))
			sys.exit(1)

	def tunnelforwarding(self):
		ip_addr = self.public_ip()
		tunnel_remote_port = 8889
		tunnel_local_port = 8880
		tunnel_host = '127.0.0.1'
		try:
			server = SSHTunnelForwarder(
				ip_addr,
				ssh_username=self.username,
				ssh_password=self.password,
				remote_bind_address=(tunnel_host, tunnel_remote_port),
				local_bind_address=(tunnel_host, tunnel_local_port)
			)
			server.start()
			print(server.local_bind_port)  # show assigned local port
			#server.stop()
		except HandlerSSHTunnelForwarderError:
			traceback.print_exc()
			print('Opening SSH tunnel failed.')
			print('Please try the following command in a terminal:')
			print('ssh -N -L {local_host}:{local_port}:{remote_host}:{remote_port} {username}@{addr}'.format(
				remote_host=tunnel_host,
				remote_port=tunnel_remote_port,
				local_host=tunnel_host,
				local_port=tunnel_local_port,
				username=self.username,
				addr=ip_addr,
			))
			sys.exit(1)

	# Arg sharename: when not specified, default_fileshare is created or used
	def mount_shares(self, sharename=None):
		"""Mount a file share on all the machines in the cluster.
		For docs on how this is done, see:
		https://docs.microsoft.com/en-us/azure/container-service/container-service-dcos-fileshare
		"""
		print('Mounting file share on VM')
		key_file = os.path.basename(self.get_key_path())
		with io.open(os.path.join(SCRIPTS_DIR, 'cifsMountTemplate.sh')) as cifsMount_template, \
			 io.open(os.path.join(SCRIPTS_DIR, 'cifsMount.sh'), 'w', newline='\n') as cifsMount:
			if not sharename is None:
				cifsMount.write(
					cifsMount_template.read().format(
						storageacct=self.storage.account.name,
						sharename=sharename,
						username=self.username,
						storageacct_password=self.storage.key,
					)
				)
				self.fileshares.append(sharename)
			else:
				cifsMount.write(
					cifsMount_template.read().format(
						storageacct=self.storage.account.name,
						sharename=self.storage.default_share,
						username=self.username,
						storageacct_password=self.storage.key,
					)
				)
				self.fileshares.append('share')
		self.scp_to_master(os.path.join(SCRIPTS_DIR, 'cifsMount.sh'), '')
		self.scp_to_master(os.path.join(SCRIPTS_DIR, 'mountShares.sh'), '')
		self.scp_to_master(self.get_key_path(), key_file)
		with self.cluster_ssh() as proc:
			print('ssh to the vm...')
			print('chmod')
			proc.stdin.write('chmod 600 {}\n'.format(key_file).encode('ascii'))
			proc.stdin.write(b'eval ssh-agent -s\n')
			proc.stdin.write('ssh-add {}\n'.format(key_file).encode('ascii'))
			mountShares_cmd = 'sh mountShares.sh\n'
			print('mounting fileshare...')
			print('Running mountShares on remote master. Cmd:', mountShares_cmd, sep='\n')
			proc.stdin.write(mountShares_cmd.encode('ascii'))
			out, err = proc.communicate(input=b'exit\n')
		print('Finished mounting shares.')
		self._format_proc_output('Stdout:', out)
		self._format_proc_output('Stderr:', err)
		print("from mount def" + str(self.fileshares))

	def unmount_share(self, sharename):
		key_file = os.path.basename(self.get_key_path())
		with io.open(os.path.join(SCRIPTS_DIR, 'cifsUnmountTemplate.sh')) as cifsUnmount_template, \
			 io.open(os.path.join(SCRIPTS_DIR, 'cifsUnmount.sh'), 'w', newline='\n') as cifsUnmount:
			cifsUnmount.write(
				cifsUnmount_template.read().format(
					sharename=sharename,
				)
			)
			self.fileshares.remove(sharename)
		self.scp_to_master(os.path.join(SCRIPTS_DIR, 'cifsUnmount.sh'), '')
		self.scp_to_master(self.get_key_path(), key_file)
		with self.cluster_ssh() as proc:
			print('ssh to the vm...')
			print('chmod')
			proc.stdin.write('chmod 600 {}\n'.format(key_file).encode('ascii'))
			proc.stdin.write(b'eval ssh-agent -s\n')
			proc.stdin.write('ssh-add {}\n'.format(key_file).encode('ascii'))
			umount_cmd = 'sh cifsUnmount.sh\n'
			print('Umount. Cmd:', umount_cmd, sep='\n')
			proc.stdin.write(umount_cmd.encode('ascii'))
			out, err = proc.communicate(input=b'exit\n')
		print('Finished unmount.')
		self._format_proc_output('Stdout:', out)
		self._format_proc_output('Stderr:', err)

	def mount_n_tunnel(self, sharename):
		self.mount_shares(sharename)
		self.tunnelforwarding()

	def deploy(self):
		self.compute.create_vm()

	def deploy_image(self, image, image_resource_group):
		self.compute.create_vm(image=image, image_resource_group=image_resource_group)

	def start(self):
		self.compute.start_vm()

	def stop(self):
		self.compute.deallocate_vm()	


	def list_shares(self):
		shares = self.storage.list_shares()
		result = {}
		for share in shares:
			result[share] = self.storage.list_directories_and_files(share)
		return result

	def upload_file(self, path, sharename=None):
		self.storage.upload_file(path, sharename)

	def create_share(self, sharename):
		self.storage.create_share(sharename)

	def public_ip(self):
		return self.compute.public_ip_addr

	def get_mounted_fileshares(self):
		print("get mounted fileshares" + str(self.fileshares))
		return self.fileshares