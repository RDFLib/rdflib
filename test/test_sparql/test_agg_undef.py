import pytest

from rdflib import RDFS, Graph, Literal, URIRef, Variable

query_tpl = """
SELECT ?x (%s(?y_) as ?y) {
  VALUES (?x ?y_ ?z) {
    ("x1" undef 1)
    ("x1" undef 2)
    ("x2" undef 3)
    ("x2" 42    4)
  }
} GROUP BY ?x ORDER BY ?x
"""

Y = Variable("y")


def template_tst(agg_func, first, second):
    g = Graph()
    results = list(g.query(query_tpl % agg_func))

    print("===", results)
    assert results[0][1] == first, (results[0][1], first)
    assert results[1][1] == second, (results[1][1], second)


def get_aggregates_tests():
    yield template_tst, "SUM", Literal(0), Literal(42)
    yield template_tst, "MIN", None, Literal(42)
    yield template_tst, "MAX", None, Literal(42)
    # yield template_tst, 'AVG', Literal(0), Literal(42)
    yield template_tst, "SAMPLE", None, Literal(42)
    yield template_tst, "COUNT", Literal(0), Literal(1)
    yield template_tst, "GROUP_CONCAT", Literal(""), Literal("42")


@pytest.mark.parametrize("checker, agg_func, first, second", get_aggregates_tests())
def test_aggregates(checker, agg_func, first, second) -> None:
    checker(agg_func, first, second)


def test_group_by_null():
    g = Graph()
    results = list(
        g.query(
            """
        SELECT ?x ?y (AVG(?z) as ?az) {
            VALUES (?x ?y ?z) {
                (1 undef 10)
                (1 undef 15)
                (2 undef 20)
                (2 undef 21)
                (2 undef 24)
           }
        } GROUP BY ?x ?y
        ORDER BY ?x
    """
        )
    )
    assert len(results) == 2
    assert results[0][0] == Literal(1)
    assert results[1][0] == Literal(2)


def test_values_outside_group_by():
    """
    Ensure that VALUES defined outside an aggregate (group by) query join and filter
     on the user-defined variable names.
    """
    g = Graph()
    g.add(
        (URIRef("http://example.com/something"), RDFS.label, Literal("Match on this."))
    )
    g.add(
        (
            URIRef("http://example.com/something-else"),
            RDFS.label,
            Literal("Don't match on this."),
        )
    )

    results = list(
        g.query(
            """
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

    SELECT ?obj ?label
    WHERE {
        ?obj rdfs:label ?label
    }
    GROUP BY ?obj ?label
    VALUES ( ?obj ) {
        ( <http://example.com/something> )
    }
    """
        )
    )

    assert len(results) == 1
    assert results[0][0] == URIRef("http://example.com/something")
    assert results[0][1] == Literal("Match on this.")
