"""A pure Python package providing the core RDF constructs.

The packages is intended to provide the core RDF types and interfaces
for working with RDF. The package defines a plugin interface for
parsers, stores, and serializers that other packages can use to
implement parsers, stores, and serializers that will plug into the
rdflib package.

The primary interface `rdflib` exposes to work with RDF is
`rdflib.graph.Graph`.

A tiny example:

    >>> from rdflib import Graph, URIRef, Literal

    >>> g = Graph().parse("http://www.w3.org/2000/10/swap/test/meet/blue.rdf")

    >>> print("graph has %s statements." % len(g))
    graph has 9 statements.
    >>>
    >>> for s, p, o in g:
    ...     if (s, p, o) not in g:
    ...         raise Exception("It better be!")

    >>> tl = [
    ...       (BNode('B1'), URIRef('http://www.example.org/meeting_organization#homePage'), BNode('B4')),
    ...       (BNode('B1'), URIRef('http://www.w3.org/2000/10/swap/test/meet/about'), Literal('http://meetings.example.com/cal#m1')),
    ...       (BNode('B2'), URIRef('http://www.example.org/meeting_organization#attending'), BNode('B3')),
    ...       (BNode('B2'), URIRef('http://www.example.org/personal_details#GivenName'), Literal('Fred')),
    ...       (BNode('B2'), URIRef('http://www.example.org/personal_details#hasEmail'), BNode('B5')),
    ...       (BNode('B2'), URIRef('http://www.w3.org/2000/10/swap/test/meet/about'), Literal('http://www.example.org/people#fred')),
    ...       (BNode('B3'), URIRef('http://www.w3.org/2000/10/swap/test/meet/resource'), Literal('http://meetings.example.com/cal#m1')),
    ...       (BNode('B4'), URIRef('http://www.w3.org/2000/10/swap/test/meet/resource'), Literal('http://meetings.example.com/m1/hp')),
    ...       (BNode('B5'), URIRef('http://www.w3.org/2000/10/swap/test/meet/resource'), Literal('mailto:fred@example.com'))
    ...       ]
    >>> g2 = Graph()
    >>> g2.namespace_manager = g.namespace_manager
    >>> for t in tl:
    ...     g2.add(t)
    >>> print(g.serialize(format="turtle").decode())
    @prefix m: <http://www.example.org/meeting_organization#> .
    @prefix ns1: <http://www.w3.org/2000/10/swap/test/meet/> .
    @prefix p: <http://www.example.org/personal_details#> .
    <BLANKLINE>
    [] m:attending [ ns1:resource "http://meetings.example.com/cal#m1" ] ;
        p:GivenName "Fred" ;
        p:hasEmail [ ns1:resource "mailto:fred@example.com" ] ;
        ns1:about "http://www.example.org/people#fred" .
    <BLANKLINE>
    [] m:homePage [ ns1:resource "http://meetings.example.com/m1/hp" ] ;
        ns1:about "http://meetings.example.com/cal#m1" .
    <BLANKLINE>
    <BLANKLINE>
    >>> print(g.isomorphic(g2))
    True

"""
__docformat__ = "restructuredtext en"

# The format of the __version__ line is matched by a regex in setup.py
__version__ = "5.0.0"
__date__ = "2020-04-18"

__all__ = [
    "URIRef",
    "BNode",
    "Literal",
    "Namespace",
    "Variable",
    "Dataset",
    "Graph",
    "ConjunctiveGraph",
    "CSVW",
    "DC",
    "DCAT",
    "DCTERMS",
    "DOAP",
    "FOAF",
    "ODRL2",
    "ORG",
    "OWL",
    "PROF",
    "PROV",
    "QB",
    "RDF",
    "RDFS",
    "SDO",
    "SH",
    "SKOS",
    "SOSA",
    "SSN",
    "TIME",
    "VOID",
    "XMLNS",
    "XSD",
    "util",
]

import sys
import logging

logger = logging.getLogger(__name__)
_interactive_mode = False
try:
    import __main__

    if not hasattr(__main__, "__file__") and sys.stdout is not None and sys.stderr.isatty():
        # show log messages in interactive mode
        _interactive_mode = True
        logger.setLevel(logging.INFO)
        logger.addHandler(logging.StreamHandler())
    del __main__
except ImportError:
    # Main already imported from elsewhere
    import warnings

    warnings.warn("__main__ already imported", ImportWarning)
    del warnings

if _interactive_mode:
    logger.info("RDFLib Version: %s" % __version__)
else:
    logger.debug("RDFLib Version: %s" % __version__)
del _interactive_mode
del sys


NORMALIZE_LITERALS = True
"""
If True - Literals lexical forms are normalized when created.
I.e. the lexical forms is parsed according to data-type, then the
stored lexical form is the re-serialized value that was parsed.

Illegal values for a datatype are simply kept.  The normalized keyword
for Literal.__new__ can override this.

For example:

>>> from rdflib import Literal,XSD
>>> Literal("01", datatype=XSD.int)
rdflib.term.Literal(u'1', datatype=rdflib.term.URIRef(u'http://www.w3.org/2001/XMLSchema#integer'))

This flag may be changed at any time, but will only affect literals
created after that time, previously created literals will remain
(un)normalized.

"""


DAWG_LITERAL_COLLATION = False
"""
DAWG_LITERAL_COLLATION determines how literals are ordered or compared
to each other.

In SPARQL, applying the >,<,>=,<= operators to literals of
incompatible data-types is an error, i.e:

Literal(2)>Literal('cake') is neither true nor false, but an error.

This is a problem in PY3, where lists of Literals of incompatible
types can no longer be sorted.

Setting this flag to True gives you strict DAWG/SPARQL compliance,
setting it to False will order Literals with incompatible datatypes by
datatype URI

In particular, this determines how the rich comparison operators for
Literal work, eq, __neq__, __lt__, etc.
"""

from rdflib.term import URIRef, BNode, Literal, Variable

from rdflib.graph import Dataset, Graph, ConjunctiveGraph

from rdflib import plugin
from rdflib import query

from rdflib.namespace import (
    CSVW,
    DC,
    DCAT,
    DCTERMS,
    DOAP,
    FOAF,
    ODRL2,
    ORG,
    OWL,
    PROF,
    PROV,
    QB,
    RDF,
    RDFS,
    SDO,
    SH,
    SKOS,
    SOSA,
    SSN,
    TIME,
    VOID,
    XMLNS,
    XSD,
    Namespace
)

# tedious sop to flake8
assert plugin
assert query

from rdflib import util

from rdflib.container import *
