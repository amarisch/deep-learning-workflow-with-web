"""
Azure VM for AI and Deep Learning tools
"""

import os
import sys
import json
import traceback

from prompt_toolkit import prompt
from collections import namedtuple

from utils import *
from virtualmachinedeployer import VirtualMachineDeployer

# Forms for Flask
from Forms import ReusableForm, SimpleForm
from flask import Flask, flash, redirect, render_template, request, session, abort, url_for

# App config.
DEBUG = True
app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = '7d441f27d441f27567d441f2b6176a'

ClientArgs = namedtuple('ClientArgs', ['credentials', 'subscription_id'])
cred, sub_id = get_credentials_from_file(sys.argv[1])


@app.route("/", methods=['GET', 'POST'])
def hello():
	vmlist = list_vm_in_subscription(cred, sub_id)
	datalist = list_available_datasets()
	form = ReusableForm(request.form)
	print (form.errors)

	if request.method == 'POST':
		username=request.form['username']
		password=request.form['password']
		vmname=request.form['vmname']
		print (vmname, " ", username, " ", password)

		resource_group = vmname
		storage_account = vmname
		if form.validate():
			# Deploy a VirtualMachineDeployer and create VM
			deployer = VirtualMachineDeployer(
				ClientArgs(cred, sub_id),
				vmname,
				resource_group,
				storage_account,
			)
			deployer.deploy()
			flash('' + vmname + ' created. Find your new vm in the available vm list below.')
			return redirect(url_for('hello'))
		else:
			flash('All the form fields are required. ')
 
	return render_template('hello.html', form=form, vmlist=vmlist, datalist=datalist)

deployer_list = {}

@app.route('/manage-vm/<string:vm>/', methods=['GET', 'POST'])
def manage_virtualmachine(vm):
	if not vm in deployer_list:
		vm_name = vm
		resource_group = vm
		storage_account = vm
		deployer = VirtualMachineDeployer(
					ClientArgs(cred, sub_id),
					vm_name, resource_group, storage_account,
				)
		deployer_list[vm] = deployer
	else:
		deployer = deployer_list.get(vm)
	filesharelist = deployer.list_shares()
	ipaddr = deployer.public_ip()
	print(ipaddr)
	mountedfileshares = deployer.get_mounted_fileshares()
	if request.method=='POST':
		if 'start' in request.form:
			print('start vm')
			deployer.start()
			ipaddr = deployer.public_ip()
			flash('VM Started.')
		if 'stop' in request.form:
			print("stop vm deployment")
			deployer.stop()
			ipaddr = ''
			deployer_list.pop(vm)
			flash('Virtual Machine deployment stopped.')
		if 'mount' in request.form:
			sharename = request.form.get('mount','')
			print (sharename + "is selected.")
			deployer.mount_shares(sharename)
			ipaddr = deployer.public_ip()
			flash('Fileshare mounted.')
			return redirect(url_for('manage_virtualmachine', vm=vm))
		if 'unmount' in request.form:
			sharename = request.form.get('unmount','')
			deployer.unmount_share(sharename)
			flash('Fileshare unmounted.')
			return redirect(url_for('manage_virtualmachine', vm=vm))
		if 'file_upload' in request.form:
			filelist = request.form.getlist('files')
			sharename = request.form.get('file_upload','')
			print(sharename)
			cur_dir = os.getcwd()
			for filename in filelist:
				filepath = cur_dir + '/' + filename
				deployer.upload_file(filepath, sharename)
				print("upload file " + filename)
			flash('Files uploaded.')
			return redirect(url_for('manage_virtualmachine', vm=vm))
		if 'createfileshare' in request.form:
			newsharename = request.form.get('newsharename','')
			deployer.create_share(newsharename)
			return redirect(url_for('manage_virtualmachine', vm=vm))
		if 'opennotebook' in request.form:
			print("open jupyter notebook")
			#open_jupy_notebook(ipaddr)
		if 'tunnel' in request.form:
			deployer.tunnelforwarding()
	return render_template('manage_vm.html', vm=vm, ipaddr=ipaddr, filesharelist=filesharelist, mountedfileshares=mountedfileshares)

# @app.route('/list-resources/')
# def list_resources():
#     for item in client.resource.resource_groups.list():
#         print_item(item)
#     return 'Listed all resoures'
 
# @app.route("/hello/<string:name>/")
# def hello(name):
#     quote = "opportunities are for those who are ready"
#     return render_template(
#         'test.html',**locals())

if __name__ == "__main__":
	app.run(host='0.0.0.0', port=1048)