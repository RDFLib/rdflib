"""Process RDF statements as they are parsed, without building a graph.

The sink uses the existing parser and store interfaces. N-Triples, N-Quads,
and RDF/XML read their inputs incrementally; formats whose parsers buffer
the entire document are deliberately not accepted.
"""

from __future__ import annotations

import pathlib
from collections.abc import Callable
from typing import IO, Any, BinaryIO, TextIO, cast

from rdflib.graph import (
    DATASET_DEFAULT_GRAPH_ID,
    Dataset,
    Graph,
    _ContextType,
    _TripleType,
)
from rdflib.parser import InputSource, create_input_source
from rdflib.plugins.stores.memory import Memory
from rdflib.term import Identifier

__all__ = ["Sink"]

_StatementHandler = Callable[[_TripleType, Identifier | None], None]

_STREAMING_FORMATS = frozenset(
    {
        "nt",
        "nt11",
        "ntriples",
        "application/n-triples",
        "nquads",
        "application/n-quads",
        "xml",
        "application/rdf+xml",
    }
)


class _BorrowedStream:
    """Let parsers close their view of a stream without closing the owner."""

    def __init__(self, stream: object):
        self._stream = stream

    def __getattr__(self, name: str) -> Any:
        return getattr(self._stream, name)

    def close(self) -> None:
        pass


def _parser_source(source: InputSource) -> InputSource:
    result = InputSource(source.getSystemId())
    result.setPublicId(source.getPublicId())
    result.setEncoding(source.getEncoding())
    binary = source.getByteStream()
    text = source.getCharacterStream()
    if binary is not None:
        result.setByteStream(cast(BinaryIO, _BorrowedStream(binary)))
    if text is not None:
        result.setCharacterStream(cast(TextIO, _BorrowedStream(text)))
    return result


class _SinkStore(Memory):
    """Keep namespace bindings, but forward statements instead of indexing them."""

    formula_aware = False

    def __init__(self, handler: _StatementHandler):
        super().__init__()
        self._handler = handler

    def add(
        self, triple: _TripleType, context: _ContextType, quoted: bool = False
    ) -> None:
        if quoted:
            raise ValueError("Streaming sinks do not support quoted formulae")
        identifier = context.identifier
        self._handler(
            triple, None if identifier == DATASET_DEFAULT_GRAPH_ID else identifier
        )

    def add_graph(self, graph: Graph) -> None:
        # Parsers may create a Graph per named graph. Do not retain those either.
        pass


class Sink:
    """Deliver parsed triples and graph names to a synchronous callback.

    The callback receives ``(triple, graph_name)`` for every parsed statement.
    ``graph_name`` is ``None`` for the default graph. Duplicate statements are
    delivered repeatedly, in parser emission order. No triples are retained.

    Example:
        ```python
        >>> from rdflib.sink import Sink
        >>> statements = []
        >>> sink = Sink(lambda triple, graph: statements.append((triple, graph)))
        >>> _ = sink.parse(data='<urn:s> <urn:p> "value" .', format="nt")
        >>> str(statements[0][0][2]), statements[0][1]
        ('value', None)

        ```
    """

    def __init__(self, handler: _StatementHandler):
        self._handler = handler

    def triple(self, triple: _TripleType, context: Identifier | None = None) -> None:
        """Handle one statement. Callback exceptions stop parsing immediately."""
        self._handler(triple, context)

    def parse(
        self,
        source: IO[bytes]
        | TextIO
        | InputSource
        | str
        | bytes
        | pathlib.PurePath
        | None = None,
        *,
        format: str,
        publicID: str | None = None,  # noqa: N803
        location: str | None = None,
        file: BinaryIO | TextIO | None = None,
        data: str | bytes | None = None,
        **args: Any,
    ) -> Sink:
        """Parse N-Triples, N-Quads, or RDF/XML and return this sink.

        Source arguments have the same meaning as in :meth:`Graph.parse`.
        An explicit supported format is required. Use a file or stream, rather
        than ``data``, to avoid holding the input document in memory.
        Borrowed streams remain open. Sources opened by this method are closed
        on success or failure, as are InputSources with ``auto_close=True``.

        Memory usage includes parser buffers, namespace bindings and blank-node
        label mappings; it is not independent of the number of distinct labels.
        Statements already delivered are not rolled back after a parse error.

        Parsing may access files or URLs. The security considerations for
        :meth:`Graph.parse` apply equally here.
        """
        if format not in _STREAMING_FORMATS:
            raise ValueError(
                f"Format {format!r} is not supported for streaming; "
                "use N-Triples, N-Quads, or RDF/XML"
            )
        input_source = create_input_source(
            source=source,
            publicID=publicID,
            format=format,
            location=location,
            file=file,
            data=data,
        )
        try:
            graph = Dataset(store=_SinkStore(self.triple))
            graph.parse(source=_parser_source(input_source), format=format, **args)
        finally:
            if input_source.auto_close:
                input_source.close()
        return self
