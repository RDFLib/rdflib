"""Tests for the Jelly-RDF format, which pyjelly provides."""

from __future__ import annotations

import subprocess
import sys
from io import BytesIO
from pathlib import Path

import pytest

import rdflib.plugin
from rdflib import XSD, Dataset, Graph, Literal, URIRef
from rdflib.graph import DATASET_DEFAULT_GRAPH_ID, ConjunctiveGraph
from rdflib.parser import Parser
from rdflib.serializer import Serializer
from rdflib.util import guess_format
from test.utils import GraphHelper
from test.utils.destination import DestinationType

EG = "http://example.com/"

TRIG_DATA = """
@prefix eg: <http://example.com/> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

eg:s0 eg:p0 eg:o0 , "plain" , "English"@en , 42 , "2021-12-03"^^xsd:date ;
    eg:p1 [ eg:p2 "nested" ] ;
    eg:p3 "multi\\nline \\u00e9\\u4e2d" .

eg:g0 {
    eg:s1 eg:p0 eg:o1 , _:b0 .
    _:b0 eg:p1 "in a named graph" .
}

_:g1 {
    eg:s2 eg:p0 eg:o2 .
}
"""


@pytest.fixture
def graph() -> Graph:
    graph = Graph()
    graph.parse(data=TRIG_DATA, format="trig")
    return graph


@pytest.fixture
def dataset() -> Dataset:
    dataset = Dataset()
    dataset.parse(data=TRIG_DATA, format="trig")
    return dataset


@pytest.mark.parametrize(
    ("kind", "names", "class_name"),
    [
        (Parser, ["jelly", "application/x-jelly-rdf"], "RDFLibJellyParser"),
        (Serializer, ["jelly", "application/x-jelly-rdf"], "RDFLibJellySerializer"),
    ],
)
def test_plugins(kind: type, names: list[str], class_name: str) -> None:
    """The format names and the media type all give pyjelly's plugin."""
    for name in names:
        assert rdflib.plugin.get(name, kind).__name__ == class_name


def test_guess_format() -> None:
    assert guess_format("data.jelly") == "jelly"


def test_import_does_not_load_pyjelly() -> None:
    """pyjelly and protobuf are only imported when the format is used."""
    code = (
        "import sys, rdflib;"
        "print('pyjelly' in sys.modules, 'google.protobuf' in sys.modules)"
    )
    output = subprocess.run(
        [sys.executable, "-c", code], capture_output=True, text=True, check=True
    )
    assert output.stdout.strip() == "False False"


def test_graph_roundtrip(graph: Graph) -> None:
    data = graph.serialize(format="jelly", encoding="utf-8")
    parsed = Graph().parse(data=data, format="jelly")
    GraphHelper.assert_isomorphic(graph, parsed)


def test_dataset_roundtrip(dataset: Dataset) -> None:
    data = dataset.serialize(format="jelly", encoding="utf-8")
    parsed = Dataset().parse(data=data, format="jelly")
    GraphHelper.assert_cgraph_isomorphic(dataset, parsed, exclude_bnodes=True)
    assert len(parsed.graph(DATASET_DEFAULT_GRAPH_ID)) == len(
        dataset.graph(DATASET_DEFAULT_GRAPH_ID)
    )
    assert len(parsed.graph(URIRef(f"{EG}g0"))) == 3


def test_triples_into_dataset(graph: Graph) -> None:
    """A stream of triples goes into the default graph of a Dataset."""
    data = graph.serialize(format="jelly", encoding="utf-8")
    parsed = Dataset().parse(data=data, format="jelly")
    GraphHelper.assert_isomorphic(graph, parsed.graph(DATASET_DEFAULT_GRAPH_ID))


def test_quads_into_graph(dataset: Dataset) -> None:
    """
    A plain Graph gets the default graph of a stream of quads, the same as with
    N-Quads.
    """
    data = dataset.serialize(format="jelly", encoding="utf-8")
    parsed = Graph().parse(data=data, format="jelly")
    expected = Graph().parse(data=dataset.serialize(format="nquads"), format="nquads")
    assert len(parsed) == 8
    GraphHelper.assert_isomorphic(expected, parsed)


@pytest.mark.parametrize(
    "destination_type",
    [
        DestinationType.PATH,
        DestinationType.PURE_PATH,
        DestinationType.STR_PATH,
        DestinationType.FILE_URI,
        DestinationType.BINARY_IO,
    ],
)
def test_serialize_destinations(
    tmp_path: Path, graph: Graph, destination_type: DestinationType
) -> None:
    with destination_type.make_ref(tmp_path) as dest_ref:
        assert dest_ref is not None
        result = graph.serialize(dest_ref.param, format="jelly")  # type: ignore[arg-type]
    assert result is graph
    expected = graph.serialize(format="jelly", encoding="utf-8")
    assert dest_ref.path.read_bytes() == expected


def test_parse_path_without_format(tmp_path: Path, graph: Graph) -> None:
    """The format of a .jelly file is guessed from its suffix."""
    path = tmp_path / "data.jelly"
    graph.serialize(path, format="jelly")
    GraphHelper.assert_isomorphic(graph, Graph().parse(path))


def test_parse_binary_io(graph: Graph) -> None:
    data = graph.serialize(format="jelly", encoding="utf-8")
    GraphHelper.assert_isomorphic(
        graph, Graph().parse(BytesIO(data), format="application/x-jelly-rdf")
    )


def test_serialize_to_str_fails(graph: Graph) -> None:
    """Jelly is binary, so it can't be returned as str."""
    with pytest.raises(ValueError, match="not UTF-8 text"):
        graph.serialize(format="jelly")


def test_namespaces() -> None:
    """Namespace declarations are only written when the options ask for them."""
    from pyjelly.options import StreamParameters
    from pyjelly.serialize.streams import SerializerOptions

    graph = Graph(bind_namespaces="none")
    graph.bind("eg", EG)
    graph.add((URIRef(f"{EG}s"), URIRef(f"{EG}p"), URIRef(f"{EG}o")))

    data = graph.serialize(format="jelly", encoding="utf-8")
    parsed = Graph(bind_namespaces="none").parse(data=data, format="jelly")
    assert "eg" not in dict(parsed.namespaces())

    options = SerializerOptions(params=StreamParameters(namespace_declarations=True))
    data = graph.serialize(format="jelly", encoding="utf-8", options=options)
    parsed = Graph(bind_namespaces="none").parse(data=data, format="jelly")
    assert dict(parsed.namespaces())["eg"] == URIRef(EG)


def test_xsd_string() -> None:
    """
    RDF 1.1 makes "x"^^xsd:string and "x" the same term, and Jelly writes both as
    "x". rdflib reads that as Literal("x"), which its == tells apart from
    Literal("x", datatype=XSD.string), though Literal.eq() doesn't.
    """
    original = Literal("x", datatype=XSD.string)
    graph = Graph()
    graph.add((URIRef(f"{EG}s"), URIRef(f"{EG}p"), original))
    data = graph.serialize(format="jelly", encoding="utf-8")
    parsed = Graph().parse(data=data, format="jelly")
    (literal,) = parsed.objects()
    assert literal == Literal("x")
    assert isinstance(literal, Literal) and literal.eq(original)


@pytest.mark.xfail(
    reason="pyjelly writes a ConjunctiveGraph as the triples of its default graph",
    raises=AssertionError,
    strict=True,
)
def test_conjunctive_graph() -> None:
    with pytest.warns(DeprecationWarning):
        graph = ConjunctiveGraph()
    graph.parse(data=TRIG_DATA, format="trig")
    data = graph.serialize(format="jelly", encoding="utf-8")
    parsed = Dataset().parse(data=data, format="jelly")
    assert len(parsed) == len(graph)


def test_language_tag_case() -> None:
    """
    Language tags that differ only in case are the same in RDF 1.2, and for
    rdflib's Literal.__eq__. Jelly may write either case for both. (The graphs
    are compared as sets, as rdflib.compare compares the tags with case.)
    """
    graph = Graph()
    graph.add((URIRef(f"{EG}s"), URIRef(f"{EG}p"), Literal("x", lang="en")))
    graph.add((URIRef(f"{EG}s"), URIRef(f"{EG}q"), Literal("x", lang="EN")))
    data = graph.serialize(format="jelly", encoding="utf-8")
    parsed = Graph().parse(data=data, format="jelly")
    assert set(parsed) == set(graph)
    assert parsed.value(URIRef(f"{EG}s"), URIRef(f"{EG}q")) == Literal("x", lang="EN")
