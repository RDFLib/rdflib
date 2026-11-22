PREFIX     : <http://example.org/> 
PREFIX foaf: <http://xmlns.com/foaf/0.1/> 

DELETE 
{
  GRAPH <http://example.org/g1> { ?s ?p ?o }
}
USING <http://example.org/g1>
WHERE 
{ 
  ?s foaf:knows :b .
  ?s ?p ?o 
}
