.. _merging_graphs: 

==============
Merging graphs
==============

 Graphs share blank nodes only if they are derived from graphs described by documents or other structures (such as an RDF dataset) that explicitly provide for the sharing of blank nodes between different RDF graphs. Simply downloading a web document does not mean that the blank nodes in a resulting RDF graph are the same as the blank nodes coming from other downloads of the same document or from the same RDF source.

RDF applications which manipulate concrete syntaxes for RDF which use blank node identifiers should take care to keep track of the identity of the blank nodes they identify. Blank node identifiers often have a local scope, so when RDF from different sources is combined, identifiers may have to be changed in order to avoid accidental conflation of distinct blank nodes.

For example, two documents may both use the blank node identifier "_:x" to identify a blank node, but unless these documents are in a shared identifier scope or are derived from a common source, the occurrences of "_:x" in one document will identify a different blank node than the one in the graph described by the other document. When graphs are formed by combining RDF from multiple sources, it may be necessary to standardize apart the blank node identifiers by replacing them by others which do not occur in the other document(s).

*(copied directly from https://www.w3.org/TR/rdf11-mt/#shared-blank-nodes-unions-and-merges)*


In RDFLib, blank nodes are given unique IDs when parsing, so graph merging can be done by simply reading several files into the same graph:: 

    from rdflib import Graph

    graph = Graph()

    graph.parse(input1) 
    graph.parse(input2)

``graph`` now contains the merged graph of ``input1`` and ``input2``. 


.. note:: However, the set-theoretic graph operations in RDFLib are assumed to be performed in sub-graphs of some larger data-base (for instance, in the context of a :class:`~rdflib.graph.ConjunctiveGraph`) and assume shared blank node IDs, and therefore do NOT do *correct* merging, i.e.:: 
		  
		  from rdflib import Graph

		  g1 = Graph()
		  g1.parse(input1)
		  
		  g2 = Graph()
		  g2.parse(input2)

		  graph = g1 + g2

	May cause unwanted collisions of blank-nodes in
	``graph``. 



