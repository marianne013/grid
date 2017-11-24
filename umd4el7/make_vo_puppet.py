#!/usr/bin/python -tt
""" generates yaml snippet for users config
    (replacement for users.conf/groups.conf)
"""
import sys
import pwd

from vo_data import get_sw_dir
from vo_data import get_voms_servers
from vo_data import get_port
from vo_data import get_base_name

# general rules
# ceprod05 starts at  700 (to  999)
# ceprod06 starts at 1000 (to 1299)
# ceprod07 starts at  400 (to  699)
# ceprod08 starts at  100 (to  399)
# cetest00 starts at    0 (to   49)
# cetest01 starts at   50 (     99)

# ipv6.hepix.org is only supported on cetest00 and v6ce00.
#                It has a total of three accounts:
#                lt2-ipvssgm, lt2-ipvs000, lt2-ipvs001

# number of user accounts per CE:
# ceprod: 100, except CMS = 300
# cetest00: atlas dteam lhcb ops na62.vo.gridpp.ac.uk and ipv6.hepix.org
# cetest01: atlas cms dteam lhcb ops
#
# number of prd accounts per CE:
# ceprod: 18, cetest: 5

# number of pilot accounts per CE:
# ceprod: 10, except CMS = 30, cetest: 5, except CMS = 25
# all special roles have been dropped

# YAML: I go for a two space indent. And one space left and right from the ':'

VOS_WITH_PILOT_ROLES = ['atlas', 'cms', 'comet.j-parc.jp', 'dune', 'ilc',
                        'lhcb', 'mice', 'hyperk.org', 'ops', 'pheno',
                        't2k.org', 'gridpp', 'na62.vo.gridpp.ac.uk', 'lz',
                        'lsst', 'snoplus.snolab.ca', 'solidexperiment.org']

VOS_WITH_PROD_ROLES = ['atlas', 'cms', 'comet.j-parc.jp', 'dune', 'ilc',
                       'lhcb', 'mice', 'hyperk.org', 'pheno', 't2k.org',
                       'gridpp', 'na62.vo.gridpp.ac.uk', 'lz',
                       'lsst', 'snoplus.snolab.ca', 'solidexperiment.org']


def get_user_name(basename, i):
    """what is says on the tin"""

    user_name = ''
    if i < 10:
        user_name = basename+'00'+str(i)
    elif i < 100:
        user_name = basename+'0'+str(i)
    else:
        user_name = basename+str(i)

    return user_name


def write_vomsserver_yaml(voname, pfile):
    """writes the vomsserver section for a given VO"""

    # for the VOs we support the port is the same across all voms servers
    port = get_port(voname)
    pfile.write('    {} {} {}\n'.format('servers', ':', '['))
    list_of_servers = get_voms_servers(voname)
    for voserver in list_of_servers:
        pfile.write('      {}\n'.format('{'))
        pfile.write('        {} {} {}{}\n'.format('server', ':',
                                                  voserver.server, ','))
        pfile.write('        {} {} {}{}\n'.format('port', ':', port, ','))
        pfile.write('        {} {} {}{}\n'.format('dn', ':', voserver.dn, ','))
        pfile.write('        {} {} {}{}\n'.format('ca_dn', ':',
                                                  voserver.ca, ','))
        pfile.write('      {}\n'.format('},'))
    pfile.write('    {}{}\n'.format(']', ','))

def write_groups_yaml(voname, pfile):
    """write the groups section for a given VO:
    groups: user, sgm for all; pilot, prd for most"""

    # to get the gid, use the 001 user that always exists
    base_name = get_base_name(voname)
    user = base_name + "001"
    user_gid = pwd.getpwnam(user).pw_gid
    sgm = base_name + "sgm"
    sgm_gid = pwd.getpwnam(sgm).pw_gid
    if voname in VOS_WITH_PILOT_ROLES:
        pilot = base_name + "plt001"
        pilot_gid = pwd.getpwnam(pilot).pw_gid
    if voname in VOS_WITH_PROD_ROLES:
        prod = base_name + "prd001"
        prod_gid = pwd.getpwnam(prod).pw_gid

    pfile.write('    {} {} {}\n'.format('groups', ':', '{'))
    pfile.write('      {} {}{}{}{}{}\n'.format(base_name,
                                               ': { fqan : ["/',
                                               voname, '"], gid : ', user_gid,
                                               ' },'))
    pfile.write('      {} {}{}{}{}{}\n'.format(base_name+"sgm",
                                               ': { fqan : ["/',
                                               voname,
                                               '/Role=lcgadmin"], gid : ',
                                               sgm_gid, ' },'))
    if voname in VOS_WITH_PILOT_ROLES:
        pfile.write('      {} {}{}{}{}{}\n'.format(base_name+"plt",
                                                   ': { fqan : ["/',
                                                   voname,
                                                   '/Role=pilot"], gid : ',
                                                   pilot_gid, ' },'))
    if voname in VOS_WITH_PROD_ROLES:
        pfile.write('      {} {}{}{}{}{}\n'.format(base_name+"prd",
                                                   ': { fqan : ["/', voname,
                                                   '/Role=production"], gid : ',
                                                   prod_gid, ' },'))
    pfile.write('    },\n')



def write_yaml_snippet(vo_name, cream_ce, pfile):
    """writes the different sections for each VO"""

    first_acc_ce = first_account(cream_ce)
    n_of_users = number_of_user_accounts(vo_name, cream_ce)
    n_of_pilots = number_of_pilot_accounts(vo_name, cream_ce)
    n_of_prds = number_of_prod_accounts(vo_name, cream_ce)

    # get the VO data
    sw_dir = get_sw_dir(vo_name)

    base_name = get_base_name(vo_name)


    # print sw_dir
    pfile.write('  {} {} {}\n'.format(vo_name, ':', '{'))
    pfile.write('    {} {} {}{}\n'.format('vo_app_dir', ':', sw_dir, ','))
    pfile.write('    {} {} {}{}\n'.format('vo_default_se',
                                          ':', 'gfe02.grid.hep.ph.ic.ac.uk',
                                          ','))
    # --- voms servers ---
    write_vomsserver_yaml(vo_name, pfile)

    # --- groups ---
    write_groups_yaml(vo_name, pfile)

    pfile.write('    {} {} {}\n'.format('users', ':', '{'))


    # --- plain users ---
    pfile.write('      {} {} {}\n'.format(base_name, ':', '{'))
    pfile.write('        {} {} {}\n'.format('users_table', ':', '{'))
    for i in range(first_acc_ce, first_acc_ce+n_of_users):
        user_name = get_user_name(base_name, i)
        user_uid = pwd.getpwnam(user_name).pw_uid
        pfile.write('          {} {} {}{}\n'.format(user_name, ':',
                                                    user_uid, ','))
    pfile.write('        },  # end of users_table\n')
    pfile.write('        {}{}{}'.format('fqan : ["/', vo_name, '"],\n'))
    pfile.write('      },  # end of plain users\n')


    # pilot users
    if vo_name in VOS_WITH_PILOT_ROLES:
        pfile.write('      {} {} {}\n'.format(base_name+"plt", ':', '{'))
        pfile.write('        {} {} {}\n'.format('users_table', ':', '{'))
        for i in range(first_acc_ce, first_acc_ce+n_of_pilots):
            plt_base_name = base_name + "plt"
            user_name = get_user_name(plt_base_name, i)
            user_uid = pwd.getpwnam(user_name).pw_uid
            pfile.write('          {} {} {}{}\n'.format(user_name, ':',
                                                        user_uid, ','))
        pfile.write('        },  # end of users_table\n')
        pfile.write('        {}{}{}'.format('fqan : ["/', vo_name,
                                            '/Role=pilot"],\n'))
        pfile.write('      },  # end of pilot users\n')
    # production users
    if vo_name in VOS_WITH_PROD_ROLES:
        pfile.write('      {} {} {}\n'.format(base_name+"prd", ':', '{'))
        pfile.write('        {} {} {}\n'.format('users_table', ':', '{'))
        for i in range(first_acc_ce, first_acc_ce+n_of_prds):
            prd_base_name = base_name + "prd"
            user_name = get_user_name(prd_base_name, i)
            user_uid = pwd.getpwnam(user_name).pw_uid
            pfile.write('          {} {} {}{}\n'.format(user_name, ':',
                                                        user_uid, ','))
        pfile.write('        },  # end of users_table\n')
        pfile.write('        {}{}{}\n'.format('fqan : ["/', vo_name,
                                              '/Role=production"],'))
        pfile.write('      },   # end of production users\n')

    # sgm users (no pool accounts)
    user_name = base_name+"sgm"
    pfile.write('      {} {} {}\n'.format(user_name, ':', '{'))
    pfile.write('        {} {} {}{}\n'.format('first_uid', ':',
                                              pwd.getpwnam(user_name).pw_uid,
                                              ','))
    pfile.write('        {} {} {}\n'.format('pool_size', ':', '0,'))
    pfile.write('        {}{}{}\n'.format('primary_fqan : ["/', vo_name,
                                          '/Role=lcgadmin"],'))
    pfile.write('        {} {} {}\n'.format('pub_admin', ':', 'true,'))
    pfile.write('      },   # end of sgm user\n')

    pfile.write('    },  # end of users\n')
    # --- closes a VO ---
    pfile.write('  }\n')


def first_account(ce_name):
    """ returns the first account
    to be found on a given CE"""

    first_acc = 0
    if ce_name == "cetest00":
        first_acc = 0
    elif ce_name == "cetest01":
        first_acc = 50
    elif ce_name == 'ceprod05':
        first_acc = 700
    elif ce_name == 'ceprod06':
        first_acc = 1000
    elif ce_name == 'ceprod07':
        first_acc = 400
    elif ce_name == 'ceprod08':
        first_acc = 100
    else:
        print 'unrecognized ce: valid options are ceprod05-08 and cetest00'
        sys.exit(1)

    return first_acc


def number_of_user_accounts(voname, cename):
    """returns the number of plain users accounts for a given CE"""
    number_of_users = 100
    if voname == 'cms':
        number_of_users = 300
    # cetest00 is special
    if cename == 'cetest00':
        number_of_users = 50
        if voname == 'na62.vo.gridpp.ac.uk':
            number_of_users = 10
        if voname == 'ipv6.hepix.org':
            number_of_users = 2

    return  number_of_users


def number_of_prod_accounts(voname, cename):
    """what it says on the tin"""
    number_of_prod_acc = 0
    if voname not in VOS_WITH_PROD_ROLES:
        return number_of_prod_acc
    number_of_prod_acc = 18
    if voname == 'cms':
        number_of_prod_acc = 50

    if cename == "cetest00":
        number_of_prod_acc = 5

    return number_of_prod_acc


def number_of_pilot_accounts(voname, cename):
    """returns number of pilot accounts for a given vo and ce"""

    number_of_pilot_acc = 0
    if voname not in VOS_WITH_PILOT_ROLES:
        return number_of_pilot_acc
    number_of_pilot_acc = 10
    if voname == 'cms':
        number_of_pilot_acc = 30
    if cename == 'cetest00':
        number_of_pilot_acc = 5
        if voname == 'cms':
            number_of_pilot_acc = 25

    return number_of_pilot_acc


# read in list of VOs from file
def get_vo_list():
    """reads in config file containing list of VOs
    the config should be generrated for"""

    vofile = open("vos.txt", 'rU')
    vostr = vofile.read()
    volist = []
    for a_vo in vostr.split('\n'):
        # protect against empty lines
        if len(a_vo) > 0:
            volist.append(a_vo.strip()) # remove whitespace
    return volist



#####################################################################

def main():
    """ do stuff """
    if len(sys.argv) != 2:
        print 'Usage is ./make_co_puppet.py [cename]'
        sys.exit(1)
    cename = sys.argv[1]
    # read in list of VOs
    volist = get_vo_list()
    pfile = open("config.vos.yaml", 'w')
    # next line just for debugging
    pfile.write('---\n')
    pfile.write('creamce::vo_table :\n')

    for voname in volist:
        print voname
        write_yaml_snippet(voname, cename, pfile)
    print "Done"

    pfile.close()

if __name__ == '__main__':
    main()
