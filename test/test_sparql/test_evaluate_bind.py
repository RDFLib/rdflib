"""
Verify evaluation of BIND expressions of different types. See
<http://www.w3.org/TR/sparql11-query/#rExpression>.
"""
import pytest

from rdflib import Graph, Literal, URIRef, Variable


def get_bind_tests():
    base = "http://example.org/"
    g = Graph()
    g.add((URIRef(base + "thing"), URIRef(base + "ns#comment"), Literal("anything")))

    def check(expr, var, obj):
        r = g.query(
            """
                prefix : <http://example.org/ns#>
                select * where { ?s ?p ?o . %s } """
            % expr
        )
        assert r.bindings[0][Variable(var)] == obj

    yield (check, 'bind("thing" as ?name)', "name", Literal("thing"))

    yield (
        check,
        "bind(<http://example.org/other> as ?other)",
        "other",
        URIRef("http://example.org/other"),
    )

    yield (
        check,
        "bind(:Thing as ?type)",
        "type",
        URIRef("http://example.org/ns#Thing"),
    )


@pytest.mark.parametrize("checker, expr, var, obj", get_bind_tests())
def test_bind(checker, expr, var, obj) -> None:
    checker(expr, var, obj)
