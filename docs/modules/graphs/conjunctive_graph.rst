:mod:`rdflib.Graph.ConjunctiveGraph` -- ConjunctiveGraph
========================================================

.. autoclass:: rdflib.graph.ConjunctiveGraph
    :members:

Modelling notes
----------------
This refers to the 'top-level' Graph. It is the aggregation of all the contexts within it and is also the appropriate, absolute boundary for closed world assumptions / models. This distinction is the low-hanging fruit of RDF along the path to the semantic web and most of its value is in (corporate/enterprise) real-world problems:

There are at least two situations where the closed world assumption is used. The first is where it is assumed that a knowledge base contains all relevant facts. This is common in corporate databases. That is, the information it contains is assumed to be complete

From a store perspective, closed world assumptions also provide the benefit of better query response times due to the explicit closed world boundaries. Closed world boundaries can be made transparent by federated queries that assume each ConjunctiveGraph is a section of a larger, unbounded universe. So a closed world assumption does not preclude you from an open world assumption.

For the sake of persistence, Conjunctive Graphs must be distinguished by identifiers (that may not necessarily be RDF identifiers or may be an RDF identifier normalized - SHA1/MD5 perhaps - for database naming purposes ) which could be referenced to indicate conjunctive queries (queries made across the entire conjunctive graph) or appear as nodes in asserted statements. In this latter case, such statements could be interpreted as being made about the entire 'known' universe. For example:

<urn:uuid:conjunctive-graph-foo> rdf:type :ConjunctiveGraph

<urn:uuid:conjunctive-graph-foo> rdf:type log:Truth

<urn:uuid:conjunctive-graph-foo> :persistedBy :MySQL


