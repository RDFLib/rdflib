"""
This module contains tests for the parsing a turtle graph and check the namespace
handling.
"""

from dataclasses import dataclass
from typing import Any, Iterator

import pytest
from _pytest.mark.structures import ParameterSet

from rdflib import ConjunctiveGraph, Graph, URIRef
from rdflib.namespace import Namespace, NamespaceManager


def make_parser_namespace_tests() -> Iterator[ParameterSet]:
    @dataclass
    class Case:
        format_name: str
        data_string: str
        graph_class: Any

    cases = [
        Case(
            "ntriples",
            """
            <http://example.org/a> <http://example.org/b> <http://example.org/c> .
            """,
            Graph,
        ),
        Case(
            "nquads",
            """
            <http://example.org/a> <http://example.org/b> <http://example.org/c> <http://example.org/g> .
            """,
            ConjunctiveGraph,
        ),
        Case(
            "turtle",
            """
            @prefix ns1: <https://example.org/namespaces/testexample/> .
            @prefix ex: <http://example.org/> .
            ex:a ex:b ex:c .
            """,
            Graph,
        ),
        Case(
            "trig",
            """
            @prefix ns1: <https://example.org/namespaces/testexample/> .
            @prefix ex: <http://example.org/> .
            graph ex:g {
                ex:a ex:b ex:c .
            }
            """,
            ConjunctiveGraph,
        ),
        Case(
            "n3",
            """
            @prefix ns1: <https://example.org/namespaces/testexample/> .
            @prefix ex: <http://example.org/> .
            ex:a ex:b ex:c .
            """,
            Graph,
        ),
    ]

    for case in cases:
        yield pytest.param(case.format_name, case.data_string, case.graph_class)


@pytest.mark.parametrize(
    ["format_name", "data_string", "graph_class"],
    make_parser_namespace_tests(),
)
def test_literals(
    format_name: str,
    data_string: str,
    graph_class,
) -> None:
    """
    Setup a namespace manager, parse a file, assert that the original namespaces are still set.
    """
    namespaces = NamespaceManager(graph_class())
    namespaces.bind(
        "testexample", Namespace("https://example.org/namespaces/testexample/")
    )
    g = graph_class()
    g.namespace_manager = namespaces
    g.parse(data=data_string, format=format_name)
    all_ns = [n for n in g.namespace_manager.namespaces()]

    assert (
        "testexample",
        URIRef("https://example.org/namespaces/testexample/"),
    ) in all_ns


def test_namespacemanager() -> None:
    """
    Setup a namespace manager add two prefixes for the same IRI.
    """
    namespaces = NamespaceManager(Graph())
    namespaces.bind(
        "testexample", Namespace("https://example.org/namespaces/testexample/")
    )
    namespaces.bind("test", Namespace("https://example.org/namespaces/testexample/"))
    all_ns = [n for n in namespaces.namespaces()]
    assert (
        "testexample",
        URIRef("https://example.org/namespaces/testexample/"),
    ) in all_ns
    assert (
        "test",
        URIRef("https://example.org/namespaces/testexample/"),
    ) in all_ns
