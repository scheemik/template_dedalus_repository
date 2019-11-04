#!/bin/bash
# A bash script pull an experiment run on HPC to local
# To be run from experiment directory after called by run.sh
# Takes in arguments:
#	$ bash pull_HPC_exp.sh  -n <exp_name>
#							-r <run name>
#							-h <HPC resource: Niagara, Graham, etc.>

# Current datetime
DATETIME=`date +"%Y-%m-%d_%Hh%M"`

while getopts n:r:h: option
do
	case "${option}"
		in
		n) NAME=${OPTARG};;
		r) RUN_NAME=${OPTARG};;
		h) HPC=${OPTARG};;
	esac
done

# check to see if arguments were passed
if [ -z "$NAME" ]
then
	echo "-n, No name specified, aborting script"
	exit 1
fi
if [ -z "$RUN_NAME" ]
then
	echo "-r, No run name specified, aborting script"
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
NHOME='/home/n/ngrisoua/mschee'
NSCRATCH='/scratch/n/ngrisoua/mschee'

echo ''
echo '--Logging in to Niagara--'
# Log in to Niagara, execute commands until EOF, then exit
#	The -i flag points to an rsa file so I don't need to enter my password
ssh -i ~/.ssh/niagarasshkeys mschee@niagara.scinet.utoronto.ca << EOF
echo ''
cd ${NSCRATCH}/${DIRECTORY}/${SUBDIRECT}
echo "Pushing ${NAME} to git:"
git add -f _experiments/${NAME}/*
git commit -m "Moving ${RUN_NAME} from HPC to local"
git push
echo ''
EOF
#ssh -XY mschee@graham.computecanada.ca


# Pull HPC experiment to local
git pull

echo 'Done'
