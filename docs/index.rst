.. rdflib documentation documentation master file
   
================
rdflib |release|
================

RDFLib is a pure Python package for working with `RDF <http://www.w3.org/RDF/>`_. It contains:

* **Parsers & Serializers**

  * for RDF/XML, N3, NTriples, N-Quads, Turtle, TriX, RDFa and Microdata
  * and JSON-LD, via a plugin module

* **Store implementations**

  * for in-memory and persistent RDF storage, including remote SPARQL endpoints

* **Graph interface**

  * to a single graph
  * or a conjunctive graph (multiple Named Graphs)
  * or a dataset of graphs

* **SPARQL 1.1 implementation**

  * both Queries and Updates are supported


Getting started
---------------
If you have never used RDFLib, the following will help get you started:

.. toctree::
   :maxdepth: 1

   gettingstarted
   intro_to_parsing
   intro_to_creating_rdf
   intro_to_graphs
   intro_to_sparql
   utilities
   Examples <apidocs/examples>


In depth
--------
If you are familiar with RDF and are looking for details on how RDFLib handles it, these are for you:

.. toctree::
   :maxdepth: 1

   rdf_terms
   namespaces_and_bindings
   persistence
   merging
   upgrade5to6
   upgrade4to5
   

Reference
---------
The nitty-gritty details of everything.

API reference:

.. toctree::
   :maxdepth: 1

   apidocs/modules

.. toctree:: 
   :maxdepth: 2
			  
   plugins

.. * :ref:`genindex`
.. * :ref:`modindex`


For developers
--------------
.. toctree::
   :maxdepth: 1

   developers
   docs
   univrdfstore
   persisting_n3_terms

Developers might also like to join rdflib's dev mailing list: `<https://groups.google.com/group/rdflib-dev>`__


Source Code
-----------
The rdflib source code is hosted on GitHub at `<https://github.com/RDFLib/rdflib>`__ where you can lodge Issues and
create Pull Requests to help improve this community project!

The RDFlib organisation on GitHub at `<https://github.com/RDFLib>`__ maintains this package and a number of other RDF
and RDFlib-related packaged that you might also find useful.


Further help
------------
For asynchronous chat support, try our gitter channel at `<https://gitter.im/RDFLib/rdflib>`__

If you would like more help with using rdflib, rather than developing it, please post a question on StackOverflow using
the tag ``[rdflib]``. A list of existing ``[rdflib]`` tagged questions is kept there at:

* `<https://stackoverflow.com/questions/tagged/rdflib>`__

