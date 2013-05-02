PREFIX     : <http://example.org/> 
PREFIX foaf: <http://xmlns.com/foaf/0.1/> 

DELETE WHERE 
{ 
  ?a foaf:knows :b .
}
