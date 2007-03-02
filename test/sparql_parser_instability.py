BAD_SPARQL=\
"""
BASE <tag:chimezie@ogbuji.net,2007:exampleNS>.
SELECT ?s
WHERE { ?s ?p ?o }"""

def test():
    from rdflib.Graph import Graph
    Graph().query(BAD_SPARQL)

if __name__ == '__main__':
    test()