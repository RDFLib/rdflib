PREFIX : <http://example.org/>

# starting with an empty graph store,
# insert the same bnode in two different graphs...

INSERT DATA { GRAPH :g1  { _:b :p :o } 
       	      GRAPH :g2  { _:b :p :o } } ;

# ... then copy g1 to g2 ...

INSERT { GRAPH :g2  { ?S ?P ?O } }
 WHERE { GRAPH :g1  { ?S ?P ?O } } ;

# ... by which the number of triples in 
# g2 should not increase

INSERT { GRAPH :g3 { :s :p ?count } }
WHERE {
	SELECT (COUNT(*) AS ?count) WHERE {
		GRAPH :g2 { ?s ?p ?o }
	}
} ;
DROP GRAPH :g1 ;
DROP GRAPH :g2
