from manageresource import *
from managestorage import *
# import azure.mgmt.storage.models
# import azure.mgmt.storage.models.AccountType
# import azure.mgmt.compute.models
# import azure.mgmt.compute.models.VirtualMachineSizeTypes
# import azure.mgmt.compute.models.CachingTypes
# import azure.mgmt.compute.models.DiskCreateOptionTypes
import azure.mgmt.storage
import azure.mgmt.compute
from azure.mgmt.storage.models import StorageAccountCreateParameters
from azure.mgmt.storage.models import Sku, SkuName, Kind
from msrestazure.azure_exceptions import CloudError
from azure.mgmt.compute import ComputeManagementClient



VM_REFERENCE = {
    'linux': {
        'publisher': 'Canonical',
        'offer': 'UbuntuServer',
        'sku': '16.04.0-LTS',
        'version': 'latest'
    },
    'linux_datascience': {
        'publisher': 'microsoft-ads',
        'offer': 'linux-data-science-vm-ubuntu',
        'sku': 'linuxdsvmubuntu',
        'version': '1.1.7'
    },
    'windows': {
        'publisher': 'MicrosoftWindowsServerEssentials',
        'offer': 'WindowsServerEssentials',
        'sku': 'WindowsServerEssentials',
        'version': 'latest'
    }
}

# Create a Linux VM
# The supplied password must be between 6-72 characters long 
# and must satisfy at least 3 of password complexity requirements from the following: 
# 1) Contains an uppercase character
# 2) Contains a lowercase character
# 3) Contains a numeric digit
# 4) Contains a special character
# 5) Control characters are not allowed
def create_linux_vm(network_client, compute_client, group_name, vm_name='myvm', username='myuser', pw='Mypassword1', location='westus'):

	# create a NIC
	nic = create_nic(network_client, group_name)

	# Create Linux VM
	print('\nCreating Linux Virtual Machine')
	vm_parameters = create_vm_parameters(nic.id, VM_REFERENCE['linux'], vm_name, username, pw, location)
	async_vm_creation = compute_client.virtual_machines.create_or_update(
		group_name, vm_name, vm_parameters)
	async_vm_creation.wait()
	# TODO check that the VM has started

def deallocate_vm(compute_client, group_name, vm_name):
	# Deallocating the VM
	print('\nDeallocating the VM')
	async_vm_deallocate = compute_client.virtual_machines.deallocate(group_name, vm_name)
	async_vm_deallocate.wait()

def start_vm(compute_client, group_name, vm_name):
	# Start the VM
	print('\nStart VM')
	async_vm_start = compute_client.virtual_machines.start(group_name, vm_name)
	async_vm_start.wait()

def restart_vm(compute_client, group_name, vm_name):
	# Start the VM
	print('\nRestart VM')
	async_vm_restart = compute_client.virtual_machines.restart(group_name, vm_name)
	async_vm_restart.wait()	

def stop_vm(compute_client, group_name, vm_name):
	# Stop the VM
	print('\nStop VM')
	async_vm_stop = compute_client.virtual_machines.power_off(group_name, vm_name)
	async_vm_stop.wait()

def delete_vm(compute_client, group_name, vm_name):
	# Delete VM
	print('\nDelete VM')
	async_vm_delete = compute_client.virtual_machines.delete(group_name, vm_name)
	async_vm_delete.wait()

def attach_data_disk(compute_client, group_name, vm_name, data_disk_name, data_disk_id):
	print('\nAttach Data Disk')
	virtual_machine = compute_client.virtual_machines.get(group_name, vm_name)
	virtual_machine.storage_profile.data_disks.append({
		'lun': 12,
		'name': data_disk_name,
		'create_option': 'Attach',
		'managed_disk': {
			'id': data_disk_id
		}
	})
	async_disk_attach = compute_client.virtual_machines.create_or_update(
		group_name,
		virtual_machine.name,
		virtual_machine
	)
	async_disk_attach.wait()

def detach_data_disk(compute_client, group_name, vm_name, data_disk_name):
	print('\nDetach Data Disk')
	virtual_machine = compute_client.virtual_machine.get(group_name, vm_name)
	data_disks = virtual_machine.storage_profile.data_disks
	data_disks[:] = [disk for disk in data_disks if disk.name != 'mydatadisk1']
	async_vm_update = compute_client.virtual_machines.create_or_update(
		group_name,
		vm_name,
		virtual_machine
	)
	virtual_machine = async_vm_update.result()

# Increases OS disk size
# input: additional_os_disk_size (in GB)
def increase_os_disk_size(compute_client, group_name, vm_name, additional_os_disk_size):
	print('\nUpdate OS disk size by ' + additional_os_disk_size + 'gb')
	virtual_machine = compute_client.virtual_machine.get(group_name, vm_name)	
	os_disk_name = virtual_machine.storage_profile.os_disk.name
	os_disk = compute_client.disks.get(group_name, os_disk_name)
	if not os_disk.disk_size_gb:
		print("\tServer is not returning the OS disk size, possible bug in the server?")
		print("\tAssuming that the OS disk size is 30 GB")
		os_disk.disk_size_gb = 30

	os_disk.disk_size_gb += additional_os_disk_size

	async_disk_update = compute_client.disks.create_or_update(
		group_name,
		os_disk.name,
		os_disk
	)
	async_disk_update.wait()

def list_vm_in_subscription(compute_client):
	# List VMs in subscription
	print('\nList VMs in subscription')
	for vm in compute_client.virtual_machines.list_all():
		print("\tVM: {}".format(vm.name))

def list_vm_in_resource_group(compute_client, group_name):
	print('\nList VMs in resource group')
	for vm in compute_client.virtual_machines.list(group_name):
		print("\tVM: {}".format(vm.name))
		print("\t    {}".format(vm))	

def get_vm_ip_address(network_client, group_name, vm_name):
	public_ip_address = network_client.public_ip_addresses.get(group_name, vm_name)
	print('VM available at {}'.format(public_ip_address.ip_address))
	return public_ip_address.ip_address

# TODO error handling when something has ben created already
def create_nic(network_client, group_name, vnet_name='myvnet', subnet_name='mysubnet', ip_name='myip',\
				nic_name='mynic', ip_config_name='default', location='westus'):
	"""Create a Network Interface for a VM.
	"""
	# Create VNet
	print('\nCreate Vnet')
	async_vnet_creation = network_client.virtual_networks.create_or_update(
		group_name,
		vnet_name,
		{
			'location': location,
			'address_space': {
				'address_prefixes': ['10.0.0.0/16']
			}
		}
	)
	async_vnet_creation.wait()

	# Create Subnet
	print('\nCreate Subnet')
	async_subnet_creation = network_client.subnets.create_or_update(
		group_name,
		vnet_name,
		subnet_name,
		{'address_prefix': '10.0.0.0/24'}
	)
	async_subnet_creation.wait()
	subnet_info = network_client.subnets.get(group_name, vnet_name, subnet_name)


	# Create public ip address
	print('\nCreate Public IP Address')
	result = network_client.public_ip_addresses.create_or_update(
		group_name,
		ip_name,
		{	'location': location,
			'public_ip_allocation_method': 'Dynamic',
			'idle_timeout_in_minutes': 4
		}
	)
	result.wait()
	public_ip_address = network_client.public_ip_addresses.get(group_name, ip_name)
	public_ip_id = public_ip_address.id

	# Create NIC
	print('\nCreate NIC')
	async_nic_creation = network_client.network_interfaces.create_or_update(
		group_name,
		nic_name,
		{
			'location': location,
			'ip_configurations': [{
				'name': ip_config_name,
				'subnet': {
					'id': subnet_info.id
				},
				'public_ip_address': {
					'id': public_ip_id
				}
			}]
		}
	)
	async_nic_creation.wait()
	result = network_client.network_interfaces.get(group_name, nic_name)
	return result

# Creates a data disk
# input: data_disk_name
#		 disk_size (in gigabytes)
def create_data_disk(compute_client, group_name, data_disk_name='mydatadisk1', disk_size=1):
	LOCATION = 'westus'

	# Create managed data disk
	print('\nCreate (empty) managed Data Disk')
	async_disk_creation = compute_client.disks.create_or_update(
	    group_name,
	    data_disk_name,
	    {
	        'location': LOCATION,
	        'disk_size_gb': disk_size,
	        'creation_data': {
	            'create_option': 'Empty'
	        }
	    }
	)
	data_disk = async_disk_creation.result()
	return data_disk.id

def create_vm_parameters(nic_id, vm_reference, vm_name, os_disk_name, username, pw, location):
	"""Create the VM parameters structure.
	"""
	return {
		'location': location,
		'os_profile': {
			'computer_name': vm_name,
			'admin_username': username,
			'admin_password': pw
		},
		'hardware_profile': {
			'vm_size': 'Standard_DS1_v2'
		},
		'storage_profile': {
			'image_reference': {
				'publisher': vm_reference['publisher'],
				'offer': vm_reference['offer'],
				'sku': vm_reference['sku'],
				'version': vm_reference['version']
		    },
			# 'osDisk': {
			# 	'caching': 'ReadWrite',
			# 	'managedDisk': {
			# 		'storageAccountType': 'Standard_LRS'
			# 	},
			# 	'name': os_disk_name,
			# 	'createOption': 'FromImage'
			# }
		},
		# az vm image accept-terms --urn microsoft-ads:linux-data-science-vm-ubuntu:linuxdsvmubuntu:1.1.7
	  #   'plan': {
			# 'name': vm_reference['sku'],
			# 'product': vm_reference['offer'],
			# 'publisher': vm_reference['publisher'],
	  #   },
		'network_profile': {
			'network_interfaces': [{
				'id': nic_id,
			}]
		},
	}

def create_vm(resource_client, compute_client, network_client, storage_client, basename):

	BASE_NAME = basename

	GROUP_NAME = BASE_NAME
	STORAGE_NAME = BASE_NAME
	VIRTUAL_NETWORK_NAME = BASE_NAME
	SUBNET_NAME = BASE_NAME
	NETWORK_INTERFACE_NAME = BASE_NAME
	VM_NAME = BASE_NAME
	OS_DISK_NAME = BASE_NAME
	DATA_DISK_NAME = BASE_NAME
	PUBLIC_IP_NAME = BASE_NAME
	COMPUTER_NAME = BASE_NAME
	ADMIN_USERNAME='azureadminuser'
	ADMIN_PASSWORD='Azureadminpw1'
	REGION = 'westus'

	# 1. Create a resource group
	result = create_resource_group(resource_client, GROUP_NAME)

	# 2. Create Azure storage account
	print('\nCreate Storage Account')
	result = storage_client.storage_accounts.create(
		GROUP_NAME,
		STORAGE_NAME,
		# {
		# 	'location': REGION,
		#     'account_type': 'standard_lrs',
		# }
		StorageAccountCreateParameters(
			sku=Sku(SkuName.standard_ragrs),
			kind=Kind.storage,
			location=REGION
		)
	)
	result.wait() # async operation

	# 3. Create the network interface using a helper function (defined below)
	nic = create_nic(network_client, GROUP_NAME, VIRTUAL_NETWORK_NAME, SUBNET_NAME, PUBLIC_IP_NAME, \
				NETWORK_INTERFACE_NAME, 'default', REGION)
	nic = network_client.network_interfaces.get(GROUP_NAME, NETWORK_INTERFACE_NAME)

	# 4. Create the virtual machine
	print('\nCreating Linux Virtual Machine')
	vm_parameters = create_vm_parameters(nic.id, VM_REFERENCE['linux'], VM_NAME, OS_DISK_NAME, ADMIN_USERNAME, ADMIN_PASSWORD, REGION)
	async_vm_creation = compute_client.virtual_machines.create_or_update(
		GROUP_NAME, VM_NAME, vm_parameters)
	async_vm_creation.wait()

	# 4. Attach data disk
	print('\nCreate data disk and attach to VM')
	data_disk_id = create_data_disk(compute_client, GROUP_NAME, DATA_DISK_NAME, 10)
	attach_data_disk(compute_client, GROUP_NAME, VM_NAME, DATA_DISK_NAME, data_disk_id)


	# Display the public ip address
	# You can now connect to the machine using SSH
	public_ip_address = network_client.public_ip_addresses.get(GROUP_NAME, PUBLIC_IP_NAME)
	print('VM available at {}'.format(public_ip_address.ip_address))
	print('ssh into the vm with {}@{} and password ({})'.format(ADMIN_USERNAME, public_ip_address.ip_address, ADMIN_PASSWORD))
	print('Run jupyter notebook: jupyter notebook --no-browser --port=8889')
	print('Enable local port forward: ssh -N -f -L localhost:8888:localhost:8889 {}@{}'.format(ADMIN_USERNAME, public_ip_address.ip_address))

# TODO
def create_vm_from_image():
	return

def get_vm(compute_client, group_name, vm_name):
    vm = compute_client.virtual_machines.get(group_name, vm_name, expand='instanceView')
    print("hardwareProfile")
    print("   vmSize: ", vm.hardware_profile.vm_size)
    print("\nstorageProfile")
    print("  imageReference")
    print("    publisher: ", vm.storage_profile.image_reference.publisher)
    print("    offer: ", vm.storage_profile.image_reference.offer)
    print("    sku: ", vm.storage_profile.image_reference.sku)
    print("    version: ", vm.storage_profile.image_reference.version)
    print("  osDisk")
    print("    osType: ", vm.storage_profile.os_disk.os_type.value)
    print("    name: ", vm.storage_profile.os_disk.name)
    print("    createOption: ", vm.storage_profile.os_disk.create_option.value)
    print("    caching: ", vm.storage_profile.os_disk.caching.value)
    print("\nosProfile")
    print("  computerName: ", vm.os_profile.computer_name)
    print("  adminUsername: ", vm.os_profile.admin_username)
    #print("  provisionVMAgent: {0}".format(vm.os_profile.windows_configuration.provision_vm_agent))
    #print("  enableAutomaticUpdates: {0}".format(vm.os_profile.windows_configuration.enable_automatic_updates))
    print("\nnetworkProfile")
    for nic in vm.network_profile.network_interfaces:
        print("  networkInterface id: ", nic.id)
    print("\nvmAgent")
    print("  vmAgentVersion", vm.instance_view.vm_agent.vm_agent_version)
    # print("    statuses")
    # for stat in vm_result.instance_view.vm_agent.statuses:
    #     print("    code: ", stat.code)
    #     print("    displayStatus: ", stat.display_status)
    #     print("    message: ", stat.message)
    #     print("    time: ", stat.time)
    print("\ndisks");
    for disk in vm.instance_view.disks:
        print("  name: ", disk.name)
        print("  statuses")
        for stat in disk.statuses:
            print("    code: ", stat.code)
            print("    displayStatus: ", stat.display_status)
            print("    time: ", stat.time)
    print("\nVM general status")
    print("  provisioningStatus: ", vm.provisioning_state)
    print("  id: ", vm.id)
    print("  name: ", vm.name)
    print("  type: ", vm.type)
    print("  location: ", vm.location)
    print("\nVM instance status")
    for stat in vm.instance_view.statuses:
        print("  code: ", stat.code)
        print("  displayStatus: ", stat.display_status)