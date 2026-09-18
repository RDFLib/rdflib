from rdflib import Graph, Namespace

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
