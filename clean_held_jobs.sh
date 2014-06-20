#!/bin/bash


CONDOR_CRAP=`condor_q -hold | grep glite | awk '{print $1}'`

for JOB_ID in $CONDOR_CRAP
do
echo "Removing job: " $JOB_ID
condor_rm $JOB_ID
# sleep 2
condor_rm -forcex $JOB_ID
done
