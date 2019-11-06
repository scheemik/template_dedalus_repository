#!/bin/bash
# A bash script to setup ssh keys for a new HPC
# Takes in arguments:
#	$ sh setup_new_HPC.sh 	-u <username>
#							-s <remote.server.com>
#							-v <version: what scripts to run>

while getopts u:s:v: option
do
	case "${option}"
		in
		u) USER=${OPTARG};;
		s) SERVER=${OPTARG};;
		v) VER=${OPTARG};;
	esac
done

if [ -z "$USER" ]
then
	echo "-u, No username specified, aborting script"
	exit 1
fi
if [ -z "$SERVER" ]
then
	echo "-s, No remote server specified, aborting script"
	exit 1
fi
if [ -z "$VER" ]
then
	VER=1
	echo "-v, No version specified, using VER=$VER"
fi

###############################################################################
echo ''
echo '--Checking for local ssh keys--'
echo ''

# Check if id_rsa exists already
if [ ! -e ~/.ssh/id_rsa ]
then
	echo "Generating new id_rsa, hit 'Enter' through all three prompts"
	ssh-keygen -t rsa
fi

if [ -e ~/.ssh/id_rsa ]
then
	echo "Local ssh keys found, copying to remote server: ${USER}@${SERVER}"
	ssh-copy-id ${USER}@${SERVER}
else
	echo "Local ssh keys not found, aborting script"
	exit 1
fi
echo "Logging into remote server: ${USER}@${SERVER}"
ssh -i ~/.ssh/id_rsa ${USER}@${SERVER} << EOF
echo ""
pwd
echo "Checking for remote ssh keys"
ls ~/.ssh

EOF
