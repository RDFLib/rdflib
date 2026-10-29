"""Parser selection for RDF sources whose media type is unknown.

The parser buffers an input source once and replays it into isolated graphs.  A
successful attempt is copied to the caller's graph only after parsing finishes,
so a failed parser cannot leave triples behind for the next attempt or in the
destination graph.
"""

from __future__ import annotations

import codecs
import copy
import io
import json
import re
from dataclasses import dataclass
from typing import Any, Optional, Union, cast

import rdflib.plugin
from rdflib.exceptions import ParserError
from rdflib.graph import Graph, QuotedGraph
from rdflib.parser import InputSource, Parser, PythonInputSource, StringInputSource
from rdflib.term import IdentifiedNode, Node

__all__ = ["AutoDetectParser"]


_Payload = Union[str, bytes, dict[str, Any], list[Any]]


@dataclass(frozen=True)
class _Format:
    name: str
    priority: int


@dataclass(frozen=True)
class _Failure:
    format: str
    error: BaseException

    def summary(self) -> str:
        message = str(self.error).strip().replace("\n", " ")
        if len(message) > 160:
            message = f"{message[:157]}..."
        if message:
            return f"{self.format}: {type(self.error).__name__}: {message}"
        return f"{self.format}: {type(self.error).__name__}"


@dataclass(frozen=True)
class _ReplayableSource:
    payload: _Payload
    public_id: Optional[str]
    system_id: Optional[str]
    encoding: Optional[str]
    content_type: Optional[str]
    url: Optional[str]
    links: Optional[tuple[str, ...]]

    @classmethod
    def capture(cls, source: InputSource) -> _ReplayableSource:
        if isinstance(source, PythonInputSource):
            data = source.data
            if not isinstance(data, (dict, list)):
                raise ParserError(
                    "Automatic RDF format detection requires JSON-compatible "
                    "Python input or a readable character/byte stream."
                )
            return cls(
                copy.deepcopy(data),
                source.getPublicId(),
                source.getSystemId(),
                None,
                source.content_type,
                cast(Optional[str], getattr(source, "url", None)),
                cls._links(source),
            )

        character_stream = source.getCharacterStream()
        byte_stream = source.getByteStream()

        payload: object
        if isinstance(source, StringInputSource):
            character_position: Optional[int] = None
            byte_position: Optional[int] = None
            if character_stream is not None:
                tell = getattr(character_stream, "tell", None)
                try:
                    if callable(tell):
                        character_position = tell()
                except OSError:
                    pass
            if byte_stream is not None:
                tell = getattr(byte_stream, "tell", None)
                try:
                    if callable(tell):
                        byte_position = tell()
                except OSError:
                    pass

            # A TextIOWrapper shares the byte cursor. Equal positions mean
            # there is no unread decoded text to preserve; retaining bytes lets
            # XML parsers honor an encoding declaration. Read-ahead instead
            # leaves the character cursor behind the byte cursor.
            shared_byte_position = (
                isinstance(character_stream, io.TextIOWrapper)
                and character_stream.buffer is byte_stream
                and character_position == byte_position
            )
            if (
                character_stream is not None
                and character_position not in (None, 0)
                and not shared_byte_position
            ):
                payload = character_stream.read()
            elif byte_stream is not None and byte_position not in (None, 0):
                payload = byte_stream.read()
            elif isinstance(character_stream, io.StringIO):
                payload = character_stream.read()
            elif byte_stream is not None:
                payload = byte_stream.read()
            elif character_stream is not None:
                payload = character_stream.read()
            else:
                raise ParserError(
                    "Automatic RDF format detection requires a readable input stream."
                )
        elif character_stream is not None:
            payload = character_stream.read()
        elif byte_stream is not None:
            payload = byte_stream.read()
        else:
            raise ParserError(
                "Automatic RDF format detection requires a readable input stream."
            )

        if not isinstance(payload, (str, bytes)):
            raise ParserError(
                "Automatic RDF format detection expected the input stream to "
                f"return str or bytes, not {type(payload).__name__}."
            )

        encoding = source.getEncoding()
        if (
            isinstance(source, StringInputSource)
            and isinstance(payload, bytes)
            and encoding is not None
            and codecs.lookup(encoding).name == "utf-8"
        ):
            # StringInputSource defaults to UTF-8 even when the byte payload
            # declares its own encoding. Leave decoding to the selected parser.
            encoding = None

        return cls(
            payload,
            source.getPublicId(),
            source.getSystemId(),
            encoding,
            source.content_type,
            cast(Optional[str], getattr(source, "url", None)),
            cls._links(source),
        )

    @staticmethod
    def _links(source: InputSource) -> Optional[tuple[str, ...]]:
        links = getattr(source, "links", None)
        if links is None:
            return None
        return tuple(cast(list[str], links))

    def open(self) -> InputSource:
        if isinstance(self.payload, (dict, list)):
            result: InputSource = PythonInputSource(
                copy.deepcopy(self.payload), system_id=self.system_id
            )
        else:
            payload = self.payload
            encoding = self._effective_encoding()
            if isinstance(payload, bytes) and self._bom_encoding() is not None:
                payload = payload.decode(encoding)
            elif isinstance(payload, str) and payload.startswith("\ufeff"):
                payload = payload[1:]
            if isinstance(payload, bytes):
                result = InputSource(self.system_id)
                result.setByteStream(io.BytesIO(payload))
                result.setEncoding(self.encoding)
            elif self._requires_generic_source():
                result = InputSource(self.system_id)
                encoding = "utf-8"
                result.setCharacterStream(io.StringIO(payload))
                result.setByteStream(io.BytesIO(payload.encode(encoding)))
                result.setEncoding(encoding)
            else:
                result = StringInputSource(
                    payload,
                    encoding=encoding,
                    system_id=self.system_id,
                )
        result.setPublicId(self.public_id)
        result.content_type = self.content_type
        if self.url is not None:
            result.url = self.url  # type: ignore[attr-defined]
        if self.links is not None:
            result.links = list(self.links)  # type: ignore[attr-defined]
        return result

    def _requires_generic_source(self) -> bool:
        return (
            self.content_type in ("text/html", "application/xhtml+xml")
            or self.url is not None
            or self.links is not None
        )

    def _bom_encoding(self) -> Optional[str]:
        if isinstance(self.payload, bytes):
            for bom, encoding in (
                (codecs.BOM_UTF8, "utf-8-sig"),
                (codecs.BOM_UTF32_LE, "utf-32"),
                (codecs.BOM_UTF32_BE, "utf-32"),
                (codecs.BOM_UTF16_LE, "utf-16"),
                (codecs.BOM_UTF16_BE, "utf-16"),
            ):
                if self.payload.startswith(bom):
                    return encoding
        return None

    def _effective_encoding(self) -> str:
        bom_encoding = self._bom_encoding()
        if bom_encoding is not None:
            return bom_encoding
        return self.encoding or "utf-8"

    def text(self) -> str:
        if isinstance(self.payload, (dict, list)):
            return json.dumps(self.payload, ensure_ascii=False)
        if isinstance(self.payload, str):
            return self.payload

        data = self.payload
        for bom, encoding in (
            (codecs.BOM_UTF8, "utf-8-sig"),
            (codecs.BOM_UTF32_LE, "utf-32"),
            (codecs.BOM_UTF32_BE, "utf-32"),
            (codecs.BOM_UTF16_LE, "utf-16"),
            (codecs.BOM_UTF16_BE, "utf-16"),
        ):
            if data.startswith(bom):
                return data.decode(encoding, errors="replace")

        encodings = []
        if self.encoding:
            encodings.append(self.encoding)
        encodings.extend(("utf-8", "latin-1"))
        for encoding in encodings:
            try:
                return data.decode(encoding)
            except (LookupError, UnicodeDecodeError):
                continue
        return data.decode("utf-8", errors="replace")


class _InputShape:
    _xml_declaration = re.compile(r"^\s*(?:<\?xml\b|<!DOCTYPE\b)", re.I)
    _xml_root = re.compile(
        r"^\s*<(?!https?://|urn:|_:)(?:[A-Za-z_][\w.-]*:)?[A-Za-z_][\w.-]*"
        r"(?:\s|/?>)",
        re.I,
    )
    _trix = re.compile(
        r"(?:<\s*(?:\w+:)?TriX\b|http://www\.w3\.org/2004/03/trix/trix-1/)",
        re.I,
    )
    _rdfxml = re.compile(
        r"(?:<\s*(?:\w+:)?RDF\b|"
        r"http://www\.w3\.org/1999/02/22-rdf-syntax-ns#)",
        re.I,
    )
    _trig = re.compile(
        r"(?:^|[\r\n])\s*(?:GRAPH\s+)?(?:<[^>]+>|[\w-]+:[^\s{]*)?\s*\{",
        re.I,
    )
    _n3 = re.compile(
        r"(?:=>|<=|"
        r"(?<![\w:.-])is\s+\S+\s+of(?![\w:.-])|"
        r"(?<![\w:.-])has(?=\s))",
        re.I,
    )
    _turtle_directive = re.compile(
        r"(?:^|[\r\n])\s*(?:@prefix|@base|PREFIX|BASE)\b", re.I
    )
    _hext_line = re.compile(r"^\s*\[")
    _nquads_line = re.compile(
        r"^\s*(?:<[^>]*>|_:[^\s]+)\s+<[^>]*>\s+"
        r"(?:<[^>]*>|_:[^\s]+|\"(?:[^\"\\]|\\.)*\"(?:@[\w-]+|\^\^<[^>]*>)?)"
        r"\s+(?:<[^>]*>|_:[^\s]+)\s*\.\s*(?:#.*)?$",
        re.M,
    )
    _ntriples_line = re.compile(
        r"^\s*(?:<[^>]*>|_:[^\s]+)\s+<[^>]*>\s+"
        r"(?:<[^>]*>|_:[^\s]+|\"(?:[^\"\\]|\\.)*\"(?:@[\w-]+|\^\^<[^>]*>)?)"
        r"\s*\.\s*(?:#.*)?$",
        re.M,
    )

    def __init__(self, source: _ReplayableSource):
        self.python_json = isinstance(source.payload, (dict, list))
        self.content_type = source.content_type
        self.text = source.text()
        self.trimmed = self._without_leading_comments(self.text).lstrip("\ufeff \t\r\n")
        self.structural = self._structural_text(self.trimmed)

    @staticmethod
    def _without_leading_comments(text: str) -> str:
        remaining = text
        while True:
            stripped = remaining.lstrip()
            if stripped.startswith("#"):
                newline = stripped.find("\n")
                if newline < 0:
                    return ""
                remaining = stripped[newline + 1 :]
                continue
            return remaining

    @staticmethod
    def _structural_text(text: str) -> str:
        """Hide RDF comments, string bodies, and IRI bodies from syntax probes."""
        output: list[str] = []
        index = 0
        quote: Optional[str] = None
        triple_quoted = False
        in_iri = False
        in_comment = False
        escaped = False

        while index < len(text):
            character = text[index]

            if in_comment:
                if character in "\r\n":
                    in_comment = False
                    output.append(character)
                else:
                    output.append(" ")
                index += 1
                continue

            if in_iri:
                output.append(">" if character == ">" else " ")
                if escaped:
                    escaped = False
                elif character == "\\":
                    escaped = True
                elif character == ">":
                    in_iri = False
                index += 1
                continue

            if quote is not None:
                if escaped:
                    escaped = False
                    output.append(" ")
                    index += 1
                    continue
                if character == "\\":
                    escaped = True
                    output.append(" ")
                    index += 1
                    continue
                if triple_quoted and text.startswith(quote * 3, index):
                    output.extend(quote * 3)
                    index += 3
                    quote = None
                    triple_quoted = False
                    continue
                if not triple_quoted and character == quote:
                    output.append(character)
                    index += 1
                    quote = None
                    continue
                output.append(character if character in "\r\n" else " ")
                index += 1
                continue

            if character == "#":
                in_comment = True
                output.append(" ")
                index += 1
                continue
            if character == "<":
                if index + 1 < len(text) and text[index + 1] == "=":
                    output.extend("<=")
                    index += 2
                else:
                    in_iri = True
                    output.append("<")
                    index += 1
                continue
            if character in ('"', "'"):
                quote = character
                triple_quoted = text.startswith(character * 3, index)
                count = 3 if triple_quoted else 1
                output.extend(character * count)
                index += count
                continue

            output.append(character)
            index += 1

        return "".join(output)

    def is_json(self) -> bool:
        if self.python_json:
            return True
        return self.trimmed.startswith(("{", "["))

    def is_html_jsonld(self) -> bool:
        return self.content_type in ("text/html", "application/xhtml+xml")

    def is_hextuples(self) -> bool:
        if not self._hext_line.match(self.trimmed):
            return False
        lines = [line for line in self.trimmed.splitlines() if line.strip()]
        if not lines:
            return False
        try:
            values = [json.loads(line) for line in lines[:4]]
        except (TypeError, ValueError):
            return False
        return all(isinstance(value, list) and len(value) == 6 for value in values)

    def is_xml(self) -> bool:
        return bool(
            self._xml_declaration.search(self.trimmed)
            or self._xml_root.search(self.trimmed)
        )

    def scores(self) -> dict[str, int]:
        scores = {
            "trix": 20,
            "xml": 19,
            "json-ld": 18,
            "hext": 17,
            "nquads": 15,
            # TriG accepts an ordinary Turtle document as its default graph.
            # Prefer the narrower grammar until graph-block syntax supplies
            # positive evidence for TriG.
            "turtle": 16,
            "trig": 14,
            "n3": 13,
            "nt": 12,
        }

        if self.python_json:
            scores["json-ld"] += 1000
            return scores

        if self.is_html_jsonld():
            scores["json-ld"] += 1000

        if self.is_hextuples():
            scores["hext"] += 900
            scores["json-ld"] += 300
        elif self.is_json():
            scores["json-ld"] += 900
            scores["hext"] += 100

        if self.is_xml():
            scores["xml"] += 700
            scores["trix"] += 650
        if self._trix.search(self.trimmed):
            # RDF/XML can accept a TriX root as a typed node. Try the stricter
            # TriX grammar first even if RDF namespace text is also present.
            scores["trix"] += 700
        if self._rdfxml.search(self.trimmed):
            scores["xml"] += 500

        if self._trig.search(self.structural):
            scores["trig"] += 550
        if self._n3.search(self.structural):
            scores["n3"] += 500
        if self._turtle_directive.search(self.structural):
            scores["turtle"] += 450
            scores["trig"] += 200
            scores["n3"] += 150
        if self._nquads_line.search(self.trimmed):
            scores["nquads"] += 450
        if self._ntriples_line.search(self.trimmed):
            scores["nt"] += 350
            scores["nquads"] += 200
            scores["turtle"] += 100

        return scores


class AutoDetectParser(Parser):
    """Try RDF parsers in an order inferred from the source contents."""

    _formats = (
        "trix",
        "xml",
        "json-ld",
        "hext",
        "trig",
        "nquads",
        "turtle",
        "n3",
        "nt",
    )

    def parse(self, source: InputSource, sink: Graph, **kwargs: Any) -> None:
        replayable = _ReplayableSource.capture(source)
        shape = _InputShape(replayable)
        failures: list[_Failure] = []

        for candidate in self._ordered_candidates(shape):
            try:
                staged = self._try_parser(candidate.name, replayable, sink, kwargs)
            except Exception as error:
                failures.append(_Failure(candidate.name, error))
                continue

            self._commit(staged, sink)
            return

        details = "; ".join(failure.summary() for failure in failures)
        message = "Could not determine an RDF format from the source contents."
        if details:
            message = f"{message} Parser attempts: {details}"
        final_error = ParserError(message)
        if failures:
            raise final_error from failures[0].error
        raise final_error

    def _ordered_candidates(self, shape: _InputShape) -> list[_Format]:
        scores = shape.scores()
        formats: list[_Format] = []
        for position, name in enumerate(self._formats):
            try:
                parser_class = rdflib.plugin.get(name, Parser)
            except rdflib.plugin.PluginException:
                continue
            if parser_class is AutoDetectParser:
                continue
            formats.append(_Format(name, scores.get(name, 0) * 100 - position))
        formats.sort(key=lambda candidate: candidate.priority, reverse=True)
        return formats

    @staticmethod
    def _try_parser(
        format_name: str,
        replayable: _ReplayableSource,
        sink: Graph,
        kwargs: dict[str, Any],
    ) -> Graph:
        parser_class = rdflib.plugin.get(format_name, Parser)
        parser = parser_class()
        staged = Graph(
            store="Memory",
            identifier=sink.identifier,
            base=sink.base,
            bind_namespaces="none",
        )
        staged.store.context_aware = sink.store.context_aware
        staged.store.formula_aware = sink.store.formula_aware
        staged.store.graph_aware = sink.store.graph_aware
        attempt_source = replayable.open()
        try:
            parser.parse(attempt_source, staged, **kwargs)
        finally:
            attempt_source.close()
        return staged

    @staticmethod
    def _commit(staged: Graph, sink: Graph) -> None:
        for prefix, namespace in staged.namespaces():
            sink.bind(prefix, namespace)

        contexts = [cast(Graph, context) for context in staged.store.contexts()]
        quoted_targets: dict[IdentifiedNode, QuotedGraph] = {}

        def quoted_target(formula: QuotedGraph) -> QuotedGraph:
            identifier = cast(IdentifiedNode, formula.identifier)
            target = quoted_targets.get(identifier)
            if target is None:
                target = QuotedGraph(sink.store, identifier)
                quoted_targets[identifier] = target
                if sink.store.graph_aware:
                    sink.store.add_graph(target)
            return target

        def remap_term(term: Node) -> Node:
            if isinstance(term, QuotedGraph):
                return quoted_target(term)
            return term

        for context_graph in contexts:
            if not isinstance(context_graph, QuotedGraph):
                continue
            quoted_target(context_graph)

        for context in contexts:
            context_graph = context
            identifier = cast(IdentifiedNode, context_graph.identifier)

            if isinstance(context_graph, QuotedGraph):
                target: Graph = quoted_targets[identifier]
            elif identifier == staged.identifier:
                target = sink
            else:
                target = Graph(
                    store=sink.store,
                    identifier=identifier,
                    namespace_manager=sink.namespace_manager,
                )

            # Adding statements registers their context through the store's
            # normal insertion path. Only a new empty context needs creation.
            if (
                sink.store.graph_aware
                and not isinstance(target, QuotedGraph)
                and target != sink
                and len(context_graph) == 0
                and not any(
                    getattr(existing, "identifier", existing) == identifier
                    for existing in sink.store.contexts()
                )
            ):
                sink.store.add_graph(target)

            for triple, _ in staged.store.triples(
                (None, None, None), context=context_graph
            ):
                subject, predicate, object_ = triple
                mapped = (
                    remap_term(subject),
                    remap_term(predicate),
                    remap_term(object_),
                )
                target.add(mapped)
