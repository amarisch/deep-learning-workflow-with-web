# cifsMount.sh
# This file must have LF (UNIX-style) line endings!

# Install the cifs utils, should be already installed
sudo apt-get update && sudo apt-get -y install cifs-utils

# Create the local folder that will contain our share
if [ ! -d "/mnt/{sharename}" ]; then sudo mkdir -p "/mnt/{sharename}" ; fi

sudo chown -R {username} /mnt/{sharename}

# Mount the share under the previous local folder created
sudo mount -t cifs //{storageacct}.file.core.windows.net/{sharename} /mnt/{sharename} -o uid={username},vers=3.0,username={storageacct},password={storageacct_password},dir_mode=0777,file_mode=0777