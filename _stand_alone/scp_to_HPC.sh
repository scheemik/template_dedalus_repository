#!/bin/bash

DIRECTORY='Dedalus_Projects'
SUBDIRECT='_stand_alone'
NSCRATCH="/scratch/mschee"
CED_LOGIN='mschee@cedar.computecanada.ca'
GRA_LOGIN='mschee@graham.computecanada.ca'

scp -r $SUBDIRECT ${CED_LOGIN}:${NSCRATCH}/${DIRECTORY}
scp -r $SUBDIRECT ${GRA_LOGIN}:${NSCRATCH}/${DIRECTORY}
