import logging
from test.data import TEST_DATA_DIR
from test.utils import GraphHelper
from test.utils.graph import load_sources
from test.utils.namespace import EGDO
from typing import Callable

import pytest

from rdflib.graph import ConjunctiveGraph, Dataset, Graph


@pytest.mark.parametrize("graph_factory", [Graph, ConjunctiveGraph, Dataset])
def test_load_into_default(graph_factory: Callable[[], Graph]) -> None:
    """
    Evaluation of ``LOAD <source>`` into default graph works correctly.
    """
    source_path = TEST_DATA_DIR / "variants" / "simple_triple.ttl"

    expected_graph = graph_factory()
    load_sources(source_path, graph=expected_graph)

    actual_graph = graph_factory()
    actual_graph.update(f"LOAD <{source_path.as_uri()}>")

    if logging.getLogger().isEnabledFor(logging.DEBUG):
        debug_format = (
            "trig" if isinstance(expected_graph, ConjunctiveGraph) else "turtle"
        )
        logging.debug(
            "expected_graph = \n%s", expected_graph.serialize(format=debug_format)
        )
        logging.debug(
            "actual_graph = \n%s", actual_graph.serialize(format=debug_format)
        )

    if isinstance(expected_graph, ConjunctiveGraph):
        assert isinstance(actual_graph, ConjunctiveGraph)
        GraphHelper.assert_collection_graphs_equal(expected_graph, actual_graph)
    else:
        GraphHelper.assert_triple_sets_equals(expected_graph, actual_graph)


@pytest.mark.parametrize("graph_factory", [ConjunctiveGraph, Dataset])
def test_load_into_named(graph_factory: Callable[[], ConjunctiveGraph]) -> None:
    """
    Evaluation of ``LOAD <source> INTO GRAPH <name>`` works correctly.
    """
    source_path = TEST_DATA_DIR / "variants" / "simple_triple.ttl"

    expected_graph = graph_factory()
    load_sources(source_path, graph=expected_graph.get_context(EGDO.graph))

    actual_graph = graph_factory()

    actual_graph.update(f"LOAD <{source_path.as_uri()}> INTO GRAPH <{EGDO.graph}>")

    if logging.getLogger().isEnabledFor(logging.DEBUG):
        debug_format = "trig"
        logging.debug(
            "expected_graph = \n%s", expected_graph.serialize(format=debug_format)
        )
        logging.debug(
            "actual_graph = \n%s", actual_graph.serialize(format=debug_format)
        )

    GraphHelper.assert_collection_graphs_equal(expected_graph, actual_graph)
