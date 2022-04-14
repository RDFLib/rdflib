# -*- coding: utf-8 -*-
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
    tarek,
)

import pytest

from rdflib import URIRef, plugin
from rdflib.graph import Dataset, Graph, Literal
from rdflib.store import VALID_STORE, NO_STORE
from test.pluginstores import (
    HOST,
    root,
    get_plugin_stores,
    set_store_and_path,
    open_store,
    cleanup,
    dburis,
)

timblcardn3 = open(os.path.join(CONSISTENT_DATA_DIR, "timbl-card.n3")).read()


@pytest.fixture(
    scope="function",
    params=get_plugin_stores(),
)
def get_config(request):
    storename = request.param

    store, path = set_store_and_path(storename)

    yield store, path


def test_create(get_config):
    store, path = get_config

    g = Graph(store, URIRef("http://rdflib.net"))

    if store != "Memory":
        rt = g.open(path, create=True)
        assert rt == VALID_STORE, "The underlying store is corrupt"

    assert g.identifier == URIRef('http://rdflib.net')
    assert str(g).startswith(
        f"<http://rdflib.net> a rdfg:Graph;rdflib:storage [a rdflib:Store;rdfs:label '{store}"
    )
    g.close()
    if store != "Memory":
        g.destroy(configuration=path)


def test_reuse(get_config):
    store, path = get_config

    if store == "Memory":
        pytest.skip(reason="Skipping test of Memory")

    g = Graph(store, URIRef("http://rdflib.net"))
    rt = g.open(path, create=True)
    assert rt == VALID_STORE, "The underlying store is corrupt"
    assert g.identifier == URIRef('http://rdflib.net')
    assert str(g).startswith(
        f"<http://rdflib.net> a rdfg:Graph;rdflib:storage [a rdflib:Store;rdfs:label '{store}"
    )
    g.parse(data=timblcardn3, format="n3")
    assert len(g) == 86
    g.close()

    del g

    g = Graph(store, URIRef("http://rdflib.net"))
    g.open(path, create=False)
    assert g.identifier == URIRef('http://rdflib.net')
    assert str(g).startswith(
        f"<http://rdflib.net> a rdfg:Graph;rdflib:storage [a rdflib:Store;rdfs:label '{store}"
    )

    assert len(g) == 86

    g.close()
    g.destroy(configuration=path)


def test_example(get_config):
    store, path = get_config
    g = Graph(store, URIRef("http://rdflib.net"))
    rt = g.open(path, create=True)
    if store != "Memory":
        assert rt == VALID_STORE, "The underlying store is corrupt"
    # Parse in an RDF file hosted locally
    g.parse(data=timblcardn3, format="n3")

    # Loop through each triple in the graph (subj, pred, obj)
    for subj, pred, obj in g:
        # Check if there is at least one triple in the Graph
        if (subj, pred, obj) not in g:
            raise Exception("It better be!")

    assert len(g) == 86, len(g)

    # Print out the entire Graph in the RDF Turtle format
    # print(g.serialize(format="turtle"))
    if hasattr(g.store, "dumpdb"):
        assert "timbl-image-by-Coz-cropped.jpg" in g.store.dumpdb()

    g.close()
    if store != "Memory":
        g.destroy(configuration=path)


def test_graph_reopen_missing(get_config):
    store, path = get_config
    if store != "Memory":
        g = Dataset(store, URIRef("http://rdflib.net"))
        assert g.store.open("DOESNT EXIST", create=False) is NO_STORE


def test_store_graph_readable_index(get_config):
    store, path = get_config
    if store == "BerkeleyDB":
        from rdflib.plugins.stores.berkeleydb import readable_index
    elif store == "Shelving":
        from rdflib.plugins.stores.shelving import readable_index
    elif store == "SQLiteDBStore":
        from rdflib.plugins.stores.sqlitedbstore import readable_index
    else:
        pytest.skip("Store does not have readable_index")

    assert readable_index(1) == "s,?,?"
    assert readable_index(11) == "s,p,?"
    assert readable_index(111) == "s,p,o"
    assert readable_index(2) == "?,p,?"
    assert readable_index(3) == "s,p,?"
    assert readable_index(4) == "?,?,o"


def test_store_open_nonexistent(get_config):
    storename, path = get_config

    if storename == "BerkeleyDB":
        from rdflib.plugins.stores.berkeleydb import BerkeleyDB

        store = BerkeleyDB(path, URIRef("http://rdflib.net"))
    elif storename == "SQLiteDBStore":
        from rdflib.plugins.stores.sqlitedbstore import SQLiteDBStore

        store = SQLiteDBStore(path, URIRef("http://rdflib.net"))
    elif storename == "Shelving":
        from rdflib.plugins.stores.shelving import Shelving

        store = Shelving(path, URIRef("http://rdflib.net"))
    else:
        pytest.skip(f"test_store_basic skipped for '{storename}', not yet handled.")

    with pytest.raises(Exception):
        assert store.open("DOESNT EXIST", create=False) is VALID_STORE


def test_store_basic(get_config):
    storename, path = get_config

    if storename == "BerkeleyDB":
        from rdflib.plugins.stores.berkeleydb import BerkeleyDB

        store = BerkeleyDB(path, URIRef("http://rdflib.net"))
    elif storename == "SQLiteDBStore":
        from rdflib.plugins.stores.sqlitedbstore import SQLiteDBStore

        store = SQLiteDBStore(path, URIRef("http://rdflib.net"))
    elif storename == "Shelving":
        from rdflib.plugins.stores.shelving import Shelving

        store = Shelving(path, URIRef("http://rdflib.net"))
    else:
        pytest.skip(f"test_store_basic skipped for '{storename}', not yet handled.")

    store.open(path, create=True)

    assert store.identifier == URIRef("http://rdflib.net")

    try:
        store.open(path, create=True)
    except Exception:
        pass

    subgraph1 = Graph(store=store, identifier=context1)
    subgraph2 = Graph(store=store, identifier=context2)

    assert subgraph1.identifier == context1

    assert store.is_open()

    triple = (bob, likes, michel)

    subgraph1.add(triple)

    assert len(subgraph1) == 1
    assert len(list(store.contexts())) == 1

    with pytest.raises(TypeError):
        store.add_graph(subgraph1)

    with pytest.raises(TypeError):
        store.add_graph(None)

    store.add_graph(context1)

    assert len(list(store.contexts())) == 1

    store_contexts = list(store.contexts())
    assert str(store_contexts) == "[rdflib.term.URIRef('urn:example:context-1')]"

    store.add_graph(context2)
    assert len(list(store.contexts())) == 2

    assert sorted(list(store.contexts())) == [context1, context2]

    assert store.__len__(context=context1) == 1
    assert store.__len__(context=context2) == 0

    with pytest.raises(AssertionError):
        assert len(list(store.triples(triple, context=subgraph1))) == 1

    with pytest.raises(AssertionError):
        assert len(list(store.triples(triple, context=store.identifier))) == 1

    with pytest.raises(AssertionError):
        assert (
            str(list(store.contexts(triple)))
            == "[<Graph identifier=urn:example:context-1 (<class 'rdflib.graph.Graph'>)>]"
        )

    triple2 = (tarek, likes, cheese)

    subgraph2.add(triple2)

    assert len(subgraph2) == 1

    assert subgraph2.identifier == context2

    store.add(triple, store.identifier)

    assert store.__len__(context=subgraph2.identifier) == 1
    assert store.__len__(context=store.identifier) == 1

    storelen = store.__len__(context=None)

    assert storelen == 2

    assert len(list(store.contexts(triple))) == 2

    store.remove_graph(context2)

    assert len(list(store.contexts())) == 2

    store.remove_graph(context1)

    assert len(list(store.contexts())) == 1

    store.add_graph(context2)

    store.add(triple, context2)

    store.add(
        (michel, likes, bob),
        context2,
        True,
    )

    assert len(list(store.contexts())) == 2

    store.remove((None, None, None), context1)

    store.remove_graph(store.identifier)

    with pytest.raises(Exception):
        store._from_string("99")

    if hasattr(store, "unbind"):
        nnamespaces = len(list(store.namespaces()))
        store.bind("ex", URIRef("urn:exemplar:"))
        assert len(list(store.namespaces())) == nnamespaces + 1
        store.unbind("ex")
        assert len(list(store.namespaces())) == nnamespaces

    store.remove((None, None, None), URIRef("urn:example:context-3"))

    store.close()
    store.destroy(configuration=path)

    tmpdir = tempfile.mkdtemp()
    store.open(tmpdir, True)
    g = Graph(store=store)
    g.parse(data=timblcardn3, format="n3")
    g.remove(
        (
            URIRef("http://www.w3.org/2011/Talks/0331-hyderabad-tbl/data#talk"),
            URIRef("http://purl.org/dc/terms/title"),
            Literal("Designing the Web for an Open Society"),
        )
    )
    store.close()
    store.destroy(configuration=tmpdir)
