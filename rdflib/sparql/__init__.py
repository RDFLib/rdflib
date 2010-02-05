# -*- coding: utf-8 -*-
#
#
# $Date: 2005/11/04 14:06:36 $, by $Author: ivan $, $Revision: 1.1 $
# The documentation of the module, hence the convention for the documentation of methods and classes,
# is based on the epydoc tool.  This tool parses Python source files
# and generates API descriptions XHTML.
# The latest release of epydoc (version 2.0) can be
# downloaded from the <a href="http://sourceforge.net/project/showfiles.php?group_id=32455">SourceForge
# download page</a>.
#
#
"""
TODO: merge this first bit from sparql.sparql.py into rest of doc... 
updating all along the way.

SPARQL implementation on top of RDFLib

Implementation of the `W3C SPARQL <http://www.w3.org/TR/rdf-sparql-query/>`_ 
language (version April 2005). The basic class here is supposed to be a 
superclass of rdflib.sparql.graph; it has been separated only for 
a better maintainability.

There is a separate
`description <http://dev.w3.org/cvsweb/%7Echeckout%7E/2004/PythonLib-IH/Doc/sparqlDesc.html>`_
for the functionalities.


For a general description of the SPARQL API, see the separate, more complete
`description <http://dev.w3.org/cvsweb/%7Echeckout%7E/2004/PythonLib-IH/Doc/sparqlDesc.html>`_.

Variables, Imports
==================

The top level (__init__.py) module of the Package imports the
important classes. In other words, the user may choose to use the
following imports only::

    from rdflibUtils   import myTripleStore
    from rdflibUtils   import retrieveRDFFiles
    from rdflibUtils   import SPARQLError
    from rdflibUtils   import GraphPattern

The module imports and/or creates some frequently used Namespaces, and
these can then be imported by the user like::

    from rdflibUtils import ns_rdf

Finally, the package also has a set of convenience string defines for
XML Schema datatypes (ie, the URI-s of the datatypes); ie, one can
use::

    from rdflibUtils import type_string
    from rdflibUtils import type_integer
    from rdflibUtils import type_long
    from rdflibUtils import type_double
    from rdflibUtils import type_float
    from rdflibUtils import type_decimal
    from rdflibUtils import type_dateTime
    from rdflibUtils import type_date
    from rdflibUtils import type_time
    from rdflibUtils import type_duration

These are used, for example, in the sparql-p implementation.

The three most important classes in RDFLib for the average user are
Namespace, URIRef and Literal; these are also imported, so the user
can also use, eg::

    from rdflibUtils import Namespace, URIRef, Literal

History
=======

 - Version 1.0: based on an earlier version of the SPARQL, first released implementation

 - Version 2.0: version based on the March 2005 SPARQL document, 
   also a major change of the core code (introduction of the separate 
   ``GraphPattern`` :class:`rdflibUtils.graph.GraphPattern` class, etc).

 - Version 2.01: minor changes only: - switch to epydoc as a documentation tool, 
   it gives a much better overview of the classes - addition of the 
   SELECT * feature to sparql-p

 - Version 2.02: - added some methods to
   ``myTripleStore`` :class:`rdflibUtils.myTripleStore.myTripleStore` to handle
   ``Alt`` and ``Bag`` the same way as ``Seq`` - added also methods to
   :meth:`add` collections and containers to the triple store, not only
   retrieve them

 - Version 2.1: adapted to the inclusion of the code into rdflib, thanks to Michel Pelletier

 - Version 2.2: added the sorting possibilities; introduced the Unbound class and have a better
   interface to patterns using this (in the BasicGraphPattern class)

@author: `Ivan Herman <http://www.ivan-herman.net>`_

@license: This software is available for use under the
`W3C Software License <http://www.w3.org/Consortium/Legal/2002/copyright-software-20021231>`_

@contact: Ivan Herman, ivan@ivan-herman.net

@version: 2.2

"""
from rdflib.term import URIRef

DESCRIBE=URIRef('http://www.w3.org/TR/rdf-sparql-query/#describe')

__version__ = "2.2"

Debug = False

# Note that the SPARQL draft allows the usage of a different query character, but I decided not to be that
# generous, and keep to one only. I put it into a separate variable to avoid problems if the group decides
# to change the syntax on that detail...
_questChar  = "?"


def generateCollectionConstraint(triplets,collection,item) :
    """

    Generate a function that can then be used as a global constaint in
    sparql to check whether the 'item' is an element of the
    'collection' (a.k.a. list). Both collection and item can be a real
    resource or a query string. Furthermore, item might be a plain
    string, that is then turned into a literal run-time.

    The function returns an adapted filter method that can then be
    plugged into a sparql request.

    @param triplets: the
    L{SPARQLGraph<graph.SPARQLGraph>} instance

    @param collection: is either a query string (that has to be bound
    by the query) or an RDFLib Resource representing the collection

    @param item: is either a query string (that has to be bound by the
    query) or an RDFLib Resource that must be tested to be part of the
    collection

    @rtype: a function suitable as a sparql filter

    @raises SPARQLError: if the collection or the
    item parameters are illegal (not valid resources for a collection
    or an object)
    """	
    return isOnCollection(collection,item, triples)

############################################################################################

class Processor(object):

    def __init__(self, graph):
        pass

    def query(self, strOrQuery, initBindings={}, initNs={}, DEBUG=False):
        pass

from rdflib.exceptions  import Error

##
# SPARQL Error Exception (subclass of the RDFLib Exceptions)
class SPARQLError(Error) :
    """Am SPARQL error has been detected"""
    def __init__(self,msg):
        Error.__init__(self, ("SPARQL Error: %s." % msg))
