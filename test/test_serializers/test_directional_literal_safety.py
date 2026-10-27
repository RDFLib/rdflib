from __future__ import annotations

from io import BytesIO

import pytest

from rdflib import RDF, BNode, Dataset, Graph, Literal, Namespace
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
        "nquads",
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
        "nquads",
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


@pytest.mark.parametrize("format_name", ["xml", "pretty-xml"])
@pytest.mark.parametrize("direction", ["ltr", "rtl"])
def test_rdfxml_rejects_directional_rdf_type_object(
    format_name: str, direction: str
) -> None:
    graph = Graph()
    graph.add((EX.subject, RDF.type, Literal("hello", lang="en", direction=direction)))

    with pytest.raises(Error, match=ERROR_PATTERN):
        graph.serialize(format=format_name)


@pytest.mark.parametrize("direction", ["ltr", "rtl"])
def test_prettyxml_rejects_directional_collection_annotation_before_writing(
    direction: str,
) -> None:
    graph = Graph()
    head = BNode()
    graph.add((EX.subject, EX.items, head))
    graph.add((head, RDF.first, EX.item))
    graph.add((head, RDF.rest, RDF.nil))
    graph.add((head, EX.label, Literal("hello", lang="en", direction=direction)))
    stream = BytesIO()

    with pytest.raises(Error, match=ERROR_PATTERN):
        graph.serialize(destination=stream, format="pretty-xml")

    assert stream.getvalue() == b""


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
