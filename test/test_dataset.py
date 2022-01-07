import sys
import os
from typing import Optional
import pytest

import tempfile
import shutil

from rdflib import Dataset, Graph, URIRef, plugin
from rdflib.graph import DATASET_DEFAULT_GRAPH_ID
from rdflib.store import VALID_STORE
from rdflib.plugins.stores.sparqlstore import SPARQLUpdateStore

michel = URIRef("urn:example:michel")
tarek = URIRef("urn:example:tarek")
bob = URIRef("urn:example:bob")
likes = URIRef("urn:example:likes")
hates = URIRef("urn:example:hates")
pizza = URIRef("urn:example:pizza")
cheese = URIRef("urn:example:cheese")

c1 = URIRef("urn:example:context-1")
c2 = URIRef("urn:example:context-2")


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

HOST = "http://localhost:3031"
DB = "/db/"

# dynamically create classes for each registered Store

pluginstores = ["default"]

for s in plugin.plugins(None, plugin.Store):
    skip_reason: Optional[str] = None
    if s.name in ("default", "Memory", "Auditable", "Concurrent", "SPARQLStore"):
        continue  # these are tested by default

    if not s.getClass().graph_aware:
        continue

    if s.name == "SPARQLUpdateStore":
        from urllib.request import urlopen

        try:
            assert len(urlopen(HOST).read()) > 0
        except BaseException:
            skip_reason = "No SPARQL endpoint for %s (tests skipped)\n" % s.name
            sys.stderr.write(skip_reason)
            continue

    pluginstores.append(s.name)


@pytest.fixture(
    scope="function",
    params=pluginstores,
)
def get_dataset(request):
    store = request.param
    path = os.path.join(tempfile.gettempdir(), f"test_{store.lower()}")

    try:
        shutil.rmtree(path)
    except Exception:
        pass

    try:
        dataset = Dataset(store=store)
    except ImportError:
        pytest.skip("Dependencies for store '%s' not available!" % store)

    if store == "SPARQLUpdateStore":
        root = HOST + DB
        dataset.open((root + "sparql", root + "update"))
    elif store != "default":
        rt = dataset.open(configuration=path, create=True)
        assert rt == VALID_STORE, "The underlying store is corrupt"

    assert (
        len(dataset) == 0 if store != "SPARQLUpdateStore" else 1
    ), "There must be zero triples in the graph just after store (file) creation"

    # delete the graph for each test!
    dataset.remove((None, None, None))
    for c in dataset.graphs():
        c.remove((None, None, None))
        assert len(c) == 0
        dataset.remove_graph(c)

    yield dataset

    if store != "SPARQLUpdateStore":
        dataset.close()
        dataset.destroy(configuration=path)
    else:
        dataset.remove((None, None, None))
        for c in dataset.graphs():
            c.remove((None, None, None))
            assert len(c) == 0
            dataset.remove_graph(c)
        dataset.close()


def test_graph_aware(get_dataset):

    dataset = get_dataset

    if not dataset.store.graph_aware:
        return

    g1 = dataset.graph(c1)

    # Some SPARQL endpoint backends (e.g. TDB) do not consider
    # empty named graphs
    if type(dataset.store) is not SPARQLUpdateStore:
        # added graph exists
        assert set(
            x.identifier if isinstance(x, Graph) else x for x in dataset.graphs()
        ) == set([c1, DATASET_DEFAULT_GRAPH_ID])

    # added graph is empty
    assert len(g1) == 0

    g1.add((tarek, likes, pizza))

    # added graph still exists
    assert set(
        x.identifier if isinstance(x, Graph) else x for x in dataset.graphs()
    ) == set([c1, DATASET_DEFAULT_GRAPH_ID])

    # added graph contains one triple
    assert len(g1) == 1

    g1.remove((tarek, likes, pizza))

    # added graph is empty
    assert len(g1) == 0

    # Some SPARQL endpoint backends (e.g. TDB) do not consider
    # empty named graphs
    if type(dataset.store) is not SPARQLUpdateStore:
        # graph still exists, although empty
        assert set(
            x.identifier if isinstance(x, Graph) else x for x in dataset.graphs()
        ), set([c1, DATASET_DEFAULT_GRAPH_ID])

    dataset.remove_graph(c1)

    # graph is gone
    assert set(
        x.identifier if isinstance(x, Graph) else x for x in dataset.graphs()
    ) == set([DATASET_DEFAULT_GRAPH_ID])


def test_default_graph(get_dataset):

    dataset = get_dataset

    # Sometimes the default graph is read-only (e.g. TDB in union mode)
    if type(dataset.store) is SPARQLUpdateStore:
        print(
            "Please make sure updating the default graph "
            "is supported by your SPARQL endpoint"
        )

    dataset.add((tarek, likes, pizza))

    if type(dataset.store) is SPARQLUpdateStore:
        try:
            assert len(dataset) == 1
        except Exception:
            pass
    else:
        assert len(dataset) == 1

    # only default exists
    assert set(
        x.identifier if isinstance(x, Graph) else x for x in dataset.graphs()
    ), set([DATASET_DEFAULT_GRAPH_ID])

    # removing default graph removes triples but not actual graph
    dataset.remove_graph(DATASET_DEFAULT_GRAPH_ID)

    assert len(dataset) == 0 if type(dataset.store) is not SPARQLUpdateStore else 1

    # default still exists
    assert set(
        x.identifier if isinstance(x, Graph) else x for x in dataset.graphs()
    ) == set([DATASET_DEFAULT_GRAPH_ID])


def test_not_union(get_dataset):

    dataset = get_dataset

    # Union depends on the SPARQL endpoint configuration

    if type(dataset.store) is SPARQLUpdateStore:
        print(
            "Please make sure your SPARQL endpoint has not configured "
            "its default graph as the union of the named graphs"
        )
    g1 = dataset.graph(c1)
    g1.add((tarek, likes, pizza))

    if type(dataset.store) is SPARQLUpdateStore:
        try:
            assert list(dataset.objects(tarek, None)) == []
        except Exception:
            pass
    else:
        assert list(dataset.objects(tarek, None)) == []

    assert list(g1.objects(tarek, None)) == [pizza]


def test_iter(get_dataset):
    """PR 1382: adds __iter__ to Dataset"""
    dataset = get_dataset

    uri_a = URIRef("https://example.com/a")
    uri_b = URIRef("https://example.com/b")
    uri_c = URIRef("https://example.com/c")
    uri_d = URIRef("https://example.com/d")

    dataset.add_graph(URIRef("https://example.com/g1"))
    dataset.add((uri_a, uri_b, uri_c, URIRef("https://example.com/g1")))
    dataset.add(
        (uri_a, uri_b, uri_c, URIRef("https://example.com/g1"))
    )  # pointless addition: duplicates above

    dataset.add_graph(URIRef("https://example.com/g2"))
    dataset.add((uri_a, uri_b, uri_c, URIRef("https://example.com/g2")))
    dataset.add((uri_a, uri_b, uri_d, URIRef("https://example.com/g1")))  # new, uri_d

    # Unreliable, fails with Python 3.7, disable pro tem
    if type(dataset.store) is not SPARQLUpdateStore and sys.version_info[1] > 7:

        # traditional iterator
        i_trad = 0
        for t in dataset.quads((None, None, None)):
            i_trad += 1

        # new Dataset.__iter__ iterator
        i_new = 0
        for t in dataset:
            i_new += 1

        assert i_new == i_trad  # both should be 3
