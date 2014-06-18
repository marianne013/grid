#!/usr/bin/python -tt

import ldap
# import ldapurl
import os
import sys
import string
import re
import datetime
import csv
import urllib


# this requires a UI and a valid dteam or ops proxy
# as the name alludes, this is for SL6

# needs 'disclaimer_small.html' to work out of the box:
# http://www.hep.ph.ic.ac.uk/~dbauer/grid/public_logs/emi_deployment/disclaimer_small.html

# query resource bdii of a service:
# old:  /usr/bin/ldapsearch -x -H ldap://bdii.grid.hep.ph.ic.ac.uk:2170 -b mds-vo-name=resource,o=grid
# new:  /usr/bin/ldapsearch -x -H ldap://bdii.grid.hep.ph.ic.ac.uk:2170 -b GLUE2GroupID=resource,o=glue

# note port when querying an arc ce directly:
# ldapsearch -LLL -x -H ldap://cetest01.grid.hep.ph.ic.ac.uk:2135 -b o=glue


WN_VERS_URL = "http://lt2admin.grid.hep.ph.ic.ac.uk/sitemon/versions.txt"

########## helper functions ####################


def bdii_name(sitename):
    """returns name fo bdii for a given site"""
    # currently this saves me from having to use the topbdii 
    bdiis = {}
    # London
    bdiis['UKI-LT2-IC-HEP'] = 'bdii.grid.hep.ph.ic.ac.uk'
    bdiis['UKI-LT2-Brunel'] = 'dc2-grid-69.brunel.ac.uk'
    bdiis['UKI-LT2-RHUL'] = 'sbdii2.ppgrid1.rhul.ac.uk'
    bdiis['UKI-LT2-QMUL'] = 'bdii02.esc.qmul.ac.uk'
    bdiis['UKI-LT2-UCL-HEP'] = 'lcg-bdii01.hep.ucl.ac.uk'
    # Southgrid
    bdiis['UKI-SOUTHGRID-BHAM-HEP'] = 'epgr09.ph.bham.ac.uk'
    bdiis['UKI-SOUTHGRID-BRIS-HEP'] = 'lcgbdii02.phy.bris.ac.uk'
    bdiis['UKI-SOUTHGRID-RALPP'] = 'site-bdii.pp.rl.ac.uk'
    bdiis['UKI-SOUTHGRID-OX-HEP'] = 't2bdii06.physics.ox.ac.uk'
    bdiis['UKI-SOUTHGRID-CAM-HEP'] = 'vserv08.hep.phy.cam.ac.uk'
    bdiis['UKI-SOUTHGRID-SUSX'] = 'grid-bdii-02.hpc.susx.ac.uk'
    bdiis['EFDA-JET'] = 'grid005.jet.efda.org'
    # Northgrid
    bdiis['UKI-NORTHGRID-SHEF-HEP'] = 'lcg.shef.ac.uk'
    bdiis['UKI-NORTHGRID-LANCS-HEP'] = 'fal-pygrid-14.lancs.ac.uk'
    bdiis['UKI-NORTHGRID-LIV-HEP'] = 'hepgrid4.ph.liv.ac.uk'
    bdiis['UKI-NORTHGRID-MAN-HEP'] = 'site-bdii.tier2.hep.manchester.ac.uk'
    # Scotgrid
    bdiis['UKI-SCOTGRID-DURHAM'] = 'site-bdii.dur.scotgrid.ac.uk'
    bdiis['UKI-SCOTGRID-ECDF'] = 'info3.glite.ecdf.ed.ac.uk'
    bdiis['UKI-SCOTGRID-GLASGOW'] = 'svr030.gla.scotgrid.ac.uk'
   # Tier 1
    bdiis['RAL-LCG2'] = 'site-bdii.gridpp.rl.ac.uk'


    return bdiis[sitename]



def get_list_of_ces(ce_ldapresult):
    """gets list of unique CE names from all the queue names"""
    ces = {}
    # protect against bdii being down 
    if len(ce_ldapresult) > 0:
        for ce_q in ce_ldapresult: 
            match = re.search(r'=\w+.+:', ce_q[0]) #find an '=' sign, followed by some letters and dots until the colon
            testkey = match.group()[1:-1] # except first (=) and last (:) letter -> this is the name of the CE
            # appease Simon's paranoia
            # check if the CE name only contains letters, numbers and dots to avoid 'bdii hacks'    
            allowed = set(string.ascii_lowercase + string.digits + '.' + '-')
            # check if set is a subset of allowed characters                    
            if set(testkey) <= allowed:
                # don't do anything                                                                              
                pass
            else:
                print 'dodgy characters in CE name: '+testkey+' ! Exiting program'
                sys.exit(1)
            # end of paranoia test
            if testkey not in ces:
                # print ce_q[1]
                if ce_q[1]['GlueCEInfoJobManager'][0] == 'arc':
                    # print ce_q[1] # this does not contain the version
                    # I could try a direct query, pah
                    # arcmds = 'o=grid'
                    # arcbdii = "ldap://"+str(testkey)+':2135'
                    # arcldap = ldap.initialize(arcbdii)
                    # arctest = [] # list
                    # arctest = arcldap.search_s(arcmds, ldap.SCOPE_SUBTREE,'objectClass=nordugrid-cluster')
                    # print arctest[0][1]['nordugrid-cluster-middleware'][0]
                    ces[testkey] = 'ARC'
                else:
                    ces[testkey] = ce_q[1]['GlueCEImplementationVersion'][0]
    return ces


# and now for some glue2
def get_middleware_version(sitename, gridnode):
    """tries to extract middleware version as advertised by the grid node"""
    print 'get_middleware_version: '+gridnode+ ' at '+sitename
    mds2 = 'o=glue'
    sbdii = "ldap://"+bdii_name(sitename)+':2170'
    l2 = ldap.initialize(sbdii)
    magicendpoint = "(GLUE2EndpointID=*"+gridnode+"*)"
    glue2test = [] # list
    mw_ver = []
    # example: glue2test=l2.search_s(mds2, ldap.SCOPE_SUBTREE, '(GLUE2EndpointID=*dc2-grid*)')
    glue2test = l2.search_s(mds2, ldap.SCOPE_SUBTREE, magicendpoint)
    if len(glue2test) > 0:
        if 'GLUE2EntityOtherInfo' in glue2test[0][1]:
            # that's apparently a list comprehension
            mw_ver = [x for x in glue2test[0][1]['GLUE2EntityOtherInfo'] if x.startswith('MiddlewareVersion=')]
            # Append a default entry, in-case the above filter finds nothing...
            mw_ver.append('Stealth middleware version') # Here I don't need brackets...
            # print 'And now for something completely different: '
            # print '%s' % mw_ver[0]
        else:
            mw_ver.extend(['Stealth middleware version']) # I need those brackets, otherwise I end up with chars
    else:
        # this is basically RAL-LCG2
        mw_ver.extend(['Middleware: N/A'])
    # print len(mw_ver)   
    # make sure Simon hasn't put any Christmas messages in the bdii
    # check if the CE name only contains letters, numbers and dots to avoid 'bdii hacks'                                          
    allowed = set(string.ascii_letters + string.digits + '.' + '-' + '=' + ':' + '/' + string.whitespace)
    # check if set is a subset of allowed characters
    if set(mw_ver[0]) <= allowed:
        # don't do anything                                                                                                       
        pass
    else:
        print 'dodgy characters in Middleware version: '+mw_ver[0]+' ! Exiting program'
        sys.exit(1)
    # end of paranoia test     

    return mw_ver[0]


### print the different sections

def write_ce_info(ce_ldapresult, sitename, outfile):
    """CE section in any given row"""
    # CE names are not unique, they show up once for each queue
    outfile.write('<td bgcolor=#CCFFCC>')
    # protect against bdii being down 
    if len(ce_ldapresult) > 0: 
        ces = get_list_of_ces(ce_ldapresult)
        for key in ces:
            # see if I can extract the middleware version
            emiversion = get_middleware_version(sitename, key)
            emi2test = 'MiddlewareVersion=2.' in str(emiversion)
            if emi2test == True:
                outfile.write('<font color=#FF000>')
            outfile.write(key + ': ' + ces[key] + ' <br>')
            outfile.write(emiversion+' <br>')
            if ces[key] == 'ARC':
                # for the ARC CEs, try and determine the arc version:
                arcmds = 'o=grid'
                arcbdii = "ldap://"+str(key)+':2135'
                arcldap = ldap.initialize(arcbdii)
                arctest = [] # list
                arctest = arcldap.search_s(arcmds, ldap.SCOPE_SUBTREE,'objectClass=nordugrid-cluster')
                outfile.write(str(arctest[0][1]['nordugrid-cluster-middleware'][0])+' <br>')
            if emi2test == True:
                outfile.write('</font>')
            # try and determine the operating system (CREAMCEs only)   
            # for ipv6 CEs this times out
            if (ces[key] != 'ARC') and (key != 'v6ce00.grid.hep.ph.ic.ac.uk'):
                cmdstr = 'uberftp ' + key + ' \"cat /etc/redhat-release\"  | head -3 | tail -1 >> ce.tmp'
                opsys = os.system(cmdstr)
                if opsys == 0:
                    ftmp = open("ce.tmp", 'rU')
                    ceop = ftmp.read()
                    if ceop[0:3] == '220':
                        # outfile.write('Could not determine CE operating system. <br> <br>')
                        outfile.write('<br><br>')
                    else:
                        outfile.write(str(ceop) + ' <br> <br>') 
                        ftmp.close()
                else:
                 # outfile.write('Could not determine CE operating system. <br> <br>')
                    outfile.write('<br><br>')
                os.system("rm -rf ce.tmp")  
            else:
                if ces[key] == 'ARC':
                    # outfile.write('ARC CE: Cannot determine CE operating system <br> <br>')         
                    outfile.write('<br><br>')
                else:
                    outfile.write('uberftp: Network problem <br><br>')
        # done (matches 'for') , close column    
        outfile.write('</td>')
    else:
        outfile.write('No CEs found. </td>')
                    

def write_se_info(se_ldapresult, sitename, outfile):
    outfile.write('<td>')
    if len(se_ldapresult) > 0:
        for se in se_ldapresult:
            match = re.search(r'=\w+.+,M', se[0])
            if match:
                # print (match.group()[1:-2])
                # print se[1] 

                emiversion = get_middleware_version(sitename, (match.group()[1:-2]))
                emi2test = 'MiddlewareVersion=2.' in str(emiversion)
                if emi2test == True:
                    outfile.write('<font color=#FF000>')
                  
                outfile.write(match.group()[1:-2] + ': ')
                # make it look pretty on web page
                if sitename == 'RAL-LCG2':
                    outfile.write(' <br>')

                outfile.write(se[1]['GlueSEImplementationName'][0]+' '+se[1]['GlueSEImplementationVersion'][0] + ' <br>') 
                outfile.write(emiversion)
                if emi2test == True:
                    outfile.write('</font>')
                outfile.write(' <br><br> ')   
            else:
                outfile.write('No SE found at.')
    else:
        outfile.write('No SE found.')
    # done, close column        
    outfile.write('</td>')        
                    

def format_wmslb_results(wmslbres, sitename, outfile):
    """Make WMS/LB results look pretty"""
    for i in range(0, len(wmslbres)):
        match = re.search(r'=+\w+.+?_', str(wmslbres[i][0]))
        testkey = match.group()[1:-1] # except first (=) and last (:) letter
        outfile.write(testkey+': '+str(wmslbres[i][1]['GLUE2EndpointImplementationVersion'][0])+' <br>')
        emiversion = get_middleware_version(sitename, testkey)
        emi2test = 'MiddlewareVersion=2.' in str(emiversion)
        if emi2test == True:
            outfile.write('<font color=#FF000>')
        outfile.write(emiversion+' <br> <br> ')
        if emi2test == True:
            outfile.write('</font>')  

def write_wmslb_info(sitename, outfile):
    """WMS/LB section of extra services table"""
    sbdii = "ldap://"+bdii_name(sitename)+':2170'
    lq = ldap.initialize(sbdii)
    mds = 'o=glue'
    # WMS
    wmsres = lq.search_s(mds, ldap.SCOPE_SUBTREE, '(GLUE2EndpointInterfaceName=org.glite.wms.WMProxy)')
    # this should also be outsourced
    if len(wmsres) > 0:
        format_wmslb_results(wmsres, sitename, outfile)
    else:
        outfile.write('WMS: N/A <br>')
    # LB    
    lbres = lq.search_s(mds, ldap.SCOPE_SUBTREE, '(GLUE2EndpointInterfaceName=org.glite.lb.Server)')
    if len(lbres) > 0:
        format_wmslb_results(lbres, sitename, outfile)
    else:
        outfile.write('LB: N/A <br>')


def write_bdii_info(bdii_ldapresults, sitename, outfile):
    """Fills bdii column in any given row"""
    # find the bdiis name in glue output
    found = str(bdii_ldapresults[0][0]).find('_')
    bdiinodename = str(bdii_ldapresults[0][0][16:found])
    # apply the paranoia test
    allowed = set(string.ascii_lowercase + string.digits + '.' + '-')
    # check if set is a subset of allowed characters                                                                              
    if set(bdiinodename) <= allowed:
        # don't do anything                                                                                                       
        pass
    else:
        print 'dodgy characters in BDII name: '+bdiinodename+' ! Exiting program'
        sys.exit(1)
   # end of paranoia test

    emi2test = False
    emiversion = get_middleware_version(sitename, bdiinodename)
    emi2test = 'MiddlewareVersion=2.' in str(emiversion)             
    if emi2test:
        outfile.write('<font color=#FF000>')                
    outfile.write(bdiinodename+': ')
    outfile.write(bdii_ldapresults[0][1]['GLUE2EndpointImplementationVersion'][0]+' <br> ')
    outfile.write(emiversion)
    if emi2test == True:
        outfile.write('</font>')


def write_site_info(sitename, wns, outfile):
    """Assemble all info for one site (row)"""
    # --- CEs ---
    ce_ldapresult = [] # list
    sbdii = "ldap://"+bdii_name(sitename)+':2170'
    l = ldap.initialize(sbdii)
    mds = 'Mds-vo-name='+sitename+',o=grid'
    # print mds
    try:
        ce_ldapresult = l.search_s(mds, ldap.SCOPE_SUBTREE, '(GlueCEUniqueID=*)')
    except ldap.SERVER_DOWN:
        print 'site bdii not reachable at '+sitename
    except ldap.NO_SUCH_OBJECT:
        print 'no CE found at ' +sitename
    except ldap.OTHER:
        print 'I give up at '+sitename
    # giving all these variables the same name is probably bad practice
    write_ce_info(ce_ldapresult, sitename, outfile)

    # --- SE ---
    se_ldapresult = []
    try:
        se_ldapresult = l.search_s( mds, ldap.SCOPE_SUBTREE, '(GlueSEUniqueID=*)')
    except ldap.SERVER_DOWN:   
        # don't do anything
        pass
    except ldap.NO_SUCH_OBJECT:
        print 'no SE found at ' +sitename
    except ldap.OTHER:
        print 'I give up at '+sitename

    write_se_info(se_ldapresult, sitename, outfile)

    # --- bdii ---        
    outfile.write('<td bgcolor=#CCFFCC>')
    # print 'BDII:'
    mds = 'o=glue'
    bdii_ldapresults = []
    try:
        bdii_ldapresults = l.search_s(mds, ldap.SCOPE_SUBTREE,'(GLUE2EndpointInterfaceName=bdii_site)')
        write_bdii_info(bdii_ldapresults, sitename, outfile)
    except ldap.SERVER_DOWN:
        outfile.write('bdii down')        
    except ldap.INVALID_DN_SYNTAX:
        outfile.write('<font color="#FF0000">'+bdii_name(sitename)+': <br> Cannot determine version (probably glite)</font>')
    except ldap.NO_SUCH_OBJECT:
        outfile.write('no information in site bdii')
    except ldap.OTHER:
        outfile.write('unsepcified ldap error')
   
    outfile.write('</td>')

    # --- WN ---
    outfile.write('<td>')
    ces = get_list_of_ces(ce_ldapresult)
    # if the bdii is down, I can't get the list of CEs
    if len(ce_ldapresult) == 0:
        outfile.write('no information available')
    else:    
        for key in ces:
            # apparently that construct is obsolete as well, sigh
            # only CREAMCEs have nagios tests for WN versions
            if wns.has_key(key):
                emi2ce = False
                if wns[key] in ('EMI 2.8.0-1', 'EMI 2.10.2-1.el6', 'EMI Tarball 2.6.0-1', 'EMI 2.10.5-1.el6', 'EMI Tarball 2.10.4-1.el6', 'EMI 2.8.1-1', 'EMI 2.5.0-1', 'EMI 2.10.0-1.el6', 'EMI 2.10.7-1.el6'):
                    outfile.write('<font color=#FF000>')
                    emi2ce = True
                outfile.write(key + ': ' + wns[key] + ' <br>')
                if emi2ce == True:
                    outfile.write('</font>')

    outfile.write('</td></tr>')   # matches else for len(ce_ldapresult) == 0
    outfile.write('\n')
        



def main():
    """write table listing al UK grid nodes and their versions"""
    # clean slate
    os.system("rm -rf s_o_n.html")
    os.system("rm -rf ce.tmp")


    # read in WNs from URL
    # CE names are dictionary keys
    ver_file = urllib.urlopen(WN_VERS_URL)
    wns = dict(csv.reader(ver_file))
    ver_file.close()

    # London, Southgrid, Northgrid, Scotgrid, Tier 1    
    uksites = [ 'UKI-LT2-IC-HEP', 'UKI-LT2-Brunel', 'UKI-LT2-RHUL',
                'UKI-LT2-QMUL', 'UKI-LT2-UCL-HEP', 'UKI-SOUTHGRID-BHAM-HEP',
                'UKI-SOUTHGRID-BRIS-HEP', 'UKI-SOUTHGRID-RALPP', 'UKI-SOUTHGRID-OX-HEP',
                'UKI-SOUTHGRID-CAM-HEP', 'UKI-SOUTHGRID-SUSX', 'EFDA-JET', 'UKI-NORTHGRID-SHEF-HEP', 
                'UKI-NORTHGRID-LANCS-HEP', 'UKI-NORTHGRID-LIV-HEP', 'UKI-NORTHGRID-MAN-HEP', 
                'UKI-SCOTGRID-DURHAM','UKI-SCOTGRID-ECDF', 'UKI-SCOTGRID-GLASGOW', 'RAL-LCG2']
        
    # now what I really want is to write this to an html file
    # read in a standard disclaimer and copy it to a new file
    fr = open("disclaimer_small.html", 'rU')
    disclaimer = fr.read()
    f = open("s_o_t_n.html", 'wa')
    f.write(disclaimer) # this also contains the first line of the table
      
    

    for site in sorted(uksites):
        f.write('\n')
        # write table
        f.write('<tr><td>' + site + '</td>')
        print '===================================================='
        print site, 'using: ', bdii_name(site)
        sbdii = "ldap://"+bdii_name(site)+':2170'
        # print ldapurl.isLDAPUrl(sbdii)
        # print sbdii
        write_site_info(site, wns, f)
    # end of uksites
    f.write('</table>')
    f.write('\n')
 

    f.write('<br><br>')
    f.write('\n\n')
    

    #----------------------------------------------
    # generate the 'special services' table (WMS,topbdii,LFC)

    specialsites =  [ 'UKI-LT2-IC-HEP', 'RAL-LCG2', 'UKI-SCOTGRID-GLASGOW', 'UKI-NORTHGRID-MAN-HEP']

    f.write('<table border="1"> \n')
    f.write('<tr> <td><b>Site</b></td> <td bgcolor=#CCFFCC><b>WMS/LB</b> </td> <td><b>topbdii</b></td> </td> <td bgcolor=#CCFFCC><b>LFC</b></td> </tr>')
    f.write('\n\n')
    
    for site in sorted(specialsites):
        f.write('\n')
        f.write('<tr><td>'+site+'</td><td bgcolor=#CCFFCC>')
        sbdii = "ldap://"+bdii_name(site)+':2170'
        lq = ldap.initialize(sbdii)
        mds = 'o=glue'
        # WMS/LB
        write_wmslb_info(site, f)
        f.write('</td><td>')
        # topbdii
        topresult = lq.search_s(mds, ldap.SCOPE_SUBTREE, '(GLUE2EndpointInterfaceName=bdii_top)')
        found = str(topresult[0][0]).find('_')
        topbdiiname = str(topresult[0][0][16:found])
        # print '%s' %topbdiiname
        emiversion = get_middleware_version(site,  topbdiiname)
        emi2test = 'MiddlewareVersion=2.' in str(emiversion)
        if emi2test == True:
            f.write('<font color=#FF000>')
        f.write(topbdiiname+': ')
        f.write('<br>')
        f.write(emiversion) 
        if emi2test == True:
            f.write('</font>')
        f.write('</td><td bgcolor=#CCFFCC>')
        # LFC
        lfcres = lq.search_s(mds, ldap.SCOPE_SUBTREE,'(GLUE2EndpointImplementationName=LFC)')
        if len(lfcres) > 0:
            match = re.search(r'=+\w+.+?-', str(lfcres[0]))
            lfcname = match.group()[1:-1] # except first (=) and last (:) letter
            f.write(lfcname+': '+ str(lfcres[0][1]['GLUE2EndpointImplementationVersion'][0])+' <br>')
            f.write('(' + lfcres[0][1]['GLUE2EntityOtherInfo'][1] + ') <br> <br>')
        else:
            f.write('LFC: N/A')

        f.write('</td></tr>')
        f.write('\n\n') # for loop end here

    f.write('</table>')    
    f.write('<br>')   
    f.write('\n\n')

    f.write('<b>The information from the bdiis/Nagios was last extracted on ')
    f.write('<font color=FF0000>')
    now = datetime.datetime.now()
    f.write(str(now.day)+'.'+str(now.month)+'.'+str(now.year)+'.')
    f.write('</font>')
    
    f.write('</body> \n')
    f.write('</html> \n')

    f.close()

if __name__ == '__main__':
    main()
  
