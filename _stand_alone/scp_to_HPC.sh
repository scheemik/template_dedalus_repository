#!/bin/bash

DIRECTORY='Dedalus_Projects'
SUBDIRECT='_stand_alone'
NSCRATCH="/scratch/mschee"
CED_LOGIN='mschee@cedar.computecanada.ca'
GRA_LOGIN='mschee@graham.computecanada.ca'
NIA_LOGIN='mschee@niagara.scinet.utoronto.ca'

scp -r $SUBDIRECT ${CED_LOGIN}:${NSCRATCH}/${DIRECTORY}
scp -r $SUBDIRECT ${GRA_LOGIN}:${NSCRATCH}/${DIRECTORY}
scp -r $SUBDIRECT ${NIA_LOGIN}:/scratch/n/ngrisoua/mschee/${DIRECTORY}
