PREFIX     : <http://example.org/> 
PREFIX foaf: <http://xmlns.com/foaf/0.1/> 

WITH <http://example.org/g1>
DELETE 
{
  ?s ?p ?o .
}
WHERE 
{
  ?s foaf:knows :c .
  ?s ?p ?o
}
