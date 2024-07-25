from __future__ import annotations

import itertools
import logging
from typing import Iterable, Type, Union

import pytest
from _pytest.mark.structures import ParameterSet

from rdflib.graph import DATASET_DEFAULT_GRAPH_ID, ConjunctiveGraph, Dataset
from rdflib.term import BNode, URIRef
from test.data import TEST_DATA_DIR


def make_load_default_and_named() -> Iterable[ParameterSet]:
    for container_type, file_extension in itertools.product(
        (Dataset, ConjunctiveGraph), ("trig", "nq", "jsonld")
    ):
        yield pytest.param(
            container_type,
            file_extension,
            id=f"{container_type.__name__}-{file_extension}",
        )


EXTENSION_FORMATS = {
    "trig": "trig",
    "nq": "nquads",
    "jsonld": "json-ld",
    "nt": "ntriples",
    "ttl": "turtle",
    "hext": "hext",
    "n3": "n3",
}


@pytest.mark.parametrize(
    ["container_type", "file_extension"], make_load_default_and_named()
)
def test_load_default_and_named(
    container_type: Union[Type[Dataset], Type[ConjunctiveGraph]], file_extension: str
) -> None:
    logging.debug("container_type = %s", container_type)
    container = container_type()

    if container_type is Dataset:
        # An empty dataset has 1 default graph and no named graphs, so 1 graph in
        # total.
        assert 1 == sum(1 for _ in container.contexts())
        assert DATASET_DEFAULT_GRAPH_ID == next(
            (context.identifier for context in container.contexts()), None
        )
        assert container.default_context == next(container.contexts(), None)
    else:
        assert isinstance(container.default_context.identifier, BNode)

    # Load an RDF document with triples in three graphs into the container.
    format = EXTENSION_FORMATS[file_extension]
    source = TEST_DATA_DIR / "variants" / f"more_quads.{file_extension}"
    container.parse(source=source, format=format)

    context_identifiers = set(context.identifier for context in container.contexts())

    logging.info("context_identifiers = %s", context_identifiers)
    logging.info(
        "container.default_context.triples(...) = %s",
        set(container.default_context.triples((None, None, None))),
    )

    all_contexts = set(container.contexts())
    logging.info(
        "all_contexts = %s", set(context.identifier for context in all_contexts)
    )

    non_default_contexts = set(container.contexts()) - {container.default_context}
    # There should now be two graphs in the container that are not the default graph.
    logging.info(
        "non_default_graphs = %s",
        set(context.identifier for context in non_default_contexts),
    )
    assert 2 == len(non_default_contexts)

    # The identifiers of the the non-default graphs should be the ones from the document.
    assert {
        URIRef("http://example.org/g2"),
        URIRef("http://example.org/g3"),
    } == set(context.identifier for context in non_default_contexts)

    # The default graph should have 4 triples.
    assert 4 == len(container.default_context)


def make_load_default_only_cases() -> Iterable[ParameterSet]:
    for container_type, file_extension in itertools.product(
        (Dataset, ConjunctiveGraph), ("trig", "ttl", "nq", "nt", "jsonld", "hext", "n3")
    ):
        yield pytest.param(
            container_type,
            file_extension,
            id=f"{container_type.__name__}-{file_extension}",
        )


@pytest.mark.parametrize(
    ["container_type", "file_extension"], make_load_default_only_cases()
)
def test_load_default_only(
    container_type: Union[Type[Dataset], Type[ConjunctiveGraph]], file_extension: str
) -> None:
    logging.debug("container_type = %s", container_type)
    container = container_type()

    if container_type is Dataset:
        # An empty dataset has 1 default graph and no named graphs, so 1 graph in
        # total.
        assert 1 == sum(1 for _ in container.contexts())
        assert DATASET_DEFAULT_GRAPH_ID == next(
            (context.identifier for context in container.contexts()), None
        )
        assert container.default_context == next(container.contexts(), None)
    else:
        assert isinstance(container.default_context.identifier, BNode)

    # Load an RDF document with only triples in the default graph into the container.
    format = EXTENSION_FORMATS[file_extension]
    source = TEST_DATA_DIR / "variants" / f"simple_triple.{file_extension}"
    container.parse(source=source, format=format)

    context_identifiers = set(context.identifier for context in container.contexts())

    logging.info("context_identifiers = %s", context_identifiers)
    logging.info(
        "container.default_context.triples(...) = %s",
        set(container.default_context.triples((None, None, None))),
    )

    all_contexts = set(container.contexts())
    logging.info(
        "all_contexts = %s", set(context.identifier for context in all_contexts)
    )

    non_default_contexts = set(container.contexts()) - {container.default_context}
    # There should now be no graphs in the container that are not the default graph.
    logging.info(
        "non_default_graphs = %s",
        set(context.identifier for context in non_default_contexts),
    )
    assert 0 == len(non_default_contexts)

    # The identifiers of the the non-default graphs should be an empty set.
    assert set() == set(context.identifier for context in non_default_contexts)

    # The default graph should have 3 triples.
    assert 1 == len(container.default_context)
