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
		vmoption=request.form['vmoption']
		print (vmname, " ", username, " ", password, " ", vmoption)

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
			deployer.deploy_new()
			flash('' + vmname + ' created. Find your new vm in the available vm list below.')
			return redirect(url_for('hello'))
		else:
			flash('All the form fields are required. ')
 
	return render_template('hello.html', form=form, vmlist=vmlist, datalist=datalist)

@app.route('/manage-vm/<string:vm>/', methods=['GET', 'POST'])
def manage_virtualmachine(vm):
	vm_name = vm
	resource_group = vm
	storage_account = vm
	deployer = VirtualMachineDeployer(
				ClientArgs(cred, sub_id),
				vm_name, resource_group, storage_account,
			)
	filesharelist = deployer.list_shares()
	ipaddr = deployer.public_ip()
	if request.method=='POST':
		if 'start' in request.form:
			print('start vm')
			deployer.deploy()
			ipaddr = deployer.public_ip()
			flash('VM Started.')
		if 'stop' in request.form:
			print("stop vm deployment")
			deployer.stop()
			ipaddr = ''
			flash('Virtual Machine deployment stopped.')
		if 'mount' in request.form:
			sharename = request.form.get('mount','')
			print (sharename + "is selected.")
			deployer.mount_n_tunnel(sharename)
			ipaddr = deployer.public_ip()
			flash('Fileshare mounted.')
		if 'opennotebook' in request.form:
			deployer.tunnelforwarding()
			print("open jupyter notebook")
			#open_jupy_notebook(ipaddr)

	return render_template('manage_vm.html', vm=vm, ipaddr=ipaddr, filesharelist=filesharelist)
	#start_vm(client.compute, vm, vm)
	#ipaddr = get_vm_ip_address(client.network, vm, vm)
	#return render_template('manage_vm.html', vm=vm)

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