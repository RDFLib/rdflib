import pytest

from rdflib import RDF, Graph, Namespace

EX = Namespace("http://example.org/gmark/")


def test_negated_property_set_with_forward_and_reverse_paths() -> None:
    graph = Graph()
    graph.add((EX.C, EX.p2, EX.D))
    graph.add((EX.B, EX.p1, EX.C))
    graph.add((EX.A, EX.p0, EX.B))

    results = graph.query(
        """
        PREFIX : <http://example.org/gmark/>
        SELECT ?x1 ?x2
        WHERE {
            ?x1 !(:p1|^:p2) ?x2
        }
        """
    )

    assert set(results) == {
        (EX.A, EX.B),
        (EX.B, EX.A),
        (EX.C, EX.B),
        (EX.C, EX.D),
    }


def test_negated_property_set_with_only_reverse_path() -> None:
    graph = Graph()
    graph.add((EX.C, EX.p2, EX.D))
    graph.add((EX.B, EX.p1, EX.C))
    graph.add((EX.A, EX.p0, EX.B))

    results = graph.query(
        """
        PREFIX : <http://example.org/gmark/>
        SELECT ?x1 ?x2
        WHERE {
            ?x1 !^:p2 ?x2
        }
        """
    )

    assert set(results) == {
        (EX.B, EX.A),
        (EX.C, EX.B),
    }


@pytest.mark.parametrize(
    "bindings, expected",
    [
        ({"x1": EX.A}, {(EX.A, EX.B)}),
        ({"x2": EX.B}, {(EX.A, EX.B), (EX.C, EX.B)}),
        ({"x1": EX.C, "x2": EX.B}, {(EX.C, EX.B)}),
        ({"x1": EX.B, "x2": EX.C}, set()),
    ],
)
def test_negated_property_set_with_bound_endpoints(bindings, expected) -> None:
    graph = Graph()
    graph.add((EX.C, EX.p2, EX.D))
    graph.add((EX.B, EX.p1, EX.C))
    graph.add((EX.A, EX.p0, EX.B))
    results = graph.query(
        "SELECT ?x1 ?x2 WHERE { ?x1 !(<%s>|^<%s>) ?x2 }" % (EX.p1, EX.p2),
        initBindings=bindings,
    )
    assert set(results) == expected


def test_inverse_negated_property_set_in_sequence() -> None:
    graph = Graph()
    graph.add((EX.C, EX.p2, EX.D))
    graph.add((EX.B, EX.p1, EX.C))
    graph.add((EX.A, EX.p0, EX.B))
    results = graph.query(
        "SELECT ?x1 ?x2 WHERE { ?x1 (!^<%s>)/<%s> ?x2 }" % (EX.p2, EX.p0)
    )
    assert set(results) == {(EX.B, EX.B)}


def test_inverse_negated_rdf_type_shorthand() -> None:
    graph = Graph()
    graph.add((EX.A, RDF.type, EX.Class))
    graph.add((EX.B, EX.p1, EX.C))
    results = graph.query("SELECT ?x1 ?x2 WHERE { ?x1 !^a ?x2 }")
    assert set(results) == {(EX.C, EX.B)}
