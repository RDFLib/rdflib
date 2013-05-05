.. rdflib documentation documentation master file
   
==========
rdflib |release|
==========

Introduction
============

RDFLib is a pure Python package work working with `RDF <http://www.w3.org/RDF/>`_. ``rdflib`` contains most things you need to work with RDF, including: 

* parsers and serializers for RDF/XML, N3, NTriples, N-Quads, Turtle, TriX, RDFa and Microdata.

* a Graph interface which can be backed by any one of a number of Store implementations. 

* store implementations for in memory storage and persistent storage on top of the Berkeley DB. 

* a SPARQL 1.1 implementation - supporting SPARQL 1.1 Queries and Update statements. 


.. toctree::
   :maxdepth: 1

   gettingstarted
   intro_to_graphs
   using_graphs
   rdf_terms
   namespaces_and_bindings
   intro_to_sparql

   persistence

   howto
   upgrade3to4
   assorted_examples

   plugin_parsers
   plugin_serializers

   
   Module documentation <modules/index>

Plugins
=======

The package defines a plugin interface for parsers, stores, and serializers that other packages can use to implement parsers, stores, and serializers that will plug into the ``rdflib`` package.

The diagram below describes the current set of plugins that are either built in to rdflib or are available in extension projects:

.. image:: /_static/plugins-diagram.svg
   :alt: rdflib plugin "architecture"
   :width: 90%


API Documentation
=================

    rdflib has epydoc-generated `API Documentation`__

.. __: ./_static/api/index.html


Additional discussions / notes
==============================

.. toctree::
   :maxdepth: 2

   univrdfstore
   persisting_n3_terms
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
    
    
