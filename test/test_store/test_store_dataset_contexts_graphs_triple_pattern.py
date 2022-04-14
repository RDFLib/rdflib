import os
import shutil
import tempfile
from test.data import tarek, likes, pizza, michel, hates, cheese, bob, context0, context1, context2
from urllib.request import urlopen

import pytest

from rdflib import logger
from rdflib.graph import Dataset
from rdflib.store import VALID_STORE
from rdflib.term import URIRef
from test.pluginstores import HOST, root, get_plugin_stores, set_store_and_path, open_store, cleanup, dburis

try:
    assert len(urlopen(HOST).read()) > 0
    skipsparql = False
except:
    skipsparql = True

skipsparql = True

@pytest.fixture(
    scope="function",
    params=get_plugin_stores(),
)
def get_dataset(request):
    storename = request.param

    store, path = set_store_and_path(storename)

    dataset = Dataset(store=store, identifier=URIRef("urn:example:testgraph"))

    ds = open_store(dataset, storename, path)

    yield dataset

    cleanup(dataset, storename, path)


@pytest.fixture(
    scope="function",
    params=get_plugin_stores(),
)
def get_dataset_defaultunion(request):
    storename = request.param

    store, path = set_store_and_path(storename)

    dataset = Dataset(store=store, identifier=URIRef("urn:example:testgraph"), default_union=True)

    ds = open_store(dataset, storename, path)

    yield dataset

    cleanup(dataset, storename, path)



def test_dataset_graphs_with_triple_pattern(get_dataset):
    ds = get_dataset

    store = ds.store

    ds.add((tarek, likes, pizza))

    g1 = ds.graph(context1)
    g1.add((tarek, likes, cheese))
    g1.add((michel, likes, tarek))

    g2 = ds.graph(context2)
    g2.add((michel, likes, cheese))
    g2.add((michel, likes, pizza))

    assert len(list(ds.graphs((michel, likes, cheese)))) == 1  # Is only in one graph

    assert (
        str(list(ds.graphs((michel, likes, cheese))))
        == "[<Graph identifier=urn:example:context-2 (<class 'rdflib.graph.Graph'>)>]"
    )

    if "LevelDBStore" in str(store):
        assert len(list(ds.graphs((michel, likes, None)))) == 0  # Should yield two graphs
    else:
        assert len(list(ds.graphs((michel, likes, None)))) == 2  # Should yield two graphs

    if "LevelDBStore" in str(store):
        assert len(list(ds.graphs((tarek, None, None)))) == 0  # Should yield one graph
    elif "OxigraphStore" in str(store):
        assert len(list(ds.graphs((tarek, None, None)))) == 2  # Should yield one graph
    else:
        assert len(list(ds.graphs((tarek, None, None)))) == 1  # Should yield one graph

    if "LevelDBStore" in str(store):
        assert len(list(ds.graphs((None, likes, None)))) == 0  # Should yield two graphs
    elif "OxigraphStore" in str(store):
        assert len(list(ds.graphs((None, likes, None)))) == 3  # Should yield two graphs
    else:
        assert len(list(ds.graphs((None, likes, None)))) == 2  # Should yield two graphs


    if "LevelDBStore" in str(store):
        assert len(list(ds.graphs((None, None, pizza)))) == 0  # Should yield two graphs
    elif "OxigraphStore" in str(store):
        assert len(list(ds.graphs((None, None, pizza)))) == 2  # Should yield two graphs
    else:
        assert len(list(ds.graphs((None, None, pizza)))) == 1  # Should yield two graphs

    if "LevelDBStore" in str(store):
        assert len(list(ds.graphs((None, None, None)))) == 0  # Should yield both graphs
    elif "OxigraphStore" in str(store):
        assert len(list(ds.graphs((None, None, None)))) == 3  # Should yield both graphs
    else:
        assert len(list(ds.graphs((None, None, None)))) == 2  # Should yield both graphs


def test_dataset_contexts_with_triple_pattern(get_dataset):
    ds = get_dataset

    ds.add((tarek, likes, pizza))

    g1 = ds.graph(context1)
    g1.add((tarek, likes, cheese))
    g1.add((michel, likes, tarek))

    g2 = ds.graph(context2)
    g2.add((michel, likes, cheese))
    g2.add((michel, likes, pizza))

    store = ds.store

    assert len(list(ds.contexts((michel, likes, cheese)))) == 1  # Is only in one graph

    assert (
        str(list(ds.contexts((michel, likes, cheese))))
        == "[rdflib.term.URIRef('urn:example:context-2')]"
    )

    if "LevelDBStore" in str(store):
        assert (
            len(list(ds.contexts((michel, likes, None)))) == 0
        )  # Should yield two contextss
    else:
        assert (
            len(list(ds.contexts((michel, likes, None)))) == 2
        )  # Should yield two contextss

    if "LevelDBStore" in str(store):
        assert len(list(ds.contexts((tarek, None, None)))) == 0  # Should yield one context
    elif "OxigraphStore" in str(store):
        assert len(list(ds.contexts((tarek, None, None)))) == 2  # Should yield one context
    else:
        assert len(list(ds.contexts((tarek, None, None)))) == 1  # Should yield one context

    if "LevelDBStore" in str(store):
        assert len(list(ds.contexts((None, likes, None)))) == 0  # Should yield two contexts
    elif "OxigraphStore" in str(store):
        assert len(list(ds.contexts((None, likes, None)))) == 3  # Should yield two contexts
    else:
        assert len(list(ds.contexts((None, likes, None)))) == 2  # Should yield two contexts

    if "LevelDBStore" in str(store):
        assert len(list(ds.contexts((None, None, pizza)))) == 0  # Should yield one context
    elif "OxigraphStore" in str(store):
        assert len(list(ds.contexts((None, None, pizza)))) == 2  # Should yield one context
    else:
        assert len(list(ds.contexts((None, None, pizza)))) == 1  # Should yield one context

    if "LevelDBStore" in str(store):
        assert len(list(ds.contexts((None, None, None)))) == 0  # Should yield both contexts
    elif "OxigraphStore" in str(store):
        assert len(list(ds.contexts((None, None, None)))) == 3  # Should yield both contexts
    else:
        assert len(list(ds.contexts((None, None, None)))) == 2  # Should yield both contexts
