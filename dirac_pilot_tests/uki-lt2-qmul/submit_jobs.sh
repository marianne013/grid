#!/bin/bash

rm -rf *.log
rm -rf *.xml

source /home/hep/dbauer/dirac_site_tests/set_me_up.sh

# loop through the VOs
vos="gridpp lsst lz t2k.org hyperk.org"

for vo in $vos 
do
    echo -e "\n"
    echo "**** $vo"
    export X509_USER_PROXY=${PWD}/${vo}_pilot.proxy 
 
    
    voms-proxy-init -cert /srv/localstage/scratch/dbauer/pilotcert.pem -key /srv/localstage/scratch/dbauer/pilotkey.pem -out ${PWD}/${vo}_pilot.proxy -valid 24:00 -voms ${vo}:/${vo}/Role=pilot  
 
    voms-proxy-info --all | grep attributes


    echo "arcce02.esc.qmul.ac.uk"
    arcsub -c  arcce02.esc.qmul.ac.uk -j ${vo}_arcce02.esc.qmul.ac.uk.xml arc_test.rsl
    echo "arcce03.esc.qmul.ac.uk"
    arcsub -c  arcce03.esc.qmul.ac.uk -j ${vo}_arcce03.esc.qmul.ac.uk.xml arc_test.rsl


done
