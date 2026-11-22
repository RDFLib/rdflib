PREFIX     : <http://example.org/> 

INSERT {
	?s ?p "q"
}
USING :g1
WHERE {
	?s ?p ?o
}
