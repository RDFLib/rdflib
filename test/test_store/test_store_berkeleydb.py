import tempfile

import pytest

from rdflib import ConjunctiveGraph, URIRef
from rdflib.plugins.stores.berkeleydb import has_bsddb
from rdflib.store import VALID_STORE

pytestmark = pytest.mark.skipif(
    not has_bsddb, reason="skipping berkeleydb tests, modile not available"
)


@pytest.fixture
def get_graph():
    path = tempfile.NamedTemporaryFile().name
    g = ConjunctiveGraph("BerkeleyDB")
    rt = g.open(path, create=True)
    assert rt == VALID_STORE, "The underlying store is corrupt"
    assert (
        len(g) == 0
    ), "There must be zero triples in the graph just after store (file) creation"
    data = """
            PREFIX : <https://example.org/>

            :a :b :c .
            :d :e :f .
            :d :g :h .
            """
    g.parse(data=data, format="ttl")

    yield path, g

    g.close()
    g.destroy(path)


def test_write(get_graph):
    path, g = get_graph
    assert (
        len(g) == 3
    ), "There must be three triples in the graph after the first data chunk parse"
    data2 = """
            PREFIX : <https://example.org/>

            :d :i :j .
            """
    g.parse(data=data2, format="ttl")
    assert (
        len(g) == 4
    ), "There must be four triples in the graph after the second data chunk parse"
    data3 = """
            PREFIX : <https://example.org/>

            :d :i :j .
            """
    g.parse(data=data3, format="ttl")
    assert (
        len(g) == 4
    ), "There must still be four triples in the graph after the third data chunk parse"


def test_read(get_graph):
    path, g = get_graph
    sx = None
    for s in g.subjects(
        predicate=URIRef("https://example.org/e"),
        object=URIRef("https://example.org/f"),
    ):
        sx = s
    assert sx == URIRef("https://example.org/d")


def test_sparql_query(get_graph):
    path, g = get_graph
    q = """
        PREFIX : <https://example.org/>

        SELECT (COUNT(*) AS ?c)
        WHERE {
            :d ?p ?o .
        }"""

    c = 0
    for row in g.query(q):
        c = int(row.c)
    assert c == 2, "SPARQL COUNT must return 2"


def test_sparql_insert(get_graph):
    path, g = get_graph
    q = """
        PREFIX : <https://example.org/>

        INSERT DATA {
            :x :y :z .
        }"""

    g.update(q)
    assert len(g) == 4, "After extra triple insert, length must be 4"


def test_multigraph(get_graph):
    path, g = get_graph
    q = """
        PREFIX : <https://example.org/>

        INSERT DATA {
            GRAPH :m {
                :x :y :z .
            }
            GRAPH :n {
                :x :y :z .
            }
        }"""

    g.update(q)

    q = """
        SELECT (COUNT(?g) AS ?c)
        WHERE {
            SELECT DISTINCT ?g
            WHERE {
                GRAPH ?g {
                    ?s ?p ?o
                }
            }
        }
        """
    c = 0
    for row in g.query(q):
        c = int(row.c)
    assert c == 3, "SPARQL COUNT must return 3 (default, :m & :n)"


def test_open_shut(get_graph):
    path, g = get_graph
    assert len(g) == 3, "Initially we must have 3 triples from setUp"
    g.close()
    g = None

    # reopen the graph
    g = ConjunctiveGraph("BerkeleyDB")
    g.open(path, create=False)
    assert (
        len(g) == 3
    ), "After close and reopen, we should still have the 3 originally added triples"
