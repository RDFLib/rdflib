PREFIX :       <http://example/>

DELETE { GRAPH ?g { ?s ?p ?o } }
INSERT { ?s ?p ?o {| :source ?g |} }
WHERE {
  GRAPH ?g { ?s ?p ?o }
}
