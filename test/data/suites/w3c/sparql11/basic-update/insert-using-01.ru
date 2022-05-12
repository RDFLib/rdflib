PREFIX     : <http://example.org/> 

INSERT {
	?s ?p "q"
}
USING :g1
USING :g2
WHERE {
	?s ?p ?o
}
