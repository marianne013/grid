#!/bin/bash

source ../set_me_up.sh

export GETOUTPUT='NO'

if [ $# -ge 1 ]; then
    if [ $1 == 'YES' ]; then
	echo "Retrieving output"
	export GETOUTPUT='YES'
    else
	echo "Unknown argument $1"
    fi
fi


# loop through the VOs
vos=`cat /home/hep/dbauer/dirac_site_tests/testfiles/supported_vos.txt`

for vo in $vos 
do
    checkvo=`find ${PWD} -name "${vo}*xml" -print0`
    if [  -z "${checkvo}" ]; then
        # echo "Not checking VO: " $vo
        continue
    fi

    echo -e "\n"
    echo "**** $vo"
    export X509_USER_PROXY=${PWD}/${vo}_pilot.proxy 
    
    # maybe I should should check for validity and renew it if it has run out ? 
    # voms-proxy-init -cert /srv/localstage/scratch/dbauer/pilotcert.pem -key /srv/localstage/scratch/dbauer/pilotkey.pem -out ${PWD}/${vo}_pilot.proxy -valid 24:00 -voms ${vo}:/${vo}/Role=pilot

    echo `voms-proxy-info --all | grep "attribute"`


    # ARC
    ces=`ls ${PWD}/${vo}*xml`
    for ce in ${ces}
    do
	echo ${ce}
        arcstat -j $ce

        if [ $GETOUTPUT == 'YES' ]; then
            mkdir -p ${vo}_job_output
            arcget -D "${vo}_job_output" -j ${ce}
        fi
    done

done
