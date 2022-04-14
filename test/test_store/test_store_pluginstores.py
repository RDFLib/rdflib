from tempfile import mktemp

import pytest

from rdflib import Dataset, URIRef
from test.data import tarek, likes, pizza, michel, hates, cheese, bob
from rdflib.store import VALID_STORE
from test.pluginstores import HOST, root, get_plugin_stores, set_store_and_path, open_store, cleanup, dburis


@pytest.fixture(
    scope="function",
    params=get_plugin_stores(),
)
def get_dataset(request):
    storename = request.param

    store, path = set_store_and_path(storename)

    d = Dataset(store=store, identifier=URIRef("urn:example:testgraph"), default_union=True)

    dataset = open_store(d, storename, path)

    data = """
            PREFIX : <https://example.org/>

            :a :b :c .
            :d :e :f .
            :d :g :h .
            """
    dataset.parse(data=data, format="ttl")
    assert (
        len(dataset.default_graph) == 3
    ), "There must be three triples in the default graph after the first data chunk parse"

    yield store, path, dataset

    cleanup(dataset, storename, path)


def test_write(get_dataset):
    store, path, dataset = get_dataset
    assert (
        len(dataset.default_graph) == 3
    ), "There must be three triples in the graph after the first data chunk parse"
    data2 = """
            PREFIX : <https://example.org/>

            :d :i :j .
            """
    dataset.parse(data=data2, format="ttl")
    assert (
        len(dataset) == 4
    ), "There must be four triples in the graph after the second data chunk parse"
    data3 = """
            PREFIX : <https://example.org/>

            :d :i :j .
            """
    dataset.parse(data=data3, format="ttl")
    assert (
        len(dataset) == 4
    ), "There must still be four triples in the graph after the third data chunk parse"


def test_read(get_dataset):
    store, path, dataset = get_dataset
    sx = None
    for s in dataset.subjects(
        predicate=URIRef("https://example.org/e"),
        object=URIRef("https://example.org/f"),
    ):
        sx = s
    assert sx == URIRef("https://example.org/d")


def test_sparql_query(get_dataset):
    store, path, dataset = get_dataset
    q = """
        PREFIX : <https://example.org/>

        SELECT (COUNT(*) AS ?c)
        WHERE {
            :d ?p ?o .
        }"""

    c = 0
    for row in dataset.query(q):
        c = int(row.c)
    assert c == 2, "SPARQL COUNT must return 2"


def test_sparql_insert(get_dataset):
    store, path, dataset = get_dataset
    q = """
        PREFIX : <https://example.org/>

        INSERT DATA {
            :x :y :z .
        }"""

    dataset.update(q)
    assert len(dataset) == 4, "After extra triple insert, length must be 4"


def test_multigraph(get_dataset):
    store, path, dataset = get_dataset
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

    dataset.update(q)

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
    for row in dataset.query(q):
        c = int(row.c)
    assert c == 2, "SPARQL COUNT must return 2 (:m & :n)"


def test_open_shut(get_dataset):
    store, path, dataset = get_dataset
    if store != "Memory":
        assert len(dataset) == 3, "Initially we must have 3 triples from setUp"
        dataset.close()
        dataset = None

        # reopen the graph
        new_dataset = Dataset(store, identifier=URIRef("urn:example:testgraph"))
        new_dataset.open(path, create=False)
        assert (
            len(new_dataset) == 3
        ), "After close and reopen, we should still have the 3 originally added triples"
