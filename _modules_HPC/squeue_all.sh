#!/bin/bash
# A bash script to list all squeues on HPC's

# An array
declare -a arr=("niagara" "graham" "cedar")
for hpc_name in "${arr[@]}"
do

done


if [ -e ~/.ssh/id_rsa ]
then
	echo "Local ssh keys found, copying to remote server: ${USER}@${SERVER}"

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
