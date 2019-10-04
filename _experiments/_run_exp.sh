#!/bin/bash
# A bash script to run the Dedalus python code
# Optionally takes in arguments:
#	$ sh _run_exp.sh -n <name of experiment> <- not optional
#				-c <cores>
#				-l <local(1) or Niagara(0)>
#				-v <version: what scripts to run>

# Name of the core code file
code_file='core_code.py'
# Location of the modules-other directory
modules_o_dir='_modules-other'
# Location of the modules-physics directory
modules_p_dir='_modules-physics'
# Path to snapshot files
snapshot_path="snapshots"
# Name of merging file
merge_file="${modules_o_dir}/merge.py"
# Name of plotting file
plot_file="${modules_o_dir}/plot_slices.py"

# if:
# VER = 0 (Full)
#	-> run the script, plot frames, create gif, create mp4, etc
# VER = 1
#	-> run the script
# VER = 2
#	-> run the script, plot frames, and create gif
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
echo '--Checking experiment directory--'
echo ''
if [ -e _experiments/$NAME ]
then
	echo 'Experiment directory found'
	echo ''
else
	echo "Experiment directory for $NAME not found. Aborting script."
	exit 1
fi

###############################################################################
# Populate directory with relevant modules
if [ -e _experiments/${NAME}/${modules_o_dir} ]
then
	echo 'Other module files already added'
else
	echo ''
	echo '--Adding module files--'
	echo ''
	if [ -e $modules_o_dir ]
	then
		cp -r $modules_o_dir _experiments/$NAME
		echo "Copied $modules_o_dir"
	else
		echo "Cannot find other modules"
	fi
fi

###############################################################################
###############################################################################
echo ''
echo '--Navigating to experiment directory--'
echo ''
cd _experiments/$NAME
echo 'Done'
echo ''
###############################################################################
###############################################################################
# Create log file if running code
#	if (VER = 0, 1, 2)
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
	#	This way, the most recent run's information is at the top
	echo -e "${LINE1}\n${LINE2}\n${LINE3}\n${LINE4}\n${LINE5}\n${LINE6}\n${LINE7}\n${LINE8}\n${LINE9}\n$(cat ${LOG_FILE})" > $LOG_FILE
	echo 'Done creating log file'
	echo ''
fi

###############################################################################
# run the script
#	if (VER = 0, 1, 2)
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
	echo 'Done running script'
	echo ''
fi

###############################################################################
# merge snapshots
#	if (VER = 0, 1, 2)
if [ $VER -eq 0 ] || [ $VER -eq 1 ] || [ $VER -eq 2 ]
then
	echo ''
	echo '--Merging snapshots--'
	echo ''
	# Check to make sure snapshots folder exists
	echo "Checking for snapshots in $snapshot_path"
	if [ -e $snapshot_path ] || [ $VER -eq 5 ]
	then
		echo "Found snapshots"
	else
		echo "Cannot find snapshots. Aborting script"
		exit 1
	fi
	# Check if snapshots have already been merged
	if [ -e $snapshot_path/snapshots_s1.h5 ] || [ $VER -eq 5 ]
	then
		echo "Snapshots already merged"
	else
		echo "Merging snapshots"
		mpiexec -n $CORES python3 $merge_file $snapshot_path
	fi
	echo 'Done merging snapshots'
fi

###############################################################################
# plot frames
#	if (VER = 0, 2, 3)

if [ $VER -eq 0 ] || [ $VER -eq 2 ] || [ $VER -eq 3 ]
then
	echo ''
	echo '--Plotting frames--'
	echo ''
	if [ -e frames ]
	then
		echo "Removing old frames"
		rm -rf frames
	fi
	echo "Plotting 2d slices"
	mpiexec -n $CORES python3 $plot_file $snapshot_path/*.h5
	echo 'Done plotting frames'
	echo ''
fi
