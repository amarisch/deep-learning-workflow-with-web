"""
Azure VM for AI and Deep Learning tools
"""

import os
import json
import traceback

from haikunator import Haikunator

from prompt_toolkit import prompt

from flask import Flask, flash, redirect, render_template, request, session, abort

from utils import *
from manageresource import *
from managevm import *

# Forms for Flask
from Forms import ReusableForm

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
client = get_azure_client('id.txt')


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
        print (username, " ", vmname, " ", password)
 
        if form.validate():
            # Save the comment here.
            flash('Creating VM ' + vmname + ' ...')
        else:
            flash('All the form fields are required. ')
 
    return render_template('hello.html', form=form, vmlist=vmlist, datalist=datalist)

@app.route('/manage-vm/<string:vm>/', methods=['GET', 'POST'])
def manage_virtualmachine(vm):
	#start_vm(client.compute, vm, vm)
	ipaddr = get_vm_ip_address(client.network, vm, vm)
	return render_template('manage_vm.html', vm=vm, ipaddr=ipaddr)

@app.route('/list-resources/')
def list_resources():
    for item in client.resource.resource_groups.list():
        print_item(item)
    return 'Listed all resoures'
 
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