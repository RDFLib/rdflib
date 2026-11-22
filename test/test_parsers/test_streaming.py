"""Streaming delivers statements before EOF without retaining a graph."""

from __future__ import annotations

from io import BytesIO

import pytest

from rdflib import Literal, URIRef
from rdflib.graph import _TripleType
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


@pytest.mark.parametrize("format", ["turtle", "trig", "n3", "json-ld"])
def test_buffering_formats_are_rejected_before_reading(format):
    source = BytesIO(b"not RDF")
    with pytest.raises(ValueError, match="not supported for streaming"):
        Sink(lambda triple, graph: None).parse(source, format=format)
    assert source.tell() == 0
