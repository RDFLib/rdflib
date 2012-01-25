.. rdflib documentation documentation master file
   
============
rdflib 3.2.1
============

Introduction
============

A pure Python package providing the core RDF constructs. The ``rdflib`` package is intended to provide core RDF types and interfaces for working with RDF. 

.. toctree::
   :maxdepth: 1

   gettingstarted
   intro_to_graphs
   using_graphs
   rdf_terms
   plugin_parsers
   plugin_serializers
   namespaces_and_bindings
   persistence
   intro_to_sparql
   howto
   assorted_examples
   Module documentation <modules/index>

Plugins
=======

The package defines a plugin interface for parsers, stores, and serializers that other packages can use to implement parsers, stores, and serializers that will plug into the ``rdflib`` package.

The diagram below describes the current set of plugins that are either built in to rdflib or are available in the `rdfextras <http://pypi.python.org/pypi/rdfextras/>`_ support package:

.. image:: /_static/plugins-diagram.svg
   :alt: rdflib plugin "architecture"
   :width: 698
   :height: 450


API Documentation
=================

    rdflib has epydoc-generated `API Documentation`__

.. __: ./_static/api/index.html


Additional discussions / notes
==============================

.. toctree::
   :maxdepth: 2

   univrdfstore
   graphs_bnodes
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
    
    
