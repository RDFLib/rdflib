PREFIX     : <http://example.org/> 

WITH :g1
INSERT {
	?s ?p "z"
} WHERE {
	?s ?p ?o
}
