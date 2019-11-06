#!/bin/bash
# A bash script pull an experiment run on HPC to local
# To be run from experiment directory after called by run.sh
# Takes in arguments:
#	$ bash pull_HPC_exp.sh  -n <exp_name>
#							-h <HPC resource: Niagara, Graham, etc.>

# Current datetime
DATETIME=`date +"%Y-%m-%d_%Hh%M"`

while getopts n:h: option
do
	case "${option}"
		in
		n) NAME=${OPTARG};;
		h) HPC=${OPTARG};;
	esac
done

# check to see if arguments were passed
if [ -z "$NAME" ]
then
	echo "-n, No name specified, aborting script"
	exit 1
fi
if [ -z "$HPC" ]
then
	echo "-h, No HPC specified, aborting script"
	exit 1
fi

###############################################################################
# Move outputs from scratch to local
DATE=`date +"%m-%d_%Hh%M"`
DIRECTORY='Dedalus_Projects'
SUBDIRECT='template_dedalus_repository'

if [ $HPC = 'Niagara' ]
then
	NHOME='/home/n/ngrisoua/mschee'
	NSCRATCH='/scratch/n/ngrisoua/mschee'
	SSH_KEY='~/.ssh/id_rsa'
	SSH_LOGIN='mschee@niagara.scinet.utoronto.ca'
elif [ $HPC = 'Graham' ]
then
	NHOME='/home/mschee'
	NSCRATCH='/scratch/mschee'
	SSH_KEY='~/.ssh/id_rsa'
	SSH_LOGIN='mschee@graham.computecanada.ca'
elif [ $HPC = 'Cedar' ]
then
	NHOME='/home/mschee'
	NSCRATCH='/scratch/mschee'
	SSH_KEY='~/.ssh/id_rsa'
	SSH_LOGIN='mschee@cedar.computecanada.ca'
fi

echo ''
echo "--Logging in to ${HPC}--"
# Log in to HPC, execute commands until EOF, then exit
#	The -i flag points to an rsa file so I don't need to enter my password
ssh -i $SSH_KEY $SSH_LOGIN << EOF
echo ''
echo "Navigating to ${NSCRATCH}/${DIRECTORY}/${SUBDIRECT}"
cd ${NSCRATCH}/${DIRECTORY}/${SUBDIRECT}
echo "Adding ${NAME} to git"
git add -f _experiments/${NAME}/*
echo "Commiting"
git commit -m "Moving ${NAME} from HPC to local"
echo "Pushing from scratch directory"
git config --global push.default simple
git push -f origin master
cd
cd ${NHOME}/${DIRECTORY}/${SUBDIRECT}
git pull
echo ''
EOF

# Pull HPC experiment to local
echo "Pulling ${NAME} to local"
git pull

echo 'Done'
