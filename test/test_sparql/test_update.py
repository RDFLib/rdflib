import itertools
import logging
from typing import Callable

import pytest

from rdflib.graph import ConjunctiveGraph, Dataset, Graph
from test.data import TEST_DATA_DIR
from test.utils import GraphHelper
from test.utils.graph import GraphSource
from test.utils.namespace import EGDO


@pytest.mark.parametrize(
    ("graph_factory", "source"),
    itertools.product(
        [Graph, ConjunctiveGraph, Dataset],
        GraphSource.from_paths(
            TEST_DATA_DIR / "variants" / "simple_triple.ttl",
            TEST_DATA_DIR / "variants" / "relative_triple.ttl",
        ),
    ),
    ids=GraphSource.idfn,
)
def test_load_into_default(
    graph_factory: Callable[[], Graph], source: GraphSource
) -> None:
    """
    Evaluation of ``LOAD <source>`` into default graph works correctly.
    """

    expected_graph = graph_factory()
    source.load(graph=expected_graph)

    actual_graph = graph_factory()
    actual_graph.update(f"LOAD <{source.public_id_or_path_uri()}>")

    if logging.getLogger().isEnabledFor(logging.DEBUG):
        debug_format = (
            "nquads" if isinstance(expected_graph, ConjunctiveGraph) else "ntriples"
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


@pytest.mark.parametrize(
    ("graph_factory", "source"),
    itertools.product(
        [ConjunctiveGraph, Dataset],
        GraphSource.from_paths(
            TEST_DATA_DIR / "variants" / "simple_triple.ttl",
            TEST_DATA_DIR / "variants" / "relative_triple.ttl",
        ),
    ),
    ids=GraphSource.idfn,
)
def test_load_into_named(
    graph_factory: Callable[[], ConjunctiveGraph], source: GraphSource
) -> None:
    """
    Evaluation of ``LOAD <source> INTO GRAPH <name>`` works correctly.
    """

    expected_graph = graph_factory()
    source.load(graph=expected_graph.get_context(EGDO.graph))

    actual_graph = graph_factory()

    actual_graph.update(
        f"LOAD <{source.public_id_or_path_uri()}> INTO GRAPH <{EGDO.graph}>"
    )

    if logging.getLogger().isEnabledFor(logging.DEBUG):
        debug_format = "nquads"
        logging.debug(
            "expected_graph = \n%s", expected_graph.serialize(format=debug_format)
        )
        logging.debug(
            "actual_graph = \n%s", actual_graph.serialize(format=debug_format)
        )

    GraphHelper.assert_collection_graphs_equal(expected_graph, actual_graph)
