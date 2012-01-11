.. _nodes:

=======
Nodes
=======

Nodes are a subset of the Terms that the underlying store actually persists.
The set of such Terms depends on whether or not the store is formula-aware. 
Stores that aren't formula-aware would only persist those terms core to the 
RDF Model, and those that are formula-aware would be able to persist the N3 
extensions as well. However, utility terms that only serve the purpose for 
matching nodes by term-patterns probably will only be terms and not nodes.

The set of nodes of an RDF graph is the set of subjects and objects of triples in the graph.

The RDFLib classes listed below model RDF `terms`__ in a graph and inherit from a common `Identifier`_ class, which extends Python unicode.  Instances of these are nodes in an RDF graph.

.. automodule:: rdflib.term

.. autoclass:: rdflib.term.Node
    :members:

.. autoclass:: rdflib.term.Identifier
    :members:

.. autoclass:: rdflib.term.BNode
    :members:

.. autoclass:: rdflib.term.URIRef
    :members:

.. autoclass:: rdflib.term.Literal
    :members:

.. autoclass:: rdflib.term.Variable
    :members:


.. __: univrdfstore.html#Terms
.. _Identifier: http://www.w3.org/2002/07/rdf-identifer-terminology/
