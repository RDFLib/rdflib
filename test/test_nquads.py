import os
import shutil
import tempfile

import pytest

from rdflib import ConjunctiveGraph, Namespace, URIRef, plugin
from rdflib.store import VALID_STORE

TEST_DIR = os.path.abspath(os.path.dirname(__file__))
TEST_BASE = "test/nquads.rdflib"


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

    pluginstores.append(s.name)


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

    try:
        graph = ConjunctiveGraph(store=store)
    except ImportError:
        pytest.skip("Dependencies for store '%s' not available!" % store)

    if store != "default":
        rt = graph.open(configuration=path, create=True)
        assert rt == VALID_STORE, "The underlying store is corrupt"

    assert len(graph) == 0, "There must be zero triples in the graph just after store (file) creation"

    nq_path = os.path.relpath(os.path.join(TEST_DIR, "nquads.rdflib/example.nquads"), os.curdir)
    with open(nq_path, "rb") as data:
        graph.parse(data, format="nquads")

    yield graph

    graph.close()
    graph.destroy(path)
    try:
        shutil.rmtree(path)
    except Exception:
        pass


def test_01_simple_open(get_graph):
    graph = get_graph
    assert len(graph.store) == 449


def test_02_contexts(get_graph):
    # There should be 16 separate contexts
    graph = get_graph
    assert len([x for x in graph.store.contexts()]) == 16


def test_03_get_value(get_graph):
    # is the name of entity E10009 "Arco Publications"?
    # (in graph http://bibliographica.org/entity/E10009)
    # Looking for:
    # <http://bibliographica.org/entity/E10009>
    #       <http://xmlns.com/foaf/0.1/name>
    #       "Arco Publications"
    #       <http://bibliographica.org/entity/E10009>

    graph = get_graph
    s = URIRef("http://bibliographica.org/entity/E10009")
    FOAF = Namespace("http://xmlns.com/foaf/0.1/")

    assert graph.value(subject=s, predicate=FOAF.name).eq("Arco Publications")


def test_context_is_optional(get_graph):
    graph = get_graph
    nq_path = os.path.relpath(os.path.join(TEST_DIR, "nquads.rdflib/test6.nq"), os.curdir)
    with open(nq_path, "rb") as data:
        graph.parse(data, format="nquads")
    assert len(graph) > 0


def test_serialize():
    g = ConjunctiveGraph()
    uri1 = URIRef("http://example.org/mygraph1")
    uri2 = URIRef("http://example.org/mygraph2")

    bob = URIRef("urn:example:bob")
    likes = URIRef("urn:example:likes")
    pizza = URIRef("urn:example:pizza")

    g.get_context(uri1).add((bob, likes, pizza))
    g.get_context(uri2).add((bob, likes, pizza))

    s = g.serialize(format="nquads", encoding="utf-8")
    assert len([x for x in s.split(b"\n") if x.strip()]) == 2

    g2 = ConjunctiveGraph()
    g2.parse(data=s, format="nquads")

    assert len(g) == len(g2)
    assert sorted(x.identifier for x in g.contexts()) == sorted(x.identifier for x in g2.contexts())


@pytest.fixture
def get_data():
    data = open("test/nquads.rdflib/bnode_context.nquads", "rb")
    data_obnodes = open("test/nquads.rdflib/bnode_context_obj_bnodes.nquads", "rb")
    yield data, data_obnodes

    data.close()


def test_parse_shared_bnode_context(get_data):
    data, data_obnodes = get_data
    bnode_ctx = dict()
    g = ConjunctiveGraph()
    h = ConjunctiveGraph()
    g.parse(data, format="nquads", bnode_context=bnode_ctx)
    data.seek(0)
    h.parse(data, format="nquads", bnode_context=bnode_ctx)
    assert set(h.subjects()) == set(g.subjects())


def test_parse_shared_bnode_context_same_graph(get_data):
    data, data_obnodes = get_data

    bnode_ctx = dict()
    g = ConjunctiveGraph()
    g.parse(data_obnodes, format="nquads", bnode_context=bnode_ctx)
    o1 = set(g.objects())
    data_obnodes.seek(0)
    g.parse(data_obnodes, format="nquads", bnode_context=bnode_ctx)
    o2 = set(g.objects())
    assert o1 == o2


def test_parse_distinct_bnode_context(get_data):
    data, data_obnodes = get_data
    g = ConjunctiveGraph()
    g.parse(data, format="nquads", bnode_context=dict())
    s1 = set(g.subjects())
    data.seek(0)
    g.parse(data, format="nquads", bnode_context=dict())
    s2 = set(g.subjects())
    assert set() != s2 - s1


def test_parse_distinct_bnode_contexts_between_graphs(get_data):
    data, data_obnodes = get_data
    g = ConjunctiveGraph()
    h = ConjunctiveGraph()
    g.parse(data, format="nquads")
    s1 = set(g.subjects())
    data.seek(0)
    h.parse(data, format="nquads")
    s2 = set(h.subjects())
    assert s1 != s2


def test_parse_distinct_bnode_contexts_named_graphs(get_data):
    data, data_obnodes = get_data
    g = ConjunctiveGraph()
    h = ConjunctiveGraph()
    g.parse(data, format="nquads")
    data.seek(0)
    h.parse(data, format="nquads")
    assert set(h.contexts()) != set(g.contexts())


def test_parse_shared_bnode_contexts_named_graphs(get_data):
    data, data_obnodes = get_data
    bnode_ctx = dict()
    g = ConjunctiveGraph()
    h = ConjunctiveGraph()
    g.parse(data, format="nquads", bnode_context=bnode_ctx)
    data.seek(0)
    h.parse(data, format="nquads", bnode_context=bnode_ctx)
    assert set(h.contexts()) == set(g.contexts())
