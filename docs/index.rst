.. rdflib documentation documentation master file
   
================
rdflib |release|
================

Introduction
============

RDFLib is a pure Python package work working with `RDF <http://www.w3.org/RDF/>`_. ``RDFLib`` contains most things you need to work with RDF, including: 

* parsers and serializers for RDF/XML, N3, NTriples, N-Quads, Turtle, TriX, RDFa and Microdata.

* a Graph interface which can be backed by any one of a number of Store implementations. 

* store implementations for in memory storage and persistent storage on top of the Berkeley DB. 

* a SPARQL 1.1 implementation - supporting SPARQL 1.1 Queries and Update statements. 

Getting started
---------------

If you never used ``RDFLib``, click through these

.. toctree::
   :maxdepth: 1

   gettingstarted
   intro_to_parsing
   intro_to_creating_rdf
   intro_to_graphs
   intro_to_sparql

In depth
--------

.. toctree::
   :maxdepth: 1

   rdf_terms
   namespaces_and_bindings
   persistence

   upgrade3to4

   howto
   assorted_examples

Reference
---------

Plugins
^^^^^^^

Many parts of ``RDFLib`` are extensible with plugins through `setuptools entry-points <http://pythonhosted.org/distribute/setuptools.html#dynamic-discovery-of-services-and-plugins>`_. These pages list the plugins included in ``RDFLib`` core.  

.. toctree::
   :maxdepth: 1

   plugin_parsers
   plugin_serializers
   plugin_stores
   plugin_query_results   

API docs
^^^^^^^^

.. toctree::
   :maxdepth: 1

   Full API docs <apidocs/modules>

* :ref:`genindex`
* :ref:`modindex`


Plugins
=======

The package defines a plugin interface for parsers, stores, and serializers that other packages can use to implement parsers, stores, and serializers that will plug into the ``RDFLib`` package.

The diagram below describes the current set of plugins that are either built in to rdflib or are available in extension projects:

.. image:: /_static/plugins-diagram.svg
   :alt: rdflib plugin "architecture"
   :width: 90%


For developers
==============

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
    
    
