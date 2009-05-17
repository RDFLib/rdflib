from rdflib.sparql.parser import parse

# second query from here:
# http://www.w3.org/TR/rdf-sparql-query/#GroupPatterns

query = """
PREFIX foaf:    <http://xmlns.com/foaf/0.1/>
SELECT ?name ?mbox
WHERE  { { ?x foaf:name ?name . }
         { ?x foaf:mbox ?mbox . }
       }
"""

correct = """{ [<SPARQLParser.GraphPattern: [[?x [foaf:name([u'?name'])], ?x [foaf:mbox([u'?mbox'])]]]>] }"""

if __name__ == "__main__":
    p = parse(query)
    tmp = p.query.whereClause.parsedGraphPattern
    if str(tmp) == correct:
        print "PASSED"
