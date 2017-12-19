#!/usr/bin/env python
"""contains most of the actual VO data (voms servers etc)
     plus some access functions
     currently we are supporting the following VOs:
     (1) atlas (2) biomed (3) calice (4) cms (5) comet.j-parc.jp (6) dteam (7) dune (8) gridpp
     (9) hyperk.org  (10) ilc (11) lhcb (12) lsst (13) lz (14) mice (15) na62.vo.gridpp.ac.uk
     (16) ops (17) pheno (18) snoplus.snolab.ca (19) solidexperiment.org  (10) t2k.org "
"""
import collections

# for data storage
def vodata(voname):
    """ basename, swdir, port """
    VOData = collections.namedtuple('VOData', 'basename swdir port')
    vo = {}
    vo['atlas'] = VOData('lt2-atlas', '/cvmfs/atlas.cern.ch', '15001')
    vo['biomed'] = VOData('lt2-biomed', '/cvmfs/biomed.egi.eu', '15000')
    vo['calice'] = VOData('lt2-calice', '/cvmfs/calice.desy.de', '15102')
    vo['cms'] = VOData('lt2-cms','/cvmfs/cms.cern.ch','15002')
    vo['comet.j-parc.jp'] = VOData('lt2-comet', '/cvmfs/comet.egi.eu', '15505')
    
    vo['dteam'] = VOData('lt2-dteam', '/vols/sl5_exp_software/dteam', '15004')
    vo['dune'] = VOData('lt2-dune', '/cvmfs/dune.opensciencegrid.org', '15042')
    vo['gridpp'] = VOData('lt2-gridpp', '/cvmfs/gridpp.egi.eu', '15000')
    vo['hyperk.org'] = VOData('lt2-hyperk', '/cvmfs/hyperk.egi.eu', '15510')
    vo['ilc'] = VOData('lt2-ilc', '/cvmfs/ilc.desy.de', '15110')

    vo['lhcb'] = VOData('lt2-lhcb', '/cvmfs/lhcb.cern.ch', '15003')
    vo['lsst'] = VOData('lt2-lsst', '/cvmfs/lsst.opensciencegrid.org', '15003')
    vo['lz'] = VOData('lt2-lz', '/cvmfs/lz.opensciencegrid.org', '15001')
    vo['mice'] = VOData('lt2-mice', '/cvmfs/mice.egi.eu', '15001')
    vo['na62.vo.gridpp.ac.uk'] = VOData('lt2-nast', '/cvmfs/na62.cern.ch', '15501')

    vo['ops'] = VOData('lt2-ops', '/vols/sl5_exp_software/ops', '15009')
    vo['pheno'] = VOData('lt2-pheno', '/cvmfs/pheno.egi.eu', '15011')
    vo['snoplus.snolab.ca'] = VOData('lt2-snopl', '/cvmfs/snoplus.egi.eu', '15503')
    vo['solidexperiment.org'] = VOData('lt2-solid', '/cvmfs/solidexperiment.egi.eu', '15513')
    vo['t2k.org'] = VOData('lt2-t2k', '/cvmfs/t2k.egi.eu', '15003')
  
    
    return vo[voname]


# access functions
def get_voms_servers(voname):
    """returns a list of voms servers for a VO
    format is: server, DN. CA"""
    VomsServer = collections.namedtuple('VomsServer', 'server dn ca')
    vomsservers = []
    # first a list of all voms servers
    gridpp1 = VomsServer('voms.gridpp.ac.uk',
                         '/C=UK/O=eScience/OU=Manchester/L=HEP/CN=voms.gridpp.ac.uk',
                         '/C=UK/O=eScienceCA/OU=Authority/CN=UK e-Science CA 2B')
    gridpp2 = VomsServer('voms02.gridpp.ac.uk',
                         '/C=UK/O=eScience/OU=Oxford/L=OeSC/CN=voms02.gridpp.ac.uk',
                         '/C=UK/O=eScienceCA/OU=Authority/CN=UK e-Science CA 2B')
    gridpp3 = VomsServer('voms03.gridpp.ac.uk',
                         '/C=UK/O=eScience/OU=Imperial/L=Physics/CN=voms03.gridpp.ac.uk',
                         '/C=UK/O=eScienceCA/OU=Authority/CN=UK e-Science CA 2B')
    wisc = VomsServer('voms.hep.wisc.edu',
                      '/DC=org/DC=opensciencegrid/O=Open Science Grid/OU=Services/CN=voms.hep.wisc.edu',
                      '/DC=org/DC=cilogon/C=US/O=CILogon/CN=CILogon OSG CA 1')
    cern1 = VomsServer('voms2.cern.ch',
                       '/DC=ch/DC=cern/OU=computers/CN=voms2.cern.ch',
                       '/DC=ch/DC=cern/CN=CERN Grid Certification Authority')
    cern2 = VomsServer('lcg-voms2.cern.ch',
                       '/DC=ch/DC=cern/OU=computers/CN=lcg-voms2.cern.ch',
                       '/DC=ch/DC=cern/CN=CERN Grid Certification Authority')
    fnal1 = VomsServer('voms1.fnal.gov',
                       '/DC=org/DC=opensciencegrid/O=Open Science Grid/OU=Services/CN=voms1.fnal.gov',
                       '/DC=org/DC=cilogon/C=US/O=CILogon/CN=CILogon OSG CA 1')
    fnal2 =  VomsServer('voms2.fnal.gov',
                       '/DC=org/DC=opensciencegrid/O=Open Science Grid/OU=Services/CN=voms2.fnal.gov',
                       '/DC=org/DC=cilogon/C=US/O=CILogon/CN=CILogon OSG CA 1')
    desy = VomsServer('grid-voms.desy.de',
                      '/C=DE/O=GermanGrid/OU=DESY/CN=host/grid-voms.desy.de',
                      '/C=DE/O=GermanGrid/CN=GridKa-CA')
    france = VomsServer('cclcgvomsli01.in2p3.fr',
                        '/O=GRID-FR/C=FR/O=CNRS/OU=CC-IN2P3/CN=cclcgvomsli01.in2p3.fr',
                        '/C=FR/O=CNRS/CN=GRID2-FR')
    greece1 = VomsServer('voms.hellasgrid.gr',
                         '/C=GR/O=HellasGrid/OU=hellasgrid.gr/CN=voms.hellasgrid.gr',
                         '/C=GR/O=HellasGrid/OU=Certification Authorities/CN=HellasGrid CA 2016')
    greece2 =  VomsServer('voms2.hellasgrid.gr',
                          '/C=GR/O=HellasGrid/OU=hellasgrid.gr/CN=voms2.hellasgrid.gr',
                          '/C=GR/O=HellasGrid/OU=Certification Authorities/CN=HellasGrid CA 2016')

    if voname in ['comet.j-parc.jp', 'gridpp', ' hyperk.org', 'mice', 'na62.vo.gridpp.ac.uk', 'pheno', 'snoplus.snolab.ca', 'solidexperiment.org ', 't2k.org']:
        vomsservers = [gridpp1, gridpp2, gridpp3]
    elif voname == 'lz':
        vomsservers = [wisc]
    elif voname in ['atlas', 'cms', 'lhcb', 'ops']:
        vomsservers = [cern1, cern2]
    elif voname in ['dune', 'lsst']:
        vomsservers = [fnal1, fnal2]
    elif voname in ['calice', 'ilc']:
         vomsservers = [desy]
    elif voname == 'biomed':
        vomsserver = [france]
    elif voname == 'dteam':
        vomsserver = ['greece1', 'greece2']
    else:
        print "ERROR: Cannot find any vomsserver for VO %s" %voname
    

    
    return vomsservers

def get_sw_dir(voname):
    """returns software dir for given VO as a string"""
    return  vodata(voname).swdir

def get_base_name(voname):
    """returns the basename to construct user accounts"""
    return vodata(voname).basename

def get_port(voname):
    """returns port number of voms server
    all our VOs use the same port number accross all voms servers"""
    return vodata(voname).port
