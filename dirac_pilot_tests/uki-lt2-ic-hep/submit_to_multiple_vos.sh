#!/bin/bash


rm -rf *.log
rm -rf *.xml
source /home/hep/dbauer/dirac_site_tests/set_me_up.sh

# loop through the VOs
# vos="comet.j-parc.jp gridpp lz na62.vo.gridpp.ac.uk pheno snoplus.snolab.ca solidexperiment.org t2k.org"
vos="gridpp lz solidexperiment.org" 

BASEDIR=`pwd`
for vo in $vos 
do
    echo -e "\n"
    echo "**** $vo"
    export X509_USER_PROXY=${PWD}/${vo}_pilot.proxy 
    
    voms-proxy-init -cert /srv/localstage/scratch/dbauer/pilotcert.pem -key /srv/localstage/scratch/dbauer/pilotkey.pem -out ${PWD}/${vo}_pilot.proxy -valid 24:00 -voms ${vo}:/${vo}/Role=pilot  

    voms-proxy-info --all | grep attribute
    

    ICCONDORS="ceprod00.grid.hep.ph.ic.ac.uk ceprod01.grid.hep.ph.ic.ac.uk ceprod02.grid.hep.ph.ic.ac.uk ceprod03.grid.hep.ph.ic.ac.uk"
    for ce in ${ICCONDORS}
    do
	# ./usr/bin/condor_q -pool ${ce}:9619 -name ${ce}
	${MYCONDOR}/usr/bin/condor_submit -terse -remote ${ce} -pool ${ce}:9619 ${BASEDIR}/htcondorce.sub | tee ${vo}.${ce}.log 
    done

done
