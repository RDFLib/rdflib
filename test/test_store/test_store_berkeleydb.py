from tempfile import mktemp

import pytest

from rdflib import Dataset, URIRef
from rdflib.plugins.stores.berkeleydb import has_bsddb
from rdflib.store import VALID_STORE

pytestmark = pytest.mark.skipif(
    not has_bsddb, reason="skipping berkeleydb tests, modile not available"
)


@pytest.fixture(
    scope="function",
    params=[True, False],
)
def get_dataset(request):
    path = mktemp()
    dataset = Dataset("BerkeleyDB", default_union=request.param)
    rt = dataset.open(path, create=True)
    assert rt == VALID_STORE, "The underlying store is corrupt"
    assert (
        len(dataset) == 0
    ), "There must be zero triples in the graph just after store (file) creation"
    data = """
            PREFIX : <https://example.org/>

            :a :b :c .
            :d :e :f .
            :d :g :h .
            """
    # if request.param is True:
    #     dataset.parse(data=data, format="ttl")
    # else:
    #     dataset.default_graph.parse(data=data, format="ttl")

    dataset.parse(data=data, format="ttl")

    yield path, dataset

    dataset.close()
    dataset.destroy(path)


def test_write(get_dataset):
    path, dataset = get_dataset
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
    path, dataset = get_dataset
    sx = None
    for s in dataset.subjects(
        predicate=URIRef("https://example.org/e"),
        object=URIRef("https://example.org/f"),
    ):
        sx = s
    assert sx == URIRef("https://example.org/d")


def test_sparql_query(get_dataset):
    path, dataset = get_dataset
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
    path, dataset = get_dataset
    q = """
        PREFIX : <https://example.org/>

        INSERT DATA {
            :x :y :z .
        }"""

    dataset.update(q)
    assert len(dataset) == 4, "After extra triple insert, length must be 4"


def test_multigraph(get_dataset):
    path, dataset = get_dataset
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
    path, dataset = get_dataset
    assert len(dataset) == 3, "Initially we must have 3 triples from setUp"
    dataset.close()
    dataset = None

    # reopen the graph
    dataset = Dataset("BerkeleyDB")
    dataset.open(path, create=False)
    assert (
        len(dataset) == 3
    ), "After close and reopen, we should still have the 3 originally added triples"
