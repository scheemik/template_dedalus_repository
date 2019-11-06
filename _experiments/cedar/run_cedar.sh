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
#	-> run the script, merge, plot frames, and create gif
# VER = 3
# 	-> merge, plot frames, and create a gif
# VER = 4
#	-> create mp4 from frames
# VER = 5
#	-> run the script, merge

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
# Path to snapshot files
snapshot_path="snapshots"
# Name of merging file
merge_file="${modules_o_dir}/merge.py"
# Name of plotting file
plot_file="${modules_o_dir}/plot_slices.py"
# Path to frames
frames_path='frames'
# Name of gif creation file
gif_cre_file="${modules_o_dir}/create_gif.py"
# Name of output directory
output_dir="outputs/${RUN_NAME}"

###############################################################################
# run the script
#	if (VER = 0, 1, 2)
if [ $VER -eq 0 ] || [ $VER -eq 1 ] || [ $VER -eq 2 ] || [ $VER -eq 5 ]
then
	echo ''
	echo '--Running script--'
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
        ${mpiexec_command} -n $CORES python3 $code_file $switch_file
        echo ""
    fi
    # If running on Niagara
    if [ $LOC -eq 0 ]
    then
        echo "Running Dedalus script for remote HPC"
        # mpiexec uses -n flag for number of processes to use
        ${mpiexec_command} -n $CORES python3.6 $code_file $switch_file
        echo ""
    fi
	echo 'Done running script'
fi

###############################################################################
# merge snapshots
#	if (VER = 0, 2, 3)
if [ $VER -eq 0 ] || [ $VER -eq 2 ] || [ $VER -eq 3 ] || [ $VER -eq 5 ]
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
	echo 'Done merging snapshots'
fi

###############################################################################
# plot frames - note: already checked if snapshots exist in step above
#	if (VER = 0, 2, 3)
if [ $VER -eq 0 ] || [ $VER -eq 2 ] || [ $VER -eq 3 ]
then
	echo ''
	echo '--Plotting frames--'
	if [ -e frames ]
	then
		echo "Removing old frames"
		rm -rf frames
	fi
	echo "Plotting 2d slices"
	${mpiexec_command} -n $CORES python3 $plot_file $NAME $snapshot_path/*.h5
	echo 'Done plotting frames'
fi

###############################################################################
# create gif
#	if (VER = 0, 2, 3)
if [ $VER -eq 0 ] || [ $VER -eq 2 ] || [ $VER -eq 3 ]
then
	echo ''
	echo '--Creating gif--'
	gif_name="${output_dir}/${RUN_NAME}.gif"
	# Check if output directory exists
	if [ ! -e $output_dir ]
	then
		echo "Creating $output_dir directory"
		mkdir $output_dir
	fi
	# Check if gis already exists
	if [ -e $gif_name ]
	then
		echo "Overwriting $gif_name"
		rm $gif_name
	fi
	files=/$frames_path/*
	if [ -e $frames_path ] && [ ${#files[@]} -gt 0 ]
	then
		echo "Executing gif script"
		python3 $gif_cre_file $gif_name $frames_path
	else
		echo "No frames found"
	fi
	echo 'Done with gif creation'
fi

###############################################################################
# create mp4
#	if (VER = 0, 4)
if [ $VER -eq 0 ] || [ $VER -eq 4 ]
then
	echo ''
	echo '--Creating mp4--'
	mp4_name="${DATETIME}_${NAME}.mp4"
	# Check if frames exist
	echo "Checking frames in ${frames_path}"
	files=/$frames_path/*
	if [ -e $frames_path ] && [ ${#files[@]} -gt 0 ]
	then
		echo "Executing mp4 command"
		cd $frames_path/
		ffmpeg -framerate 10 -i write_%06d.png -c:v libx264 -pix_fmt yuv420p $mp4_name
		cd $Running_directory
		mv $frames_path/$mp4_name ./$output_dir
	else
		echo "No frames found"
	fi
	echo 'Done with mp4 creation'
fi

echo ''
echo 'Done running experiment'
echo ''