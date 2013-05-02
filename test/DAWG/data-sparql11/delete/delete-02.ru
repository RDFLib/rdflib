PREFIX     : <http://example.org/> 
PREFIX foaf: <http://xmlns.com/foaf/0.1/> 

DELETE 
{
  GRAPH <http://example.org/g1> { ?s ?p ?o }
}
WHERE 
{
  GRAPH <http://example.org/g1> { :a foaf:knows ?s .
                                  ?s ?p ?o }
}
