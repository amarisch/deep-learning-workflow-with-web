# mountShares.sh
# This file must have LF (UNIX-style) line endings!

keyfile=$1

sh cifsMount.sh

# Install jq used for the next command
sudo apt-get install -y jq