#!/bin/bash
# A bash script to submit a job to HPC
# To be run from experiment directory after called by run.sh
# Takes in arguments:
#	$ bash HPC_job_submit.sh -n <exp_name>
#							 -r <run name>
#							 -h <HPC resource: Niagara, Graham, etc.>
#							 -c <cores>
#							 -s <sanity: pause to check setup before running>

# Current datetime
DATETIME=`date +"%Y-%m-%d_%Hh%M"`

while getopts n:r:h:c:s: option
do
	case "${option}"
		in
		n) NAME=${OPTARG};;
		r) RUN_NAME=${OPTARG};;
		h) HPC=${OPTARG};;
		c) CORES=${OPTARG};;
		s) SANITY=${OPTARG};;
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
	RUN_NAME=${DATETIME}_${NAME}
	echo "-r, No run name specified, using RUN_NAME=$RUN_NAME"
fi
if [ -z "$HPC" ]
then
	HPC='Niagara'
	echo "-h, No HPC specified, using HPC=$HPC"
fi
if [ -z "$CORES" ]
then
    CORES=32
	echo "No number of cores specified, using CORES=${CORES}"
fi
if [ -z "$SANITY" ]
then
    SANITY=0
	echo "No saity specified, using SANITY=${SANITY}"
fi
LOC=0

###############################################################################
# Prepare variables
DATE=`date +"%m-%d_%Hh%M"`
JOBNAME=$RUN_NAME
DIRECTORY='Dedalus_Projects'
SUBDIRECT='template_dedalus_repository'
SSH_KEY='~/.ssh/id_rsa'
LANCEUR_SCRIPT="_modules_HPC/${HPC}_lanceur.slrm"
USER='mschee'
LOCAL='ngws19.atmosp.physics.utoronto.ca'
LOCAL_DIR="/home/${USER}/Documents/Dedalus_Projects/example_projects"

if [ $HPC = 'Niagara' ]
then
	NHOME="/home/n/ngrisoua/${USER}"
	NSCRATCH="/scratch/n/ngrisoua/${USER}"
	SSH_LOGIN="${USER}@niagara.scinet.utoronto.ca"
elif [ $HPC = 'Graham' ]
then
	NHOME="/home/${USER}"
	NSCRATCH="/scratch/${USER}"
	SSH_LOGIN="${USER}@graham.computecanada.ca"
elif [ $HPC = 'Cedar' ]
then
	NHOME="/home/${USER}"
	NSCRATCH="/scratch/${USER}"
	SSH_LOGIN="${USER}@cedar.computecanada.ca"
fi

###############################################################################
# Secure copy experiment folder from local to HPC

echo ''
echo "--Logging in to ${HPC}--"
# Log in to HPC, execute commands until EOF, then exit
#	The -i flag points to an rsa file so I shouldn't need to enter my password
ssh -i $SSH_KEY $SSH_LOGIN << EOF
echo "We're in"
cd ${NSCRATCH}/${DIRECTORY}/${SUBDIRECT}/_experiments
if [ -e ${NAME} ]
then
    echo "An old version of ${NAME} will be removed."
	if [ $SANITY -eq 1 ]
	then
		read -p 'Press enter to continue or Ctrl+c to cancel.'
	fi
	rm -rf ${NAME}
fi
mkdir ${NAME}
echo ''
EOF

# A bit of a round-about way to make sure I never try to transfer the snapshots folder
echo "Copying ${NAME} from local to ${HPC} scratch directory"
cd ${LOCAL_DIR}/${SUBDIRECT}/_experiments/${NAME}
if [ -e snapshots ]
then
	for file in ./*
	do
		if [ ${file} != './snapshots' ]
		then
			#echo $file
			scp -r $file ${SSH_LOGIN}:${NSCRATCH}/${DIRECTORY}/${SUBDIRECT}/_experiments/${NAME}
		fi
	done
else
	cd ..
	scp -r ${NAME} ${SSH_LOGIN}:${NSCRATCH}/${DIRECTORY}/${SUBDIRECT}/_experiments
fi

echo ''
echo "--Logging in to ${HPC}--"
# Log in to HPC, execute commands until EOF, then exit
#	The -i flag points to an rsa file so I shouldn't need to enter my password
ssh -i $SSH_KEY $SSH_LOGIN << EOF
echo "We're in"
cd ${NSCRATCH}/${DIRECTORY}/${SUBDIRECT}/_experiments/${NAME}
sbatch --job-name=$JOBNAME $LANCEUR_SCRIPT -n ${NAME} -r ${RUN_NAME} -c ${CORES}
squeue -u mschee
EOF

echo 'Done'
