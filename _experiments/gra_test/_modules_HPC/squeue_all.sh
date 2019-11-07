#!/bin/bash
# A bash script to list all squeues on HPC's

# Check if id_rsa exists
if [ ! -e ~/.ssh/id_rsa ]
then
	echo "Local ssh keys not found, aborting script"
	exit 1
fi

USER='mschee'

# An array
declare -a arr=("niagara.scinet.utoronto.ca" "graham.computecanada.ca" "cedar.computecanada.ca")
for SERVER in "${arr[@]}"
do
	echo "Logging into remote server: ${USER}@${SERVER}"
	ssh -i ~/.ssh/id_rsa ${USER}@${SERVER} 'squeue -u mschee'
done
