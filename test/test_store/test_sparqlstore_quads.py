from io import BytesIO
from unittest.mock import patch
from urllib.error import HTTPError

import pytest

from rdflib import BNode, Dataset, Graph, Literal, URIRef, Variable
from rdflib.graph import DATASET_DEFAULT_GRAPH_ID, _TriplePatternType
from rdflib.plugins.stores.sparqlstore import SPARQLStore, SPARQLUpdateStore
from rdflib.query import Result
from rdflib.term import Node

S, P, OBJ, G1, G2 = map(URIRef, ("urn:s", "urn:p", "urn:o", "urn:g1", "urn:g2"))


@pytest.fixture
def source() -> Dataset:
    dataset = Dataset()
    for graph in (dataset.default_graph, dataset.graph(G1), dataset.graph(G2)):
        graph.add((S, P, OBJ))
        graph.add((BNode("shared"), P, Literal("shared")))
        for value in (Literal(False), Literal(0), Literal(""), Literal("g")):
            graph.add((S, P, value))
    dataset.graph(G2).add((OBJ, P, OBJ))
    return dataset


@pytest.mark.parametrize("store_type", [SPARQLStore, SPARQLUpdateStore])
@pytest.mark.parametrize("default_union", [False, True])
def test_dataset_iteration(source, store_type, default_union):
    store = store_type()
    dataset = Dataset(store, default_union=default_union)

    def query(text, **kwargs):
        assert kwargs == {"default_graph": None}
        result = source.query(text)
        return Result.parse(BytesIO(result.serialize(format="json")), format="json")

    with patch.object(store, "_query", side_effect=query) as remote:
        assert set(dataset) == set(source)
        remote.assert_called_once()


def test_xml_default_and_named_memberships() -> None:
    result = b"""<sparql xmlns="http://www.w3.org/2005/sparql-results#">
      <head><variable name="s"/><variable name="p"/><variable name="o"/><variable name="g"/></head>
      <results>
        <result>
          <binding name="s"><bnode>shared</bnode></binding>
          <binding name="p"><uri>urn:p</uri></binding>
          <binding name="o"><literal datatype="http://www.w3.org/2001/XMLSchema#boolean">false</literal></binding>
        </result>
        <result>
          <binding name="s"><bnode>shared</bnode></binding>
          <binding name="p"><uri>urn:p</uri></binding>
          <binding name="o"><literal datatype="http://www.w3.org/2001/XMLSchema#boolean">false</literal></binding>
          <binding name="g"><uri>urn:g1</uri></binding>
        </result>
      </results>
    </sparql>"""
    store = SPARQLStore()
    with patch.object(
        store, "query", return_value=Result.parse(BytesIO(result), format="xml")
    ):
        assert set(Dataset(store)) == {
            (BNode("shared"), P, Literal(False), DATASET_DEFAULT_GRAPH_ID),
            (BNode("shared"), P, Literal(False), G1),
        }


@pytest.mark.parametrize(
    "pattern",
    [
        (S, P, OBJ),
        (S, P, URIRef("urn:missing")),
        (S, P, Literal(False)),
        (S, P, Literal(0)),
        (S, P, Literal("")),
        (None, P, Literal("g")),
        (None, P, Variable("s")),
        (Variable("g"), P, None),
        (Variable("s"), P, Variable("s")),
    ],
)
def test_quad_patterns(source: Dataset, pattern: _TriplePatternType) -> None:
    store = SPARQLStore(sparql11=False)
    dataset = Dataset(store)

    def matches(triple):
        bindings = {}
        for term, value in zip(pattern, triple):
            if isinstance(term, Variable):
                if term in bindings and bindings[term] != value:
                    return False
                bindings[term] = value
            elif term is not None and term != value:
                return False
        return True

    expected = {quad for quad in source if matches(quad[:3])}
    with patch.object(
        store, "_query", side_effect=lambda text, **kw: source.query(text)
    ) as remote:
        assert set(dataset.quads(pattern)) == expected
        remote.assert_called_once()


@pytest.mark.parametrize("named", [False, True])
def test_single_graph_and_empty_dataset(named: bool) -> None:
    source = Dataset()
    store = SPARQLStore()
    dataset = Dataset(store)
    with patch.object(
        store, "_query", side_effect=lambda text, **kw: source.query(text)
    ):
        assert list(dataset) == []
        graph = source.graph(G1) if named else source.default_graph
        graph.add((S, P, OBJ))
        assert set(dataset.quads((S, P, OBJ))) == set(source)


@pytest.mark.parametrize("store_type", [SPARQLStore, SPARQLUpdateStore])
def test_custom_triples_override(store_type):
    class CustomStore(store_type):
        def triples(self, pattern, context=None):
            yield (S, P, OBJ), iter((Graph(self, G1),))

    store = CustomStore()
    with patch.object(store, "query", side_effect=AssertionError("bypassed triples")):
        assert list(iter(Dataset(store))) == [(S, P, OBJ, G1)]

    store = store_type()
    with patch.object(
        store, "triples", return_value=iter([((S, P, OBJ), iter([Graph(store, G2)]))])
    ):
        assert list(iter(Dataset(store))) == [(S, P, OBJ, G2)]


@pytest.mark.parametrize("store_type", [SPARQLStore, SPARQLUpdateStore])
def test_explicit_context_preserves_paging(store_type):
    store = store_type()
    graph = Graph(store, G1)
    graph.LIMIT = 1
    graph.OFFSET = 2
    source = Dataset()
    source.add((S, P, OBJ))
    with patch.object(
        store, "_query", return_value=source.query("SELECT ?s ?p ?o {?s ?p ?o}")
    ) as remote:
        assert list(Dataset(store).quads((None, None, None, graph))) == [
            (S, P, OBJ, G1)
        ]
        assert remote.call_args.kwargs == {"default_graph": G1}
        assert "UNION" not in remote.call_args.args[0]
        assert list(store.quads((None, None, None), context=graph)) == [
            (S, P, OBJ, graph)
        ]
        assert "ORDER BY ?s LIMIT 1 OFFSET 2" in remote.call_args.args[0]
        assert "UNION" not in remote.call_args.args[0]


@pytest.mark.parametrize("dirty_reads", [False, True])
def test_pending_updates(dirty_reads: bool) -> None:
    source = Dataset()
    store = SPARQLUpdateStore(
        update_endpoint="http://example.invalid/update",
        autocommit=False,
        dirty_reads=dirty_reads,
    )
    dataset = Dataset(store)
    store.add((S, P, OBJ), Graph(store, G1))
    with (
        patch.object(store, "_update", side_effect=source.update) as update,
        patch.object(
            store, "_query", side_effect=lambda text, **kw: source.query(text)
        ),
    ):
        assert set(dataset) == (set() if dirty_reads else {(S, P, OBJ, G1)})
        assert update.call_count == (0 if dirty_reads else 1)
        store.commit()
        assert set(dataset) == {(S, P, OBJ, G1)}
        assert update.call_count == 1


def test_query_override_and_node_serialization(source: Dataset) -> None:
    class CustomStore(SPARQLStore):
        def query(self, text, *args, **kwargs):
            return source.query(text)

    blank = BNode("alias")

    def serialize(node: Node) -> str:
        return S.n3() if node == blank else node.n3()

    store = CustomStore(node_to_sparql=serialize)
    assert set(Dataset(store).quads((blank, P, OBJ))) == {
        (blank, P, OBJ, graph) for graph in (G1, G2, DATASET_DEFAULT_GRAPH_ID)
    }


def test_query_error_propagates() -> None:
    store = SPARQLStore()
    with patch.object(store, "query", side_effect=ValueError("endpoint failure")):
        with pytest.raises(ValueError, match="endpoint failure"):
            list(iter(Dataset(store)))


@pytest.mark.parametrize("method", ["POST", "POST_FORM"])
@pytest.mark.parametrize("store_type", [SPARQLStore, SPARQLUpdateStore])
def test_unauthorized_query(method, store_type):
    endpoint = "http://example.invalid/query"
    store = store_type(query_endpoint=endpoint, method=method)
    with patch(
        "rdflib.plugins.stores.sparqlconnector.urlopen",
        side_effect=HTTPError(endpoint, 401, "Unauthorized", {}, None),
    ):
        with pytest.raises(ValueError, match="HTTP unauthorized"):
            list(Dataset(store).quads())
