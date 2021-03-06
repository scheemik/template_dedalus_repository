#!/bin/bash
# A bash script to run the Dedalus python code
# Optionally takes in arguments:
#	$ sh _run_exp.sh -n <name of experiment> <- not optional
#					 -r <run name>
#					 -c <cores>
#					 -l <local(1) or HPC(0)>
#					 -v <version: what scripts to run>

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
#	-> merge, plot frames
# VER = 4
#	-> create mp4
# VER = 5
#	-> create gif

while getopts n:r:c:l:v: option
do
	case "${option}"
		in
		n) NAME=${OPTARG};;
		r) RUN_NAME=${OPTARG};;
		c) CORES=${OPTARG};;
		l) LOC=${OPTARG};;
		v) VER=${OPTARG};;
	esac
done

echo ""
echo "Begin run script"
echo ""

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
	CORES=2
	echo "-c, No number of cores specified, using CORES=$CORES"
fi
if [ -z "$LOC" ]
then
	LOC=1 # 1 if local, 0 if on HPC
	echo "-l, No version specified, using LOC=$LOC"
fi
if [ -z "$VER" ]
then
	VER=1
	echo "-v, No version specified, using VER=$VER"
fi

# The command and arguments for running scripts with mpi
mpiexec_command="mpiexec"
# Version of python you want to run
python_ver='python3.7'
# The directory in which this code is being run
Project_directory="$(pwd)"
Running_directory="${Project_directory}/_experiments/${NAME}"
# Name of the core code file
code_file='core_code.py'
# Name of switchboard file
switch_file="switchboard"
# Location of the modules-other directory
modules_o_dir='_modules_other'
# Location of the modules-physics directory
modules_p_dir='_modules_physics'
# Name of output directory
output_dir="outputs/${RUN_NAME}"
# Path to snapshot files
snapshot_path="${output_dir}/snapshots"
# Name of merging file
merge_file="${modules_o_dir}/merge.py"
# Name of plotting file
plot_file="${modules_o_dir}/plot_slices.py"
# Path to frames
frames_path="${output_dir}/frames"
# Name of graphics making file
make_graphics_file="${modules_o_dir}/make_graphics.sh"
# Name of gif creation file
gif_cre_file="${modules_o_dir}/create_gif.py"


###############################################################################
# run the script
#	if (VER = 0, 1, 2)
if [ $VER -eq 0 ] || [ $VER -eq 1 ] || [ $VER -eq 2 ]
then
	echo ''
	echo '--Running script--'
	# Check if snapshots already exist. If so, remove them
	if [ -e $snapshot_path ]
	then
		echo "Removing old snapshots"
		rm -rf $snapshot_path
	fi
    # If running on local pc
    if [ $LOC -eq 1 ]
    then
        echo "Running Dedalus script for local pc"
        # mpiexec uses -n flag for number of processes to use
        ${mpiexec_command} -n $CORES python3 $code_file $switch_file
        echo ""
    fi
    # If running on Niagara
    if [ $LOC -eq 0 ]
    then
        echo "Running Dedalus script for remote HPC"
        # mpiexec uses -n flag for number of processes to use
        ${mpiexec_command} -n $CORES $python_ver $code_file $switch_file
        echo ""
    fi
	echo 'Done running script'
	mv snapshots $snapshot_path
fi

###############################################################################
# merge snapshots
#	if (VER = 0, 2, 3)
if [ $VER -eq 0 ] || [ $VER -eq 2 ] || [ $VER -eq 3 ]
then
	echo ''
	echo '--Merging snapshots--'
	# Check to make sure snapshots folder exists
	echo "Checking for snapshots in directory: $snapshot_path"
	if [ -e $snapshot_path ]
	then
		echo "Found snapshots"
	else
		echo "Cannot find snapshots. Aborting script"
		exit 1
	fi
	# Check if snapshots have already been merged
	if [ -e $snapshot_path/snapshots_s1.h5 ]
	then
		echo "Snapshots already merged"
	else
		echo "Merging snapshots"
		${mpiexec_command} -n $CORES python3 $merge_file $snapshot_path
	fi
	# Check if there are auxiliary snapshots to merge
	for f in ${snapshot_path}/*; do
		# Check if this file is a directory
		if [ -d "$f" ]
		then
			# Build relevant file strings
			aux_snap=${f#"${snapshot_path}/"}
			merged_h5_file="${f}/${aux_snap}_s1.h5"
			# Check to see if aux snapshots have already been merged
			if [ -e $merged_h5_file ] || [ $f == "${snapshot_path}/snapshots_s1" ]
			then
				echo "Already merged $f"
			else
				echo "Merging $f"
				${mpiexec_command} -n $CORES python3 $merge_file $f
			fi
		fi
	done
	pattern="snapshots_s"
	for f in ${snapshot_path}/*; do
		if [ -d "$f" ]
		then
			case "$f" in
				*${pattern}* ) echo "Removing un-merged snapshots ${f}" && rm -rf $f ;;
				* ) ;;
			esac
		fi
	done
	echo 'Done merging snapshots'
fi

###############################################################################
# make graphics
#	if (VER = 0, 3, 4, 5)
if [ $VER -eq 0 ] || [ $VER -eq 3 ] || [ $VER -eq 4 ] || [ $VER -eq 5 ]
then
	echo ''
	echo '--Making graphics--'
	bash $make_graphics_file -n $NAME -r $RUN_NAME -c $CORES -l $LOC -v $VER
fi

echo ''
echo 'Done running experiment'
echo ''
