"""
Tests for usage of the Store interface from Graph/NamespaceManager.
"""

from __future__ import annotations

import itertools
import logging
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    Iterable,
    Mapping,
    Optional,
    Sequence,
    Tuple,
    Type,
    Union,
)
from unittest.mock import patch

import pytest

import rdflib.namespace
from rdflib.graph import ConjunctiveGraph, Dataset, Graph
from rdflib.namespace import Namespace
from rdflib.plugins.sparql.sparql import Query
from rdflib.plugins.stores.memory import Memory
from rdflib.query import Result
from rdflib.store import Store
from rdflib.term import Identifier, URIRef, Variable
from test.data import SIMPLE_TRIPLE_GRAPH

if TYPE_CHECKING:
    from _pytest.mark.structures import ParameterSet

NamespaceBindings = Dict[str, URIRef]


def check_ns(graph: Graph, expected_bindings: NamespaceBindings) -> None:
    actual_graph_bindings = list(graph.namespaces())
    logging.info("actual_bindings = %s", actual_graph_bindings)
    assert list(expected_bindings.items()) == actual_graph_bindings
    store: Store = graph.store
    actual_store_bindings = list(store.namespaces())
    assert list(expected_bindings.items()) == actual_store_bindings
    for prefix, uri in expected_bindings.items():
        assert store.prefix(uri) == prefix
        assert store.namespace(prefix) == uri


class MemoryWithoutBindOverride(Memory):
    def bind(self, prefix, namespace) -> None:  # type: ignore[override]
        return super().bind(prefix, namespace, False)


class GraphWithoutBindOverrideFix(Graph):
    def bind(self, prefix, namespace, override=True, replace=False) -> None:
        old_value = rdflib.namespace._with_bind_override_fix
        rdflib.namespace._with_bind_override_fix = False
        try:
            return super().bind(prefix, namespace, override, replace)
        finally:
            rdflib.namespace._with_bind_override_fix = old_value


GraphFactory = Callable[[], Graph]
GraphOperation = Callable[[Graph], None]
GraphOperations = Sequence[GraphOperation]

EGNS = Namespace("http://example.com/namespace#")
EGNS_V0 = EGNS["v0"]
EGNS_V1 = EGNS["v1"]
EGNS_V2 = EGNS["v2"]


def make_graph_store_bind_cases(
    store_type: Type[Store] = Memory,
    graph_type: Type[Graph] = Graph,
) -> Iterable[Union[Tuple[Any, ...], ParameterSet]]:
    """
    Generate test cases for test_graph_store_bind.
    """

    def graph_factory():
        return graph_type(bind_namespaces="none", store=store_type())

    id_prefix = f"{store_type.__name__}-{graph_type.__name__}"

    def _p(
        graph_factory: GraphFactory,
        ops: GraphOperations,
        expected_bindings: NamespaceBindings,
        expected_bindings_overrides: Optional[
            Dict[Tuple[Type[Graph], Type[Store]], NamespaceBindings]
        ] = None,
        *,
        id: Optional[str] = None,
    ):
        if expected_bindings_overrides is not None:
            expected_bindings = expected_bindings_overrides.get(
                (graph_type, store_type), expected_bindings
            )
        if id is not None:
            return pytest.param(graph_factory, ops, expected_bindings, id=id)
        else:
            return (graph_factory, ops, expected_bindings)

    yield from [
        _p(
            graph_factory,
            [
                lambda g: g.bind("eg", EGNS_V0),
            ],
            {"eg": EGNS_V0},
            id=f"{id_prefix}-default-args",
        ),
        # reused-prefix
        _p(
            graph_factory,
            [
                lambda g: g.bind("eg", EGNS_V0),
                lambda g: g.bind("eg", EGNS_V1, override=False),
            ],
            {"eg": EGNS_V0, "eg1": EGNS_V1},
            id=f"{id_prefix}-reused-prefix-override-false-replace-false",
        ),
        _p(
            graph_factory,
            [
                lambda g: g.bind("eg", EGNS_V0),
                lambda g: g.bind("eg", EGNS_V1),
            ],
            {"eg": EGNS_V0, "eg1": EGNS_V1},
            id=f"{id_prefix}-reused-prefix-override-true-replace-false",
        ),
        _p(
            graph_factory,
            [
                lambda g: g.bind("eg", EGNS_V0),
                lambda g: g.bind("eg", EGNS_V1, override=False, replace=True),
            ],
            {"eg": EGNS_V0},
            {(GraphWithoutBindOverrideFix, Memory): {"eg": EGNS_V1}},
            id=f"{id_prefix}-reused-prefix-override-false-replace-true",
        ),
        _p(
            graph_factory,
            [
                lambda g: g.bind("eg", EGNS_V0),
                lambda g: g.bind("eg", EGNS_V1, replace=True),
            ],
            {"eg": EGNS_V1},
            {(Graph, MemoryWithoutBindOverride): {"eg": EGNS_V0}},
            id=f"{id_prefix}-reused-prefix-override-true-replace-true",
        ),
        # reused-namespace
        _p(
            graph_factory,
            [
                lambda g: g.bind("eg", EGNS_V0),
                lambda g: g.bind("egv0", EGNS_V0, override=False),
            ],
            {"eg": EGNS_V0},
            id=f"{id_prefix}-reused-namespace-override-false-replace-false",
        ),
        _p(
            graph_factory,
            [
                lambda g: g.bind("eg", EGNS_V0),
                lambda g: g.bind("egv0", EGNS_V0),
            ],
            {"egv0": EGNS_V0},
            {(Graph, MemoryWithoutBindOverride): {"eg": EGNS_V0}},
            id=f"{id_prefix}-reused-namespace-override-true-replace-false",
        ),
        _p(
            graph_factory,
            [
                lambda g: g.bind("eg", EGNS_V0),
                lambda g: g.bind("egv0", EGNS_V0, override=False, replace=True),
            ],
            {"eg": EGNS_V0},
            id=f"{id_prefix}-reused-namespace-override-false-replace-true",
        ),
        _p(
            graph_factory,
            [
                lambda g: g.bind("eg", EGNS_V0),
                lambda g: g.bind("egv0", EGNS_V0, replace=True),
            ],
            {"egv0": EGNS_V0},
            {(Graph, MemoryWithoutBindOverride): {"eg": EGNS_V0}},
            id=f"{id_prefix}-reused-namespace-override-true-replace-true",
        ),
    ]


@pytest.mark.parametrize(
    ["graph_factory", "ops", "expected_bindings"],
    itertools.chain(
        make_graph_store_bind_cases(),
        make_graph_store_bind_cases(store_type=MemoryWithoutBindOverride),
        make_graph_store_bind_cases(graph_type=GraphWithoutBindOverrideFix),
    ),
)
def test_graph_store_bind(
    graph_factory: GraphFactory,
    ops: GraphOperations,
    expected_bindings: NamespaceBindings,
) -> None:
    """
    The expected sequence of graph operations results in the expected
    namespace bindings.
    """
    graph = graph_factory()
    for op in ops:
        op(graph)
    check_ns(graph, expected_bindings)


@pytest.mark.parametrize(
    ("graph_factory", "query_graph"),
    [
        (Graph, lambda graph: graph.identifier),
        (ConjunctiveGraph, "__UNION__"),
        (Dataset, lambda graph: graph.default_context.identifier),
        (lambda store: Dataset(store=store, default_union=True), "__UNION__"),
    ],
)
def test_query_query_graph(
    graph_factory: Callable[[Store], Graph],
    query_graph: Union[str, Callable[[Graph], str]],
) -> None:
    """
    The `Graph.query` method passes the correct ``queryGraph`` argument
    to stores that have implemented a `Store.query` method.
    """

    mock_result = Result("SELECT")
    mock_result.vars = [Variable("s"), Variable("p"), Variable("o")]
    mock_result.bindings = [
        {
            Variable("s"): URIRef("http://example.org/subject"),
            Variable("p"): URIRef("http://example.org/predicate"),
            Variable("o"): URIRef("http://example.org/object"),
        },
    ]

    query_string = r"FAKE QUERY, NOT USED"
    store = Memory()
    graph = graph_factory(store)

    if callable(query_graph):
        query_graph = query_graph(graph)

    def mock_query(
        query: Union[Query, str],
        initNs: Mapping[str, Any],  # noqa: N803
        initBindings: Mapping[str, Identifier],  # noqa: N803
        queryGraph: str,  # noqa: N803
        **kwargs,
    ) -> Result:
        assert query_string == query
        assert dict(store.namespaces()) == initNs
        assert {} == initBindings
        assert query_graph == queryGraph
        assert {} == kwargs
        return mock_result

    with patch.object(store, "query", wraps=mock_query) as wrapped_query:
        actual_result = graph.query(query_string)
        assert actual_result.type == "SELECT"
        assert list(actual_result) == list(
            SIMPLE_TRIPLE_GRAPH.triples((None, None, None))
        )
        assert wrapped_query.call_count == 1


@pytest.mark.parametrize(
    ("graph_factory", "query_graph"),
    [
        (Graph, lambda graph: graph.identifier),
        (ConjunctiveGraph, "__UNION__"),
        (Dataset, lambda graph: graph.default_context.identifier),
        (lambda store: Dataset(store=store, default_union=True), "__UNION__"),
    ],
)
def test_update_query_graph(
    graph_factory: Callable[[Store], Graph],
    query_graph: Union[str, Callable[[Graph], str]],
) -> None:
    """
    The `Graph.update` method passes the correct ``queryGraph`` argument
    to stores that have implemented a `Store.update` method.
    """

    update_string = r"FAKE UPDATE, NOT USED"
    store = Memory()
    graph = graph_factory(store)

    if callable(query_graph):
        query_graph = query_graph(graph)

    def mock_update(
        query: Union[Query, str],
        initNs: Mapping[str, Any],  # noqa: N803
        initBindings: Mapping[str, Identifier],  # noqa: N803
        queryGraph: str,  # noqa: N803
        **kwargs,
    ) -> None:
        assert update_string == query
        assert dict(store.namespaces()) == initNs
        assert {} == initBindings
        assert query_graph == queryGraph
        assert {} == kwargs

    with patch.object(store, "update", wraps=mock_update) as wrapped_update:
        graph.update(update_string)
        assert wrapped_update.call_count == 1
