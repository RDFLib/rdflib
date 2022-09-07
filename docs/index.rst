.. rdflib documentation documentation main file

================
rdflib |release|
================

RDFLib is a pure Python package for working with `RDF <http://www.w3.org/RDF/>`_. It contains:

* **Parsers & Serializers**

  * for RDF/XML, N3, NTriples, N-Quads, Turtle, TriX, JSON-LD, HexTuples, RDFa and Microdata


* **Store implementations**

  * memory stores
  * persistent, on-disk stores, using databases such as BerkeleyDB
  * remote SPARQL endpoints

* **Graph interface**

  * to a single graph
  * or to multiple Named Graphs within a dataset

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

Provisional functionality is available in the :py:mod:`rdflib._provisional` module.

.. toctree::
   :maxdepth: 1

   apidocs/rdflib._provisional

Provisional functionality is not part of the public API and is not subject to
semantic versioning guarantees. The functionality may be removed or changed at
any time, however we will try to avoid doing so as much as possible.

Once provisional functionality is ready to be integrated into the public RDFLib
API it will be moved to the :py:mod:`rdflib` package and aliased into the
:py:mod:`rdflib._provisional` module for backwards compatibility of anything
that may have been using it.

Provisional functionality is provided to allow early access to new and
experimental features while the APIs are being finalized.

For developers
--------------
.. toctree::
   :maxdepth: 1

   developers
   CODE_OF_CONDUCT
   docs
   persisting_n3_terms
   type_hints
   CONTRIBUTING
   decisions/index

Source Code
-----------
The rdflib source code is hosted on GitHub at `<https://github.com/RDFLib/rdflib>`__ where you can lodge Issues and
create Pull Requests to help improve this community project!

The RDFlib organisation on GitHub at `<https://github.com/RDFLib>`__ maintains this package and a number of other RDF
and RDFlib-related packaged that you might also find useful.


.. _further_help_and_contact:

Further help & Contact
----------------------

If you would like help with using RDFlib, rather than developing it, please post
a question on StackOverflow using the tag ``[rdflib]``. A list of existing
``[rdflib]`` tagged questions can be found 
`here <https://stackoverflow.com/questions/tagged/rdflib>`_.

You might also like to join RDFlib's `dev mailing list
<https://groups.google.com/group/rdflib-dev>`_ or use RDFLib's `GitHub
discussions section <https://github.com/RDFLib/rdflib/discussions>`_.

The chat is available at `gitter <https://gitter.im/RDFLib/rdflib>`_ or via
matrix `#RDFLib_rdflib:gitter.im
<https://matrix.to/#/#RDFLib_rdflib:gitter.im>`_.
