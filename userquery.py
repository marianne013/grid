#!/usr/bin/env python

# queries a voms server, returns a list of users
# to be run on a dirac server (after setting up dirac via 'source bashrc')
# needs valid certificate

import urllib2, httplib, socket, re
import suds
from suds.client import Client
from suds.transport.http import HttpTransport, Reply, TransportError

class HTTPSClientAuthHandler(urllib2.HTTPSHandler):
    def __init__(self, key, cert):
        urllib2.HTTPSHandler.__init__(self)
        self.key = key
        self.cert = cert

    def https_open(self, req):
        #Rather than pass in a reference to a connection class, we pass in
        # a reference to a function which, for all intents and purposes,
        # will behave as a constructor
        return self.do_open(self.getConnection, req)

    def getConnection(self, host, timeout=300):
        return httplib.HTTPSConnection(host,
                                       key_file=self.key,
                                       cert_file=self.cert)

class HTTPSClientCertTransport(HttpTransport):
    def __init__(self, key, cert, *args, **kwargs):
        HttpTransport.__init__(self, *args, **kwargs)
        self.key = key
        self.cert = cert

    def u2open(self, u2request):
        """
        Open a connection.
        @param u2request: A urllib2 request.
        @type u2request: urllib2.Requet.
        @return: The opened file-like urllib2 object.
        @rtype: fp
        """
        tm = self.options.timeout
        url = urllib2.build_opener(HTTPSClientAuthHandler(self.key, self.cert))
        if self.u2ver() < 2.6:
            socket.setdefaulttimeout(tm)
            return url.open(u2request)
        else:
            return url.open(u2request, timeout=tm)

# These lines enable debug logging; remove them once everything works.
#import logging
#logging.basicConfig(level=logging.INFO)
#logging.getLogger('suds.client').setLevel(logging.DEBUG)
#logging.getLogger('suds.transport').setLevel(logging.DEBUG)

c = Client('https://voms.gridpp.ac.uk:8443/voms/vo.londongrid.ac.uk/services/VOMSAdmin?wsdl',
    transport = HTTPSClientCertTransport('/opt/dirac/etc/grid-security/hostkey.pem',
                                         '/opt/dirac/etc/grid-security/hostcert.pem'))
c.set_options(headers={"X-VOMS-CSRF-GUARD":"1"})
users = c.service.listMembers()

for i, user in enumerate(users):
  # make a sensible users name
  # use email as unlike DN it won't contain any dodgy characters
  # add a number just in case we encounter multiple John Smiths
  usernmtmp = str(user["mail"]).split('@')
  username =  re.sub(r'\W+', '', usernmtmp[0])
  usernamefinal = username[0:8]+str(i)
  TEMPL = """
    %(uname)s
    {
      DN = %(DN)s
      CA = %(CA)s
      Email = %(mail)s
    }
"""
  user["num"] = i
  user["uname"] = usernamefinal
  print TEMPL % user

