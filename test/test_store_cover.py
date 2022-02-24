# -*- coding: utf-8 -*-
import os
import shutil
import tempfile

import pytest

from rdflib import URIRef, plugin
from rdflib.graph import ConjunctiveGraph, Graph, Literal
from rdflib.store import VALID_STORE
from rdflib.plugins.stores.sqlitedbstore import (
    SQLhash,
    SQLhashItemsView,
    SQLhashValuesView,
    SQLhashKeysView,
    open as sqlhashopen,
    ListRepr,
)

timblcardn3 = open(
    os.path.join(
        os.path.dirname(__file__),
        "consistent_test_data",
        "timbl-card.n3",
    )
).read()

michel = URIRef("urn:example:michel")
tarek = URIRef("urn:example:tarek")
bob = URIRef("urn:example:bob")
likes = URIRef("urn:example:likes")
hates = URIRef("urn:example:hates")
pizza = URIRef("urn:example:pizza")
cheese = URIRef("urn:cheese")

# Use regular URIs because SPARQL endpoints like Fuseki alter short names
context1 = URIRef("urn:example:context-1")
context2 = URIRef("urn:example:context-2")

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
        graph = Graph(store=s.name)
        pluginstores.append(s.name)
    except ImportError:
        pass


@pytest.fixture(
    scope="function",
    params=pluginstores,
)
def get_graph(request):
    store = request.param
    path = tempfile.mktemp()
    try:
        shutil.rmtree(path)
    except Exception:
        pass

    yield store, path


def test_create(get_graph):
    store, path = get_graph

    g = Graph(store, URIRef("http://rdflib.net"))
    rt = g.open(path, create=True)
    assert rt == VALID_STORE, "The underlying store is corrupt"

    assert g.identifier == URIRef('http://rdflib.net')
    assert str(g).startswith(f"<http://rdflib.net> a rdfg:Graph;rdflib:storage [a rdflib:Store;rdfs:label '{store}")
    g.close()
    g.destroy(configuration=path)


def test_reuse(get_graph):
    store, path = get_graph
    g = Graph(store, URIRef("http://rdflib.net"))
    rt = g.open(path, create=True)
    assert rt == VALID_STORE, "The underlying store is corrupt"
    assert g.identifier == URIRef('http://rdflib.net')
    assert str(g).startswith(f"<http://rdflib.net> a rdfg:Graph;rdflib:storage [a rdflib:Store;rdfs:label '{store}")
    g.parse(data=timblcardn3, format="n3")
    assert len(g) == 86
    g.close()

    del g

    g = Graph(store, URIRef("http://rdflib.net"))
    g.open(path, create=False)
    assert g.identifier == URIRef('http://rdflib.net')
    assert str(g).startswith(f"<http://rdflib.net> a rdfg:Graph;rdflib:storage [a rdflib:Store;rdfs:label '{store}")

    assert len(g) == 86

    g.close()
    g.destroy(configuration=path)


def test_example(get_graph):
    store, path = get_graph
    g = Graph(store, URIRef("http://rdflib.net"))
    rt = g.open(path, create=True)
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
    g.destroy(configuration=path)


def test_graph_basic(get_graph):
    store, path = get_graph
    g = ConjunctiveGraph(store, URIRef("http://rdflib.net"))
    rt = g.open(path, create=True)
    assert rt == VALID_STORE, "The underlying store is corrupt"

    assert g.identifier == URIRef("http://rdflib.net")

    try:
        g.open(path, create=True)
    except Exception:
        pass
    with pytest.raises(AssertionError):
        assert g.store.open("DOESNT EXIST", create=False) is VALID_STORE

    context1 = URIRef("urn:example:context-1")
    context2 = URIRef("urn:example:context-2")

    subgraph1 = g.get_context(context1)
    subgraph2 = g.get_context(context2)

    triple = (
        URIRef("urn:example:bob"),
        URIRef("urn:example:likes"),
        URIRef("urn:example:michel"),
    )

    assert subgraph1.identifier == context1

    assert g.store.is_open()

    subgraph1.add(triple)

    assert len(subgraph1) == 1

    g.store.add_graph(subgraph1)

    assert len(list(g.triples(triple, context=context1))) == 1

    assert len(list(g.triples(triple, context=g.identifier))) == 1

    assert (
        str(list(g.store.contexts(triple)))
        == "[<Graph identifier=urn:example:context-1 (<class 'rdflib.graph.Graph'>)>]"
    )

    assert (
        str(
            list(
                g.store.contexts(
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

    assert g.store.__len__(context=context1) == 0

    assert g.store.__len__(context=g.store) == 1

    assert len(list(g.store.contexts(triple))) == 1

    g.store.remove(triple, context1)

    g.store.remove((None, None, None), context1)

    g.store.remove((None, None, None), context1)

    g.store.remove((None, None, None), URIRef("urn:example:context-2"))

    assert len(list(g.contexts())) == 1

    # g.store.remove_graph(subgraph1 if store == "BerkeleyDB" else context1)

    subgraph1.add((michel, likes, cheese))
    subgraph1.add((bob, likes, cheese))

    g.store.remove_graph(subgraph1)

    assert len(list(g.store.contexts())) == 0

    assert len(list(g.contexts())) == 0

    g.store.add_graph(subgraph2)

    g.store.add(triple, subgraph2)

    g.store.add(
        (
            URIRef("urn:example:michel"),
            URIRef("urn:example:likes"),
            URIRef("urn:example:bob"),
        ),
        subgraph2,
        True,
    )

    assert len(list(g.contexts())) == 1

    g.remove((None, None, None))

    g.store.remove_graph(g.store)

    if hasattr(g.store, "unbind"):
        nnamespaces = len(list(g.store.namespaces()))
        g.store.bind("ex", URIRef("urn:exemplar:"))
        assert len(list(g.store.namespaces())) == nnamespaces + 1
        g.store.unbind("ex")
        assert len(list(g.store.namespaces())) == nnamespaces

    g.parse(data=timblcardn3, format="n3")
    g.remove((None, None, None, g.identifier))

    g.close()
    g.destroy(configuration=path)


def test_store_graph_readable_index(get_graph):
    storename, path = get_graph
    if storename == "SQLiteDB":
        from rdflib.plugins.stores.sqlitedb import readable_index
    elif storename == "BerkeleyDB":
        from rdflib.plugins.stores.berkeleydb import readable_index
    else:
        pytest.skip("Store does not have readable_index")

    assert readable_index(1) == "s,?,?"
    assert readable_index(11) == "s,p,?"
    assert readable_index(111) == "s,p,o"
    assert readable_index(2) == "?,p,?"
    assert readable_index(3) == "s,p,?"
    assert readable_index(4) == "?,?,o"


def test_store_basic(get_graph):
    storename, path = get_graph

    if storename == "SQLiteDBStore":
        from rdflib.plugins.stores.sqlitedbstore import SQLiteDBStore

        store = SQLiteDBStore(path, URIRef("http://rdflib.net"))

    elif storename == "BerkeleyDB":
        from rdflib.plugins.stores.berkeleydb import BerkeleyDB

        store = BerkeleyDB(path, URIRef("http://rdflib.net"))
    else:
        pytest.skip(f"test_store_basic skipped for '{storename}', not yet handled.")

    store.open(path, create=True)

    assert store.identifier == URIRef("http://rdflib.net")

    try:
        store.open(path, create=True)
    except Exception:
        pass
    with pytest.raises(AssertionError):
        assert store.open("DOESNT EXIST", create=False) is VALID_STORE

    context1 = URIRef("urn:example:context-1")
    context2 = URIRef("urn:example:context-2")

    subgraph1 = Graph(identifier=context1)
    subgraph2 = Graph(identifier=context2)

    triple = (
        URIRef("urn:example:bob"),
        URIRef("urn:example:likes"),
        URIRef("urn:example:michel"),
    )

    assert subgraph1.identifier == context1

    assert store.is_open()

    subgraph1.add(triple)

    assert len(subgraph1) == 1

    assert len(list(store.contexts())) == 0

    store.add_graph(subgraph1)
    assert len(list(store.contexts())) == 1
    store.add_graph(subgraph2)
    assert len(list(store.contexts())) == 2

    assert store.__len__(context=context1) == 0

    assert store.__len__(context=context1) == 0
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

    assert store.__len__(context=context1) == 0

    assert store.__len__(context=store.identifier) == 0

    assert len(list(store.contexts(triple))) == 0

    store.remove_graph(context2)

    assert len(list(store.contexts())) == 2

    store.remove_graph(subgraph1)

    assert len(list(store.contexts())) == 1

    store.add_graph(subgraph2)

    store.add(triple, context2)

    store.add(
        (
            URIRef("urn:example:michel"),
            URIRef("urn:example:likes"),
            URIRef("urn:example:bob"),
        ),
        context2,
        True,
    )

    assert len(list(store.contexts())) == 2

    store.remove((None, None, None), context1)

    store.remove_graph(store)

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
    store.sync()
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
