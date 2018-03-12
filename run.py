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
from virtualmachinedeployer import VirtualMachineDeployer

ClientArgs = namedtuple('ClientArgs', ['credentials', 'subscription_id'])

def run(id_filename):

	# Change these parameters according to your Azure subscription
	vm_name = 'azuremachine'
	resource_group = vm_name
	storage_account = vm_name
	sharename = 'deeplearningfileshare'

	cred, sub_id = get_credentials_from_file(id_filename)
	deployer = VirtualMachineDeployer(
		ClientArgs(cred, sub_id),
		vm_name,
		resource_group,
		storage_account,
	)

	deployer.deploy()

	#deployer.mount_n_tunnel(sharename)
	deployer.list_shares()

	#filename = 'test.txt'
	#deployer.upload_file(filename)
	#print('\nVirtual Machine at http://{}'.format(deployer.public_ip()))

if __name__ == '__main__':
	run(sys.argv[1])
