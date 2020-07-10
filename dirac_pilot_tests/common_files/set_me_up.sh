#!/bin/bash


# clean up a bit
for i in `env | sed 's/=.*//'` ; do
    if [ $i != "BASH_FUNC_module()" -a  $i != "}" ] 
    then
        unset $i
    fi
done

export PATH=/usr/lib64/qt-3.3/bin:/usr/local/bin:/bin:/usr/bin:/usr/local/sbin:/usr/sbin:/sbin

export HOME=/home/hep/dbauer

export PWD=`pwd`

# now get at least my bash stuff back
source /home/hep/dbauer/.bashrc

RELVER=0

if [ -e /usr/bin/lsb_release ]; then
    RELVER=`/usr/bin/lsb_release -rs | cut -f1 -d"."`
else
    echo "/usr/bin/lsb_release not found, cannot determine release version."
    exit 0
fi

# echo "running on EL ${RELVER}"

if [ $RELVER == 6 ]; then
    source /cvmfs/grid.cern.ch/umd-sl6ui-latest/etc/profile.d/setup-ui-example.sh
    echo "Warning: Log file issues causing problems forCREAM on SL6."
else
    source /cvmfs/grid.cern.ch/umd-c7ui-latest/etc/profile.d/setup-c7-ui-example.sh   
    export LCG_GFAL_INFOSYS="topbdii.grid.hep.ph.ic.ac.uk:2170"
fi

# setup condor
echo "Setting up local condor submit. This might have to be removed if cvmfs ui gets updated."
export MYCONDOR=/home/hep/dbauer/dirac_site_tests/condor
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:${MYCONDOR}/usr/lib64/
export CONDOR_CONFIG=${MYCONDOR}/condor_config

