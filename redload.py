from rdflib.Loader import Loader
from rdflib import __version__

import sys, getopt
    
def usage(msg):
    print msg, """

USAGE: redload.py <rdf uri>

    options:
           [-h,--help]

"""    
        
print """
redload version: %s
-------------------
""" % __version__    

try:
    optlist, args = getopt.getopt(sys.argv[1:], 'h:', ["help"])
except getopt.GetoptError, msg:
    usage(msg)
    sys.exit(-1)
if len(sys.argv)!=2:
    usage("Wrong number of arguments")
    sys.exit(-1)
try:
    uri = sys.argv[1]
    rl = Loader()
    rl.load(uri)
    rl.boot()

except Exception, e:
    print "Unexpected Error: ", e
    print "----------------"
    raise
