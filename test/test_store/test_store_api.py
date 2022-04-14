import logging
import os
import shutil
import tempfile
from test.data import (
    CONSISTENT_DATA_DIR,
    bob,
    cheese,
    context1,
    context2,
    likes,
    michel,
    pizza,
    context0,
)

import pytest

from rdflib import RDFS, XSD, Literal, URIRef, plugin
from rdflib.graph import Dataset, Graph, DATASET_DEFAULT_GRAPH_ID
from rdflib.store import NO_STORE, VALID_STORE, Store
from test.pluginstores import HOST, root, get_plugin_stores, set_store_and_path, open_store, cleanup, dburis

timblcardn3 = open(os.path.join(CONSISTENT_DATA_DIR, "timbl-card.n3")).read()

logging.basicConfig(level=logging.ERROR, format="%(message)s")
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


@pytest.fixture(
    scope="function",
    params=get_plugin_stores(),
)
def get_graph(request):

    storename = request.param

    store, path = set_store_and_path(storename)

    s = plugin.get(storename, Store)(identifier=context0)

    if storename == "SPARQLUpdateStore":
        s.open(configuration=path, create=False)
    elif storename == "FileStorageZODB":
        s.open(configuration=path, create=True)
    elif storename != "Memory":
        # rt = g.store.open(configuration=path, create=True)
        rt = s.open(path=path, create=True)
        assert rt == VALID_STORE, "The underlying store is corrupt"

    graph = Graph(store=s, identifier=s.identifier)

    data = """
            PREFIX : <https://example.org/>

            :a :b :c .
            :d :e :f .
            :d :g :h .
            """
    graph.parse(data=data, format="ttl")
    assert (
        len(graph) == 3
    ), "There must be three triples in the graph after the first data chunk parse"

    yield storename, path, graph

    cleanup(graph, storename, path)


@pytest.fixture(
    scope="function",
    params=get_plugin_stores(),
)
def get_dataset(request):

    storename = request.param

    store, path = set_store_and_path(storename)

    s = plugin.get(storename, Store)(identifier=context0)

    if storename == "SPARQLUpdateStore":
        s.open(configuration=path, create=False)
    elif storename == "FileStorageZODB":
        s.open(configuration=path, create=True)
    elif storename != "Memory":
        # rt = g.store.open(configuration=path, create=True)
        rt = s.open(path=path, create=True)
        assert rt == VALID_STORE, "The underlying store is corrupt"

    dataset = Dataset(store=s, identifier=s.identifier)

    data = """
            PREFIX : <https://example.org/>

            :a :b :c .
            :d :e :f .
            :d :g :h .
            """
    dataset.parse(data=data, format="ttl")
    assert (
        len(dataset) == 3
    ), "There must be three triples in the graph after the first data chunk parse"

    yield store, path, dataset

    cleanup(dataset, storename, path)


def test_graph_create_db(get_graph):
    store, path, graph = get_graph
    graph.add((michel, likes, pizza))
    graph.add((michel, likes, cheese))
    graph.commit()
    assert (
        len(graph) == 5
    ), f"There must be five triples in the graph after the above data chunk parse, not {len(graph)}"


def test_graph_escape_quoting(get_graph):
    store, path, graph = get_graph
    test_string = "That’s a Literal!!"
    graph.add(
        (
            URIRef("http://example.org/foo"),
            RDFS.label,
            Literal(test_string, datatype=XSD.string),
        )
    )
    graph.commit()
    assert "That’s a Literal!!" in graph.serialize(format="xml")


def test_graph_namespaces(get_graph):
    store, path, graph = get_graph
    no_of_default_namespaces = len(list(graph.namespaces()))
    graph.bind("exorg", "http://example.org/")
    graph.bind("excom", "http://example.com/")
    assert (
        len(list(graph.namespaces())) == no_of_default_namespaces + 2
    ), f"expected {no_of_default_namespaces + 2}, got {len(list(graph.namespaces()))}"
    assert ("exorg", URIRef("http://example.org/")) in list(graph.namespaces())


def test_graph_reopening_db(get_graph):
    store, path, graph = get_graph
    graph.add((michel, likes, pizza))
    graph.add((michel, likes, cheese))
    graph.commit()
    graph.store.close()
    graph.store.open(path, create=False)
    ntriples = list(graph.triples((None, None, None)))
    assert len(ntriples) == 5, f"Expected 5 not {len(ntriples)}"


def test_graph_missing_db_returns_no_store(get_graph):
    store, path, graph = get_graph
    graph.store.close()
    if store != "Memory":
        shutil.rmtree(path)
        assert graph.store.open(path, create=False) == NO_STORE


def test_graph_reopening_missing_db_returns_no_store(get_graph):
    store, path, graph = get_graph
    graph.store.close()
    graph.store.destroy(configuration=path)
    if store == "BerkeleyDB":
        assert graph.open(path, create=False) == 1
    elif store == "Memory":
        assert graph.open(path, create=False) == None
    else:
        assert graph.open(path, create=False) == NO_STORE


def test_graph_isopen_db(get_graph):
    store, path, graph = get_graph
    if store != "Memory":
        assert graph.store.is_open() is True
        graph.store.close()
        assert graph.store.is_open() is False


def test_graph_write(get_graph):
    store, path, g = get_graph
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
    ), "There must still be four triples in the graph after the thrd data chunk parse"


def test_graph_read(get_graph):
    store, path, g = get_graph
    sx = None
    for s in g.subjects(
        predicate=URIRef("https://example.org/e"),
        object=URIRef("https://example.org/f"),
    ):
        sx = s
    assert sx == URIRef("https://example.org/d")


def test_graph_sparql_query(get_graph):
    store, path, g = get_graph
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


def test_graph_sparql_insert(get_graph):
    store, path, g = get_graph
    q = """
        PREFIX : <https://example.org/>

        INSERT DATA {
            :x :y :z .
        }"""

    g.update(q)
    assert len(g) == 4, "After extra triple insert, length must be 4"


def test_graph_open_shut(get_graph):
    store, path, g = get_graph
    if store == "Memory":
        pytest.skip("Memory does not open/shut")
    assert len(g) == 3, "Initially we must have 3 triples from setUp"
    g.store.commit()
    g.close()
    strid = g.identifier
    g = None

    # reopen the graph - RE-USING THE IDENTIFIER!!
    g = Graph(store, identifier=strid)

    g.open(path, create=False)
    assert (
        len(g) == 3
    ), "After close and reopen, we should still have the 3 originally added triples"


def test_dataset_namespaces(get_dataset):
    store, path, ds = get_dataset
    no_of_default_namespaces = len(list(ds.namespaces()))
    ds.bind("exorg", "http://example.org/")
    ds.bind("excom", "http://example.com/")
    assert (
        len(list(ds.namespaces())) == no_of_default_namespaces + 2
    ), f"expected {no_of_default_namespaces + 2}, got {len(list(ds.namespaces()))}"
    assert ("exorg", URIRef("http://example.org/")) in list(ds.namespaces())


def test_dataset_triples_context(
    get_dataset,
):

    store, path, ds = get_dataset

    graph = ds.graph(context1)

    graph.add((michel, likes, pizza))
    graph.add((michel, likes, cheese))

    graph.commit()

    triples = list(graph.triples((None, None, None)))
    assert len(triples) == 2, len(triples)


def test_dataset_remove_context_reset(
    get_dataset,
):
    store, path, ds = get_dataset
    graph = ds.graph(identifier=context1)

    graph.add((michel, likes, pizza))
    graph.add((michel, likes, cheese))
    graph.commit()

    triples = list(graph.triples((None, None, None)))

    assert len(triples) == 2, len(triples)

    graph.remove((michel, likes, cheese))
    graph.remove((michel, likes, pizza))

    graph.commit()

    triples = list(graph.triples((None, None, None)))

    assert len(triples) == 0, len(triples)


def test_dataset_nquads_default_graph(
    get_dataset,
):
    data = """
    <http://example.org/s1> <http://example.org/p1> <http://example.org/o1> .
    <http://example.org/s2> <http://example.org/p2> <http://example.org/o2> .
    <http://example.org/s3> <http://example.org/p3> <http://example.org/o3> <http://example.org/g3> .
    """

    publicID = URIRef("http://example.org/g0")

    store, path, ds = get_dataset
    ds.parse(data=data, format="nquads", publicID=publicID)

    assert len(ds) == 3  # 2 in default graph
    assert len(ds.graph(URIRef("http://example.org/g3"))) == 1
    # Two contexts: the publicID and one from the quad
    assert len(list(ds.contexts())) == 2, f"contexts:\n{list(ds.contexts())}"

    assert len(ds.graph(publicID)) == 2  # 2 in publicID


def test_dataset_serialize(get_dataset):
    store, path, ds1 = get_dataset
    ds1.graph(context1).add((bob, likes, pizza))
    ds1.graph(context2).add((bob, likes, pizza))
    s = ds1.serialize(format="nquads")
    assert len([x for x in s.split("\n") if x.strip()]) == 5

    ds2 = Dataset(store=store)
    ds2.open(tempfile.mktemp(prefix="sqlitelsmstoretest"), create=True)
    ds2.parse(data=s, format="nquads")
    assert len(ds1) == len(ds2)
    assert sorted(ds1.contexts()) == sorted(ds2.contexts())


def test_graph_basic(get_dataset):
    store, path, ds = get_dataset

    subgraph1 = ds.graph(context1)
    subgraph2 = ds.graph(context2)

    triple = (bob, likes, michel)

    assert subgraph1.identifier == context1

    if store != "Memory":
        assert ds.store.is_open()

    subgraph1.add(triple)

    assert len(subgraph1) == 1

    ds.store.add_graph(context1)

    assert len(list(ds.triples(triple, context=context1))) == 1

    assert len(list(ds.triples(triple, context=ds.identifier))) == 0

    assert (
        str(list(ds.store.contexts(triple)))
        == "[rdflib.term.URIRef('urn:example:context-1')]"
    )

    assert (
        str(
            list(
                ds.store.contexts(
                    (
                        URIRef("urn:example:harry"),
                        URIRef("urn:example:likes"),
                        URIRef("urn:example:sally"),
                    )
                )
            )
        )
        == "[]"  # Trigger KeyError for coverage
    )

    assert ds.store.__len__(context=context1) == 1

    assert ds.store.__len__(context=None) == 4

    assert len(list(ds.store.contexts(triple))) == 1

    ds.store.remove(triple, context1)

    ds.store.remove((None, None, None), context1)

    ds.store.remove((None, None, None), context1)

    ds.store.remove((None, None, None), URIRef("urn:example:context-2"))

    dsc = list(ds.contexts())

    if store == "Memory":
        assert len(list(ds.contexts())) == 2
    else:
        assert len(list(ds.contexts())) == 0

    subgraph1.add((michel, likes, cheese))
    subgraph1.add((bob, likes, cheese))

    ds.store.remove_graph(context1)

    if store == "Memory":
        assert len(list(ds.store.contexts())) == 2
    else:
        assert len(list(ds.store.contexts())) == 1

    if store == "Memory":
        assert len(list(ds.contexts())) == 1
    else:
        assert len(list(ds.contexts())) == 0

    ds.store.add_graph(context2)

    ds.store.add(triple, context2)

    ds.store.add(
        (michel, likes, bob),
        context2,
        True,
    )

    assert len(list(ds.contexts())) == 1

    ds.remove((None, None, None))

    ds.store.remove_graph(ds.store.identifier)

    if hasattr(ds.store, "unbind"):
        nnamespaces = len(list(ds.store.namespaces()))
        ds.store.bind("ex", URIRef("urn:exemplar:"))
        assert len(list(ds.store.namespaces())) == nnamespaces + 1
        ds.store.unbind("ex")
        assert len(list(ds.store.namespaces())) == nnamespaces

    ds.parse(data=timblcardn3, format="n3")
    assert len(ds) == 86


    ds.remove((None, None, None, DATASET_DEFAULT_GRAPH_ID))
    assert len(ds) == 0

