#!/usr/bin/python -tt 

import os
import sys
import string
import re
import datetime
import pwd
import grp

# any VO installed in the original setup has a total of 400 accounts                                                                
# any VO setup thereafter has 200 accounts
BIG_VOS = [ 'atlas' ,'cms' , 'lhcb', 'dteam', 'ilc', 'ops']
SMALL_VOS = [ 'comet.j-parc.jp', 'hyperk.org', 'pheno', 't2k.org', 'gridpp', 'na62.vo.gridpp.ac.uk', 
              'vo.londongrid.ac.uk', 'vo.landslides.mossaic.org', 'lz']

def write_groups_conf(vo, groupsfile):

    # glexec only contains the default groups
    # try all wildcard combinations, so I don't need to worry
    # about finer points of the middleware
    groupsfile.write('\"/' + vo + '/ROLE=*\"::::\n')
    groupsfile.write('\"/' + vo + '/*\"::::\n')
# new version of yaim doesn't like this notation any longer    
#    groupsfile.write('\"/' + vo + '\"::::\n')


def write_users_conf(vo, ce, usersfile):

    
    first_account = 0
    number_of_users = 0

    # work out which argus server and which type of VO we have
 
    if ce == 'lt2argus00':
        first_account = 100
        number_of_users = 200
        if vo in SMALL_VOS:
            number_of_users = 50
    elif ce == 'lt2argus01':
        first_account = 300
        number_of_users = 200
        if vo in SMALL_VOS:
            first_account = 150
            number_of_users = 50
    else:
        print 'unrecognized ce: valid options are lt2argus00 and lt2argus01'
        sys.exit(1)
        
        
            

    basename = get_base_name(vo)
    glxbasename = 'glx-'+basename[4:]
    basegroup=grp.getgrnam(basename)
     
    # lets construct some plain users first
    for i in range(first_account,first_account+number_of_users):
        username=''
        if i < 10:
            username=glxbasename+'00'+str(i)
        elif i < 100:
            username=glxbasename+'0'+str(i)
        else:
            username=glxbasename+str(i)    

        details=pwd.getpwnam(username)
        usersfile.write(str(details.pw_uid)+':'+username+':'+str(details.pw_gid)+':'+basename+':'+vo+'::\n')    


            

 # read in list of VOs from file   
def get_vo_list():
    vofile = open("vos.txt", 'rU')
    vostr = vofile.read()
    volist = []
    for vo in vostr.split('\n'):
        # protect against empty lines
        if len(vo) > 0:
            volist.append(vo.strip()) # remove whitespace
    return volist    


# matches official VO name to base group
def get_base_name(voname):
    # beats having lots of if statements, until I think of something better
     vo={}
     vo['atlas'] = ['lt2-atlas']
     vo['biomed'] = ['lt2-biomed']
     vo['calice'] = ['lt2-calice']
     vo['camont']= ['lt2-camont']
     vo['cedar'] = ['lt2-cedar']
     vo['cms'] = ['lt2-cms']
     vo['comet.j-parc.jp'] = ['lt2-comet']
     vo['dteam'] = ['lt2-dteam']
     vo['dzero'] = ['lt2-dzero']
     vo['fusion'] = ['lt2-fusion']
     vo['gridpp'] = ['lt2-gridpp']
     vo['hone'] = ['lt2-hone']
     vo['ilc'] = ['lt2-ilc']
     vo['lhcb'] = ['lt2-lhcb']
     vo['mice'] = ['lt2-mice']
     vo['monitoring.ngs.ac.uk'] = ['lt2-monngs']
     vo['na62.vo.gridpp.ac.uk'] = ['lt2-nast']
     vo['ngs.ac.uk'] = ['lt2-ngs']
     vo['ops'] = ['lt2-ops']
     vo['pheno'] = ['lt2-pheno']
     vo['supernemo.vo.eu-egee.org'] = ['lt2-snemo']
     vo['t2k.org'] = ['lt2-t2k']
     vo['vo.landslides.mossaic.org'] = ['lt2-lands']
     vo['vo.londongrid.ac.uk'] = ['lt2-london']
     vo['hyperk.org'] = ['lt2-hyperk']
     vo['vo.helio-vo.eu'] = ['lt2-helio']
     vo['ipv6.hepix.org'] = ['lt2-ipvs']
     vo['lz'] = ['lt2-lz']

     return vo[voname][0]

#####################################################################

def main():
    
    if len(sys.argv) != 2:
        print 'Usage is ./make_conf_glx.py [argus_name]'
        sys.exit(1)
    cename = sys.argv[1]
    # read in list of VOs
    volist = get_vo_list()

    # check if I've heard of this VO
    try:
        for vo in volist:
            get_base_name(vo)
    except KeyError:       
        print 'Detected typo in vos.txt (%s), please fix before proceeding' %vo
        sys.exit(1)


    gfile = open("groups.conf.new", 'wa')
    ufile = open("users.conf.new",'wa')
    
    for  vo in volist:
        print vo
        write_groups_conf(vo, gfile)
        write_users_conf(vo,cename,ufile)
    print "Done"
    gfile.close()

if __name__ == '__main__':
    main()
