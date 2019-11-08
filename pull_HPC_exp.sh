#!/bin/bash
# A bash script pull an experiment run on HPC to local
# To be run from experiment directory after called by run.sh
# Takes in arguments:
#	$ bash pull_HPC_exp.sh  -n <exp_name>
#							-r <run name>
#							-i <job id>
#							-h <HPC resource: Niagara, Graham, etc.>

# Current datetime
DATETIME=`date +"%Y-%m-%d_%Hh%M"`

while getopts n:r:i:h: option
do
	case "${option}"
		in
		n) NAME=${OPTARG};;
		r) RUN_NAME=${OPTARG};;
		i) JOBID=${OPTARG};;
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
LOCAL_DIR="/home/${USER}/Documents/Dedalus_Projects/example_projects"

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

# Check to see if this run actually exists
echo ''
echo "--Logging in to ${HPC}--"
# Log in to HPC, execute commands until EOF, then exit
#	The -i flag points to an rsa file so I shouldn't need to enter my password
ssh -i $SSH_KEY $SSH_LOGIN << EOF
echo "We're in"
cd ${NSCRATCH}/${DIRECTORY}/${SUBDIRECT}/_experiments
if [ -e ${NAME} ]
then
    echo "Found ${NAME} directory."
	cd ${NAME}
	if [ -e outputs/${RUN_NAME} ]
	then
		echo "Found ${RUN_NAME}."
		cd outputs
		if [ -z "$JOBID" ]
		then
			echo "-J, No JOBID specified"
		else
			echo "Moving slurm and seff outputs for ${JOBID} to ${RUN_NAME}"
			mv slurm_${JOBID}.out ${RUN_NAME}/
			seff ${JOBID} >> ${RUN_NAME}/seff_${JOBID}.out
		fi
	else
		echo "${RUN_NAME} not found, aborting script."
		exit 1
	fi
else
	echo "${NAME} directory not found, aborting script."
	exit 1
fi
echo ''
EOF

# Pull HPC experiment to local
echo "Copying ${RUN_NAME} from ${HPC} scratch directory to local"
cd ${LOCAL_DIR}/${SUBDIRECT}/_experiments/${NAME}

scp -r ${SSH_LOGIN}:${NSCRATCH}/${DIRECTORY}/${SUBDIRECT}/_experiments/${NAME}/outputs/${RUN_NAME} ./outputs/

echo 'Done'
