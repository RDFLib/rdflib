.. _graphs:

=======
Graphs
=======

RDFLib defines the following kinds of Graphs:

* Graph(**store**, **identifier**)
* QuotedGraph(**store**, **identifier**)
* ConjunctiveGraph(**store**, **default_identifier** = None)

A Conjunctive Graph is the most relevant collection of graphs that are considered to be the boundary for closed world assumptions.  This boundary is equivalent to that of the store instance (which is itself uniquely identified and distinct from other instances of :class:`Store` that signify other Conjunctive Graphs).  It is equivalent to all the named graphs within it and associated with a ``_default_`` graph which is automatically assigned a :class:`BNode` for an identifier - if one isn't given.  

.. automodule:: rdflib.graph

.. toctree::
   :maxdepth: 2

   graph
   conjunctive_graph
   ../nodes/quoted_graph