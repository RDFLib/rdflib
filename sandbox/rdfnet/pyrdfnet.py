##$Id: pyrdfnet.py,v 1.1 2003/10/21 21:19:36 kendall Exp $

"""This module provides a very Pythonick interface for the RDF NET Api,
which is a web services (REST and SOAP) way of interacting with a local or
remote RDF triple store. """

import urllib2
from rdflib import URIRef, Literal

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

class PyRdfNet(object): pass

def newTripleStore(uri): pass

def query(uri, query, context=None): pass

def put(uri, query, context=None): pass

def options(uri): pass

def insert(uri, graph, context=None): pass

def remove(uri, graph, context=None): pass

def update(uri, new, context=None): pass
