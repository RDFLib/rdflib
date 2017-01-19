from rdflib.graph import Graph
from rdflib.term import URIRef
from rdflib.collection import Collection

ttl = """
@prefix : <http://example.org/>.

:s :p (:a :b :a).
"""
def test_collection_with_duplicates():
    g = Graph().parse(data=ttl, format="turtle")
    for _,_,o in g.triples((URIRef("http://example.org/s"), URIRef("http://example.org/p"), None)):
        break
    c = list(Collection(g, o))
    assert c == list(URIRef("http://example.org/" + x) for x in ["a", "b", "a"])

if __name__ == '__main__':
    test_collection_with_duplicates()
