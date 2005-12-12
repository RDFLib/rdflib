# RDF Library

__version__ = "2.3.0"
__date__ = "2005/12/08"

import sys
# TODO: what version of python does rdflib require??
#if sys.version_info <= (2,3,0):
#    print "This version of rdflib has not yet been tested on version prior to Python 2.3"

# generator expressions require 2.4
assert sys.version_info >= (2,4,0), "rdflib requires Python 2.4 or higher"
del sys

import logging
_logger = logging.getLogger("rdflib")
_logger.setLevel(logging.DEBUG)
_hdlr = logging.StreamHandler()
_hdlr.setFormatter(logging.Formatter('%(name)s %(levelname)s: %(message)s'))
_logger.addHandler(_hdlr)

from rdflib.URIRef import URIRef
from rdflib.BNode import BNode
from rdflib.Literal import Literal
from rdflib.Variable import Variable

from rdflib.Namespace import Namespace

#from rdflib.Graph import Graph # perhaps in 3.0, but for 2.x we don't
#want to break compatibility.
#from rdflib.Graph import ConjunctiveGraph as Graph
from rdflib.Graph import BackwardCompatGraph as Graph
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


