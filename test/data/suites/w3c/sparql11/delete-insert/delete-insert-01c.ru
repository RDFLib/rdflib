PREFIX     : <http://example.org/> 
PREFIX foaf: <http://xmlns.com/foaf/0.1/> 

INSERT
{
  ?b foaf:knows ?a .
}
WHERE
{
  ?a foaf:knows ?b .
}
;
DELETE 
{
  ?a foaf:knows ?b .
}
WHERE
{
  ?a foaf:knows ?b .
}

