from subprocess import call

from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.storage import StorageManagementClient

from prompt_toolkit import prompt

class AzureClient(object):
    """An Azure client class that allows us to manage Azure services via AZure's python SDK:

    Attributes:
        resource: 
        compute:
        network:
        storage:
    """
    def __init__(self, subscription_id, resource, compute, network, storage):
        self.subscription_id = subscription_id
        self.resource = resource
        self.compute = compute
        self.network = network
        self.storage = storage

def get_azure_client(filename):
    credentials, subscription_id = get_credentials_from_file(filename)

    resource = ResourceManagementClient(credentials, subscription_id)
    compute = ComputeManagementClient(credentials, subscription_id)
    network = NetworkManagementClient(credentials, subscription_id)
    storage = StorageManagementClient(credentials, subscription_id)
    return AzureClient(subscription_id, resource, compute, network, storage)

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

def list_available_datasets():
    datalist = [
                ['Titanic', 'Simple Machine Learning Problem for disaster', 'https://www.kaggle.com/c/titanic'],
                ['Zillow Zestimate', 'Can you improve the algorithm that changed the world of real estate?', 'https://www.kaggle.com/c/zillow-prize-1'],
                ['Speech Challenge', 'Hands-on Practice with Tensorflow', 'https://www.kaggle.com/c/tensorflow-speech-recognition-challenge'],
            ]
    return datalist

def open_jupy_notebook(ipaddr):
    return_code = call("echo Hello World", shell=True)
    command = "ssh -N -f -L localhost:8888:localhost:8889 azureadminuser@" + ipaddr
    return_code = call(command, shell=True)            

def print_item(group):
    """Print a ResourceGroup instance."""
    print("\tName: {}".format(group.name))
    print("\tId: {}".format(group.id))
    print("\tLocation: {}".format(group.location))
    print("\tTags: {}".format(group.tags))
    print_properties(group.properties)

def print_properties(props):
    """Print a ResourceGroup propertyies instance."""
    if props and props.provisioning_state:
        print("\tProperties:")
        print("\t\tProvisioning State: {}".format(props.provisioning_state))
        print("\t\t{}".format(props.properties))
    print("\n\n")
