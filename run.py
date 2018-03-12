"""
Run Virtual Machine Deployer from command line
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

from collections import namedtuple

from utils import *
from manageresource import *
from managevm import *
from virtualmachinedeployer import VirtualMachineDeployer

ClientArgs = namedtuple('ClientArgs', ['credentials', 'subscription_id'])

def run():
	vm_name = 'azdeeplearningvm'
	resource_group = 'azdeeplearningvm'
	storage_account = 'azdeeplearningvm'

	cred, sub_id = get_credentials_from_file('newid.txt')
	deployer = VirtualMachineDeployer(
		ClientArgs(cred, sub_id),
		vm_name,
		resource_group,
		storage_account,
	)

	#deployer.deploy()
	#deployer.mount_shares(sharename='deeplearningfileshare')
	deployer.list_shares()
	#filename = 'test.txt'
	#deployer.upload_file(filename)
	#print('\nVirtual Machine at http://{}'.format(deployer.public_ip()))

if __name__ == '__main__':
	run()
