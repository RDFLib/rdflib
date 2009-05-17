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

.. _ReadOnlyGraphAggregate:
.. autoclass:: rdflib.graph.ReadOnlyGraphAggregate

.. _Variable:
.. automodule:: rdflib.term
.. autoclass:: rdflib.term.Variable


.. __: univrdfstore.html#Terms
.. _Identifier: http://www.w3.org/2002/07/rdf-identifer-terminology/