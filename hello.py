"""
Azure VM for AI and Deep Learning tools
"""

import os
import json
import traceback

from haikunator import Haikunator

from prompt_toolkit import prompt

from flask import Flask, flash, redirect, render_template, request, session, abort, url_for

from utils import *
from manageresource import *
from managevm import *

# Forms for Flask
from Forms import ReusableForm, SimpleForm

# App config.
DEBUG = True
app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = '7d441f27d441f27567d441f2b6176a'

WEST_US = 'westus'

"""
AZURE_TENANT_ID: your Azure Active Directory tenant id or domain
AZURE_CLIENT_ID: your Azure Active Directory Application Client ID
AZURE_CLIENT_SECRET: your Azure Active Directory Application Secret
AZURE_SUBSCRIPTION_ID: your Azure Subscription Id

'id.txt' contains the above information
"""
client = get_azure_client('newid.txt')


@app.route("/", methods=['GET', 'POST'])
def hello():

    vmlist = list_available_vms(client)

    datalist = list_available_datasets()

    form = ReusableForm(request.form)
 
    print (form.errors)
    if request.method == 'POST':
        username=request.form['username']
        password=request.form['password']
        vmname=request.form['vmname']
        datadisk=request.form['datadisk']
        print (vmname, " ", username, " ", password, " ", datadisk)
 
        if form.validate():
            # Save the comment here.
            #flash('Creating VM ' + vmname + ' ...')
            #create_vm(client.resource, client.compute, client.network, client.storage, vmname, datadisk)
            flash('' + vmname + ' created. Find your new vm in the available vm list below.')
            return redirect(url_for('hello'))
        else:
            flash('All the form fields are required. ')
 
    return render_template('hello.html', form=form, vmlist=vmlist, datalist=datalist)

@app.route('/manage-vm/<string:vm>/', methods=['GET', 'POST'])
def manage_virtualmachine(vm):
	ipaddr = ''
	if request.method=='POST':
		if 'start' in request.form:
			print('start vm')
			#start_vm(client.compute, vm, vm)
			result = get_vm_status(client.compute, vm, vm)
			print (result)
			ipaddr = get_vm_ip_address(client.network, vm, vm)
			flash('VM Started.')
		if 'stop' in request.form:
			print("stop vm")
			stop_vm(client.compute, vm, vm)
			ipaddr = ''
			flash('VM Stopped (still using computing resources).')
		if 'deallocate' in request.form:
		 	print("deallo vm")
		 	deallocate_vm(client.compute, vm, vm)
		 	ipaddr = ''
		 	flash('VM Stopped and deallocated.')
		# if 'attach' in request.form:
		# 	print('Attach data disk')
		# 	attach_data_disk(client.compute, vm, vm, vm)
		# if 'detach' in request.form:
		# 	print('Detach data disk')
		# 	detach_data_disk(client.compute, vm, vm, vm)
		if 'opennotebook' in request.form:
		 	print("open jupyter notebook")
		 	#open_jupy_notebook(ipaddr)

	return render_template('manage_vm.html', vm=vm, ipaddr=ipaddr)
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
 
@app.route("/members")
def members():
    return "Members"
 
@app.route("/members/<string:name>/")
def getMember(name):
    return name
 
if __name__ == "__main__":
    #app.run()
    app.run(host='0.0.0.0', port=1048)