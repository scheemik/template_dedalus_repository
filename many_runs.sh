#!/bin/bash
# A bash script to run many different experiments in a row
# Takes in arguments:
#	$ sh run.sh -c <cores>
#				-l <local(1) or Niagara(0)>
#				-v <version: what scripts to run>

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

while getopts c:l:v: option
do
	case "${option}"
		in
		c) CORES=${OPTARG};;
		l) LOC=${OPTARG};;
		v) VER=${OPTARG};;
	esac
done

if [ -z "$CORES" ]
then
	CORES=2
	echo "-c, No number of cores specified, using CORES=$CORES"
fi
if [ -z "$LOC" ]
then
	LOC=1 # 1 if local, 0 if on Niagara
	echo "-l, No locality specified, using LOC=$LOC"
fi
if [ -z "$VER" ]
then
	VER=1
	echo "-v, No version specified, using VER=$VER"
fi

###############################################################################
echo ''
echo '--Starting many runs--'
echo ''
declare -a arr=("sl_th_1" "sl_th_4")
for exp_name in "${arr[@]}"
do
	# Check if this experiment has a run file
	if [ -e _experiments/${exp_name}/run_${exp_name}.sh ]
	then
		echo "Executing experiment run file: run_${exp_name}.sh"
		echo ''
		bash _experiments/${exp_name}/run_${exp_name}.sh -n $exp_name -c $CORES -l $LOC -v $VER
	else
		echo 'Experiment run file does not exist. Aborting script'
		exit 1
	fi
done
