#! /bin/bash 
echo "Excuting pilot_test.sh at " $SITE_NAME
echo -e "\n"
date 

sleep 10
echo -e "\n"
echo "Checking the environment"
echo -e "\n"
echo "Current directory: "
pwd
echo "And who am I ? "
whoami

ghostname=`hostname --long 2>&1` 
gipname=`hostname --ip-address 2>&1` 
echo "WN: " $ghostname "has address" $gipname

echo "Operating system: "
uname -a
cat /etc/redhat-release

env | sort >> environment.txt
echo "==============================" >> environment.txt
rpm -qa | sort >> environment.txt

# **** who am i on the grid ***
ls /cvmfs/
echo -e "\n"
voms-proxy-info -all


