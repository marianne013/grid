#!/usr/bin/python -tt 

# creates a users.conf groups.conf for an existing
# set of users
# note that the "base names" used to create these users
# accounts are just an example and not the ones actually used
# on our systems :-D

import os
import sys
import string
import re
import datetime
import pwd
import grp

def write_groups_conf(vo, groupsfile):

    # (almost) all VOs have sgm and prd
    if vo != 'ngs.ac.uk' and vo != 'monitoring.ngs.ac.uk':
        groupsfile.write('\"/' + vo + '/ROLE=lcgadmin\":::sgm:\n')
        groupsfile.write('\"/' + vo + '/ROLE=production\":::prd:\n')
    else:
        groupsfile.write('\"/' + vo + '/ROLE=Operations\":::sgm:\n')

    # very special roles for CMS
    if vo == 'cms':
        groupsfile.write('\"/cms/ROLE=hiproduction\":::prd:\n')
        groupsfile.write('\"/cms/ROLE=t1production\":::prd:\n')
        groupsfile.write('\"/cms/ROLE=priorityuser\":::pri:\n')
                
    # pilot roles
#    if vo == 'cms' or vo == 'atlas' or vo == 'ops' or vo == 'lhcb':
    if vo in ['cms','atlas','ops','lhcb']:
        groupsfile.write('\"/' + vo + '/ROLE=pilot\":::pilot:\n')

    # generic accounts for all versions of middleware    
    groupsfile.write('\"/' + vo + '/*\"::::\n')    
    groupsfile.write('\"/' + vo + '\"::::\n')


def write_users_conf(vo, ce, usersfile):
    
    first_account = 0
    if ce == 'ceprod05':
        first_account = 700
    elif ce == 'ceprod06':
        first_account = 1000
    elif ce == 'ceprod07':
        first_account = 400
    elif ce == 'ceprod08':
        first_account = 100
    elif ce == 'cetest00':
        first_account = 0
    else:
        print 'unrecognized ce: valid options are ceprod05-08 and cetest00'
        sys.exit(1)
        
    # number of accounts
    number_of_users = 100
    if vo == 'cms':
        number_of_users = 300
    if vo == 'monitoring.ngs.ac.uk':
        number_of_users = 10
    if vo == 'vo.helio-vo.eu':
        number_of_users = 10
        
    number_of_prd = 18
    if vo == 'cms':
        number_of_prd = 50
    if vo == 'vo.helio-vo.eu':
        number_of_prd = 10
                
    number_of_plt = 10
    if vo == 'cms':
        number_of_plt = 30
        
    number_of_pri = 90 # cms only

    # cetest00 is special
    if ce == 'cetest00':
       number_of_users = 50
       if vo == 'na62.vo.gridpp.ac.uk':
           number_of_users = 10
       number_of_prd = 5
       if vo == 'dteam' or vo == 'ops':
           number_of_prd = 0
       number_of_plt = 5 # except of course for cms
       if vo == 'cms':
           number_of_plt = 25
       number_of_pri = 50

    basename = get_base_name(vo)
    basegroup=grp.getgrnam(basename)
     
    # lets construct some plain users first
    for i in range(first_account,first_account+number_of_users):
        username=''
        if i < 10:
            username=basename+'00'+str(i)
        elif i < 100:
            username=basename+'0'+str(i)
        else:
            username=basename+str(i)    

        details=pwd.getpwnam(username)
        usersfile.write(str(details.pw_uid)+':'+username+':'+str(details.pw_gid)+':'+basename+':'+vo+'::\n')    

    
    # priority users (CMS only)
    
    if vo == 'cms':
        write_special_users(usersfile,vo,first_account,number_of_pri,'pri')
                                                                                

    # pilot users (ATLAS, CMS, LHCB, OPS, ILC) # apparently not dteam
    if vo in ['cms', 'atlas', 'lhcb', 'ops', 'ilc']:
        write_special_users(usersfile,vo,first_account,number_of_plt,'pilot')

    # prd users
    if vo != 'monitoring.ngs.ac.uk':
        write_special_users(usersfile,vo,first_account,number_of_prd,'prd')


    # sgm users - there's only one (unless you are a WMS that is)
    # sgm users do not have their own unix groups
    username=basename+'sgm'
    details=pwd.getpwnam(username)
    usersfile.write(str(details.pw_uid)+':'+username+':'+str(details.pw_gid)+','+str(basegroup.gr_gid)+':'+basename+','+basename+':'+vo+':sgm:\n')
    

# atype can be: prd, pri or pilot
def write_special_users(usersfile, vo, first_account, n_of_users, atype):
#    print 'In write_special users: '+vo+' '+atype
    suffix = str(atype)
    if atype == 'pilot':
        suffix = 'plt'
                
    basename = get_base_name(vo)
    basegroup=grp.getgrnam(basename)
      
    for i in range(first_account,first_account+n_of_users):
        username=''
        if i < 10:
            username=basename+suffix+'00'+str(i)
        elif i < 100:
            username=basename+suffix+'0'+str(i)
        else:
            username=basename+suffix+str(i)
            
        # i hate languages where indentations count
        details=pwd.getpwnam(username)
        usersfile.write(str(details.pw_uid)+':'+username+':'+str(details.pw_gid)+','+str(basegroup.gr_gid)+':'+basename+suffix+','
                        +basename+':'+vo+':'+atype+':\n')
            

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
     vo['atlas'] = ['grid-atlas'] 
     vo['biomed'] = ['grid-biomed']
     vo['calice'] = ['grid-calice']
     vo['camont']= ['grid-camont']
     vo['cedar'] = ['grid-cedar']
     vo['cms'] = ['grid-cms']
     vo['comet.j-parc.jp'] = ['grid-comet']
     vo['dteam'] = ['grid-dteam']
     vo['dzero'] = ['grid-dzero']
     vo['fusion'] = ['grid-fusion']
     vo['gridpp'] = ['grid-gridpp']
     vo['hone'] = ['grid-hone']
     vo['ilc'] = ['grid-ilc']
     vo['lhcb'] = ['grid-lhcb']
     vo['mice'] = ['grid-mice']
     # vo['monitoring.ngs.ac.uk'] = ['grid-monngs']
     vo['na62.vo.gridpp.ac.uk'] = ['grid-nast']
     # vo['ngs.ac.uk'] = ['grid-ngs']
     vo['ops'] = ['grid-ops']
     vo['pheno'] = ['grid-pheno']
     # vo['supernemo.vo.eu-egee.org'] = ['grid-snemo']
     vo['t2k.org'] = ['grid-t2k']
     vo['vo.helio-vo.eu'] = ['grid-helio']
     vo['vo.landslides.mossaic.org'] = ['grid-lands']
     vo['vo.londongrid.ac.uk'] = ['grid-london']
     
     return vo[voname][0]

#####################################################################

def main():
    
    if len(sys.argv) != 2:
        print 'Usage is ./make_conf.py [cename]'
        sys.exit(1)
    cename = sys.argv[1]
    # read in list of VOs
    volist = get_vo_list()
    
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
