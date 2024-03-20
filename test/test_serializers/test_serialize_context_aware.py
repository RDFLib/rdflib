import itertools
import logging
from test.utils.graph import GRAPH_FORMATS, GraphType
from test.utils.variants import load_pyvariant
from typing import Dict, Iterable, Type

import pytest
from _pytest.mark.structures import ParameterSet
from _pytest.outcomes import Failed

from rdflib.graph import ConjunctiveGraph, Dataset, Graph


def make_quads_in_triples_cases() -> Iterable[ParameterSet]:
    """
    Generate test cases for serializing named graphs (i.e. quads) into a format
    that does not support named graphs.
    """
    triple_only_formats = [
        graph_format
        for graph_format in GRAPH_FORMATS
        if graph_format.info.graph_types == {GraphType.TRIPLE}
    ]
    for graph_type, graph_format in itertools.product(
        (ConjunctiveGraph, Dataset), triple_only_formats
    ):
        for serializer in graph_format.info.serializers:
            yield pytest.param(
                graph_type, serializer, marks=pytest.mark.xfail(raises=Failed)
            )


CONJUNCTIVE_GRAPH_WITH_QUADS = load_pyvariant("diverse_quads", ConjunctiveGraph)
DATASET_WITH_QUADS = load_pyvariant("diverse_quads", Dataset)

GRAPHS: Dict[Type[Graph], Graph] = {
    ConjunctiveGraph: CONJUNCTIVE_GRAPH_WITH_QUADS,
    Dataset: DATASET_WITH_QUADS,
}


@pytest.mark.parametrize(["graph_type", "serializer"], make_quads_in_triples_cases())
def test_quads_in_triples(graph_type: Type[ConjunctiveGraph], serializer: str) -> None:
    """
    Serializing named graphs (i.e. quads) inside a `ConjunctiveGraph` into a
    format that does not support named graphs should result in an exception.
    """
    graph = GRAPHS[graph_type]
    assert type(graph) is graph_type
    with pytest.raises(Exception) as caught:
        graph.serialize(format=serializer)

    logging.debug("caught.value = %r", caught.value, exc_info=caught.value)
