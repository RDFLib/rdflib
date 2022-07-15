"""
Tests for usage of the Store interface from Graph/NamespaceManager.
"""

import itertools
import logging
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    Iterable,
    Optional,
    Sequence,
    Tuple,
    Type,
    Union,
)

import pytest

import rdflib.namespace
from rdflib.graph import Graph
from rdflib.namespace import Namespace
from rdflib.plugins.stores.memory import Memory
from rdflib.store import Store
from rdflib.term import URIRef

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


def make_test_graph_store_bind_cases(
    store_type: Type[Store] = Memory,
    graph_type: Type[Graph] = Graph,
) -> Iterable[Union[Tuple[Any, ...], "ParameterSet"]]:
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
        make_test_graph_store_bind_cases(),
        make_test_graph_store_bind_cases(store_type=MemoryWithoutBindOverride),
        make_test_graph_store_bind_cases(graph_type=GraphWithoutBindOverrideFix),
    ),
)
def test_graph_store_bind(
    graph_factory: GraphFactory,
    ops: GraphOperations,
    expected_bindings: NamespaceBindings,
) -> None:
    """
    The expected sequence of graph operations results in the expected namespace bindings.
    """
    graph = graph_factory()
    for op in ops:
        op(graph)
    check_ns(graph, expected_bindings)
