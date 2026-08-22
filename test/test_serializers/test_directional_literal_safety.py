from __future__ import annotations

import pytest

from rdflib import Dataset, Graph, Literal, Namespace
from rdflib.exceptions import Error

EX = Namespace("https://example.org/")
ERROR_PATTERN = (
    "Directional language-tagged Literal requires an RDF 1.2-capable serializer"
)


@pytest.mark.parametrize(
    "format_name",
    [
        "xml",
        "pretty-xml",
        "n3",
        "turtle",
        "longturtle",
        "nt",
        "nt11",
        "json-ld",
        "hext",
    ],
)
def test_rdf11_graph_serializers_reject_directional_literal(
    format_name: str,
) -> None:
    graph = Graph()
    graph.add(
        (
            EX.subject,
            EX.label,
            Literal("hello", lang="en", direction="ltr"),
        )
    )

    with pytest.raises(Error, match=ERROR_PATTERN):
        graph.serialize(format=format_name)


@pytest.mark.parametrize("format_name", ["nquads", "trix", "trig", "patch"])
def test_rdf11_dataset_serializers_reject_directional_literal(
    format_name: str,
) -> None:
    dataset = Dataset()
    dataset.add(
        (
            EX.subject,
            EX.label,
            Literal("مرحبا", lang="ar", direction="rtl"),
            dataset.graph(EX.graph),
        )
    )

    with pytest.raises(Error, match=ERROR_PATTERN):
        dataset.serialize(format=format_name)


@pytest.mark.parametrize(
    "format_name",
    [
        "xml",
        "pretty-xml",
        "n3",
        "turtle",
        "longturtle",
        "nt",
        "nt11",
        "json-ld",
        "hext",
    ],
)
def test_rdf11_graph_serializers_still_accept_ordinary_language_literal(
    format_name: str,
) -> None:
    graph = Graph()
    graph.add((EX.subject, EX.label, Literal("hello", lang="en")))

    result = graph.serialize(format=format_name)

    assert result


@pytest.mark.parametrize("format_name", ["nquads", "trix", "trig", "patch"])
def test_rdf11_dataset_serializers_still_accept_ordinary_language_literal(
    format_name: str,
) -> None:
    dataset = Dataset()
    dataset.add(
        (
            EX.subject,
            EX.label,
            Literal("hello", lang="en"),
            dataset.graph(EX.graph),
        )
    )

    result = dataset.serialize(format=format_name)

    assert result
