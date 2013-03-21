PREFIX     : <http://example.org/> 
PREFIX foaf: <http://xmlns.com/foaf/0.1/> 

DELETE 
{
  ?s ?p ?o .
}
WHERE
{
  :a foaf:knows ?s .
  ?s ?p ?o
}
