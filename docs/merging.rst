.. _merging_graphs: 

==============
Merging graphs
==============

	A merge of a set of RDF graphs is defined as follows. If the graphs in
	the set have no blank nodes in common, then the union of the graphs is
	a merge; if they do share blank nodes, then it is the union of a set
	of graphs that is obtained by replacing the graphs in the set by
	equivalent graphs that share no blank nodes. This is often described
	by saying that the blank nodes have been 'standardized apart'. It is
	easy to see that any two merges are equivalent, so we will refer to
	the merge, following the convention on equivalent graphs. Using the
	convention on equivalent graphs and identity, any graph in the
	original set is considered to be a subgraph of the merge.

	One does not, in general, obtain the merge of a set of graphs by
	concatenating their corresponding N-Triples documents and constructing
	the graph described by the merged document. If some of the documents
	use the same node identifiers, the merged document will describe a
	graph in which some of the blank nodes have been 'accidentally'
	identified. To merge N-Triples documents it is necessary to check if
	the same nodeID is used in two or more documents, and to replace it
	with a distinct nodeID in each of them, before merging the
	documents. Similar cautions apply to merging graphs described by
	RDF/XML documents which contain nodeIDs

*(copied directly from http://www.w3.org/TR/rdf-mt/#graphdefs)*


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



