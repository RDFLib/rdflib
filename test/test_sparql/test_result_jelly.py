"""Tests for SPARQL query results in Jelly-SPARQL, which pyjelly provides."""

from __future__ import annotations

from collections.abc import Mapping
from io import BytesIO, StringIO
from pathlib import Path

import pytest

import rdflib.plugin
from rdflib import XSD, BNode, Graph, Literal, URIRef, Variable
from rdflib.query import Result, ResultParser, ResultSerializer
from rdflib.term import Identifier
from test.data import TEST_DATA_DIR
from test.utils import GraphHelper
from test.utils.destination import DestinationType

GRAPH_DATA = """
@prefix eg: <http://example.com/> .

eg:s0 eg:p0 eg:o0 , "plain" , "English"@en , 42 , [ eg:p1 "nested" ] .
eg:s1 eg:p0 eg:o1 .
"""

SELECT_QUERY = """
PREFIX eg: <http://example.com/>
SELECT ?s ?o ?unbound WHERE {
    ?s eg:p0 ?o
    OPTIONAL { ?s eg:none ?unbound }
}
ORDER BY ?s ?o
"""


@pytest.fixture(scope="module")
def graph() -> Graph:
    return Graph().parse(data=GRAPH_DATA, format="turtle")


@pytest.fixture(scope="module")
def select_result(graph: Graph) -> Result:
    return graph.query(SELECT_QUERY)


@pytest.mark.parametrize(
    ("kind", "class_name"),
    [
        (ResultParser, "RDFLibJellySparqlParser"),
        (ResultSerializer, "RDFLibJellySparqlSerializer"),
    ],
)
@pytest.mark.parametrize("name", ["jelly", "jellys", "application/x-jelly-sparql"])
def test_plugins(name: str, kind: type, class_name: str) -> None:
    """The format names and the media type all give pyjelly's plugin."""
    assert rdflib.plugin.get(name, kind).__name__ == class_name


@pytest.mark.parametrize(
    "destination_type",
    [
        DestinationType.RETURN,
        DestinationType.BINARY_IO,
        DestinationType.STR_PATH,
        DestinationType.FILE_URI,
    ],
)
def test_select_roundtrip(
    tmp_path: Path, select_result: Result, destination_type: DestinationType
) -> None:
    with destination_type.make_ref(tmp_path) as dest_ref:
        destination = None if dest_ref is None else dest_ref.param
        data = select_result.serialize(destination, format="jelly")  # type: ignore[arg-type]
    if dest_ref is not None:
        assert data is None
        data = dest_ref.path.read_bytes()
    assert isinstance(data, bytes)

    parsed = Result.parse(BytesIO(data), format="jelly")
    assert parsed.type == "SELECT"
    assert parsed.vars == select_result.vars
    assert len(parsed) == 6
    # The blank node gets a new label, so it is compared apart
    rows = [_without_bnodes(row) for row in parsed.bindings]
    assert rows == [_without_bnodes(row) for row in select_result.bindings]
    assert all(Variable("unbound") not in row for row in parsed.bindings)


def _without_bnodes(
    row: Mapping[Variable, Identifier],
) -> dict[Variable, Identifier]:
    return {
        var: BNode("b") if isinstance(value, BNode) else value
        for var, value in row.items()
    }


@pytest.mark.parametrize("answer", [True, False])
def test_ask_roundtrip(graph: Graph, answer: bool) -> None:
    query = "ASK { ?s ?p ?o }" if answer else "ASK { ?s ?p <urn:none> }"
    data = graph.query(query).serialize(format="jelly")
    assert isinstance(data, bytes)
    parsed = Result.parse(BytesIO(data), format="jelly")
    assert parsed.type == "ASK"
    assert parsed.askAnswer is answer


def test_construct(graph: Graph) -> None:
    """
    The result of a CONSTRUCT query is a graph, which is written in Jelly-RDF.
    rdflib reads it by its media type, as "jelly" is Jelly-SPARQL for results.
    """
    result = graph.query("CONSTRUCT WHERE { ?s ?p ?o }")
    data = result.serialize(format="jelly")
    assert isinstance(data, bytes)
    parsed = Result.parse(BytesIO(data), content_type="application/x-jelly-rdf")
    assert parsed.type == "CONSTRUCT"
    assert parsed.graph is not None
    GraphHelper.assert_isomorphic(graph, parsed.graph)


def test_text_streams_fail(select_result: Result) -> None:
    """Jelly-SPARQL is binary, so text streams don't work."""
    with pytest.raises(TypeError):
        select_result.serialize(StringIO(), format="jelly")
    data = select_result.serialize(format="jelly")
    assert isinstance(data, bytes)
    with pytest.raises(TypeError):
        Result.parse(StringIO(data.decode("latin-1")), format="jelly")


# The W3C SPARQL test suites have the expected results of many queries
W3C_RESULT_FILES = sorted(
    path
    for path in (TEST_DATA_DIR / "suites" / "w3c").rglob("*")
    if path.suffix in (".srx", ".srj")
)


def _w3c_result_params():
    for path in W3C_RESULT_FILES:
        yield pytest.param(path, id=f"{path.relative_to(TEST_DATA_DIR).as_posix()}")


def _comparable(value: Identifier | None) -> object:
    """
    Make a value comparable as an RDF term, which rdflib's Literal doesn't do
    in every case: "x"^^xsd:string is the same term as "x", and language tags
    are compared without case (as in RDF 1.2, and rdflib's Literal). Blank
    nodes get new labels in a roundtrip.
    """
    if isinstance(value, BNode):
        return BNode("b")
    if isinstance(value, Literal):
        language = value.language
        if language is not None:
            return ("lang", str(value), language.lower())
        if value.datatype == XSD.string:
            return Literal(str(value))
    return value


@pytest.mark.parametrize("path", list(_w3c_result_params()))
def test_w3c_results_roundtrip(path: Path) -> None:
    """
    The expected results of the W3C SPARQL tests are the same after a
    roundtrip through Jelly-SPARQL, as through the other result formats.
    """
    format = "xml" if path.suffix == ".srx" else "json"
    try:
        with path.open("rb") as source:
            expected = Result.parse(source, format=format)
    except Exception:
        pytest.skip("rdflib can't read this result file")

    data = expected.serialize(format="jelly")
    assert isinstance(data, bytes)
    parsed = Result.parse(BytesIO(data), format="jelly")

    assert parsed.type == expected.type
    if expected.type == "ASK":
        assert parsed.askAnswer == expected.askAnswer
        return
    assert parsed.vars == expected.vars
    assert expected.vars is not None
    assert [
        [_comparable(row.get(var)) for var in expected.vars] for row in parsed.bindings
    ] == [
        [_comparable(row.get(var)) for var in expected.vars]
        for row in expected.bindings
    ]


def test_w3c_result_files_found() -> None:
    assert len(W3C_RESULT_FILES) > 300


def test_namespace_bindings_in_results() -> None:
    """Results keep the URIRefs as they are, no matter the bound namespaces."""
    graph = Graph()
    graph.bind("eg", "http://example.com/")
    graph.add((URIRef("http://example.com/s"), URIRef("urn:p"), Literal(1)))
    data = graph.query("SELECT ?s ?o { ?s ?p ?o }").serialize(format="jelly")
    assert isinstance(data, bytes)
    parsed = Result.parse(BytesIO(data), format="jelly")
    assert list(parsed) == [(URIRef("http://example.com/s"), Literal(1))]
