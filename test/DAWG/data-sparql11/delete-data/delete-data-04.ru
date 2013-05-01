PREFIX     : <http://example.org/> 
PREFIX foaf: <http://xmlns.com/foaf/0.1/> 

DELETE DATA 
{
  GRAPH <http://example.org/g1> { :a foaf:knows :c }
}
