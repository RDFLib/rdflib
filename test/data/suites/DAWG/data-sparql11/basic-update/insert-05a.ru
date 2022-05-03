PREFIX : <http://example.org/>

INSERT { GRAPH :g2  { ?S ?P ?O } }
WHERE { GRAPH :g1  { ?S ?P ?O } } ;

INSERT { GRAPH :g2  { ?S ?P ?O } }
WHERE { GRAPH :g1  { ?S ?P ?O } } ;

INSERT { GRAPH :g3 { :s :p ?count } }
WHERE {
	SELECT (COUNT(*) AS ?count) WHERE {
		GRAPH :g2 { ?s ?p ?o }
	}
} ;
DROP GRAPH :g1 ;
DROP GRAPH :g2
