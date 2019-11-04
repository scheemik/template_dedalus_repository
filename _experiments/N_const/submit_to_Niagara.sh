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
git commit -m "Added ${NAME} to run ${RUN_NAME} on supercomputer"
git push

# Prepare scratch

DATE=`date +"%m-%d_%Hh%M"`
# create a 2 digit version of CORES
#printf -v CO "%02d" $CORES
JOBNAME="${DATE}_${NAME}"
#JOBNAME="$DATE-2D_RB-n$CO"
DIRECTORY='Dedalus_Projects'
SUBDIRECT='template_dedalus_repository'
RUN_DIR='runs'

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
cp -r _experiments/${NAME} ${SCRATCH}/${DIRECTORY}/${SUBDIRECT}/_experiments/
cd ${SCRATCH}${SCRATCH}/${DIRECTORY}/${SUBDIRECT}/_experiments/${NAME}
ls
EOF
#ssh -XY mschee@graham.computecanada.ca

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
