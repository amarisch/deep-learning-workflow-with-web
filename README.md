# Azure Virtual Machine and File Share for Deep Learning Development
![alt text](https://github.com/amarisch/deep-learning-workflow-with-web/blob/master/images/azure-deep-learning-project-framework.jpg)

This repo contains a simple workflow for deep learning development/deployment on Azure using python SDK. You will be able to easily set up a deep learning development environment with access to Azure file where you can preload and share datasets.

**On this page**

- [Run this sample](#run)
- [What does run.py do?](#example)
- [Running the web interface](#run_web)
- [How is the code laid out?](#code)
- [Notes and troubleshooting](#troubleshooting)
- [More Ideas and Functionality](#ideas)

<a id="run"></a>

## Run this sample

1.  If you don't already have them, install the following:

    - [Python](https://www.python.org/downloads/)
    - [Anaconda](#anaconda)
    - [Azure CLI 2.0](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli?view=azure-cli-latest)
    
1.  Install python requirements
    ```
    pip install -r requirements.txt
    ```
1. To run from commandline
    ```
    python run.py <Azure credentials filename>
    ```
1. To run with a web browser
    ```
    python hello.py <Azure credentials filename>
    ```
1. Azure credentials file instructions:  
    Azure credentials file template has been provided in *id_template.txt*
    ```
    az account list
    ```
    Find the subscription account to use and use its _id_ to set subscription account  
    ```
    az account set --subscription <id>
    ```
    AZURE_SUBSCRIPTION_ID = id  
    ```
    az ad sp create-for-rbac --name ServicePrincipalName --password PASSWORD
    ```
    TENANT_ID = tenantid  
    CLIENT_ID = clientid  
    CLIENT_SECRET = password  

<a id="example"></a>
## What does run.py do?
`run.py` goes through the necessary steps to create a virtual machine, create a fileshare, and mount the fileshare on the virtual machine. When `deployer.deploy()` is called:

1. Creates a resource group.

   Ideally, each virtual machine should be created in a separate resource group. This makes deleting and clean up simpler, you can just delete the entire resource group when you are done. The [`ResourceHelper`](helpers/resource_helper.py) class creates a resource group.

1. Creates the network interface.

   This includes creating the virtual network, subnet, public ip address, and the network interface. Code can be found in [`ComputerHelper`](helpers/compute_helper.py) class starting line 81.
   
1. Creates the virtual machine.

   Creates linux vm (Canonical UbuntuServer 16.04-LTS). VM image reference has been hard-coded in `ComputerHelper` class.  
   
   If you would like to create a VM from a customized image, call `deployer.deploy_image(image, group)` specifying *image* name and the *group* the image belongs to.
   
   When the virtual machine is created, it will provide the public address for you to `ssh` into the vm.

1. Mounts file share.
  
   `deploy()` also mounts a default *fileshare* which you can find in `/mnt/fileshare/` on the virtual machine.  
   
   If you would like to mount a specific fileshare in the same storage account, call `mount_shares(filesharename)` specifying the fileshare you would like to mount. Likewise, you will be able to find the share in `/mnt/{filesharename}/`.

1. Tunnel Forwarding.

   `deployer.tunnelforwarding()` links local port *8880* to port *8889* on the virtual machine.
   
1. [Run Jupyter notebook.](#jupyter)


<a id="run_web"></a>
## Running the web interface

In your terminal run:
```
python run_web.py <Azure credentials file>
```
Open your browser and go to:
```
localhost:1048
```
1. The main page:   
     * allows you to **create** and deploy a new vm (similar to running run.py).
     * lists existing vms to manage.
     
1. Manage Virtual Machine page allows you to:
      * run virual machines.
      * mount specific fileshares.
      * launch jupyter notebook browser (after doing step #3).
      
1. [Run Jupyter notebook.](#jupyter)

<a id="code"></a>
## Code Layout and Additional Functionalities

**helpers** directory contains various helper class used by [`VirtualMachineDeployer`](virtualmachinedeployer.py) class
   - [`ComputeHelper`](helpers/compute_helper.py)
   - [`ResourceHelper`](helpers/resource_helper.py)
   - [`StorageHelper`](helpers/storage_helper.py)
   
**scripts** directory contains scripts and templates used for mounting VM fileshares

[`VirtualMachineDeployer`](virtualmachinedeployer.py) class handles all the tasks related to deploying a virtual machine

### Other [`ComputeHelper`](helpers/compute_helper.py) functionalities
* Customize VM with cloud-init

   Edit `cloud-init.txt` file and the file used in `create_vm_parameters()`.  
   More info on cloud config scripting can be found [here](https://www.digitalocean.com/community/tutorials/an-introduction-to-cloud-config-scripting)
   
* Data Disk Operations

   * create data disk
   * attach/detach data disk
   

<a id="troubleshooting"></a>
## Notes and Troubleshooting

Mounting new data disk to VM, a step by step guide can be found [here](https://docs.microsoft.com/en-us/azure/virtual-machines/linux/add-disk#connect-to-the-linux-vm-to-mount-the-new-disk)  

Kaggle commandline tool for data download can be found [here](https://github.com/floydwch/kaggle-cli)


<a id="ideas"></a>
## More Ideas and Functionality
Things to look further into:
1. GPU-enabled VM
https://azure.microsoft.com/en-us/pricing/details/virtual-machines/series/
2. Docker for Azure
https://azuremarketplace.microsoft.com/en-us/marketplace/apps/docker.dockerdatacenter?tab=Overview

<a id="anaconda"></a>
## Anaconda Installation
```
curl -O https://repo.continuum.io/archive/Anaconda3-5.0.1-Linux-x86_64.sh
chmod +x Anaconda3-5.0.1-Linux-x86_64.sh
bash Anaconda3-5.0.1-Linux-x86_64.sh
```
Follow the installation steps and set the PATH. Now when you run `python`, it should return python 3.

<a id="jupyter"></a>
## Run jupyter notebook on vm
   
   `ssh` into the vm
   
   Install [Anaconda](#anaconda) to run jupyter notebook.
   
   Once Anaconda and jupyter-notebook have been installed, configure jupyter-notebook by first generate a config file
   
   ```
   jupyter notebook --generate-config
   ```
   Open and edit the config file
   ```
   vi ~/.jupyter/jupyter_notebook_config.py
   ```
   Uncomment and make changes to these lines
   ```
   c.NotebookApp.open_browser = False    # no browser needed on a server
   ```
   ```
   c.NotebookApp.ip = '0.0.0.0'          # listen on the network
   ```
   ```
   c.NotebookApp.password = ''            # don't require a password
   ```
   ```
   c.NotebookApp.token = ''              # don't require a security token
   ```
   There is a sample [`jupyter_notebook_config.py`](jupyter_notebook_config.py) file in the repo.
   
   Make a notebook directory to launch the jupyter notebook server
   ```
   mkdir notebook
   ```
   Run jupyter notebook in background using nohup
   ```
   nohup jupyter notebook --port=8889 --notebook-dir=notebook&
   ```
   
