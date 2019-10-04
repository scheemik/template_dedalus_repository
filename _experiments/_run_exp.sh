#!/bin/bash
# A bash script to run the Dedalus python code
# Optionally takes in arguments:
#	$ sh _run_exp.sh -n <name of experiment> <- not optional
#				-c <cores>
#				-l <local(1) or Niagara(0)>
#				-v <version: what scripts to run>

code_file='core_code.py'
plot_file='plot_slices.py'

# if:
# VER = 0 (Full)
#	-> run the script, merge, plot frames, create gif, create mp4, etc
# VER = 1
#	-> run the script
# VER = 2
#	-> run the script, merge
# VER = 3
# 	-> merge, plot frames, and create a gif
# VER = 4
#	-> create mp4 from frames

while getopts n:c:l:v:k:x:z: option
do
	case "${option}"
		in
		n) NAME=${OPTARG};;
		c) CORES=${OPTARG};;
		l) LOC=${OPTARG};;
		v) VER=${OPTARG};;
	esac
done

DATETIME=`date +"%Y-%m-%d_%Hh%M"`

# check to see if arguments were passed
if [ -z "$NAME" ]
then
	echo "-n, No name specified, aborting script"
	exit 1
fi
if [ -z "$CORES" ]
then
	CORES=2
	echo "-c, No number of cores specified, using CORES=$CORES"
fi
if [ -z "$LOC" ]
then
	LOC=1 # 1 if local, 0 if on Niagara
	echo "-l, No version specified, using LOC=$LOC"
fi
if [ -z "$VER" ]
then
	VER=1
	echo "-v, No version specified, using VER=$VER"
fi

###############################################################################
echo ''
echo '--Navigating to experiment directory--'
echo ''
if [ -e _experiments/$NAME ]
then
	cd _experiments/$NAME
	echo 'Done'
	echo ''
else
	echo "Experiment directory for $NAME not found. Aborting script."
	exit 1
fi

###############################################################################
# Create log file if version 0, 1, or 2
if [ $VER -eq 0 ] || [ $VER -eq 1 ] || [ $VER -eq 2 ]
then
	echo ''
	echo '--Creating experiment log file--'
	echo ''
	LOG_FILE=LOG_${NAME}.txt
	touch $LOG_FILE
	LINE1="Log created: ${DATETIME}"
	LINE2=""
	LINE3="--Run options--"
	LINE4=""
	LINE5="-n, Experiment name = ${NAME}"
	LINE6="-c, Number of cores = ${CORES}"
	if [ $LOC -eq 1 ]
	then
		LINE7="-l, (${LOC}) Simulation run on local pc"
	else
		LINE7="-l, (${LOC}) Simulation run on Niagara"
	fi
	LINE8="-v, Version of run = ${VER}"
	LINE9=""
	# This pre-pends the information to the log file
	#	This way, the most recent run is at the top
	echo -e "${LINE1}\n${LINE2}\n${LINE3}\n${LINE4}\n${LINE5}\n${LINE6}\n${LINE7}\n${LINE8}\n${LINE9}\n$(cat ${LOG_FILE})" > $LOG_FILE
	echo 'Done'
	echo ''
fi

###############################################################################
# Populate directory with relevant auxilary files and modules
echo ''
echo '--Adding auxilary files--'
echo ''

# add plot function if not there already
# option to update on subsequent runs?

###############################################################################
# run the script if version 0, 1, or 2
if [ $VER -eq 0 ] || [ $VER -eq 1 ] || [ $VER -eq 2 ]
then
	echo ''
	echo '--Running script--'
	echo ''
	# Check if snapshots already exist. If so, remove them
	if [ -e snapshots ]
	then
		echo "Removing old snapshots"
		rm -rf snapshots
	fi
    # If running on local pc
    if [ $LOC -eq 1 ]
    then
        echo "Running Dedalus script for local pc"
        # mpiexec uses -n flag for number of processes to use
        mpiexec -n $CORES python3 $code_file $NAME $N_X $N_Z
        echo ""
    fi
    # If running on Niagara
    if [ $LOC -eq 0 ]
    then
        echo "Running Dedalus script for Niagara"
        # mpiexec uses -n flag for number of processes to use
        mpiexec -n $CORES python3.6 $code_file $NAME $N_X $N_Z
        echo ""
    fi
fi
