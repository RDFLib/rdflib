from __future__ import annotations

import codecs
import io
import json
import re
from collections.abc import Callable
from functools import wraps
from pathlib import Path
from typing import Any, cast

import pytest

from rdflib import BNode, Dataset, Graph, Literal, URIRef, plugin
from rdflib.exceptions import ParserError
from rdflib.graph import QuotedGraph
from rdflib.parser import InputSource, Parser, StringInputSource
from rdflib.plugins.parsers.notation3 import N3Parser, TurtleParser
from rdflib.plugins.parsers.nquads import NQuadsParser
from rdflib.plugins.parsers.ntriples import NTParser
from rdflib.plugins.parsers.trig import TrigParser
from rdflib.plugins.parsers.trix import TriXParser
from rdflib.plugins.shared.jsonld import util as jsonld_util
from rdflib.plugins.stores.sparqlstore import SPARQLUpdateStore

SUBJECT = URIRef("urn:subject")
PREDICATE = URIRef("urn:predicate")
OBJECT = URIRef("urn:object")
GRAPH = URIRef("urn:graph")
TRIPLE = (SUBJECT, PREDICATE, OBJECT)
OPTION_TRIPLE = (URIRef("urn:option-subject"), PREDICATE, OBJECT)
RDFXML_PROPERTY = b"""<?xml version="1.0"?>
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
         xmlns:e="urn:">
  <rdf:Description rdf:about="urn:subject">
    <e:predicate rdf:resource="urn:object"/>
  </rdf:Description>
</rdf:RDF>
"""

TRIX = b"""<?xml version="1.0"?>
<TriX xmlns="http://www.w3.org/2004/03/trix/trix-1/">
  <graph>
    <uri>urn:graph</uri>
    <triple>
      <uri>urn:subject</uri>
      <uri>urn:predicate</uri>
      <uri>urn:object</uri>
    </triple>
  </graph>
</TriX>
"""


class NonSeekableBytes(io.BytesIO):
    def seekable(self) -> bool:
        return False

    def seek(self, *args: object, **kwargs: object) -> int:
        raise io.UnsupportedOperation("not seekable")

    def tell(self) -> int:
        raise io.UnsupportedOperation("not seekable")


class NonSeekableText(io.StringIO):
    def seekable(self) -> bool:
        return False

    def seek(self, *args: object, **kwargs: object) -> int:
        raise io.UnsupportedOperation("not seekable")

    def tell(self) -> int:
        raise io.UnsupportedOperation("not seekable")


def opaque_source(data: bytes, content_type: str) -> InputSource:
    source = InputSource("https://example.test/download")
    source.setPublicId("https://example.test/download")
    source.setByteStream(NonSeekableBytes(data))
    source.content_type = content_type
    return source


@pytest.fixture
def attempted_formats(monkeypatch: pytest.MonkeyPatch) -> set[str]:
    attempted: set[str] = set()
    depth = 0
    parsers = {
        name: plugin.get(name, Parser)
        for name in (
            "xml",
            "trix",
            "json-ld",
            "hext",
            "trig",
            "nquads",
            "turtle",
            "n3",
            "nt",
        )
    }
    original = {name: parser.parse for name, parser in parsers.items()}

    def record(name: str, parse: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(parse)
        def wrapped(*args: Any, **kwargs: Any) -> Any:
            nonlocal depth
            if depth == 0:
                attempted.add(name)
            depth += 1
            try:
                return parse(*args, **kwargs)
            finally:
                depth -= 1

        return wrapped

    for name, parser in parsers.items():
        monkeypatch.setattr(parser, "parse", record(name, original[name]))
    return attempted


def assert_attempts_reported(error: ParserError, attempted: set[str]) -> None:
    aliases = {
        "xml": r"xml|rdf[\s_/-]*xml",
        "trix": r"trix",
        "json-ld": r"json[\s_-]*ld|ld\+json",
        "hext": r"hext|hextuples",
        "trig": r"trig",
        "nquads": r"n[\s_-]*quads|nq",
        "turtle": r"turtle|ttl",
        "n3": r"n3|notation\s*3",
        "nt": r"nt|n[\s_-]*triples",
    }
    assert attempted, "No parser attempt was observed"
    for name in attempted:
        pattern = rf"(?<![a-z0-9])(?:{aliases[name]})(?:parser)?(?![a-z0-9])"
        assert re.search(pattern, str(error), re.IGNORECASE), (name, str(error))


@pytest.mark.parametrize(
    "content_type", ["application/octet-stream", "application/octet-binary"]
)
def test_opaque_media_types_detect_rdfxml(content_type: str) -> None:
    graph = Graph().parse(opaque_source(RDFXML_PROPERTY, content_type))
    assert set(graph) == {TRIPLE}


def test_opaque_rdfxml_honors_its_xml_encoding_declaration() -> None:
    data = (
        '<?xml version="1.0" encoding="ISO-8859-1"?>'
        '<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" '
        'xmlns:e="urn:"><rdf:Description rdf:about="urn:subject">'
        "<e:predicate>ä</e:predicate></rdf:Description></rdf:RDF>"
    ).encode("iso-8859-1")
    graph = Graph().parse(opaque_source(data, "application/octet-stream"))
    assert set(graph) == {(SUBJECT, PREDICATE, Literal("ä"))}


def test_trix_bytes_honor_their_xml_encoding_declaration() -> None:
    path = (
        Path(__file__).parents[1] / "data/suites/trix/trix-ng4j-alternateencoding.trix"
    )
    dataset = Dataset().parse(data=path.read_bytes(), format="auto")
    assert {quad[:3] for quad in dataset.quads()} == {
        (
            URIRef("http://example.org/#foo"),
            URIRef("http://example.org/#bar"),
            Literal("ä"),
        )
    }
    assert len(dataset) == 1


@pytest.mark.parametrize(
    ("data", "expected"),
    [
        ("<urn:subject> <urn:predicate> <urn:object> .", TRIPLE),
        ("@prefix e: <urn:> . e:subject e:predicate e:object .", TRIPLE),
        (
            '{"@id":"urn:subject","urn:predicate":{"@id":"urn:object"}}',
            TRIPLE,
        ),
        (
            '[{"@id":"urn:subject","urn:predicate":{"@id":"urn:object"}}]',
            TRIPLE,
        ),
        (RDFXML_PROPERTY, TRIPLE),
    ],
)
def test_explicit_auto_accepts_common_graph_formats(
    data: str | bytes, expected: tuple[URIRef, URIRef, URIRef]
) -> None:
    assert set(Graph().parse(data=data, format="auto")) == {expected}


def test_python_json_input_is_supported() -> None:
    document = {
        "@context": {"e": "urn:"},
        "@id": "e:subject",
        "e:predicate": {"@id": "e:object"},
    }
    graph = Graph().parse(data=cast(Any, document), format="auto")
    assert set(graph) == {TRIPLE}


@pytest.mark.parametrize("encoding", ["utf-8-sig", "utf-16", "utf-32"])
def test_jsonld_uses_its_byte_order_mark(encoding: str) -> None:
    data = json.dumps(
        {"@id": "urn:subject", "urn:predicate": {"@id": "urn:object"}}
    ).encode(encoding)
    assert set(Graph().parse(data=data, format="auto")) == {TRIPLE}


@pytest.mark.parametrize("encoding", ["utf-16", "utf-32"])
def test_bom_jsonld_with_utf8_only_accelerator(
    monkeypatch: pytest.MonkeyPatch, encoding: str
) -> None:
    class Utf8OnlyJSON:
        @staticmethod
        def loads(value: str | bytes) -> object:
            if isinstance(value, bytes):
                value = value.decode("utf-8")
            return json.loads(value)

    monkeypatch.setattr(jsonld_util, "_HAS_ORJSON", True)
    monkeypatch.setattr(jsonld_util, "orjson", Utf8OnlyJSON)
    data = json.dumps(
        {"@id": "urn:subject", "urn:predicate": {"@id": "urn:object"}}
    ).encode(encoding)
    assert set(Graph().parse(data=data, format="auto")) == {TRIPLE}


@pytest.mark.parametrize("encoding", ["utf-16", "utf-32"])
def test_linked_opaque_bom_jsonld_with_utf8_only_accelerator(
    monkeypatch: pytest.MonkeyPatch, encoding: str
) -> None:
    class Utf8OnlyJSON:
        @staticmethod
        def loads(value: str | bytes) -> object:
            if isinstance(value, bytes):
                value = value.decode("utf-8")
            return json.loads(value)

    monkeypatch.setattr(jsonld_util, "_HAS_ORJSON", True)
    monkeypatch.setattr(jsonld_util, "orjson", Utf8OnlyJSON)
    data = json.dumps(
        {"@id": "urn:subject", "urn:predicate": {"@id": "urn:object"}}
    ).encode(encoding)
    source = opaque_source(data, "application/octet-stream")
    source.url = "https://example.test/data"  # type: ignore[attr-defined]
    source.links = []  # type: ignore[attr-defined]
    assert set(Graph().parse(source)) == {TRIPLE}


@pytest.mark.parametrize(
    "data",
    [
        codecs.BOM_UTF8 + b"<urn:subject> <urn:predicate> <urn:object> .",
        RDFXML_PROPERTY.decode().encode("utf-16"),
    ],
)
def test_non_json_formats_use_their_byte_order_mark(data: bytes) -> None:
    assert set(Graph().parse(data=data, format="auto")) == {TRIPLE}


def test_text_ntriples_uses_its_byte_order_mark() -> None:
    graph = Graph().parse(
        data="\ufeff<urn:subject> <urn:predicate> <urn:object> .",
        format="auto",
    )
    assert set(graph) == {TRIPLE}


def test_nonseekable_stream_is_read_once_and_left_open() -> None:
    prefix = b"ignored by the caller\n"
    stream = NonSeekableBytes(prefix + RDFXML_PROPERTY)
    assert stream.read(len(prefix)) == prefix
    graph = Graph().parse(source=stream, format="auto")
    assert set(graph) == {TRIPLE}
    assert not cast(io.IOBase, stream).closed


def test_text_stream_is_supported_and_left_open() -> None:
    prefix = "ignored by the caller\n"
    stream = NonSeekableText(prefix + "<urn:subject> <urn:predicate> <urn:object> .")
    assert stream.read(len(prefix)) == prefix
    graph = Graph().parse(source=stream, format="auto")
    assert set(graph) == {TRIPLE}
    assert not cast(io.IOBase, stream).closed


def test_parsing_starts_at_the_callers_current_stream_position() -> None:
    stream = io.BytesIO(b"ignored\n<urn:subject> <urn:predicate> <urn:object> .")
    stream.seek(len(b"ignored\n"))
    assert set(Graph().parse(source=stream, format="auto")) == {TRIPLE}


def test_string_input_source_uses_the_character_stream_position() -> None:
    prefix = "ignored by the caller\n"
    source = StringInputSource(prefix + "<urn:subject> <urn:predicate> <urn:object> .")
    stream = source.getCharacterStream()
    assert stream is not None
    assert stream.read(len(prefix)) == prefix
    assert set(Graph().parse(source=source, format="auto")) == {TRIPLE}


def test_bytes_input_source_uses_the_character_stream_position() -> None:
    prefix = "ignored by the caller\n"
    source = StringInputSource(
        (prefix + "<urn:subject> <urn:predicate> <urn:object> .").encode("utf-8")
    )
    stream = source.getCharacterStream()
    assert stream is not None
    assert stream.read(len(prefix)) == prefix
    assert set(Graph().parse(source=source, format="auto")) == {TRIPLE}
    assert not cast(io.IOBase, stream).closed


def test_public_id_is_preserved_for_relative_iris() -> None:
    source = opaque_source(
        b"<subject> <predicate> <object> .", "application/octet-stream"
    )
    source.setPublicId("https://example.test/base/")
    graph = Graph().parse(source)
    assert set(graph) == {
        (
            URIRef("https://example.test/base/subject"),
            URIRef("https://example.test/base/predicate"),
            URIRef("https://example.test/base/object"),
        )
    }


def test_system_id_is_used_when_public_id_is_empty() -> None:
    source = InputSource("https://example.test/system/base/")
    source.setByteStream(io.BytesIO(b"<subject> <predicate> <object> ."))
    source.content_type = "application/octet-stream"
    graph = Graph().parse(source)
    assert set(graph) == {
        (
            URIRef("https://example.test/system/base/subject"),
            URIRef("https://example.test/system/base/predicate"),
            URIRef("https://example.test/system/base/object"),
        )
    }


def test_public_id_takes_precedence_when_both_identifiers_are_present() -> None:
    source = InputSource("https://system.example/base/")
    source.setPublicId("https://public.example/base/")
    source.setByteStream(io.BytesIO(b"<subject> <predicate> <object> ."))
    source.content_type = "application/octet-stream"
    graph = Graph().parse(source)
    assert set(graph) == {
        (
            URIRef("https://public.example/base/subject"),
            URIRef("https://public.example/base/predicate"),
            URIRef("https://public.example/base/object"),
        )
    }


def test_rdfxml_relative_iris_use_the_source_identifier() -> None:
    source = opaque_source(
        b"""<rdf:RDF
          xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
          xmlns:e="urn:">
          <rdf:Description rdf:about="subject">
            <e:predicate rdf:resource="object"/>
          </rdf:Description>
        </rdf:RDF>""",
        "application/octet-stream",
    )
    source.setPublicId("https://example.test/xml/")
    graph = Graph().parse(source)
    assert set(graph) == {
        (
            URIRef("https://example.test/xml/subject"),
            PREDICATE,
            URIRef("https://example.test/xml/object"),
        )
    }


def test_jsonld_relative_iris_use_the_source_identifier() -> None:
    source = opaque_source(
        b'{"@id":"subject","urn:predicate":{"@id":"object"}}',
        "application/octet-stream",
    )
    source.setPublicId("https://example.test/json/")
    assert set(Graph().parse(source)) == {
        (
            URIRef("https://example.test/json/subject"),
            PREDICATE,
            URIRef("https://example.test/json/object"),
        )
    }


def test_parser_options_are_forwarded_to_the_detected_parser() -> None:
    graph = Graph().parse(
        data="_:subject <urn:predicate> <urn:object> .",
        format="auto",
        skolemize=True,
    )
    subject = next(graph.subjects(PREDICATE, OBJECT))
    assert isinstance(subject, URIRef)


def test_jsonld_context_option_is_forwarded_to_the_detected_parser() -> None:
    graph = Graph().parse(
        data=cast(Any, {"@id": "e:subject", "e:predicate": {"@id": "e:object"}}),
        format="auto",
        context={"e": "urn:"},
    )
    assert set(graph) == {TRIPLE}


def test_dataset_parser_options_are_forwarded() -> None:
    dataset = Dataset().parse(
        data='["_:subject","urn:predicate","urn:object","globalId","","urn:graph"]',
        format="auto",
        skolemize=True,
    )
    subject = next(dataset.graph(GRAPH).subjects(PREDICATE, OBJECT))
    assert isinstance(subject, URIRef)


def test_arbitrary_parser_options_reach_the_selected_parser(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    marker = object()

    def parse_with_marker(
        _self: object,
        _source: InputSource,
        sink: Graph,
        **kwargs: object,
    ) -> None:
        if kwargs.get("probe_marker") is not marker:
            raise ParserError("missing parser option")
        sink.add(TRIPLE)

    monkeypatch.setattr(TriXParser, "parse", parse_with_marker)
    graph = Graph().parse(
        data=TRIX,
        format="auto",
        probe_marker=marker,
    )
    assert set(graph) == {TRIPLE}


def test_arbitrary_parser_options_reach_a_dataset_parser(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    marker = object()

    def parse_with_marker(
        _self: object,
        _source: InputSource,
        sink: Graph,
        **kwargs: object,
    ) -> None:
        if kwargs.get("probe_marker") is not marker:
            raise ParserError("missing parser option")
        sink.add(TRIPLE)

    monkeypatch.setattr(NQuadsParser, "parse", parse_with_marker)
    dataset = Dataset().parse(
        data="<urn:subject> <urn:predicate> <urn:object> <urn:graph> .",
        format="auto",
        probe_marker=marker,
    )
    assert set(dataset.default_graph) == {TRIPLE}


@pytest.mark.parametrize(
    ("parser_class", "data"),
    [
        (
            TrigParser,
            "GRAPH <urn:graph> { <urn:subject> <urn:predicate> <urn:object> . }",
        ),
        (N3Parser, "{ <urn:a> <urn:p> <urn:b> } => {} ."),
        (NTParser, "<urn:subject> <urn:predicate> <urn:object> ."),
    ],
)
def test_arbitrary_options_reach_remaining_parser_families(
    monkeypatch: pytest.MonkeyPatch,
    parser_class: type[object],
    data: str,
) -> None:
    marker = object()

    def parse_with_marker(
        _self: object,
        _source: InputSource,
        sink: Graph,
        **kwargs: object,
    ) -> None:
        if kwargs.get("probe_marker") is not marker:
            raise ParserError("missing parser option")
        sink.add(OPTION_TRIPLE)

    monkeypatch.setattr(parser_class, "parse", parse_with_marker)
    graph = Graph().parse(data=data, format="auto", probe_marker=marker)
    assert set(graph) == {OPTION_TRIPLE}


def test_long_ntriples_statement_uses_complete_content_for_detection(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    marker = object()

    def parse_with_marker(
        _self: object,
        _source: InputSource,
        sink: Graph,
        **kwargs: object,
    ) -> None:
        if kwargs.get("probe_marker") is not marker:
            raise ParserError("missing parser option")
        sink.add(OPTION_TRIPLE)

    monkeypatch.setattr(NTParser, "parse", parse_with_marker)
    data = '<urn:subject> <urn:predicate> "' + ("x" * 70_000) + '" .'
    graph = Graph().parse(data=data, format="auto", probe_marker=marker)
    assert set(graph) == {OPTION_TRIPLE}


def test_turtle_candidate_is_available_independently_of_n3(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    marker = object()

    def turtle_parse(
        _self: object, _source: InputSource, sink: Graph, **kwargs: object
    ) -> None:
        assert kwargs.get("probe_marker") is marker
        sink.add(OPTION_TRIPLE)

    def n3_parse(
        _self: object, _source: InputSource, sink: Graph, **_kwargs: object
    ) -> None:
        sink.add(TRIPLE)

    monkeypatch.setattr(TurtleParser, "parse", turtle_parse)
    monkeypatch.setattr(N3Parser, "parse", n3_parse)
    graph = Graph().parse(
        data="@prefix e: <urn:> . e:subject e:predicate e:object .",
        format="auto",
        probe_marker=marker,
    )
    assert set(graph) == {OPTION_TRIPLE}


def test_ntriples_candidate_is_not_replaced_by_superset_parsers(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def reject_overlapping_candidate(
        _self: object, _source: InputSource, _sink: Graph, **_kwargs: object
    ) -> None:
        raise ParserError("overlapping candidate disabled")

    for parser_class in (NQuadsParser, TurtleParser, N3Parser):
        monkeypatch.setattr(parser_class, "parse", reject_overlapping_candidate)

    assert set(
        Graph().parse(
            data="<urn:subject> <urn:predicate> <urn:object> .",
            format="auto",
        )
    ) == {TRIPLE}


def test_nquads_blank_node_context_is_forwarded_across_parses() -> None:
    data = "_:shared <urn:predicate> <urn:object> <urn:graph> ."
    bnode_context: dict[str, BNode] = {}
    dataset = Dataset()
    dataset.parse(data=data, format="auto", bnode_context=bnode_context)
    dataset.parse(data=data, format="auto", bnode_context=bnode_context)
    assert len(dataset.graph(GRAPH)) == 1


def test_detected_rdfxml_preserves_requested_blank_node_ids() -> None:
    data = b"""<rdf:RDF
      xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
      <rdf:Description rdf:nodeID="kept">
        <rdf:type rdf:resource="urn:Type"/>
      </rdf:Description>
    </rdf:RDF>"""
    graph = Graph().parse(data=data, format="auto", preserve_bnode_ids=True)
    assert next(graph.subjects()) == BNode("kept")


def test_existing_statements_are_retained_after_success() -> None:
    original = (URIRef("urn:old"), PREDICATE, Literal("value"))
    graph = Graph()
    graph.add(original)
    returned = graph.parse(
        data="<urn:subject> <urn:predicate> <urn:object> .", format="auto"
    )
    assert returned is graph
    assert set(graph) == {original, TRIPLE}


def test_all_failed_attempts_leave_graph_and_namespaces_unchanged(
    attempted_formats: set[str],
) -> None:
    original = (URIRef("urn:old"), PREDICATE, Literal("value"))
    graph = Graph(bind_namespaces="none")
    graph.add(original)
    graph.bind("old", URIRef("urn:old:"))
    before_namespaces = list(graph.namespaces())

    with pytest.raises(ParserError) as error:
        graph.parse(data="<rdf:RDF", format="auto")

    assert set(graph) == {original}
    assert list(graph.namespaces()) == before_namespaces
    assert_attempts_reported(error.value, attempted_formats)


def test_failure_after_valid_statements_does_not_leak_partial_results() -> None:
    graph = Graph(bind_namespaces="none")
    graph.bind("old", URIRef("urn:old:"))
    before_namespaces = list(graph.namespaces())
    data = """@prefix leaked: <urn:leaked:> .
    leaked:s leaked:p leaked:o .
    leaked:broken leaked:p "unterminated
    """

    with pytest.raises(ParserError):
        graph.parse(data=data, format="auto")

    assert len(graph) == 0
    assert list(graph.namespaces()) == before_namespaces


def test_failed_candidate_is_discarded_before_later_success(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    leaked = (URIRef("urn:leaked"), PREDICATE, OBJECT)

    def fail_after_mutation(
        _self: object, _source: InputSource, sink: Graph, **_kwargs: object
    ) -> None:
        sink.bind("leaked", URIRef("urn:leaked:"))
        sink.add(leaked)
        raise ParserError("controlled candidate failure")

    monkeypatch.setattr(TriXParser, "parse", fail_after_mutation)
    graph = Graph(bind_namespaces="none").parse(
        data=(
            "@prefix e: <urn:> .\n"
            "# http://www.w3.org/2004/03/trix/trix-1/\n"
            "e:subject e:predicate e:object ."
        ),
        format="auto",
    )
    assert set(graph) == {TRIPLE}
    assert "leaked" not in dict(graph.namespaces())


def test_detected_turtle_namespaces_are_committed() -> None:
    graph = Graph(bind_namespaces="none")
    graph.bind("existing", URIRef("urn:existing:"))
    graph.parse(
        data="@prefix zzdet: <urn:detected:> . zzdet:s zzdet:p zzdet:o .",
        format="auto",
    )
    namespaces = dict(graph.namespaces())
    assert namespaces["existing"] == URIRef("urn:existing:")
    assert namespaces["zzdet"] == URIRef("urn:detected:")


def test_detected_rdfxml_namespaces_are_committed() -> None:
    graph = Graph(bind_namespaces="none")
    graph.bind("existing", URIRef("urn:existing:"))
    graph.parse(
        data=b"""<rdf:RDF
          xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
          xmlns:detected="urn:detected:">
          <rdf:Description rdf:about="urn:subject">
            <detected:predicate rdf:resource="urn:object"/>
          </rdf:Description>
        </rdf:RDF>""",
        format="auto",
    )
    namespaces = dict(graph.namespaces())
    assert namespaces["existing"] == URIRef("urn:existing:")
    assert namespaces["detected"] == URIRef("urn:detected:")


@pytest.mark.parametrize(
    "data",
    [
        "GRAPH <urn:graph> { <urn:subject> <urn:predicate> <urn:object> . }",
        "<urn:subject> <urn:predicate> <urn:object> <urn:graph> .",
        '["urn:subject","urn:predicate","urn:object","globalId","","urn:graph"]',
        TRIX,
        {
            "@id": "urn:graph",
            "@graph": [
                {
                    "@id": "urn:subject",
                    "urn:predicate": {"@id": "urn:object"},
                }
            ],
        },
    ],
)
def test_dataset_formats_preserve_named_graphs(
    data: str | bytes | dict[str, object],
) -> None:
    dataset = Dataset().parse(data=cast(Any, data), format="auto")
    assert set(dataset.graph(GRAPH)) == {TRIPLE}
    assert TRIPLE not in dataset.default_graph


@pytest.mark.parametrize(
    "data",
    [
        RDFXML_PROPERTY,
        "@prefix e: <urn:> . e:subject e:predicate e:object .",
        "{ <urn:a> <urn:p> <urn:b> } => {} .",
        "<urn:subject> <urn:predicate> <urn:object> .",
    ],
)
def test_dataset_auto_detects_graph_serializations(data: str | bytes) -> None:
    dataset = Dataset().parse(data=cast(Any, data), format="auto")
    assert len(dataset.default_graph) == 1


@pytest.mark.parametrize(
    "data",
    [
        b"""\n<t:TriX xmlns:t="http://www.w3.org/2004/03/trix/trix-1/">
          <t:graph><t:uri>urn:graph</t:uri><t:triple>
            <t:uri>urn:subject</t:uri><t:uri>urn:predicate</t:uri>
            <t:uri>urn:object</t:uri>
          </t:triple></t:graph>
        </t:TriX>""",
        '\n  ["urn:subject", "urn:predicate", "urn:object", "globalId", "", "urn:graph"]\n',
    ],
)
def test_dataset_format_detection_accepts_lexical_variants(data: str | bytes) -> None:
    dataset = Dataset().parse(data=cast(Any, data), format="auto")
    assert set(dataset.graph(GRAPH)) == {TRIPLE}


def test_detected_dataset_namespaces_are_added_without_replacing_existing_ones() -> (
    None
):
    dataset = Dataset()
    dataset.bind("existing", URIRef("urn:existing:"))
    dataset.parse(
        data=(
            "@prefix detected: <urn:detected:> . "
            "detected:graph { detected:subject detected:predicate detected:object . }"
        ),
        format="auto",
    )
    namespaces = dict(dataset.namespaces())
    assert namespaces["existing"] == URIRef("urn:existing:")
    assert namespaces["detected"] == URIRef("urn:detected:")


def test_default_and_named_nquads_are_kept_separate() -> None:
    existing_graph = URIRef("urn:existing-graph")
    existing = (URIRef("urn:existing"), PREDICATE, Literal("retained"))
    dataset = Dataset()
    dataset.graph(existing_graph).add(existing)
    dataset.parse(
        data=(
            "<urn:subject> <urn:predicate> <urn:default> .\n"
            "<urn:subject> <urn:predicate> <urn:object> <urn:graph> .\n"
        ),
        format="auto",
    )
    assert (SUBJECT, PREDICATE, URIRef("urn:default")) in dataset.default_graph
    assert set(dataset.graph(GRAPH)) == {TRIPLE}
    assert set(dataset.graph(existing_graph)) == {existing}


def test_failed_dataset_detection_preserves_all_existing_state(
    attempted_formats: set[str],
) -> None:
    existing_graph = URIRef("urn:existing-graph")
    existing = (URIRef("urn:existing"), PREDICATE, Literal("retained"))
    dataset = Dataset()
    dataset.graph(existing_graph).add(existing)
    dataset.bind("existing", URIRef("urn:existing:"))
    before_namespaces = list(dataset.namespaces())
    before_graphs = {graph.identifier: set(graph) for graph in dataset.graphs()}

    with pytest.raises(ParserError) as error:
        dataset.parse(
            data=("<urn:leaked> <urn:p> <urn:o> <urn:leaked-graph> .\nnot valid RDF"),
            format="auto",
        )

    assert {graph.identifier: set(graph) for graph in dataset.graphs()} == before_graphs
    assert list(dataset.namespaces()) == before_namespaces
    assert_attempts_reported(error.value, attempted_formats)


def test_failed_dataset_candidate_is_discarded_before_later_success(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    leaked_graph = URIRef("urn:leaked-graph")
    leaked = (URIRef("urn:leaked"), PREDICATE, OBJECT)

    def fail_after_mutation(
        _self: object,
        _source: InputSource,
        sink: Graph,
        **_kwargs: object,
    ) -> None:
        sink.bind("leaked", URIRef("urn:leaked:"))
        Graph(store=sink.store, identifier=leaked_graph).add(leaked)
        raise ParserError("controlled dataset candidate failure")

    monkeypatch.setattr(TriXParser, "parse", fail_after_mutation)
    dataset = Dataset().parse(
        data=(
            "# http://www.w3.org/2004/03/trix/trix-1/\n"
            "GRAPH <urn:graph> { <urn:subject> <urn:predicate> <urn:object> . }"
        ),
        format="auto",
    )
    assert set(dataset.graph(GRAPH)) == {TRIPLE}
    assert len(dataset.graph(leaked_graph)) == 0
    assert "leaked" not in dict(dataset.namespaces())


@pytest.mark.parametrize(
    "content_type", ["application/octet-stream", "application/octet-binary"]
)
def test_opaque_dataset_content_uses_content_detection(content_type: str) -> None:
    source = opaque_source(
        b"<urn:subject> <urn:predicate> <urn:object> <urn:graph> .",
        content_type,
    )
    dataset = Dataset().parse(source)
    assert set(dataset.graph(GRAPH)) == {TRIPLE}


def test_dataset_preserves_source_identifiers_for_relative_trig_iris() -> None:
    source = InputSource("https://system.example/dataset/")
    source.setPublicId("https://public.example/dataset/")
    source.setByteStream(
        io.BytesIO(b"GRAPH <graph> { <subject> <predicate> <object> . }")
    )
    source.content_type = "application/octet-stream"
    dataset = Dataset().parse(source)
    assert set(dataset.graph(URIRef("https://public.example/dataset/graph"))) == {
        (
            URIRef("https://public.example/dataset/subject"),
            URIRef("https://public.example/dataset/predicate"),
            URIRef("https://public.example/dataset/object"),
        )
    }


def test_graph_auto_detects_real_trix_content() -> None:
    graph = Graph().parse(data=TRIX, format="auto")
    assert set(Graph(store=graph.store, identifier=GRAPH)) == {TRIPLE}

    empty = (
        '<TriX xmlns="http://www.w3.org/2004/03/trix/trix-1/" '
        'xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"/>'
    )
    graph = Graph().parse(data=empty, format="auto")
    assert set(graph) == set()


@pytest.mark.parametrize(
    "data",
    [
        "GRAPH <urn:graph> { <urn:subject> <urn:predicate> <urn:object> . }",
        "<urn:subject> <urn:predicate> <urn:object> <urn:graph> .",
        '["urn:subject","urn:predicate","urn:object","globalId","","urn:graph"]',
    ],
)
def test_graph_auto_detects_named_graph_syntaxes(data: str) -> None:
    graph = Graph().parse(data=data, format="auto")
    assert set(Graph(store=graph.store, identifier=GRAPH)) == {TRIPLE}


def test_nonseekable_dataset_stream_is_left_open() -> None:
    stream = NonSeekableBytes(
        b"<urn:subject> <urn:predicate> <urn:object> <urn:graph> ."
    )
    dataset = Dataset().parse(source=stream, format="auto")
    assert set(dataset.graph(GRAPH)) == {TRIPLE}
    assert not cast(io.IOBase, stream).closed


def test_nonseekable_dataset_text_starts_at_the_current_position() -> None:
    prefix = "ignored by the caller\n"
    stream = NonSeekableText(
        prefix + "GRAPH <urn:graph> { <urn:subject> <urn:predicate> <urn:object> . }"
    )
    assert stream.read(len(prefix)) == prefix
    dataset = Dataset().parse(source=stream, format="auto")
    assert set(dataset.graph(GRAPH)) == {TRIPLE}
    assert not cast(io.IOBase, stream).closed


def test_dataset_uses_system_id_when_public_id_is_empty() -> None:
    source = InputSource("https://system.example/dataset/")
    source.setByteStream(
        io.BytesIO(b"GRAPH <graph> { <subject> <predicate> <object> . }")
    )
    source.content_type = "application/octet-stream"
    dataset = Dataset().parse(source)
    assert set(dataset.graph(URIRef("https://system.example/dataset/graph"))) == {
        (
            URIRef("https://system.example/dataset/subject"),
            URIRef("https://system.example/dataset/predicate"),
            URIRef("https://system.example/dataset/object"),
        )
    }


def test_turtle_uses_its_byte_order_mark() -> None:
    data = codecs.BOM_UTF8 + b"@prefix e: <urn:> . e:subject e:predicate e:object ."
    assert set(Graph().parse(data=data, format="auto")) == {TRIPLE}


def test_trig_preserves_shared_blank_nodes_across_graphs() -> None:
    dataset = Dataset().parse(
        data=(
            "_:shared <urn:predicate> <urn:default> . "
            "GRAPH <urn:graph> { _:shared <urn:predicate> <urn:object> . }"
        ),
        format="auto",
    )
    default_subject = next(
        dataset.default_graph.subjects(PREDICATE, URIRef("urn:default"))
    )
    named_subject = next(dataset.graph(GRAPH).subjects(PREDICATE, OBJECT))
    assert isinstance(default_subject, BNode)
    assert default_subject == named_subject


def test_dataset_starts_at_the_current_position_and_leaves_stream_open() -> None:
    prefix = b"ignored by the caller\n"
    stream = io.BytesIO(
        prefix + b"<urn:subject> <urn:predicate> <urn:object> <urn:graph> ."
    )
    stream.seek(len(prefix))
    dataset = Dataset().parse(source=stream, format="auto")
    assert set(dataset.graph(GRAPH)) == {TRIPLE}
    assert not cast(io.IOBase, stream).closed


def test_failed_dataset_detection_leaves_the_stream_open() -> None:
    stream = io.BytesIO(b"not an RDF document ]]]")
    with pytest.raises(ParserError):
        Dataset().parse(source=stream, format="auto")
    assert not cast(io.IOBase, stream).closed


def test_dataset_trix_uses_its_byte_order_mark() -> None:
    dataset = Dataset().parse(data=TRIX.decode().encode("utf-16"), format="auto")
    assert set(dataset.graph(GRAPH)) == {TRIPLE}


def test_dataset_nquads_uses_its_byte_order_mark() -> None:
    data = codecs.BOM_UTF8 + b"<urn:subject> <urn:predicate> <urn:object> <urn:graph> ."
    dataset = Dataset().parse(data=cast(Any, data), format="auto")
    assert set(dataset.graph(GRAPH)) == {TRIPLE}


def test_dataset_trig_uses_its_byte_order_mark() -> None:
    data = (
        codecs.BOM_UTF8
        + b"GRAPH <urn:graph> { <urn:subject> <urn:predicate> <urn:object> . }"
    )
    dataset = Dataset().parse(data=cast(Any, data), format="auto")
    assert set(dataset.graph(GRAPH)) == {TRIPLE}


def test_dataset_hextuples_uses_its_byte_order_mark() -> None:
    data = (
        codecs.BOM_UTF8
        + b'["urn:subject","urn:predicate","urn:object","globalId","","urn:graph"]'
    )
    dataset = Dataset().parse(data=cast(Any, data), format="auto")
    assert set(dataset.graph(GRAPH)) == {TRIPLE}


def test_n3_uses_its_byte_order_mark() -> None:
    data = codecs.BOM_UTF8 + b"{ <urn:a> <urn:p> <urn:b> } => {} ."
    graph = Graph().parse(data=data, format="auto")
    antecedent, consequent = next(
        graph.subject_objects(URIRef("http://www.w3.org/2000/10/swap/log#implies"))
    )
    assert isinstance(antecedent, QuotedGraph)
    assert isinstance(consequent, QuotedGraph)


def test_blank_node_identity_is_shared_across_detected_named_graphs() -> None:
    data = """_:shared <urn:predicate> <urn:first> <urn:one> .
    _:shared <urn:predicate> <urn:second> <urn:two> .
    _:shared <urn:predicate> <urn:default> .
    """
    dataset = Dataset().parse(data=cast(Any, data), format="auto")
    first = next(dataset.graph(URIRef("urn:one")).subjects())
    second = next(dataset.graph(URIRef("urn:two")).subjects())
    default = next(dataset.default_graph.subjects(PREDICATE, URIRef("urn:default")))
    assert isinstance(first, BNode)
    assert first == second == default


def test_n3_formulae_remain_quoted() -> None:
    data = "@prefix e: <urn:> . { e:a e:p e:b } => { e:c e:p e:d } ."
    graph = Graph().parse(data=data, format="auto")
    quoted = [
        context
        for context in graph.store.contexts()
        if isinstance(context, QuotedGraph)
    ]
    assert len(quoted) == 2
    assert sorted(len(context) for context in quoted) == [1, 1]
    antecedent, consequent = next(
        graph.subject_objects(URIRef("http://www.w3.org/2000/10/swap/log#implies"))
    )
    assert isinstance(antecedent, QuotedGraph)
    assert isinstance(consequent, QuotedGraph)
    assert antecedent.store is graph.store
    assert consequent.store is graph.store
    assert set(antecedent) == {(URIRef("urn:a"), URIRef("urn:p"), URIRef("urn:b"))}
    assert set(consequent) == {(URIRef("urn:c"), URIRef("urn:p"), URIRef("urn:d"))}

    graph = Graph().parse(
        data="@prefix e: <urn:> . e:subject e:predicate { e:a e:p e:b } .",
        format="auto",
    )
    assert len(graph) == 1
    formula = graph.value(SUBJECT, PREDICATE)
    assert isinstance(formula, QuotedGraph)
    assert formula.store is graph.store
    assert set(formula) == {(URIRef("urn:a"), URIRef("urn:p"), URIRef("urn:b"))}
    assert (URIRef("urn:a"), URIRef("urn:p"), URIRef("urn:b")) not in graph


def test_nested_n3_formula_terms_use_the_destination_store() -> None:
    data = (
        "@prefix e: <urn:> . "
        "{ { e:a e:p e:b } => { e:c e:p e:d } } => { e:e e:p e:f } ."
    )
    graph = Graph().parse(data=data, format="auto")
    formula_terms = [
        term
        for context in graph.store.contexts()
        for triple in context
        for term in triple
        if isinstance(term, QuotedGraph)
    ]
    assert len({term.identifier for term in formula_terms}) == 4
    assert all(term.store is graph.store for term in formula_terms)
    assert all(len(term) == 1 for term in formula_terms)


def test_empty_n3_formula_terms_use_the_destination_store() -> None:
    graph = Graph().parse(data="{} => {} .", format="auto")
    antecedent, consequent = next(
        graph.subject_objects(URIRef("http://www.w3.org/2000/10/swap/log#implies"))
    )
    assert isinstance(antecedent, QuotedGraph)
    assert isinstance(consequent, QuotedGraph)
    assert antecedent.store is graph.store
    assert consequent.store is graph.store
    assert len(antecedent) == len(consequent) == 0


def test_leading_comments_do_not_hide_the_format() -> None:
    data = (
        "# generated file\n# second line\n<urn:subject> <urn:predicate> <urn:object> ."
    )
    assert set(Graph().parse(data=data, format="auto")) == {TRIPLE}


def test_repeated_detection_appends_each_successful_parse() -> None:
    graph = Graph()
    graph.parse(
        data='<urn:first> <urn:predicate> "<rdf:RDF>" .',
        format="auto",
    )
    graph.parse(
        data=cast(Any, {"@id": "urn:second", "urn:predicate": {"@value": "json-ld"}}),
        format="auto",
    )
    assert set(graph.objects(None, PREDICATE)) == {
        Literal("<rdf:RDF>"),
        Literal("json-ld"),
    }


def test_unknown_opaque_data_reports_detection_failure() -> None:
    source = opaque_source(b"this is not RDF }", "application/octet-stream")
    stream = source.getByteStream()
    with pytest.raises(ParserError):
        Graph().parse(source)
    assert stream is not None
    assert not cast(io.IOBase, stream).closed


@pytest.mark.parametrize(
    "data",
    [
        "@prefix e: <urn:> . e:subject has e:predicate e:object .",
        "{ <urn:subject> <urn:predicate> <urn:object> . }",
    ],
)
def test_keyword_and_default_graph_forms_are_detected(data: str) -> None:
    dataset = Dataset().parse(data=cast(Any, data), format="auto")
    assert set(dataset.default_graph) == {TRIPLE}
    assert len(dataset) == 1


def test_auto_parse_appends_to_an_existing_sparql_graph(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    remote = Dataset()
    original = (URIRef("urn:existing"), PREDICATE, OBJECT)
    remote.graph(GRAPH).add(original)
    store = SPARQLUpdateStore(
        query_endpoint="https://example.test/query",
        update_endpoint="https://example.test/update",
    )

    def update(query: str) -> None:
        for match in re.finditer(r"\bCREATE\s+(SILENT\s+)?GRAPH\s+<([^>]+)>", query):
            if not match.group(1) and URIRef(match.group(2)) in {
                graph.identifier for graph in remote.graphs()
            }:
                raise RuntimeError("named graph already exists")
        remote.update(query)

    def query(text: str, **_kwargs: object) -> Any:
        return remote.query(text)

    monkeypatch.setattr(store, "_update", update)
    monkeypatch.setattr(store, "_query", query)
    graph = Graph(store=store, identifier=GRAPH)
    for subject in (SUBJECT, URIRef("urn:second")):
        graph.parse(
            data=f"{subject.n3()} {PREDICATE.n3()} {OBJECT.n3()} .",
            format="auto",
        )
    assert set(remote.graph(GRAPH)) == {
        original,
        TRIPLE,
        (URIRef("urn:second"), PREDICATE, OBJECT),
    }
