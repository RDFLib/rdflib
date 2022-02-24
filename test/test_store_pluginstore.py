import os
import shutil
import tempfile

import pytest

from rdflib import ConjunctiveGraph, URIRef, plugin
from rdflib.store import VALID_STORE

tmpdir = tempfile.gettempdir()
path = os.path.join(tmpdir, "test_dbmstore")

pluginstores = []

for s in plugin.plugins(None, plugin.Store):
    if s.name in (
        "default",
        "Memory",
        "Auditable",
        "Concurrent",
        "SimpleMemory",
        "SPARQLStore",
        "SPARQLUpdateStore",
    ):
        continue  # inappropriate for these tests

    try:
        graph = ConjunctiveGraph(store=s.name)
        pluginstores.append(s.name)
    except ImportError:
        pass


@pytest.fixture(
    scope="function",
    params=pluginstores,
)
def get_conjunctive_graph(request):
    store = request.param
    path = tempfile.mktemp()
    try:
        shutil.rmtree(path)
    except Exception:
        pass
    graph = ConjunctiveGraph(store=store)
    rt = graph.open(path, create=True)
    assert rt == VALID_STORE, "The underlying store is corrupt"
    assert (
        len(graph) == 0
    ), "There must be zero triples in the graph just after store (file) creation"
    data = """
            PREFIX : <https://example.org/>

            :a :b :c .
            :d :e :f .
            :d :g :h .
            """
    graph.parse(data=data, format="ttl")

    yield graph, store, path

    graph.close()
    graph.store.destroy(configuration=path)

    try:
        shutil.rmtree(path)
    except Exception:
        pass


def test_open_shut(get_conjunctive_graph):
    graph, store, path = get_conjunctive_graph
    assert len(graph) == 3, "Initially we must have 3 triples from setUp"
    graph.close()
    graph = None

    # reopen the graph
    graph2 = ConjunctiveGraph(store)
    graph2.open(path, create=False)

    assert (
        len(graph2) == 3
    ), "After close and reopen, we should still have the 3 originally added triples"
    graph2.close()
    graph2.store.destroy(configuration=path)


def test_write(get_conjunctive_graph):
    graph, store, path = get_conjunctive_graph
    assert (
        len(graph) == 3
    ), "There must be three triples in the graph after the first data chunk parse"
    data2 = """
            PREFIX : <https://example.org/>

            :d :i :j .
            """
    graph.parse(data=data2, format="ttl")
    assert (
        len(graph) == 4
    ), "There must be four triples in the graph after the second data chunk parse"
    data3 = """
            PREFIX : <https://example.org/>

            :d :i :j .
            """
    graph.parse(data=data3, format="ttl")
    assert (
        len(graph) == 4
    ), "There must still be four triples in the graph after the thrd data chunk parse"


def test_read(get_conjunctive_graph):
    graph, store, path = get_conjunctive_graph
    sx = None
    for s in graph.subjects(
        predicate=URIRef("https://example.org/e"),
        object=URIRef("https://example.org/f"),
    ):
        sx = s
    assert sx == URIRef("https://example.org/d")


def test_sparql_query(get_conjunctive_graph):
    graph, store, path = get_conjunctive_graph
    q = r"""
        PREFIX : <https://example.org/>

        SELECT (COUNT(*) AS ?c)
        WHERE {
            :d ?p ?o .
        }"""

    c = 0
    for row in graph.query(q):
        c = int(row.c)
    assert c == 2, "SPARQL COUNT must return 2"


def test_sparql_insert(get_conjunctive_graph):
    graph, store, path = get_conjunctive_graph
    q = r"""
        PREFIX : <https://example.org/>

        INSERT DATA {
            :x :y :z .
        }"""

    graph.update(q)
    assert len(graph) == 4, "After extra triple insert, length must be 4"


def test_multigraph(get_conjunctive_graph):
    graph, store, path = get_conjunctive_graph
    q = r"""
        PREFIX : <https://example.org/>

        INSERT DATA {
            GRAPH :m {
                :x :y :z .
            }
            GRAPH :n {
                :x :y :z .
            }
        }"""

    graph.update(q)

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
    for row in graph.query(q):
        c = int(row.c)
    assert c == 3, "SPARQL COUNT must return 3 (default, :m & :n)"
