#!/bin/bash


source /home/hep/dbauer/dirac_site_tests/set_me_up.sh


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

BASEDIR=`pwd`

for vo in $vos 
do
    checkvo=`find ${PWD} -name "${vo}*log" -print0`
    if [  -z "${checkvo}" ]; then
        # echo "Not checking VO: " $vo
        continue
    fi

    echo -e "\n"
    echo "**** $vo"


    export X509_USER_PROXY=${PWD}/${vo}_pilot.proxy 
    
    # voms-proxy-init -cert /srv/localstage/scratch/dbauer/pilotcert.pem -key /srv/localstage/scratch/dbauer/pilotkey.pem -out ${PWD}/${vo}_pilot.proxy -valid 24:00 -voms ${vo}:/${vo}/Role=pilot  

    echo `voms-proxy-info --all | grep "attribute"`
    
    # to be sure 
    cd ${BASEDIR}
    celist=`ls ${vo}.*.log`
    for celog in $celist
    do
	# if something went wrong during submission, we might end up with an empty log file" 
	if [ ! -s "${celog}" ]; then
            echo "Logfile: ${checkvo} seems empty. Problem during job submission ?"
            continue
	fi

	# echo ${celog}
	jobid=`cat $celog | tr -s ' ' | cut -d ' ' -f 1`
	# recovering the ce name
	bah=${celog#${vo}.} # apparently this is non-greedy: remove the vo name (plus '.') from the front of the file name
	ceid=${bah%.log} # remove .log from the end of the file name
	
	echo "Checking job ${jobid} on ${ceid}"
	
	# I need the name of the ce + the job id.
	# I hate condor
	${MYCONDOR}/usr/bin/condor_q -pool ${ceid}:9619 -name ${ceid} ${jobid}

        if [ $GETOUTPUT == 'YES' ]; then
	    # apparently I cannot specify an output directory
	    # and it remebers where the job was submited from and insists on writing the data to that directory
	    # (i.e. cd doesn't work)
	    mkdir -p ${BASEDIR}/condor_${jobid}
	    ${MYCONDOR}/usr/bin/condor_transfer_data -pool ${ceid}:9619 -name ${ceid} ${jobid}
	    # move all files by hand before going to the next job
	    mv job.* ${BASEDIR}/condor_${jobid}
	    mv ce_test.log ${BASEDIR}/condor_${jobid}
	    mv environment.txt ${BASEDIR}/condor_${jobid}/environment.txt
        fi
    done

done

