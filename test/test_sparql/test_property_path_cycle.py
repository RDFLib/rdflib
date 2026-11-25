from rdflib import Graph, URIRef


def _cycle():
    g = Graph()
    a = URIRef("http://example.org/a")
    b = URIRef("http://example.org/b")
    p = URIRef("http://example.org/p")
    g.add((a, p, b))
    g.add((b, p, a))
    return g


def _names(rows):
    return [str(row[0]).rsplit("/", 1)[-1] for row in rows]


def test_star_subject_on_cycle_is_distinct():
    rows = list(
        _cycle().query(
            "SELECT ?o WHERE { <http://example.org/a> <http://example.org/p>* ?o }"
        )
    )
    assert sorted(_names(rows)) == ["a", "b"]
    assert len(rows) == 2


def test_star_object_on_cycle_is_distinct():
    rows = list(
        _cycle().query(
            "SELECT ?s WHERE { ?s <http://example.org/p>* <http://example.org/a> }"
        )
    )
    assert sorted(_names(rows)) == ["a", "b"]
    assert len(rows) == 2


def test_plus_on_cycle_still_reaches_the_start():
    rows = list(
        _cycle().query(
            "SELECT ?o WHERE { <http://example.org/a> <http://example.org/p>+ ?o }"
        )
    )
    assert sorted(_names(rows)) == ["a", "b"]
    assert len(rows) == 2


def test_star_count_on_cycle():
    count = list(
        _cycle().query(
            "SELECT (COUNT(?o) AS ?c) WHERE { <http://example.org/a> <http://example.org/p>* ?o }"
        )
    )[0][0]
    assert int(count) == 2


def test_star_self_loop_once():
    g = Graph()
    a = URIRef("http://example.org/a")
    p = URIRef("http://example.org/p")
    g.add((a, p, a))
    rows = list(
        g.query("SELECT ?o WHERE { <http://example.org/a> <http://example.org/p>* ?o }")
    )
    assert _names(rows) == ["a"]


def test_star_chain_includes_start_once():
    g = Graph()
    a = URIRef("http://example.org/a")
    b = URIRef("http://example.org/b")
    p = URIRef("http://example.org/p")
    g.add((a, p, b))
    rows = list(
        g.query("SELECT ?o WHERE { <http://example.org/a> <http://example.org/p>* ?o }")
    )
    assert sorted(_names(rows)) == ["a", "b"]
    assert len(rows) == 2
