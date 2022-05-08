from test.utils import helper
from rdflib import Graph, Literal, Variable


def test():
    """Test service returns simple literals not as NULL.

    Issue: https://github.com/RDFLib/rdflib/issues/1278
    """

    g = Graph()
    q = """SELECT ?s ?p ?o
WHERE {
    SERVICE <https://DBpedia.org/sparql> {
        VALUES (?s ?p ?o) {(<http://example.org/a> <http://example.org/b> "c")}
    }
}"""
    assert results.bindings[0].get(Variable('o')) == Literal('c')
