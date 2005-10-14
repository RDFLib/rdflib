# RDF Library

__version__ = "2.3.0"

import sys
# TODO: what version of python does rdflib require??
if sys.version_info <= (2,3,0):
    print "This version of rdflib has not yet been testing on version prior to Python 2.3"
assert sys.version_info >= (2,2,1), "rdflib requires Python 2.2.1 or higher"
del sys

import logging

try:
    logging.basicConfig(level=logging.DEBUG, format='rdflib-%(levelname)s: %(message)s')
except:
    # For Python 2.3 compatibility
    logging.basicConfig()


from rdflib.URIRef import URIRef
from rdflib.BNode import BNode
from rdflib.Literal import Literal

from rdflib.Namespace import Namespace

from rdflib.Graph import Graph
from rdflib.Graph import ConjunctiveGraph

from rdflib import RDF
from rdflib import RDFS

from rdflib.FileInputSource import FileInputSource
from rdflib.URLInputSource import URLInputSource
from rdflib.StringInputSource import StringInputSource

# if zope.interface is not installed, these calls do nothing

from rdflib.interfaces import IIdentifier, classImplements
classImplements(URIRef, IIdentifier)
classImplements(BNode, IIdentifier)
classImplements(Literal, IIdentifier)


