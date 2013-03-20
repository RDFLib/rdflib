.. _graphs:

=======
Graphs
=======

RDFLib defines the following kinds of Graphs:

* Graph(**store**, **identifier**)
* QuotedGraph(**store**, **identifier**)
* ConjunctiveGraph(**store**, **default_identifier** = None)
* Dataset(**store**, **default_identifier** = None)

Graph
-----
An RDF graph is a set of RDF triples.

The set of nodes of an RDF graph is the set of subjects and objects of triples in the graph.

.. toctree::
    :maxdepth: 2

    graph


Conjunctive Graph
-----------------

A Conjunctive Graph is the most relevant collection of graphs that are considered to be the boundary for closed world assumptions.  This boundary is equivalent to that of the store instance (which is itself uniquely identified and distinct from other instances of :class:`Store` that signify other Conjunctive Graphs).  It is equivalent to all the named graphs within it and associated with a ``_default_`` graph which is automatically assigned a :class:`BNode` for an identifier - if one isn't given.  

.. toctree::
    :maxdepth: 1

    conjunctive_graph


Quoted graph
------------

The notion of an RDF graph [14] is extended to include the concept of a formula node. A formula node may occur wherever any other kind of node can appear. Associated with a formula node is an RDF graph that is completely disjoint from all other graphs; i.e. has no nodes in common with any other graph. (It may contain the same labels as other RDF graphs; because this is, by definition, a separate graph, considerations of tidiness do not apply between the graph at a formula node and any other graph.)

This is intended to map the idea of "{ N3-expression }" that is used by N3 into an RDF graph upon which RDF semantics is defined.

.. toctree::
    :maxdepth: 2

    quoted_graph

Dataset
-------

The RDF 1.1 Dataset, a small extension to the Conjunctive Graph. The primary term is "graphs in the datasets" and not "contexts with quads" so there is a separate method to set/retrieve a graph in a dataset and to operate with dataset graphs. As a consequence of this approach, dataset graphs cannot be identified with blank nodes, a name is always required (RDFLib will automatically add a name if one is not provided at creation time). This implementation includes a convenience method to directly add a single quad to a dataset graph.

.. toctree::
    :maxdepth: 2

    dataset


Working with graphs
-------------------

.. automodule:: rdflib.graph
