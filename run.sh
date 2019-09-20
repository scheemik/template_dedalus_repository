#!/bin/bash
# A bash script to run the Dedalus python code
# Optionally takes in arguments:
#	$ sh run.sh -n <name of experiment>
#				-c <cores>
#				-l <local(1) or Niagara(0)>
#				-v <version: what scripts to run>
#				-k <keep(1) or allow overwriting(0)>
#               -x <n_x>
#               -z <n_z>

code_file='rayleigh_benard.py'

# if:
# VER = 0 (Full)
#	-> run the script, merge, plot EF if relevant, plot frames, create gif, create mp4
# VER = 1
#	-> run the script, merge, and plot EF if relevant
# VER = 2
#	-> run the script
# VER = 3
# 	-> merge, plot EF if relevant. plot frames, and create a gif
# VER = 4
#	-> create mp4 from frames
# VER = 5
#	-> plot EF and aux EF

while getopts n:c:l:v:k:x:z: option
do
	case "${option}"
		in
		n) NAME=${OPTARG};;
		c) CORES=${OPTARG};;
		l) LOC=${OPTARG};;
		v) VER=${OPTARG};;
		k) KEEP=${OPTARG};;
		x) N_X=${OPTARG};;
		z) N_Z=${OPTARG};;
	esac
done

DATETIME=`date +"%m-%d_%Hh%M"`

# check to see if arguments were passed
if [ -z "$NAME" ]
then
	NAME=$DATETIME
	echo "-n, No name specified, using $NAME"
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
if [ -z "$KEEP" ]
then
	KEEP=1
	echo "-k, No 'keep' preference specified, using KEEP=$KEEP"
fi
if [ -z "$TEST_P" ]
then
	TEST_P=2
	echo "-t, No test parameter specified, using TEST_P=$TEST_P"
fi

###############################################################################
# keep - create archive directory for experiment
#	if (KEEP = 1 and VER != 4)

if [ $KEEP -eq 1 ] && [ $VER -ne 3 ] && [ $VER -ne 4 ] && [ $VER -ne 5 ]
then
	echo ''
	echo '--Preparing archive directory--'
	echo ''
	# Check if experiments folder exists
	if [ -e _experiments ]
	then
		echo 'Experiment folder exists'
	else
		mkdir ./_experiments
	fi
	# Check if this experiment was run before
	if [ -e _experiments/$NAME ]
	then
		echo 'Experiment run previously. Overwriting data'
		rm -rf _experiments/$NAME
	else
		echo 'New experiment'
	fi
	# Make a new directory under the experiments folder
	mkdir ./_experiments/$NAME
fi

###############################################################################
# populate archive directory
if [ $KEEP -eq 1 ] && [ $VER -ne 3 ] && [ $VER -ne 4 ] && [ $VER -ne 5 ]
then
	# Create experiment log file
	LOG_FILE=_experiments/$NAME/LOG_${NAME}.txt
	touch $LOG_FILE
	echo "Log created: ${DATETIME}" >> $LOG_FILE
	echo "" >> $LOG_FILE
	echo "--Run options--" >> $LOG_FILE
	echo "" >> $LOG_FILE
	echo "-n, Experiment name = ${NAME}" >> $LOG_FILE
	echo "-c, Number of cores = ${CORES}" >> $LOG_FILE
	if [ $LOC -eq 1 ]
	then
		echo "-l, (${LOC}) Simulation run on local pc" >> $LOG_FILE
	else
		echo "-l, (${LOC}) Simulation run on Niagara" >> $LOG_FILE
	fi
	echo "-v, Version of run = ${VER}" >> $LOG_FILE
	echo "-t, Test parameter = ${TEST_P}" >> $LOG_FILE
	echo "" >> $LOG_FILE

	# Copy code and auxilary scripts
	echo 'Copying scripts to archive directory'
    cp $code_file _experiments/$NAME
    cp plot_slices.py _experiments/$NAME
	echo 'Done'
fi

###############################################################################
# run the script
if [ $VER -eq 0 ] || [ $VER -eq 1 ] || [ $VER -eq 2 ]
then
	cd _experiments/$NAME
    #echo $(ls)
    echo ''
	echo '--Running script--'
	echo ''
    # If running on local pc
    if [ $LOC -eq 1 ]
    then
        echo "Running Dedalus script for local pc"
        # mpiexec uses -n flag for number of processes to use
        mpiexec -n $CORES python3 $code_file $NAME 256 64
        echo ""
    fi
    # If running on Niagara
    if [ $LOC -eq 0 ]
    then
        echo "Running Dedalus script for Niagara"
        # mpiexec uses -n flag for number of processes to use
        mpiexec -n $CORES python3.6 $code_file $NAME 256 64
        echo ""
    fi
fi
