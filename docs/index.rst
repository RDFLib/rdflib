.. rdflib documentation documentation master file, created by sphinx-quickstart on Wed May 14 06:45:33 2008.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.
   
==========
rdflib 2.5
==========

Introduction
============
RDFLib is a Python library for working with RDF, a simple yet powerful language for representing information. The library contains an RDF/XML parser/serializer that conforms to the RDF/XML Syntax Specification (Revised) . The library also contains both in-memory and persistent Graph backends. It is being developed by a number of contributors and was created by Daniel Krech who continues to maintain it.

RDFLib's use of various Python idioms makes them an appropriate way to introduce it to a Python programmer who hasn't used it before.

RDFLib graphs redefine certain built-in Python methods in order to behave in a predictable way.  RDFLib graphs emulate container types and are best thought of as a set of 3-item triples

.. code-block:: text

    [
        (subject,  predicate,  object),
        (subject1, predicate1, object1),
        ... 
        (subjectN, predicateN, objectN)
     ]

RDFLib graphs are not sorted containers; they have ordinary set operations (e.g. :meth:`~rdflib.Graph.add` to add a triple) plus methods that search triples and return them in arbitrary order.

Contents
========
.. toctree::
   :maxdepth: 2

   gettingstarted
   univrdfstore
   graphterms
   namespace_utilities
   graph_utilities
   persistence
   persisting_n3_terms
   graph_merging
   graphs_bnodes
   assorted_examples
   addons
   Modules <modules/index>

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

