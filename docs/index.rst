.. rdflib documentation documentation master file
   
==========
rdflib 3.0
==========

.. warning:: In preparation. This documentation for rdflib 3.0.0 has not yet been reviewed. Some of the code (esp. the "assorted examples") has not been updated to reflect the changes and refactoring introduced in rdflib 3.0.0.


Introduction
============

A pure Python package providing the core RDF constructs.

The ``rdflib`` package is intended to provide core RDF types and interfaces
for working with RDF. The package defines a plugin interface for
parsers, stores, and serializers that other packages can use to
implement parsers, stores, and serializers that will plug into the
``rdflib`` package.

The primary interface that ``rdflib`` exposes for working with RDF is
:class:`~rdflib.graph.Graph`.

A tiny example:

    >>> import rdflib

    >>> g = rdflib.Graph()
    >>> result = g.parse("http://eikeon.com/foaf.rdf")

    >>> print "graph has %s statements." % len(g)
    graph has 34 statements.
    >>>
    >>> for s, p, o in g:
    ...     if (s, p, o) not in g:
    ...         raise Exception("It better be!")

    >>> s = g.serialize(format='n3')

The package uses various Python idioms that makes them an appropriate way to introduce it to a Python programmer who hasn't used it before.

``rdflib`` graphs redefine certain built-in Python methods in order to behave in a predictable way; they emulate container types and are best thought of as a set of 3-item triples:

.. code-block:: text

    [
        (subject,  predicate,  object),
        (subject1, predicate1, object1),
        ... 
        (subjectN, predicateN, objectN)
     ]

``rdflib`` graphs are not sorted containers; they have ordinary set operations (e.g. :meth:`~rdflib.Graph.add` to add a triple) plus methods that search triples and return them in arbitrary order.

API Documentation
=================

    rdflib has epydoc-generated `API Documentation`__

.. __: ./apidocs/index.html

Contents
========
.. toctree::
   :maxdepth: 2

   gettingstarted
   univrdfstore
   graph_utilities
   graphterms
   graph_merging
   graphs_bnodes
   namespace_utilities
   store
   persistence
   persisting_n3_terms
   assorted_examples
   addons
   Modules <modules/index>
   Documentation notes <apidocs>

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. glossary::

    graph
        An RDF graph is a set of RDF triples. The set of nodes of an RDF graph
        is the set of subjects and objects of triples in the graph.
    
    named graph
        Named Graphs is the idea that having multiple RDF graphs in a single
        document/repository and naming them with URIs provides useful
        additional functionality. -- http://www.w3.org/2004/03/trix/
    
    
