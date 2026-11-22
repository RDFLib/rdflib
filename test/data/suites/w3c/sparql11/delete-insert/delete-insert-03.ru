PREFIX     : <http://example.org/> 
PREFIX foaf: <http://xmlns.com/foaf/0.1/> 

DELETE 
{
  ?a foaf:knows [] .
}
WHERE
{
  ?a foaf:name "Alan" .
}
