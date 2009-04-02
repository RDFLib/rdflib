BAD_SPARQL=\
"""
BASE <tag:chimezie@ogbuji.net,2007:exampleNS>.
SELECT ?s
WHERE { ?s ?p ?o }"""

def test_bad_sparql():
    from rdflib.Graph import Graph
    Graph().query(BAD_SPARQL)
test_bad_sparql.unstable = True

if __name__ == '__main__':
    test_bad_sparql()
