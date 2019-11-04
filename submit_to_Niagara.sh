#!/bin/bash
# A bash script to submit a job to Niagara
# To be run from project directory after called by run.sh
# Takes in arguments:
#	$ sh submit_to_Niagara.sh -n <exp_name>
#							  -r <run name>
#							  -c <cores>

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
    CORES=40
	echo "No number of cores specified, using CORES=${CORES}"
fi
LOC=0

# Push specified experiment to git, using -f to override .git/info/exclude
git add -f _experiments/${NAME}/*
git commit -m "Added ${NAME} to be run on the supercomputer"
git push

# Prepare scratch

DATE=`date +"%m-%d_%Hh%M"`
# create a 2 digit version of CORES
#printf -v CO "%02d" $CORES
JOBNAME="${DATE}_${NAME}"
#JOBNAME="$DATE-2D_RB-n$CO"
DIRECTORY='Dedalus'
SUBDIRECT='template_dedalus_repository'
RUN_DIR='runs'

#set -x # echos each command as it is executed

# Go into directory of job to run
#cd ${HOME}/${DIRECTORY}/${SUBDIRECT}
# Pull from github the latest version of that project
#git pull
# Copy that into the scratch directory
#cp -r ${HOME}/${DIRECTORY}/${SUBDIRECT} ${SCRATCH}/${DIRECTORY}/${RUN_DIR}
#mv ${SCRATCH}/${DIRECTORY}/${RUN_DIR}/${SUBDIRECT} ${SCRATCH}/${DIRECTORY}/${RUN_DIR}/${JOBNAME}
#cd ${SCRATCH}/${DIRECTORY}/${RUN_DIR}/${JOBNAME}

# Submit the job
#sbatch --job-name=$JOBNAME lanceur.slrm -c $CORES -n $NAME

# Check the queue
#squeue -u mschee

echo 'Done'
