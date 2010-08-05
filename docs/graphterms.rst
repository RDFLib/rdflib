.. _graphterms:

===============
RDF Graph Terms
===============

The RDFLib classes listed below model RDF `terms`__ in a graph and inherit from a common `Identifier`_ class, which extends Python unicode.  Instances of these are nodes in an RDF graph.

.. _Seq:
.. autoclass:: rdflib.graph.Seq
    :members:

.. _QuotedGraph:
.. autoclass:: rdflib.graph.QuotedGraph
    :noindex:

.. _ReadOnlyGraphAggregate:
.. autoclass:: rdflib.graph.ReadOnlyGraphAggregate
    :noindex:

.. _Variable:
.. automodule:: rdflib.term
    :members:
    :noindex:


.. __: univrdfstore.html#Terms
.. _Identifier: http://www.w3.org/2002/07/rdf-identifer-terminology/