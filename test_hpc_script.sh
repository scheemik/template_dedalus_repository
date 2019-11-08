#!/bin/bash
# A bash script to test working with HPC

# Takes in arguments:
#	$ bash Niagara_job_submit.sh -h <HPC resource: Niagara, Graham, etc.>

while getopts h: option
do
	case "${option}"
		in
		h) HPC=${OPTARG};;
	esac
done

###############################################################################
# Prepare scratch
DATE=`date +"%m-%d_%Hh%M"`
JOBNAME=$RUN_NAME
DIRECTORY='Dedalus_Projects'
SUBDIRECT='template_dedalus_repository'
SSH_KEY='~/.ssh/id_rsa'

if [ $HPC = 'Niagara' ]
then
	NHOME='/home/n/ngrisoua/mschee'
	NSCRATCH='/scratch/n/ngrisoua/mschee'
	LANCEUR_SCRIPT='_modules_HPC/Niagara_lanceur.slrm'
	SSH_LOGIN='mschee@niagara.scinet.utoronto.ca'
elif [ $HPC = 'Graham' ]
then
	NHOME='/home/mschee'
	NSCRATCH='/scratch/mschee'
	LANCEUR_SCRIPT='_modules_HPC/Graham_lanceur.slrm'
	SSH_LOGIN='mschee@graham.computecanada.ca'
elif [ $HPC = 'Cedar' ]
then
	NHOME='/home/mschee'
	NSCRATCH='/scratch/mschee'
	LANCEUR_SCRIPT='_modules_HPC/Cedar_lanceur.slrm'
	SSH_LOGIN='mschee@cedar.computecanada.ca'
fi

echo ''
echo "--Logging in to ${HPC}--"
# Log in to HPC, execute commands until EOF, then exit
#	The -i flag points to an rsa file so I shouldn't need to enter my password
ssh -i $SSH_KEY $SSH_LOGIN << EOF
echo ''
echo "Now in ${HPC}"
cd
pwd
if [ -e Dedalus_Projects ]
then
    echo "Found Dedalus Projects"
fi
EOF

echo 'Done'
