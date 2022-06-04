# -*- coding: utf-8 -*-
import os
import shutil
import tempfile
from test.data import context1, likes, pizza, tarek

import pytest

from rdflib import URIRef, plugin
from rdflib.graph import DATASET_DEFAULT_GRAPH_ID, Dataset, Graph, Namespace

# Will also run SPARQLUpdateStore tests against local SPARQL1.1 endpoint if
# available. This assumes SPARQL1.1 query/update endpoints running locally at
# http://localhost:3030/db/
#
# Testing SPARQLUpdateStore Dataset behavior needs a different endpoint behavior
# than our ConjunctiveGraph tests in test_sparqlupdatestore.py!
#
# For the tests here to run, you can for example start fuseki with:
# ./fuseki-server --mem --update /db

# THIS WILL DELETE ALL DATA IN THE /db dataset

HOST = "http://localhost:3030"
DB = "/db/"

pluginstores = []

for s in plugin.plugins(None, plugin.Store):
    if s.name in ("Memory", "Auditable", "Concurrent", "SPARQLStore"):
        continue  # these are tested by default

    if not s.getClass().graph_aware:
        continue

    if s.name == "SPARQLUpdateStore":
        from urllib.request import urlopen

        try:
            assert len(urlopen(HOST).read()) > 0
        except Exception:
            continue

    pluginstores.append(s.name)


@pytest.fixture(
    scope="function",
    params=pluginstores,
)
def get_dataset(request):
    store = request.param

    try:
        dataset = Dataset(store=store)
    except ImportError:
        pytest.skip("Dependencies for store '%s' not available!" % store)

    graph = Dataset(store=store)

    if not graph.store.graph_aware:
        return

    if store in ["SQLiteLSM", "LevelDB"]:
        path = os.path.join(tempfile.gettempdir(), f"test_{store.lower()}")
        try:
            shutil.rmtree(path)
        except Exception:
            pass
    elif store == "SPARQLUpdateStore":
        root = HOST + DB
        path = root + "sparql", root + "update"
    else:
        path = tempfile.mkdtemp()

    graph.open(path, create=True if store != "SPARQLUpdateStore" else False)

    if store == "SPARQLUpdateStore":
        try:
            graph.store.update("CLEAR ALL")
        except Exception as e:
            if "SPARQLStore does not support BNodes! " in str(e):
                pass
            else:
                raise Exception(e)

    yield store, graph

    if store == "SPARQLUpdateStore":
        try:
            graph.store.update("CLEAR ALL")
        except Exception as e:
            if "SPARQLStore does not support BNodes! " in str(e):
                pass
            else:
                raise Exception(e)
        graph.close()
    else:
        graph.close()
        graph.destroy(path)
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            try:
                os.remove(path)
            except:
                pass


def test_graph_aware(get_dataset):

    store, dataset = get_dataset

    if not dataset.store.graph_aware:
        return

    g1 = dataset.graph(context1)

    # Some SPARQL endpoint backends (e.g. TDB) do not consider
    # empty named graphs
    if store != "SPARQLUpdateStore":
        # added graph exists
        assert set(x.identifier for x in dataset.contexts()) == set(
            [context1, DATASET_DEFAULT_GRAPH_ID]
        )

    # added graph is empty
    assert len(g1) == 0

    g1.add((tarek, likes, pizza))

    # added graph still exists
    assert set(x.identifier for x in dataset.contexts()) == set(
        [context1, DATASET_DEFAULT_GRAPH_ID]
    )

    # added graph contains one triple
    assert len(g1) == 1

    g1.remove((tarek, likes, pizza))

    # added graph is empty
    assert len(g1) == 0

    # Some SPARQL endpoint backends (e.g. TDB) do not consider
    # empty named graphs
    if store != "SPARQLUpdateStore":
        # graph still exists, although empty
        assert set(x.identifier for x in dataset.contexts()) == set(
            [context1, DATASET_DEFAULT_GRAPH_ID]
        )

    dataset.remove_graph(context1)

    # graph is gone
    assert set(x.identifier for x in dataset.contexts()) == set(
        [DATASET_DEFAULT_GRAPH_ID]
    )


def test_default_graph(get_dataset):
    # Something the default graph is read-only (e.g. TDB in union mode)

    store, dataset = get_dataset

    if store == "SPARQLUpdateStore":
        print(
            "Please make sure updating the default graph "
            "is supported by your SPARQL endpoint"
        )

    dataset.add((tarek, likes, pizza))
    assert len(dataset) == 1
    # only default exists
    assert list(dataset.contexts()) == [dataset.default_context]

    # removing default graph removes triples but not actual graph
    dataset.remove_graph(DATASET_DEFAULT_GRAPH_ID)

    assert len(dataset) == 0

    # default still exists
    assert set(dataset.contexts()) == set([dataset.default_context])


def test_not_union(get_dataset):

    store, dataset = get_dataset
    # Union depends on the SPARQL endpoint configuration
    if store == "SPARQLUpdateStore":
        print(
            "Please make sure your SPARQL endpoint has not configured "
            "its default graph as the union of the named graphs"
        )

    subgraph1 = dataset.graph(context1)
    subgraph1.add((tarek, likes, pizza))

    assert list(dataset.objects(tarek, None)) == []
    assert list(subgraph1.objects(tarek, None)) == [pizza]


def test_iter(get_dataset):

    store, d = get_dataset
    """PR 1382: adds __iter__ to Dataset"""
    uri_a = URIRef("https://example.com/a")
    uri_b = URIRef("https://example.com/b")
    uri_c = URIRef("https://example.com/c")
    uri_d = URIRef("https://example.com/d")

    d.graph(URIRef("https://example.com/subgraph1"))
    d.add((uri_a, uri_b, uri_c, URIRef("https://example.com/subgraph1")))

    d.add(
        (uri_a, uri_b, uri_c, URIRef("https://example.com/subgraph1"))
    )  # pointless addition: duplicates above

    d.graph(URIRef("https://example.com/g2"))
    d.add((uri_a, uri_b, uri_c, URIRef("https://example.com/g2")))
    d.add((uri_a, uri_b, uri_d, URIRef("https://example.com/subgraph1")))

    # traditional iterator
    i_trad = 0
    for t in d.quads((None, None, None)):
        i_trad += 1

    # new Dataset.__iter__ iterator
    i_new = 0
    for t in d:
        i_new += 1

    assert i_new == i_trad  # both should be 3


EGSCHEMA = Namespace("example:")


def test_subgraph_without_identifier() -> None:
    """
    Graphs with no identifies assigned are identified by Skolem IRIs with a
    prefix that is bound to `genid`.

    TODO: This is somewhat questionable and arbitrary behaviour and should be
    reviewed at some point.
    """

    dataset = Dataset()

    nman = dataset.namespace_manager

    genid_prefix = URIRef("https://rdflib.github.io/.well-known/genid/rdflib/")

    namespaces = set(nman.namespaces())
    assert (
        next((namespace for namespace in namespaces if namespace[0] == "genid"), None)
        is None
    )

    subgraph: Graph = dataset.graph()
    subgraph.add((EGSCHEMA["subject"], EGSCHEMA["predicate"], EGSCHEMA["object"]))

    namespaces = set(nman.namespaces())
    assert next(
        (namespace for namespace in namespaces if namespace[0] == "genid"), None
    ) == ("genid", genid_prefix)

    assert f"{subgraph.identifier}".startswith(genid_prefix)
