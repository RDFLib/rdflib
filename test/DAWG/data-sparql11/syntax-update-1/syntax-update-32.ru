BASE    <base:>
PREFIX  :     <http://example/>

WITH :g
DELETE {
  <s> ?p ?o .
}
INSERT {
  ?s ?p <#o> .
}
USING <base:g1>
USING <base:g2>
USING NAMED :gn1
USING NAMED :gn2
WHERE
  { ?s ?p ?o }
