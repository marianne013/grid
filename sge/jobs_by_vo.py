#!/usr/bin/python
import xml.dom.minidom
import os
import sys
import string
import re
import socket


hostname=socket.gethostname()
#print hostname
thiscetype = 'cetype_in_job'
if hostname == 'ceprod05.grid.hep.ph.ic.ac.uk':
	thiscetype = ['cre05']
elif hostname == 'ceprod06.grid.hep.ph.ic.ac.uk':
	thiscetype = ['cre06']
elif hostname == 'ceprod07.grid.hep.ph.ic.ac.uk':
        thiscetype = ['cre07']
elif hostname == 'ceprod08.grid.hep.ph.ic.ac.uk':
        thiscetype = ['cre08']
elif hostname == 'cetest01.grid.hep.ph.ic.ac.uk':
        # jobs on cetest01 have different names
        thiscetype = ['STDIN', 'https', 'arc']
else:
	print 'Unknown CE!'

# re is the regex module

f=os.popen('qstat -u \* -xml -r')

dom=xml.dom.minidom.parse(f)

jobs=dom.getElementsByTagName('job_info')
run=jobs[0]
pen=jobs[1]
runjobs=run.getElementsByTagName('job_list')
penjobs=pen.getElementsByTagName('job_list')
vocount={}
cmsprdcount={}
relt2=re.compile('lt2[-]')
n_running_multicore=0
n_waiting_multicore=0
n_running_multicore_cms=0 # counts CMS multicore jobs only (jobs, not slots!)
n_waiting_multicore_cms=0 

def extractvo(re,string):
#	print string
        match=re.match(string)
        if match:
                return relt2.split(string)[1][:-3]
        else:
                return 'ngrid'


def extractvo6(re,string):
        match=re.match(string)
        if match:
                return relt2.split(string)[1][:-4]
        else:
                return 'ngrid'	


def fillvocount(joblist,constraince):
	global n_running_multicore
	global n_waiting_multicore
	global n_running_multicore_cms
	global n_waiting_multicore_cms
	n_running_multicore = 0
	n_waiting_multicore = 0
	n_running_multicore_cms=0
	n_waiting_multicore_cms=0

	for r in joblist:
		# which ce am I talking about here ?
		jobown=r.getElementsByTagName('JB_name')[0].childNodes[0].data
		cetype=jobown.split("_")[0]
		jobown=r.getElementsByTagName('JB_owner')[0].childNodes[0].data
	#	print jobown
		if((cetype=='cre06') and (jobown!='lt2-lhcbplt')):
			# ceprod06 user names have 4 digits	
			voname=extractvo6(relt2,jobown)
		else:
			voname=extractvo(relt2,jobown)
                state=r.getElementsByTagName('state')[0].childNodes[0].data
                slots=int(r.getElementsByTagName('slots')[0].childNodes[0].data)
		if((constraince==1 and (cetype in thiscetype)) or (constraince==0)):
			index=0
			if(state=='r'):
				index=0
				if slots == 8:
					n_running_multicore+=1
					if (voname=='cmsplt'):
						n_running_multicore_cms+=1
			if(state=='qw'):
				index=1
				if slots == 8:
					n_waiting_multicore+=1
					if (voname=='cmsplt'):
						n_waiting_multicore_cms+=1
					
			if(state=='Eqw'):
				index=2
				
			if vocount.has_key(voname):
				vocount[voname][index]=vocount[voname][index]+slots
			else:
				if(index==0):
					vocount[voname]=[slots,0,0]
				elif(index==1):
					vocount[voname]=[0,slots,0]
				elif(index==2):	
					vocount[voname]=[0,0,slots]	
				else:
					print "Help", index

				
def dumpvocount():
        tot=[0,0,0]
        totgrid=[0,0,0]
        print "\t\t[Running,Waiting,Error]"
        for vo in vocount.keys():
                print vo,'\t\t',vocount[vo]
                if(vo!='ngrid'):
                        totgrid[0]=totgrid[0]+vocount[vo][0]
                        totgrid[1]=totgrid[1]+vocount[vo][1]
			totgrid[2]=totgrid[2]+vocount[vo][2]
                tot[0]=tot[0]+vocount[vo][0]
                tot[1]=tot[1]+vocount[vo][1]
		tot[2]=tot[2]+vocount[vo][2]
        print 'total      \t',tot
        print 'total grid \t',totgrid
	print 'number of running multicore jobs (not slots!) \t', n_running_multicore
	print 'number of waiting multicore jobs (not slots!) \t', n_waiting_multicore
	print 'running multicore CMS only \t', n_running_multicore_cms
	print 'waiting multicore CMS only \t', n_waiting_multicore_cms


fillvocount(runjobs,0)
dumpvocount()
# reset array, sigh
vocount={}
print '\n'
print 'This CE (%s) only: ' %hostname[0:8]

fillvocount(runjobs,1)
dumpvocount()
