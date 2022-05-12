prefix : <http://example.org/>
INSERT { GRAPH :g2  { ?S ?P ?O } }
 WHERE { GRAPH :g1  { ?S ?P ?O } } ;
INSERT { GRAPH :g2  { ?S ?P ?O } }
 WHERE { GRAPH :g1  { ?S ?P ?O } }
