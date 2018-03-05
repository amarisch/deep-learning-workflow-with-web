import azure.mgmt.storage
import azure.mgmt.compute
from azure.mgmt.storage.models import StorageAccountCreateParameters
from azure.mgmt.storage.models import Sku, SkuName, Kind


LOCATION = 'westus'

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