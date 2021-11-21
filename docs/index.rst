.. rdflib documentation documentation master file

================
rdflib |release|
================

RDFLib is a pure Python package for working with `RDF <http://www.w3.org/RDF/>`_. It contains:

* **Parsers & Serializers**

  * for RDF/XML, N3, NTriples, N-Quads, Turtle, TriX, JSON-LD, RDFa and Microdata


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
   persisting_n3_terms

Source Code
-----------
The rdflib source code is hosted on GitHub at `<https://github.com/RDFLib/rdflib>`__ where you can lodge Issues and
create Pull Requests to help improve this community project!

The RDFlib organisation on GitHub at `<https://github.com/RDFLib>`__ maintains this package and a number of other RDF
and RDFlib-related packaged that you might also find useful.


Further help & Contact
----------------------

If you would like more help with using rdflib, rather than developing it, please post a question on StackOverflow using
the tag ``[rdflib]``. A list of existing ``[rdflib]`` tagged questions is kept there at:

* `<https://stackoverflow.com/questions/tagged/rdflib>`__

You might also like to join rdflib's dev mailing list: `<https://groups.google.com/group/rdflib-dev>`__

The chat is available at `gitter <https://gitter.im/RDFLib/rdflib>`_ or via matrix `#RDFLib_rdflib:gitter.im <https://matrix.to/#/#RDFLib_rdflib:gitter.im>`_.



Glossary
--------

Here are a few RDF and Python terms referred to in this documentation. They are linked to wherever they occur.

.. glossary::

    functional property
        Properties than can only occur once for a resource, i.e. for any relation (triple, in RDF) ``x p y``,
        if ``p`` is functional, for any individual ``x``, there can be at most one individual ``y``.

    OWL
        The OWL 2 Web Ontology Language, informally OWL 2 or just OWL, is an ontology language for the Semantic Web
        with formally defined meaning. OWL 2 ontologies provide classes, properties, individuals, and data values and
        are stored as Semantic Web documents. OWL 2 ontologies can be used along with information written in RDF, and
        OWL 2 ontologies themselves are primarily exchanged as RDF documents. See the `RDF 1.1 Concepts and Abstract
        Syntax <https://www.w3.org/TR/rdf11-concepts/>`_ for more info.

    RDF
        The Resource Description Framework (RDF) is a framework for representing information in the Web. RDF data is
        stored in graphs that are sets of subject-predicate-object triples, where the elements may be IRIs, blank nodes,
        or datatyped literals. See the `OWL 2 Web Ontology Language
        Document Overview <http://www.w3.org/TR/owl-overview/>`_ for more info.
