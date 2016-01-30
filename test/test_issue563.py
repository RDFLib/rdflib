from rdflib import BNode, Literal, Graph, Namespace
from rdflib.compare import isomorphic

EX = Namespace("http://example.org/")
QUERY = """
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?x (%s(?y) as ?ys) (%s(?z) as ?zs) WHERE {
  VALUES (?x ?y ?z) {

    (2 6 UNDEF)
    (2 UNDEF 10)

    (3 UNDEF 15)
    (3 9 UNDEF)

    (5 UNDEF 25)
  }
}
GROUP BY ?x
"""

def test_sample():
    g = Graph()
    results = set(tuple(i) for i in g.query(QUERY % ("SAMPLE", "SAMPLE")))

    assert results == set([
        (Literal(2), Literal(6), Literal(10)),
        (Literal(3), Literal(9), Literal(15)),
        (Literal(5), None, Literal(25)),
    ])

def test_count():
    g = Graph()
    results = set(tuple(i) for i in g.query(QUERY % ("COUNT", "COUNT")))

    assert results == set([
        (Literal(2), Literal(1), Literal(1)),
        (Literal(3), Literal(1), Literal(1)),
        (Literal(5), Literal(0), Literal(1)),
    ])

if __name__ == "__main__":
    test_sample()
    test_count()



