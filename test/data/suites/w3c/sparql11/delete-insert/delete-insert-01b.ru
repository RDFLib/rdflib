PREFIX     : <http://example.org/> 
PREFIX foaf: <http://xmlns.com/foaf/0.1/> 

DELETE 
{
  ?a foaf:knows ?b .
}
WHERE
{
  ?a foaf:knows ?b .
}
;
INSERT
{
  ?b foaf:knows ?a .
}
WHERE
{
  ?a foaf:knows ?b .
}
