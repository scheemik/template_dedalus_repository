#!/bin/bash
# A bash script to submit a job to Niagara
# To be run from experiment directory after called by run.sh
# Takes in arguments:
#	$ bash Niagara_job_submit.sh -n <exp_name>
#								 -r <run name>
#								 -c <cores>

# Current datetime
DATETIME=`date +"%Y-%m-%d_%Hh%M"`

while getopts n:r:c: option
do
	case "${option}"
		in
		n) NAME=${OPTARG};;
		r) RUN_NAME=${OPTARG};;
		c) CORES=${OPTARG};;
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
if [ -z "$CORES" ]
then
    CORES=32
	echo "No number of cores specified, using CORES=${CORES}"
fi
LOC=0

###############################################################################
# Navigate to project directory
cd ..
cd ..
pwd

###############################################################################
# Push specified experiment to git, using -f to override .git/info/exclude
git add -f _experiments/${NAME}/*
git commit -m "Added ${NAME} to run ${RUN_NAME} on supercomputer"
git push

###############################################################################
# Prepare scratch
DATE=`date +"%m-%d_%Hh%M"`
JOBNAME=$RUN_NAME
DIRECTORY='Dedalus_Projects'
SUBDIRECT='template_dedalus_repository'
NHOME='/home/n/ngrisoua/mschee'
NSCRATCH='/scratch/n/ngrisoua/mschee'
LANCEUR_SCRIPT='_modules_HPC/Niagara_lanceur.slrm'

echo ''
echo '--Logging in to Niagara--'
# Log in to Niagara, execute commands until EOF, then exit
#	The -i flag points to an rsa file so I don't need to enter my password
ssh -i ~/.ssh/niagarasshkeys mschee@niagara.scinet.utoronto.ca << EOF
echo ''
cd ${DIRECTORY}/${SUBDIRECT}
echo "Pulling from git:"
git pull
echo ''
echo "Copying experiment to scratch directory"
cp -r ${NHOME}/${DIRECTORY}/${SUBDIRECT}/_experiments/${NAME} ${NSCRATCH}/${DIRECTORY}/${SUBDIRECT}/_experiments/${NAME}
cd ${NSCRATCH}/${DIRECTORY}/${SUBDIRECT}/_experiments/${NAME}
pwd
sbatch --job-name=$JOBNAME $LANCEUR_SCRIPT -n ${NAME} -r ${RUN_NAME} -c ${CORES}
squeue -u mschee
EOF
#ssh -XY mschee@graham.computecanada.ca


# Submit the job
#sbatch --job-name=$JOBNAME lanceur.slrm -c $CORES -n $NAME

# Check the queue
#squeue -u mschee

echo 'Done'
