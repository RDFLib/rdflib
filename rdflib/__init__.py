"""\
A pure Python package providing the core RDF constructs.

The packages is intended to provide the core RDF types and interfaces
for working with RDF. The package defines a plugin interface for
parsers, stores, and serializers that other packages can use to
implement parsers, stores, and serializers that will plug into the
rdflib package.

The primary interface `rdflib` exposes to work with RDF is
`rdflib.graph.Graph`.

A tiny example:

    >>> import rdflib

    >>> g = rdflib.Graph()
    >>> result = g.parse("http://www.w3.org/2000/10/swap/test/meet/white.rdf")

    >>> print("graph has %s statements." % len(g))
    graph has 19 statements.
    >>>
    >>> for s, p, o in g:
    ...     if (s, p, o) not in g:
    ...         raise Exception("It better be!")

    >>> s = g.serialize(format='n3')

"""
__docformat__ = "restructuredtext en"

# The format of the __version__ line is matched by a regex in setup.py
__version__ = "3.3.0-dev"
__date__ = "2012/01/19"

__all__ = [
    'URIRef',
    'BNode',
    'Literal',
    'Variable',

    'Namespace',

    'Graph',
    'ConjunctiveGraph',

    'RDF',
    'RDFS',
    'OWL',
    'XSD',
    
    'util',
    ]

import sys
# generator expressions require 2.4
assert sys.version_info >= (2, 4, 0), "rdflib requires Python 2.4 or higher"
del sys

import logging
_LOGGER = logging.getLogger("rdflib")
_LOGGER.info("version: %s" % __version__)


from rdflib.term import URIRef, BNode, Literal, Variable

from rdflib.namespace import Namespace

from rdflib.graph import Graph, ConjunctiveGraph

from rdflib.namespace import RDF, RDFS, OWL, XSD

from rdflib import plugin
from rdflib import query

from rdflib import util

