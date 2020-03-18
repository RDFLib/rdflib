.. rdflib documentation documentation master file
   
================
rdflib |release|
================

RDFLib is a pure Python package for working with `RDF <http://www.w3.org/RDF/>`_. RDFLib contains useful APIs for working with RDF, including: 

* parsers and serializers for RDF/XML, N3, NTriples, N-Quads, Turtle, TriX, RDFa and Microdata.

* a Graph interface which can be backed by a number of store implementations. 

* store implementations for in memory storage and persistent storage on top of the Berkeley DB. 

* a SPARQL 1.1 implementation - supporting SPARQL 1.1 Queries and Update statements. 

Getting started
---------------

If you have never used RDFLib, the following will help get you started

.. toctree::
   :maxdepth: 1

   gettingstarted
   intro_to_parsing
   intro_to_creating_rdf
   intro_to_graphs
   intro_to_sparql

   utilities

   RDFLib examples <apidocs/examples>

In depth
--------

If you are familiar with RDF and are looking for details on how RDFLib handles RDF, these are for you. 

.. toctree::
   :maxdepth: 1

   rdf_terms
   namespaces_and_bindings
   persistence
   merging

   upgrade3to4
   upgrade2to3

   faq
   

Reference
---------

The nitty-gritty details of everything.

.. toctree:: 
   :maxdepth: 2
			  
   plugins

.. toctree::
   :maxdepth: 1

   apidocs/modules

* :ref:`genindex`
* :ref:`modindex`




For developers
--------------

.. toctree::
   :maxdepth: 1

   developers
   docs
   univrdfstore
   persisting_n3_terms




Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. glossary::

   functional properties 
      
        A functional property is a property that can
        have only one (unique) value y for each instance x, i.e. there
        cannot be two distinct values y1 and y2 such that the pairs
        (x,y1) and (x,y2) are both instances of this 
		property. -- http://www.w3.org/TR/owl-ref/#FunctionalProperty-def

   graph
        An RDF graph is a set of RDF triples. The set of nodes of an RDF graph
        is the set of subjects and objects of triples in the graph.
    
   named graph
        Named Graphs allow multiple RDF graphs to exist within a single
        document/repository. They can be referred to with URIs. Named graphs allow queries across multiple domains.
	-- http://www.w3.org/2004/03/trix/

   transitivity 
        A property is transitive: 
            
            if whenever an element ``a`` is related to an element
            ``b``, and ``b`` is in turn related to an element ``c``,
            then ``a`` is also related to ``c``.  --
            http://en.wikipedia.org/wiki/Transitive_relation
		
        Standard examples include ``rdfs:subClassOf`` or greater-than
   
