PREFIX  :     <http://example/>
WITH :g
DELETE {
  <base:s> ?p ?o .
}
WHERE
  { ?s ?p ?o }
