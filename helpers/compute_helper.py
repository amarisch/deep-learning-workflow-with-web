import azure.mgmt.compute
from msrestazure.azure_exceptions import CloudError
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.network import NetworkManagementClient

import base64


VM_REFERENCE = {
    'linux': {
        'publisher': 'Canonical',
        'offer': 'UbuntuServer',
        'sku': '16.04.0-LTS',
        'version': 'latest'
    },
    'linux_datascience': {
        'publisher': 'microsoft-ads',
        'offer': 'linux-data-science-vm-ubuntu',
        'sku': 'linuxdsvmubuntu',
        'version': '1.1.7'
    },
    'windows': {
        'publisher': 'MicrosoftWindowsServerEssentials',
        'offer': 'WindowsServerEssentials',
        'sku': 'WindowsServerEssentials',
        'version': 'latest'
    }
}


class ComputeHelper(object):
    """
    ComputeHelper handles computational tasks related to one Azure virtual machine.
    """
    def __init__(self, client_data, resource_helper, name, public_ip_addr=None):
        self.resource_helper = resource_helper
        self.client = ComputeManagementClient(*client_data)
        self.network = NetworkManagementClient(*client_data)
        self.name = name # The name of the vm
        self.subscription_id = client_data.subscription_id
        self._public_ip_addr = public_ip_addr

    @property
    def public_ip_addr(self):
        if self._public_ip_addr is None:
            public_ip_address = self.network.public_ip_addresses.get(self.resource_helper.group.name, self.name)
            self._public_ip_addr = public_ip_address.ip_address
        return self._public_ip_addr


    def start_vm(self):
        # Start the VM
        print('\nStart VM')
        async_vm_start = self.client.virtual_machines.start(self.resource_helper.group.name, self.name)
        async_vm_start.wait()

    def restart_vm(self):
        # Start the VM
        print('\nRestart VM')
        async_vm_restart = self.client.virtual_machines.restart(self.resource_helper.group.name, self.name)
        async_vm_restart.wait() 

    def stop_vm(self):
        # Stop the VM
        print('\nStop VM')
        async_vm_stop = self.client.virtual_machines.power_off(self.resource_helper.group.name, self.name)
        async_vm_stop.wait()

    def deallocate_vm(self):
        # Deallocating the VM
        print('\nDeallocating the VM')
        async_vm_deallocate = self.client.virtual_machines.deallocate(self.resource_helper.group.name, self.name)
        async_vm_deallocate.wait()

    def delete_vm(self):
        # Delete VM
        print('\nDelete VM')
        async_vm_delete = self.client.virtual_machines.delete(self.resource_helper.group.name, self.name)
        async_vm_delete.wait()

    def create_nic(self):
        """Create a Network Interface for a VM.
        """
        group_name = self.resource_helper.group.name
        vnet_name = subnet_name = ip_name = nic_name = self.name
        ip_config_name = 'default'
        location = self.resource_helper.group.location

        # Create VNet
        print('\nCreate Vnet')
        async_vnet_creation = self.network.virtual_networks.create_or_update(
            group_name,
            vnet_name,
            {
                'location': location,
                'address_space': {
                    'address_prefixes': ['10.0.0.0/16']
                }
            }
        )
        async_vnet_creation.wait()

        # Create Subnet
        print('\nCreate Subnet')
        async_subnet_creation = self.network.subnets.create_or_update(
            group_name,
            vnet_name,
            subnet_name,
            {'address_prefix': '10.0.0.0/24'}
        )
        async_subnet_creation.wait()
        subnet_info = self.network.subnets.get(group_name, vnet_name, subnet_name)


        # Create public ip address
        print('\nCreate Public IP Address')
        result = self.network.public_ip_addresses.create_or_update(
            group_name,
            ip_name,
            {   'location': location,
                'public_ip_allocation_method': 'Dynamic',
                'idle_timeout_in_minutes': 4
            }
        )
        result.wait()
        public_ip_address = self.network.public_ip_addresses.get(group_name, ip_name)
        public_ip_id = public_ip_address.id

        # Create NIC
        print('\nCreate NIC')
        async_nic_creation = self.network.network_interfaces.create_or_update(
            group_name,
            nic_name,
            {
                'location': location,
                'ip_configurations': [{
                    'name': ip_config_name,
                    'subnet': {
                        'id': subnet_info.id
                    },
                    'public_ip_address': {
                        'id': public_ip_id
                    }
                }]
            }
        )
        async_nic_creation.wait()

    def create_vm_parameters(self, vm_reference, username, pw, image, image_resource_group):
        """Create the VM parameters structure.
        """

        nic = self.network.network_interfaces.get(self.resource_helper.group.name, self.name)

        # Customize VM creation using cloud config
        # custom_data = b''
        # with open('cloud-init.txt', 'r') as f:
        #     custom_data=bytes(''.join(line for line in f), 'utf-8')
        # custom_data = base64.b64encode(custom_data)

        image_reference = ''
        if not image is None:
            image_id = '/subscriptions/{}/resourceGroups/{}/providers/Microsoft.Compute/images/{}'.format(self.subscription_id, image_resource_group, image)
            image_reference = {
                                'id': image_id
                            }
        else:
            image_reference = {
                    'publisher': vm_reference['publisher'],
                    'offer': vm_reference['offer'],
                    'sku': vm_reference['sku'],
                    'version': vm_reference['version']
                }

        return {
            'location': self.resource_helper.group.location,
            'os_profile': {
                'computer_name': self.name,
                'admin_username': username,
                'admin_password': pw,
                # uncomment this line to enable cloud config
                # 'custom_data': custom_data
            },
            'hardware_profile': {
                'vm_size': 'Standard_DS1_v2'
            },
            'storage_profile': {
                'image_reference': image_reference,
                'osDisk': {
                    'caching': 'ReadWrite',
                    'managedDisk': {
                        'storageAccountType': 'Standard_LRS'
                    },
                    'name': self.name,
                    'createOption': 'FromImage'
                }
            },
            # If using image from Microsoft marketplace, uncomment this section
            # Run this command to find out plan information:
            # az vm image accept-terms --urn microsoft-ads:linux-data-science-vm-ubuntu:linuxdsvmubuntu:1.1.7
          #   'plan': {
                # 'name': vm_reference['sku'],
                # 'product': vm_reference['offer'],
                # 'publisher': vm_reference['publisher'],
          #   },
            'network_profile': {
                'network_interfaces': [{
                    'id': nic.id,
                }]
            },
        }

    # Creates vm
    # fill in fields (image, subscription_id and image_resource_group) if creating a vm from an image
    def create_vm(self, username='azureadminuser', password='Azureadminpw1', image=None, image_resource_group=None):

        group_name = self.resource_helper.group.name

        # VM USER PASSWORD REQUIREMENTS:
        # The supplied password must be between 6-72 characters long 
        # and must satisfy at least 3 of password complexity requirements from the following: 
        # 1) Contains an uppercase character
        # 2) Contains a lowercase character
        # 3) Contains a numeric digit
        # 4) Contains a special character
        # 5) Control characters are not allowed

        ADMIN_USERNAME = username
        ADMIN_PASSWORD = password

        # Create the network interface using a helper function (defined below)
        self.create_nic()

        # Create the virtual machine
        print('\nCreating Linux Virtual Machine')
        vm_parameters = self.create_vm_parameters(VM_REFERENCE['linux'], ADMIN_USERNAME, ADMIN_PASSWORD, image, image_resource_group)
        async_vm_creation = self.client.virtual_machines.create_or_update(
            group_name, self.name, vm_parameters)
        async_vm_creation.wait()

        # Display the public ip address
        # You can now connect to the machine using SSH
        print('VM available at {}'.format(self.public_ip_addr))
        print('ssh into the vm with {}@{} and password ({})'.format(ADMIN_USERNAME, self.public_ip_addr, ADMIN_PASSWORD))


    """
        VM Disk operations
    """
    # Creates a data disk
    # input: data_disk_name
    #        disk_size (in gigabytes)
    def create_empty_data_disk(self, data_disk_name, disk_size=10):
        # Create managed data disk
        print('\nCreate managed Data Disk')
        async_disk_creation = self.client.disks.create_or_update(
            self.resource_helper.group.name,
            data_disk_name,
            {
                'location': self.resource_helper.group.location,
                'disk_size_gb': disk_size,
                'creation_data': {
                    'create_option': 'Empty'
                }
            }
        )
        data_disk = async_disk_creation.result()
        return data_disk.id

    def create_data_disk_from_copy(self, data_disk_name, source_resource_group, source_disk_name):
        # Create managed data disk
        print('\nCreate managed Data Disk')
        source_disk_id = "/subscriptions/{}/resourceGroups/{}/providers/Microsoft.Compute/disks/{}".format( \
                            self.subscription_id, source_resource_group, source_disk_name)
        async_disk_creation = self.client.disks.create_or_update(
            self.resource_helper.group.name,
            data_disk_name,
            {
                'location': self.resource_helper.group.location,
                'creation_data': {
                    "createOption": "Copy",
                    "sourceResourceId": source_disk_id
                }
            }
        )
        data_disk = async_disk_creation.result()
        return data_disk.id

    def attach_data_disk(self, data_disk_name):
        print('\nAttach Data Disk')
        group_name = self.resource_helper.group.name
        disk = self.client.disks.get(group_name, data_disk_name)
        virtual_machine = self.client.virtual_machines.get(group_name, self.name)
        virtual_machine.storage_profile.data_disks.append({
            'lun': 12,
            'name': data_disk_name,
            'create_option': 'Attach',
            'managed_disk': {
                'id': disk.id
            }
        })
        async_disk_attach = self.client.virtual_machines.create_or_update(
            group_name,
            virtual_machine.name,
            virtual_machine
        )
        async_disk_attach.wait()

    def detach_data_disk(self, data_disk_name):
        print('\nDetach Data Disk')
        group_name = self.resource_helper.group.name        
        virtual_machine = self.client.virtual_machine.get(group_name, self.name)
        data_disks = virtual_machine.storage_profile.data_disks
        data_disks[:] = [disk for disk in data_disks if disk.name != 'mydatadisk1']
        async_vm_update = self.client.virtual_machines.create_or_update(
            group_name,
            self.name,
            virtual_machine
        )
        virtual_machine = async_vm_update.result()

    # Increases OS disk size
    # input: additional_os_disk_size (in GB)
    def increase_os_disk_size(self, additional_os_disk_size):
        print('\nUpdate OS disk size by ' + additional_os_disk_size + 'gb')
        group_name = self.resource_helper.group.name
        virtual_machine = self.client.virtual_machine.get(group_name, self.name)   
        os_disk_name = virtual_machine.storage_profile.os_disk.name
        os_disk = self.client.disks.get(group_name, os_disk_name)
        if not os_disk.disk_size_gb:
            print("\tServer is not returning the OS disk size, possible bug in the server?")
            print("\tAssuming that the OS disk size is 30 GB")
            os_disk.disk_size_gb = 30

        os_disk.disk_size_gb += additional_os_disk_size

        async_disk_update = self.client.disks.create_or_update(
            group_name,
            os_disk.name,
            os_disk
        )
        async_disk_update.wait()

    def get_vm_status(self):
        vm = self.client.virtual_machines.get(self.resource_helper.group.name, self.name, expand='instanceView')
        print("hardwareProfile")
        print("   vmSize: ", vm.hardware_profile.vm_size)
        print("\nstorageProfile")
        print("  imageReference")
        print("    publisher: ", vm.storage_profile.image_reference.publisher)
        print("    offer: ", vm.storage_profile.image_reference.offer)
        print("    sku: ", vm.storage_profile.image_reference.sku)
        print("    version: ", vm.storage_profile.image_reference.version)
        print("  osDisk")
        print("    osType: ", vm.storage_profile.os_disk.os_type.value)
        print("    name: ", vm.storage_profile.os_disk.name)
        print("    createOption: ", vm.storage_profile.os_disk.create_option.value)
        print("    caching: ", vm.storage_profile.os_disk.caching.value)
        print("\nosProfile")
        print("  computerName: ", vm.os_profile.computer_name)
        print("  adminUsername: ", vm.os_profile.admin_username)
        print("\nnetworkProfile")
        for nic in vm.network_profile.network_interfaces:
            print("  networkInterface id: ", nic.id)
        print("\ndisks");
        for disk in vm.instance_view.disks:
            print("  name: ", disk.name)
            print("  statuses")
            for stat in disk.statuses:
                print("    code: ", stat.code)
                print("    displayStatus: ", stat.display_status)
                print("    time: ", stat.time)
        print("\nVM general status")
        print("  provisioningStatus: ", vm.provisioning_state)
        print("  id: ", vm.id)
        print("  name: ", vm.name)
        print("  type: ", vm.type)
        print("  location: ", vm.location)
        print("\nVM instance status")
        for stat in vm.instance_view.statuses:
            print("  code: ", stat.code)
            print("  displayStatus: ", stat.display_status)

        return vm