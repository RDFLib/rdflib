PREFIX foaf: <http://xmlns.com/foaf/0.1/> 

DELETE 
{
  ?a foaf:knows ?Var_B .
}
WHERE
{
  { ?a foaf:name "Alan" }
  { SELECT DISTINCT ?Var_B 
            {  { ?Var_B ?Var_B1 ?Var_B2 } UNION 
               { ?Var_B1 ?Var_B ?Var_B2 } UNION 
               { ?Var_B1 ?Var_B2 ?Var_B } UNION 
               { GRAPH ?Var_Bg {?Var_B ?Var_B1 ?Var_B2 } } UNION
               { GRAPH ?Var_Bg {?Var_B1 ?Var_B ?Var_B2 } } UNION
               { GRAPH ?Var_Bg {?Var_B1 ?Var_B2 ?Var_B } } } }
}