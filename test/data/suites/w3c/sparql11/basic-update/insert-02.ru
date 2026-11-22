PREFIX     : <http://example.org/> 

INSERT {
	GRAPH :g1 {
		?s ?p "q"
	}
} WHERE {
	?s ?p ?o
}
