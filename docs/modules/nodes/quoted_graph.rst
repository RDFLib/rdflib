:mod:`rdflib.graph.QuotedGraph` -- Quoted graphs
================================================

RDFLib graphs support an additional extension of RDF semantics for formulae. For the academically inclined, Graham Kyles `formal extension`__ is probably a good read.

.. __: http://ninebynine.org/RDFNotes/UsingContextsWithRDF.html#xtocid-6303976

Formulae are represented formally by the :class:`rdflib.Graph.QuotedGraph` class and are disjoint from regular RDF graphs in that their statements are quoted.

Module Contents
---------------

.. autoclass:: rdflib.graph.QuotedGraph
