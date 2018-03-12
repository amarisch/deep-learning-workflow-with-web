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