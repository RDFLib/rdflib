"""Streaming delivers statements before EOF without retaining a graph."""

from __future__ import annotations

import tracemalloc
from io import BytesIO, RawIOBase, StringIO

import pytest

from examples.streaming_parse import convert
from rdflib import BNode, Literal, URIRef
from rdflib.exceptions import ParserError
from rdflib.graph import _TripleType
from rdflib.parser import InputSource
from rdflib.sink import Sink
from rdflib.term import Identifier

NT = b'<urn:s> <urn:p> "caf\xc3\xa9" .\n'
NQ = b'<urn:s> <urn:p> "caf\xc3\xa9" <urn:g> .\n'
XML_START = (
    b'<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" '
    b'xmlns:ex="urn:example:">'
)
XML_TRIPLE = (
    b'<rdf:Description rdf:about="urn:s"><ex:p>caf\xc3\xa9</ex:p></rdf:Description>'
)


class ChunkedInput(BytesIO):
    def read(self, size: int | None = -1) -> bytes:
        assert size is not None and size >= 0, (
            "A streaming parser must not read the entire input"
        )
        return super().read(min(size, 17))


@pytest.mark.parametrize(
    ("format", "data", "predicate", "context"),
    [
        ("nt", NT * 1000, URIRef("urn:p"), None),
        ("nquads", NQ * 1000, URIRef("urn:p"), URIRef("urn:g")),
        (
            "xml",
            XML_START + XML_TRIPLE * 1000 + b"</rdf:RDF>",
            URIRef("urn:example:p"),
            None,
        ),
    ],
)
def test_statements_arrive_before_eof(format, data, predicate, context):
    source = ChunkedInput(data)
    count = 0

    def accept(triple: _TripleType, graph: Identifier | None) -> None:
        nonlocal count
        if count == 0:
            assert source.tell() < len(data)
        assert triple == (URIRef("urn:s"), predicate, Literal("caf\u00e9"))
        assert graph == context
        count += 1

    sink = Sink(accept)
    assert sink.parse(source, format=format) is sink
    assert count == 1000


def test_nquads_default_and_named_graphs():
    statements = []
    Sink(lambda triple, graph: statements.append((triple, graph))).parse(
        data=NT + NQ, format="nquads"
    )
    assert [graph for triple, graph in statements] == [None, URIRef("urn:g")]


def test_ntriples_delivery_order_and_literal_datatypes():
    statements = []
    Sink(lambda triple, graph: statements.append(triple)).parse(
        data=(
            '<urn:s1> <urn:p> "salut"@fr .\n'
            '<urn:s2> <urn:p> "2"^^<http://www.w3.org/2001/XMLSchema#integer> .\n'
            '<urn:s1> <urn:p> "salut"@fr .\n'
        ),
        format="nt",
    )
    assert [triple[0] for triple in statements] == [
        URIRef("urn:s1"),
        URIRef("urn:s2"),
        URIRef("urn:s1"),
    ]
    assert statements[0][2] == Literal("salut", lang="fr")
    assert statements[1][2] == Literal(2)
    assert statements[0] == statements[2]


@pytest.mark.parametrize("owned", [False, True])
def test_successful_parse_honors_input_source_ownership(owned):
    stream = ChunkedInput(NT)
    source = InputSource()
    source.setByteStream(stream)
    source.auto_close = owned
    Sink(lambda triple, graph: None).parse(source, format="nt")
    assert stream.closed is owned


def test_file_path_and_relative_rdfxml_identifiers(tmp_path):
    path = tmp_path / "input.rdf"
    path.write_bytes(
        XML_START
        + b'<rdf:Description rdf:about="s"><ex:p rdf:resource="o"/></rdf:Description>'
        + b"</rdf:RDF>"
    )
    statements = []
    Sink(lambda triple, graph: statements.append((triple, graph))).parse(
        path, format="xml"
    )
    assert statements[0][0][0] == URIRef((tmp_path / "s").as_uri())
    assert statements[0][0][2] == URIRef((tmp_path / "o").as_uri())
    assert statements[0][1] is None


@pytest.mark.parametrize("format", ["turtle", "trig", "n3", "json-ld"])
def test_buffering_formats_are_rejected_before_reading(format):
    source = BytesIO(b"not RDF")
    with pytest.raises(ValueError, match="not supported for streaming"):
        Sink(lambda triple, graph: None).parse(source, format=format)
    assert source.tell() == 0


@pytest.mark.parametrize(
    ("format", "data"),
    [
        ("nt", NT * 1000),
        ("nquads", NQ * 1000),
        ("xml", XML_START + XML_TRIPLE * 1000 + b"</rdf:RDF>"),
    ],
)
@pytest.mark.parametrize("text", [False, True])
def test_borrowed_stream_is_not_closed(format, data, text):
    source = StringIO(data.decode("utf-8")) if text else ChunkedInput(data)
    Sink(lambda triple, graph: None).parse(source, format=format)
    assert not source.closed


class StopProcessingError(Exception):
    pass


@pytest.mark.parametrize(
    ("format", "data"),
    [
        ("nt", NT * 1000),
        ("nquads", NQ * 1000),
        ("xml", XML_START + XML_TRIPLE * 1000 + b"</rdf:RDF>"),
    ],
)
@pytest.mark.parametrize("owned", [False, True])
def test_callback_failure_stops_input_and_honors_ownership(format, data, owned):
    stream = ChunkedInput(data)
    source = InputSource()
    source.setByteStream(stream)
    source.auto_close = owned
    failure = StopProcessingError("enough statements")
    calls = 0

    def accept(triple, graph):
        nonlocal calls
        calls += 1
        assert stream.tell() < len(data)
        raise failure

    with pytest.raises(StopProcessingError) as caught:
        Sink(accept).parse(source, format=format)
    assert caught.value is failure
    assert calls == 1
    assert stream.closed is owned


@pytest.mark.parametrize("owned", [False, True])
def test_parse_error_keeps_emitted_statements_and_honors_ownership(owned):
    stream = ChunkedInput(NT + b"not valid N-Triples\n")
    source = InputSource()
    source.setByteStream(stream)
    source.auto_close = owned
    statements = []
    sink = Sink(lambda triple, graph: statements.append(triple))
    with pytest.raises(ParserError):
        sink.parse(source, format="nt")
    assert len(statements) == 1
    assert stream.closed is owned
    sink.parse(data=NT, format="nt")
    assert len(statements) == 2


def test_blank_nodes_are_shared_within_but_not_between_documents():
    statements = []
    sink = Sink(lambda triple, graph: statements.append((triple, graph)))
    data = "_:a <urn:p> _:b .\n_:a <urn:p> _:b _:g .\n"
    sink.parse(data=data, format="nquads")
    sink.parse(data=data, format="nquads")
    assert statements[0][0] == statements[1][0]
    assert statements[2][0] == statements[3][0]
    assert statements[0][0] != statements[2][0]
    assert isinstance(statements[1][1], BNode)
    assert statements[1][1] != statements[3][1]


def test_rdfxml_base_uri_is_not_a_graph_name():
    statements = []
    Sink(lambda triple, graph: statements.append((triple, graph))).parse(
        data=XML_START
        + b'<rdf:Description rdf:about="s"><ex:p rdf:resource="o"/></rdf:Description>'
        + b"</rdf:RDF>",
        format="xml",
        publicID="http://example.org/base/",
    )
    assert statements == [
        (
            (
                URIRef("http://example.org/base/s"),
                URIRef("urn:example:p"),
                URIRef("http://example.org/base/o"),
            ),
            None,
        )
    ]


@pytest.mark.parametrize("format", ["nt11", "ntriples", "application/n-triples"])
def test_ntriples_aliases(format):
    statements = []
    Sink(lambda triple, graph: statements.append(triple)).parse(data=NT, format=format)
    assert len(statements) == 1


@pytest.mark.parametrize(
    ("format", "data"),
    [
        ("application/n-quads", NQ),
        ("application/rdf+xml", XML_START + XML_TRIPLE + b"</rdf:RDF>"),
    ],
)
def test_media_types(format, data):
    statements = []
    Sink(lambda triple, graph: statements.append(triple)).parse(
        data=data, format=format
    )
    assert len(statements) == 1


class GeneratedStatements(RawIOBase):
    """Generate distinct statements on demand without storing the document."""

    def __init__(self, count: int, named: bool = False):
        super().__init__()
        self.remaining = count
        self.pending = b""
        self.named = named

    def read(self, size: int | None = -1) -> bytes:
        assert size is not None and size >= 0
        while len(self.pending) < size and self.remaining:
            self.remaining -= 1
            graph = f" <urn:g{self.remaining}>" if self.named else ""
            self.pending += (
                f"<urn:s{self.remaining}> <urn:p> <urn:o>{graph} .\n".encode()
            )
        result, self.pending = self.pending[:size], self.pending[size:]
        return result


@pytest.mark.parametrize("format", ["nt", "nquads"])
def test_large_input_does_not_accumulate_statements(format):
    count = 0

    def accept(triple, graph):
        nonlocal count
        count += 1

    # A retained graph of 50,000 distinct triples uses tens of megabytes.
    # Include source generation and parsing, but not a prebuilt input document.
    tracemalloc.start()
    try:
        Sink(accept).parse(
            GeneratedStatements(50_000, named=format == "nquads"), format=format
        )
        peak = tracemalloc.get_traced_memory()[1]
    finally:
        tracemalloc.stop()
    assert count == 50_000
    assert peak < 8 * 1024 * 1024


def test_streaming_conversion_example_preserves_quads(tmp_path):
    source = tmp_path / "input.nq"
    source.write_bytes(NT + NQ + NQ)
    destination = StringIO()
    assert convert(source, destination, "nquads") == 3
    assert len(destination.getvalue().splitlines()) == 3
    statements = []
    Sink(lambda triple, graph: statements.append((triple, graph))).parse(
        data=destination.getvalue(), format="nquads"
    )
    assert [graph for triple, graph in statements] == [
        None,
        URIRef("urn:g"),
        URIRef("urn:g"),
    ]
