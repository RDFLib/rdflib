from __future__ import annotations

import logging
from typing import Iterable

import pytest
from _pytest.mark.structures import ParameterSet

from rdflib.graph import DATASET_DEFAULT_GRAPH_ID, Dataset
from rdflib.term import URIRef
from test.data import TEST_DATA_DIR


def make_load_default_and_named() -> Iterable[ParameterSet]:
    for file_extension in ("trig", "nq", "jsonld"):
        yield pytest.param(file_extension, id=file_extension)


EXTENSION_FORMATS = {
    "trig": "trig",
    "nq": "nquads",
    "jsonld": "json-ld",
    "nt": "ntriples",
    "ttl": "turtle",
    "hext": "hext",
    "n3": "n3",
}


@pytest.mark.parametrize("file_extension", make_load_default_and_named())
def test_load_default_and_named(file_extension: str) -> None:
    container = Dataset()

    assert 1 == sum(1 for _ in container.graphs())
    assert DATASET_DEFAULT_GRAPH_ID == next(
        (graph.identifier for graph in container.graphs()), None
    )
    assert container.default_graph == next(container.graphs(), None)

    # Load an RDF document with triples in three graphs into the container.
    format = EXTENSION_FORMATS[file_extension]
    source = TEST_DATA_DIR / "variants" / f"more_quads.{file_extension}"
    container.parse(source=source, format=format)

    context_identifiers = set(context.identifier for context in container.graphs())

    logging.info("context_identifiers = %s", context_identifiers)
    logging.info(
        "container.default_graph.triples(...) = %s",
        set(container.default_graph.triples((None, None, None))),
    )

    all_contexts = set(container.graphs())
    logging.info(
        "all_contexts = %s", set(context.identifier for context in all_contexts)
    )

    non_default_graphs = set(container.graphs()) - {container.default_graph}
    # There should now be two graphs in the container that are not the default graph.
    logging.info(
        "non_default_graphs = %s",
        set(context.identifier for context in non_default_graphs),
    )
    assert 2 == len(non_default_graphs)

    # The identifiers of the the non-default graphs should be the ones from the document.
    assert {
        URIRef("http://example.org/g2"),
        URIRef("http://example.org/g3"),
    } == set(context.identifier for context in non_default_graphs)

    # The default graph should have 4 triples.
    assert 4 == len(container.default_graph)


def make_load_default_only_cases() -> Iterable[ParameterSet]:
    for file_extension in ("trig", "ttl", "nq", "nt", "jsonld", "hext", "n3"):
        yield pytest.param(file_extension, id=file_extension)


@pytest.mark.parametrize("file_extension", make_load_default_only_cases())
def test_load_default_only(file_extension: str) -> None:
    container = Dataset()

    assert 1 == sum(1 for _ in container.graphs())
    assert DATASET_DEFAULT_GRAPH_ID == next(
        (graph.identifier for graph in container.graphs()), None
    )
    assert container.default_graph == next(container.graphs(), None)

    # Load an RDF document with only triples in the default graph into the container.
    format = EXTENSION_FORMATS[file_extension]
    source = TEST_DATA_DIR / "variants" / f"simple_triple.{file_extension}"
    container.parse(source=source, format=format)

    context_identifiers = set(graph.identifier for graph in container.graphs())

    logging.info("context_identifiers = %s", context_identifiers)
    logging.info(
        "container.default_graph.triples(...) = %s",
        set(container.default_graph.triples((None, None, None))),
    )

    all_contexts = set(container.graphs())
    logging.info(
        "all_contexts = %s", set(context.identifier for context in all_contexts)
    )

    non_default_graphs = set(container.graphs()) - {container.default_graph}
    # There should now be no graphs in the container that are not the default graph.
    logging.info(
        "non_default_graphs = %s",
        set(context.identifier for context in non_default_graphs),
    )
    assert 0 == len(non_default_graphs)

    # The identifiers of the non-default graphs should be an empty set.
    assert set() == set(context.identifier for context in non_default_graphs)

    # The default graph should have 3 triples.
    assert 1 == len(container.default_graph)
