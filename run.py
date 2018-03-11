"""
Manage Azure VM for AI and Deep Learning tools
"""

import os
import sys
import json
import traceback

from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.storage import StorageManagementClient

from haikunator import Haikunator

from prompt_toolkit import prompt

from utils import *
from manageresource import *
from managevm import *
from virtualmachinedeployer import VirtualMachineDeployer

"""
AZURE_TENANT_ID: your Azure Active Directory tenant id or domain
AZURE_CLIENT_ID: your Azure Active Directory Application Client ID
AZURE_CLIENT_SECRET: your Azure Active Directory Application Secret
AZURE_SUBSCRIPTION_ID: your Azure Subscription Id
"""

CLIENT_ID = 0 # application ID
TENANT_ID = 0
CLIENT_SECRET = 0
SUBSCRIPTION_ID = 0

WEST_US = 'westus'

ClientArgs = namedtuple('ClientArgs', ['credentials', 'subscription_id'])

def run():
	#credentials, subscription_id = get_credentials()
	#credentials, subscription_id = get_credentials_from_file('id.txt')

	vm_image = 'azdeeplearningvm'
	resource_group = 'azdeeplearningvm'
	storage_account = 'azdeeplearningvm'


	deployer = VirtualMachineDeployer(
        ClientArgs(get_credentials_from_file('id.txt')),
        vm_image,
        resource_group,
        storage_account,
    )

    deployer.deploy()
    print('\nVirtual Machine at http://{}'.format(deployer.public_ip()))
    print('Response:')
    print(requests.get('http://{}'.format(deployer.public_ip())).text)


	#resource_client = ResourceManagementClient(credentials, subscription_id)
	#compute_client = ComputeManagementClient(credentials, subscription_id)
	#network_client = NetworkManagementClient(credentials, subscription_id)
	#storage_client = StorageManagementClient(credentials, subscription_id)

	#options = prompt('Press r to manage resource/groups and v to manage virtual machines:')

	#create_vm(resource_client, compute_client, network_client, storage_client, "pylinux")
	#start_vm(compute_client, "pylinux", "pylinux")
	#list_vm_usage_info(network_client, "pylinux", "pylinux")
	#get_vm(compute_client, "pylinux", "pylinux")
	# action = prompt('Press c to continue')
	# while action != 'c':
	# 	action = prompt('Press c to continue: ')
	# action = prompt('Press s to stop the vm (still charges computing resources) or d to deallocate the vm: ')
	# if action is 's':
	# 	stop_vm(compute_client, 'pydatascience', 'pydatascience')
	# if action is 'd':
	# 	deallocate_vm(compute_client, 'pydatascience', 'pydatascience')

	#delete_resource_group(resource_client, 'pydatascience')


def get_credentials():
	SUBSCRIPTION_ID = prompt('Enter your Subscription ID: ')
	TENANT_ID = prompt('Enter your Tenant ID: ')
	CLIENT_ID = prompt('Enter your Client/Service Principal Application ID: ')
	CLIENT_SECRET = prompt('Enter your Service Principal password: ')

	credentials = ServicePrincipalCredentials(
		client_id=CLIENT_ID,
		secret=CLIENT_SECRET,
		tenant=TENANT_ID
	)
	return credentials, SUBSCRIPTION_ID

def get_credentials_from_file(filename):
	with open(filename, 'r') as f:
		SUBSCRIPTION_ID = f.readline().strip()
		TENANT_ID = f.readline().strip()
		CLIENT_ID = f.readline().strip()
		CLIENT_SECRET = f.readline().strip()

	credentials = ServicePrincipalCredentials(
		client_id=CLIENT_ID,
		secret=CLIENT_SECRET,
		tenant=TENANT_ID
	)

	return credentials, SUBSCRIPTION_ID

if __name__ == '__main__':
	run()


	# answer = prompt('Give me some input: ')
	# print('You said: %s' % answer)