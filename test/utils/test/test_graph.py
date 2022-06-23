import logging
from contextlib import ExitStack
from pathlib import Path
from test.data import TEST_DATA_DIR
from test.utils.graph import cached_graph, subclasses_of, superclasses_of
from test.utils.namespace import RDFT
from typing import Set, Tuple, Type, Union

import pytest
from pyparsing import Optional

from rdflib.namespace import RDFS
from rdflib.term import IdentifiedNode

RDFT_GRAPHS = (
    TEST_DATA_DIR / "defined_namespaces/rdftest.ttl",
    TEST_DATA_DIR / "defined_namespaces/rdfs.ttl",
)


@pytest.mark.parametrize(
    [
        "graph_sources",
        "node",
        "expected_result",
    ],
    [
        (
            RDFT_GRAPHS,
            RDFS.Resource,
            {RDFS.Resource, RDFS.Class, RDFS.Datatype, RDFS.Container, RDFS.Literal},
        ),
        (RDFT_GRAPHS, RDFS.Class, {RDFS.Class, RDFS.Datatype}),
        (
            RDFT_GRAPHS,
            RDFT.Test,
            {
                RDFT.Test,
                RDFT.TestEval,
                RDFT.TestNQuadsNegativeSyntax,
                RDFT.TestNQuadsPositiveSyntax,
                RDFT.TestNTriplesNegativeSyntax,
                RDFT.TestNTriplesPositiveSyntax,
                RDFT.TestSyntax,
                RDFT.TestTriGNegativeSyntax,
                RDFT.TestTriGPositiveSyntax,
                RDFT.TestTrigNegativeEval,
                RDFT.TestTurtleEval,
                RDFT.TestTurtleNegativeEval,
                RDFT.TestTurtleNegativeSyntax,
                RDFT.TestTurtlePositiveSyntax,
                RDFT.XMLEval,
            },
        ),
    ],
)
def test_graph_subclasses_of(
    graph_sources: Tuple[Path, ...],
    node: IdentifiedNode,
    expected_result: Union[Set[IdentifiedNode], Type[Exception]],
) -> None:

    catcher: Optional[pytest.ExceptionInfo[Exception]] = None

    graph = cached_graph(graph_sources)

    with ExitStack() as xstack:
        if isinstance(expected_result, type) and issubclass(expected_result, Exception):
            catcher = xstack.enter_context(pytest.raises(expected_result))
        result = subclasses_of(graph, node)
        logging.debug("result = %s", result)
    if catcher is not None:
        assert catcher is not None
        assert catcher.value is not None
    else:
        assert expected_result == result


@pytest.mark.parametrize(
    [
        "graph_sources",
        "node",
        "expected_result",
    ],
    [
        (RDFT_GRAPHS, RDFS.Class, {RDFS.Class, RDFS.Resource}),
        (RDFT_GRAPHS, RDFS.Literal, {RDFS.Literal, RDFS.Resource}),
        (
            RDFT_GRAPHS,
            RDFT.TestTurtleNegativeSyntax,
            {
                RDFT.Test,
                RDFT.TestSyntax,
                RDFT.TestTurtleNegativeSyntax,
            },
        ),
    ],
)
def test_graph_superclasses_of(
    graph_sources: Tuple[Path, ...],
    node: IdentifiedNode,
    expected_result: Union[Set[IdentifiedNode], Type[Exception]],
) -> None:

    catcher: Optional[pytest.ExceptionInfo[Exception]] = None

    graph = cached_graph(graph_sources)

    with ExitStack() as xstack:
        if isinstance(expected_result, type) and issubclass(expected_result, Exception):
            catcher = xstack.enter_context(pytest.raises(expected_result))
        result = superclasses_of(graph, node)
        logging.debug("result = %s", result)
    if catcher is not None:
        assert catcher is not None
        assert catcher.value is not None
    else:
        assert expected_result == result
