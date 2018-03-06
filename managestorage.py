import azure.mgmt.storage
import azure.mgmt.compute
from azure.mgmt.storage.models import StorageAccountCreateParameters
from azure.mgmt.storage.models import Sku, SkuName, Kind

LOCATION = 'westus'

# Creates a storage account
def create_storage_account(storage_client, group_name, storage_name):
	print('\nCreate Storage Account')
	result = storage_client.storage_accounts.create(
		group_name,
		storage_name,
		# {
		# 	'location': REGION,
		#     'account_type': 'standard_lrs',
		# }
		StorageAccountCreateParameters(
			sku=Sku(SkuName.standard_ragrs),
			kind=Kind.storage,
			location=LOCATION
		)
	)
	result.wait() # async operation

# TODO: create more data disk types
def create_datadisk_parameters(datadisk_type):
	"""Create the datadisk parameters structure.
	"""
	if datadisk_type=='all':
		return {
				"createOption": "Copy",
				"sourceResourceId": "/subscriptions/9fe8d865-a10d-423e-849b-eb2b529102f5/resourceGroups/pylinux/providers/Microsoft.Compute/disks/pylinux"
				}
	elif datadisk_type=='machinelearning':
		return {
				"createOption": "Copy",
				"sourceResourceId": "/subscriptions/9fe8d865-a10d-423e-849b-eb2b529102f5/resourceGroups/pylinux/providers/Microsoft.Compute/disks/pylinux"
				}
	elif datadisk_type=='deeplearning':
		return {
				"createOption": "Copy",
				"sourceResourceId": "/subscriptions/9fe8d865-a10d-423e-849b-eb2b529102f5/resourceGroups/pylinux/providers/Microsoft.Compute/disks/pylinux"
				}
	else:
		return {
				'create_option': 'Empty'
				}


# Creates a data disk
# input: data_disk_name
#		 disk_size (in gigabytes)
def create_data_disk(compute_client, group_name, datadisk_type, data_disk_name='mydatadisk1', disk_size=1):
	# Create managed data disk
	print('\nCreate managed Data Disk')
	datadisk_param = create_datadisk_parameters(datadisk_type)
	async_disk_creation = compute_client.disks.create_or_update(
	    group_name,
	    data_disk_name,
	    {
	        'location': LOCATION,
	        'disk_size_gb': disk_size,
	        'creation_data': datadisk_param
	    }
	)
	data_disk = async_disk_creation.result()
	return data_disk.id

# create a managed disk from an existing managed disk in the same or different subscription
# {
#   "name": "myDisk2",
#   "location": "West US",
#   "properties": {
#     "creationData": {
#       "createOption": "Copy",
#       "sourceResourceId": "subscriptions/{subscriptionId}/resourceGroups/myResourceGroup/providers/Microsoft.Compute/disks/myDisk1"
#     }
#   }
# }


# Create a managed disk by importing an unmanaged blob from the same subscription
# {
#   "name": "myDisk",
#   "location": "West US",
#   "properties": {
#     "creationData": {
#       "createOption": "Import",
#       "sourceUri": "https://mystorageaccount.blob.core.windows.net/osimages/osimage.vhd"
#     }
#   }
# }

# Create a managed disk by importing an unmanaged blob from a different subscription.
# {
#   "name": "myDisk",
#   "location": "West US",
#   "properties": {
#     "creationData": {
#       "createOption": "Import",
#       "storageAccountId": "subscriptions/{subscriptionId}/resourceGroups/myResourceGroup/providers/Microsoft.Storage/storageAccounts/myStorageAccount",
#       "sourceUri": "https://mystorageaccount.blob.core.windows.net/osimages/osimage.vhd"
#     }
#   }
# }

# Create a managed disk by copying a snapshot.
# {
#   "name": "myDisk",
#   "location": "West US",
#   "properties": {
#     "creationData": {
#       "createOption": "Copy",
#       "sourceResourceId": "subscriptions/{subscriptionId}/resourceGroups/myResourceGroup/providers/Microsoft.Compute/snapshots/mySnapshot"
#     }
#   }
# }