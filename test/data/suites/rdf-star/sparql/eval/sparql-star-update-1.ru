PREFIX :       <http://example/>

INSERT {
  << ?s ?p ?o >> :source ?g
} WHERE {
  GRAPH ?g { ?s ?p ?o }
}
