from utils import *

def create_resource_group(client, groupname):
	print('Create Resource Group')
	resource_group_params = {'location':'westus'}
	result = client.resource_groups.create_or_update(groupname, resource_group_params)
	print_item(result)
	return result

# TODO
def update_resource_group(client, groupname):
	print('Update Resource Group')
	resource_group_params = {'location':'westus'}
	print_item(client.resource_groups.create_or_update(groupname, resource_group_params))

def delete_resource_group(client, groupdname):
    print('Delete Resource Group')
    delete_async_operation = client.resource_groups.delete(groupdname)
    delete_async_operation.wait()
    print("\nDeleted: {}".format(groupdname))

def print_group_resource(client, groupname):
	for item in client.resources.list_by_resource_group(groupname):
		print_item(item)

# TODO
def print_groups(client):
	return