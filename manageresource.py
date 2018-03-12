from utils import *

def create_resource_group(client, groupname):
	print('Create Resource Group')
	resource_group_params = {'location':'westus'}
	result = client.resource_groups.create_or_update(groupname, resource_group_params)
	return result

def delete_resource_group(client, groupdname):
    print('Delete Resource Group')
    delete_async_operation = client.resource_groups.delete(groupdname)
    delete_async_operation.wait()
    print("\nDeleted: {}".format(groupdname))
