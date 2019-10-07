#!/bin/bash
# A bash script to run the Dedalus python code
# Optionally takes in arguments:
#	$ sh make_new_experiment.sh -n <name of experiment>
#								-s <name of switchboard>

code_file='core_code.py'
switch_dir='_modules-physics/switchboards'
run_file='_experiments/_run_exp.sh'
submit_file='submit_to_Niagara.sh'

# Parse arguments
while getopts n:s: option
do
	case "${option}"
		in
		n) NAME=${OPTARG};;
		s) SWITCH=${OPTARG};;
	esac
done

# Generate datetime string
DATETIME=`date +"%m-%d_%Hh%M"`

# check to see if arguments were passed
if [ -z "$NAME" ]
then
	NAME=$DATETIME
	echo "-n, No experiment name specified, using $NAME"
fi
if [ -z "$SWITCH" ]
then
	SWITCH='switchboard-default.py'
	echo "-s, No switchboard specified, using default switchboard: $SWITCH"
fi

###############################################################################
echo ''
echo '--Creating experiment directory--'
echo ''
# Check if experiment directory exists
if [ -e _experiments ]
then
	echo 'Experiment folder exists'
else
	mkdir ./_experiments
fi
# Check if an experiment under this name has already been generated
if [ -e _experiments/$NAME ]
then
	echo 'Experiment name already used.'
	read -p 'Press enter to overwrite or Ctrl+c to cancel.'
	rm -rf ./_experiments/$NAME
fi
# Make a new directory under the experiments folder
mkdir ./_experiments/$NAME
echo "New experiment directory: /_experiments/${NAME}"
echo ''
echo '--Populating experiment directory--'
echo ''
if [ -e $code_file ]
then
	cp $code_file _experiments/$NAME
	echo "Copied $code_file"
else
	echo "No code file found. Aborting script"
	rm -rf _experiments/$NAME
	exit 1
fi
switch_path=${switch_dir}/${SWITCH}
if [ -e $switch_path ]
then
	cp $switch_path _experiments/${NAME}/switchboard-${NAME}.py
	echo "Copied $switch_path"
else
	echo "No switchboard file found. Aborting script"
	exit 1
fi
if [ -e $run_file ]
then
	cp $run_file _experiments/${NAME}/run_${NAME}.sh
	echo "Copied $run_file"
else
	echo "No run file found. Aborting script"
	exit 1
fi
if [ -e $submit_file ]
then
	cp $submit_file _experiments/${NAME}
	echo "Copied $submit_file"
else
	echo "No submit file found. Aborting script"
	exit 1
fi

echo "Done generating new experiment: ${NAME}"
