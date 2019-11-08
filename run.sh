#!/bin/bash
# A bash script to run the Dedalus python code for a certain experiment
# Takes in arguments:
#	$ sh run.sh -n <name of experiment> <- not optional
#				-c <cores>
#				-l <local(1) or HPC(0)>
#				-h <HPC resource: Niagara, Graham, etc.>
#				-v <version: what scripts to run>
#				-s <sanity: pause to check setup before running>

# Current datetime
DATETIME=`date +"%Y-%m-%d_%Hh%M"`

# if:
# VER = 0 (Full)
#	-> run the script, merge, plot frames, create gif, create mp4, etc
# VER = 1
#	-> run the script
# VER = 2
#	-> run the script, merge
# VER = 3
#	-> run the script, merge, plot frames

while getopts n:c:l:h:v:s: option
do
	case "${option}"
		in
		n) NAME=${OPTARG};;
		c) CORES=${OPTARG};;
		l) LOC=${OPTARG};;
		h) HPC=${OPTARG};;
		v) VER=${OPTARG};;
		s) SANITY=${OPTARG};;
	esac
done

# check to see if arguments were passed
if [ -z "$NAME" ]
then
	echo "-n, No name specified, aborting script"
	exit 1
fi
if [ -z "$LOC" ]
then
	LOC=1 # 1 if local, 0 if on Niagara
	echo "-l, No locality specified, using LOC=$LOC"
fi
###############################################################################
# Check which HPC resource is specified, if needed
if [ $LOC -eq 0 ]
then
	if [ -z "$HPC" ]
	then
		HPC='Niagara'
		echo "-h, No HPC resource specified, using HPC=$HPC"
	fi
	if [ -z "$CORES" ]
	then
		CORES=32
		echo "-c, No number of cores specified, using CORES=$CORES"
	fi
fi
###############################################################################
if [ -z "$CORES" ]
then
	CORES=2
	echo "-c, No number of cores specified, using CORES=$CORES"
fi
if [ -z "$VER" ]
then
	VER=1
	echo "-v, No version specified, using VER=$VER"
fi
if [ -z "$SANITY" ]
then
	SANITY=1
	echo "-s, No sanity specified, using SANITY=$SANITY"
fi

###############################################################################
# The command and arguments for running scripts with mpi
mpiexec_command="mpiexec"
# Location of the modules-HPC directory
modules_h_dir='_modules_HPC'
# Location of the modules-other directory
modules_o_dir='_modules_other'
# Location of the modules-physics directory
modules_p_dir='_modules_physics'
# Name of output directory
output_dir='outputs'
# Name of write out params to log file script
write_out_script='write_out_params.py'

###############################################################################
echo ''
echo '--Checking experiment directory--'
echo ''
# Check if experiments folder exists
if [ -e _experiments ]
then
	echo 'Experiment folder exists'
else
	echo 'Experiment folder not found. Aborting script'
	exit 1
fi
# Check if this experiment has been created
if [ -e _experiments/$NAME ]
then
	echo "Experiment for $NAME exists"
else
	echo "Experiment for $NAME does not exist. Aborting script."
	exit 1
fi
# Checking modules
if [ -e _experiments/${NAME}/${modules_o_dir} ]
then
	echo 'Other module files found'
else
	echo 'Other module files not found. Aborting script'
	exit 1
fi
if [ -e _experiments/${NAME}/${modules_p_dir} ]
then
	echo 'Physics module files found'
else
	echo 'Physics module files not found. Aborting script'
	exit 1
fi
###############################################################################
###############################################################################
echo ''
echo '--Navigating to experiment directory--'
cd _experiments/${NAME}
echo 'Done'
###############################################################################
###############################################################################
# Rearranging modules
#	Call select modules script to move around the modules as needed
echo ''
echo '--Selecting physics modules--'
if [ -e select_modules.py ]
then
	python3 select_modules.py
	echo 'Modules selected'
else
	echo 'Module selection file not found'
fi
###############################################################################
# Create a name for this particular run
RUN_NAME=${DATETIME}_${NAME}
# Check if output directory exists
if [ ! -e ${output_dir} ]
then
	echo "Creating ${output_dir} directory"
	mkdir ${output_dir}
fi
# Check if output subdirectory exists
if [ ! -e ${output_dir}/${RUN_NAME} ]
then
	echo "Creating ${RUN_NAME} directory"
	mkdir ${output_dir}/${RUN_NAME}
fi
###############################################################################
# Create (or prepend) log file if running code
#	if (VER = 0, 1, 2, 3)
LOG_FILE=${output_dir}/${RUN_NAME}/${RUN_NAME}_Log.txt
if [ $VER -eq 0 ] || [ $VER -eq 1 ] || [ $VER -eq 2 ] || [ $VER -eq 3 ]
then
	echo ''
	echo '--Creating experiment log file--'
	touch $LOG_FILE
	LINE0="----------------------------------------------"
	LINE1="Log for: ${RUN_NAME}"
	LINE2=""
	LINE3="--Run options--"
	LINE4=""
	LINE5="-n, Experiment name = ${NAME}"
	LINE6="-c, Number of cores = ${CORES}"
	if [ $LOC -eq 1 ]
	then
		LINE7="-l, (${LOC}) Simulation run on local pc"
	else
		LINE7="-l, (${LOC}) Simulation run on ${HPC}"
	fi
	LINE8="-v, Version of run = ${VER}"
	LINE9=""
	# This pre-pends the information to the log file
	#	This way, the most recent run's information is at the top
	echo -e "${LINE0}\n${LINE1}\n${LINE2}\n${LINE3}\n${LINE4}\n${LINE5}\n${LINE6}\n${LINE7}\n${LINE8}\n${LINE9}\n$(cat ${LOG_FILE})" > $LOG_FILE
fi
if [ $VER -eq 0 ] || [ $VER -eq 1 ] || [ $VER -eq 2 ] || [ $VER -eq 3 ] || [ $VER -eq 4 ] || [ $VER -eq 5 ]
then
	if [ -e $LOG_FILE ]
	then
		python3 ${modules_o_dir}/${write_out_script} ${NAME} ${RUN_NAME}
		echo 'Done creating log file'
	else
		echo 'Log file not found'
	fi
fi
###############################################################################
# Sanity check by plotting vertical profiles and boundary forcing
if [ $SANITY -eq 1 ] #|| [ $LOC -eq 0 ]
then
	echo ''
	echo '--Creating plots for sanity check--'
	python3 ${modules_o_dir}/sanity_plots.py ${NAME} ${RUN_NAME}
fi
###############################################################################
# Pause for sanity check if requested
#	Always pauses if submitting to a supercomputer
if [ $SANITY -eq 1 ] #|| [ $LOC -eq 0 ]
then
	echo 'Pause for sanity check of log file and plots.'
	read -p 'Press enter to continue or Ctrl+c to cancel.'
fi
###############################################################################
# Start run of this experiment
echo ''
echo "--Starting run of experiment ${NAME}--"
# Check if this will be run locally or on supercomputer
if [ $LOC -eq 1 ]
then
	# Check if this experiment has a run file
	if [ -e run_${NAME}.sh ]
	then
		echo "Executing experiment run file: run_${NAME}.sh"
		echo ''
		bash run_${NAME}.sh -n $NAME -r $RUN_NAME -c $CORES -l $LOC -v $VER
	else
		echo 'Experiment run file does not exist. Aborting script'
		exit 1
	fi
else
	# Check if the specified HPC submit script exists
	HPC_sub_script=${modules_h_dir}/HPC_job_submit.sh
	if [ -e $HPC_sub_script ]
	then
		echo "Calling script to submit to ${HPC}"
		bash ${HPC_sub_script} -n $NAME -r $RUN_NAME -h $HPC -c $CORES -S $SANITY
	else
		echo "Submit script for ${HPC} does not exist. Aborting script"
		exit 1
	fi
fi
