"""
This implements the Tab Separated SPARQL Result Format

Parsing is implemented with pyparsing, reusing the elements from the SPARQL
Parser. Serialization uses direct string construction for precise control over
TSV field formatting and escape sequences.

http://www.w3.org/TR/sparql11-results-csv-tsv/
"""

from __future__ import annotations

import codecs
import math
import typing
from io import BufferedIOBase, TextIOBase
from typing import IO, Optional, Union, cast

from pyparsing import (
    FollowedBy,
    LineEnd,
    Literal,
    ParserElement,
    Suppress,
    ZeroOrMore,
)
from pyparsing import Optional as PypOptional

from rdflib.plugins.sparql.parser import (
    BLANK_NODE_LABEL,
    IRIREF,
    LANGTAG,
    STRING_LITERAL1,
    STRING_LITERAL2,
    BooleanLiteral,
    NumericLiteral,
    Var,
)
from rdflib.plugins.sparql.parserutils import Comp, CompValue, Param
from rdflib.query import Result, ResultParser, ResultSerializer
from rdflib.term import (
    _NUMERIC_INF_NAN_LITERAL_TYPES,
    _PLAIN_LITERAL_TYPES,
    BNode,
    Identifier,
    URIRef,
)
from rdflib.term import Literal as RDFLiteral

ParserElement.set_default_whitespace_chars(" \n")


String = STRING_LITERAL1 | STRING_LITERAL2

RDFLITERAL = Comp(
    "literal",
    Param("string", String)
    + PypOptional(
        Param("lang", LANGTAG.leave_whitespace())
        | Literal("^^").leave_whitespace()
        + Param("datatype", IRIREF).leave_whitespace()
    ),
)

NONE_VALUE = object()

EMPTY = FollowedBy(LineEnd()) | FollowedBy("\t")
EMPTY.set_parse_action(lambda x: NONE_VALUE)

TERM = RDFLITERAL | IRIREF | BLANK_NODE_LABEL | NumericLiteral | BooleanLiteral

ROW = (EMPTY | TERM) + ZeroOrMore(Suppress("\t") + (EMPTY | TERM))
ROW.parse_with_tabs()

HEADER = Var + ZeroOrMore(Suppress("\t") + Var)
HEADER.parse_with_tabs()


class TSVResultParser(ResultParser):
    """Parses SPARQL TSV results into a Result object."""

    # type error: Signature of "parse" incompatible with supertype "ResultParser"  [override]
    def parse(self, source: IO, content_type: typing.Optional[str] = None) -> Result:  # type: ignore[override]
        if isinstance(source.read(0), bytes):
            # if reading from source returns bytes do utf-8 decoding
            # type error: Incompatible types in assignment (expression has type "StreamReader", variable has type "IO[Any]")
            source = codecs.getreader("utf-8")(source)  # type: ignore[assignment]

        r = Result("SELECT")

        header = source.readline()

        r.vars = list(HEADER.parse_string(header.strip(), parse_all=True))
        r.bindings = []
        while True:
            line = source.readline()
            if not line:
                break
            line = line.strip("\r\n")
            if line == "":
                continue

            row = ROW.parse_string(line, parse_all=True)
            this_row_dict = {}
            for var, val_read in zip(r.vars, row):
                val = self.convertTerm(val_read)
                if val is None:
                    # Skip unbound vars
                    continue
                this_row_dict[var] = val
            # Preserve solution row cardinality, including fully-unbound rows.
            r.bindings.append(this_row_dict)
        return r

    def convertTerm(
        self, t: Union[object, RDFLiteral, BNode, CompValue, URIRef]
    ) -> typing.Optional[Identifier]:
        if t is NONE_VALUE:
            return None
        if isinstance(t, CompValue):
            if t.name == "literal":
                return RDFLiteral(t.string, lang=t.lang, datatype=t.datatype)
            else:
                raise Exception("I dont know how to handle this: %s" % (t,))
        elif isinstance(t, (RDFLiteral, BNode, URIRef)):
            return t
        else:
            raise ValueError(f"Unexpected type {type(t)} found in TSV result")


def _tsv_quote_encode(s: str) -> str:
    """Encode a literal's lexical form for TSV using short-form double quotes.

    The TSV format MUST NOT use triple-quoted forms and MUST escape tab,
    newline, and carriage return characters within string values.  This
    function always produces the short ``"..."`` form with appropriate
    escape sequences.

    Escapes applied (in order):
        ``\\``  -> ``\\\\``
        ``"``   -> ``\\"``
        TAB     -> ``\\t``
        LF      -> ``\\n``
        CR      -> ``\\r``
    """
    return '"%s"' % (
        s.replace("\\", "\\\\")
        .replace('"', '\\"')
        .replace("\t", "\\t")
        .replace("\n", "\\n")
        .replace("\r", "\\r")
    )


def _serialize_literal(literal: RDFLiteral) -> str:
    """Serialize an RDF Literal to its TSV representation.

    Uses abbreviated (plain) syntax for xsd:integer, xsd:decimal, xsd:double,
    xsd:boolean, and owl:rational when the literal has a valid parsed value.
    Falls back to full quoted syntax with TSV-safe escaping for all other
    literals, including inf/NaN doubles and ill-typed numerics.
    """
    # Attempt abbreviated form for numeric/boolean types.
    # These produce bare values like 123, 3.14, 1.5e+02, true, false
    # that contain no quotes, tabs, or newlines.
    if literal.datatype in _PLAIN_LITERAL_TYPES and literal.value is not None:
        # inf and NaN have no abbreviated representation -- they require
        # the full quoted form with a datatype annotation.
        if literal.datatype in _NUMERIC_INF_NAN_LITERAL_TYPES:
            try:
                v = float(literal)
                if math.isinf(v) or math.isnan(v):
                    # Fall through to full quoted encoding below
                    pass
                else:
                    return literal._literal_n3(use_plain=True)
            except (ValueError, TypeError):
                # Ill-formed numeric lexical value; fall through
                pass
        else:
            # xsd:integer, xsd:boolean, owl:rational -- always safe
            return literal._literal_n3(use_plain=True)

    # Full encoding: TSV-safe quoted lexical form + language or datatype suffix.
    encoded = _tsv_quote_encode(str(literal))

    if literal.language:
        return f"{encoded}@{literal.language}"
    elif literal.datatype:
        # Always include the datatype annotation if present.  Even xsd:string
        # is included explicitly to ensure round-trip fidelity -- the TSV parser
        # distinguishes "foo" (datatype=None) from "foo"^^<xsd:string>.
        return f"{encoded}^^<{literal.datatype}>"
    else:
        return encoded


def _serialize_term(term: Optional[Identifier]) -> str:
    """Serialize a single RDF term (or unbound variable) for a TSV field.

    Returns:
        The SPARQL/Turtle syntax representation of the term, or an empty
        string for unbound (None) values.
    """
    if term is None:
        return ""
    elif isinstance(term, URIRef):
        return f"<{term}>"
    elif isinstance(term, BNode):
        return f"_:{term}"
    elif isinstance(term, RDFLiteral):
        return _serialize_literal(term)
    else:
        raise ValueError(
            f"Cannot serialize unexpected term type {type(term).__name__} to SPARQL TSV"
        )


class TSVResultSerializer(ResultSerializer):
    """Serializes SPARQL SELECT results to the W3C TSV format.

    Implements the SPARQL 1.1 Query Results TSV Format as specified in:
    http://www.w3.org/TR/sparql11-results-csv-tsv/

    RDF terms are encoded using Turtle/SPARQL syntax with abbreviated forms
    for numeric and boolean literals.  The triple-quoted string forms are
    never used; tab, newline, and carriage return characters within literal
    values are escaped as ``\\t``, ``\\n``, and ``\\r`` respectively.
    """

    def __init__(self, result: Result):
        ResultSerializer.__init__(self, result)

        if result.type != "SELECT":
            raise Exception(
                "TSVResultSerializer can only serialize SELECT query results"
            )

    def serialize(self, stream: IO, encoding: str = "utf-8", **kwargs) -> None:
        """Serialize the result set to the given stream in TSV format.

        The output uses LF (``\\n``) line endings as required by the TSV
        specification, and is encoded in the specified character encoding
        (UTF-8 by default).
        """
        # Wrap byte streams with an encoding writer so we can write strings.
        # Text streams are used directly.
        writable_stream = cast(Union[TextIOBase, BufferedIOBase], stream)
        if isinstance(writable_stream, TextIOBase):
            string_stream: TextIOBase = writable_stream
        else:
            byte_stream = cast(BufferedIOBase, writable_stream)
            string_stream = cast(TextIOBase, codecs.getwriter(encoding)(byte_stream))

        # Header row: variable names prefixed with '?' and separated by tabs
        vars = self.result.vars
        assert vars is not None  # guaranteed by SELECT type check in __init__
        header = "\t".join(f"?{v}" for v in vars)
        string_stream.write(f"{header}\n")

        # Data rows: one line per solution, fields separated by tabs
        bindings = self.result.bindings
        assert bindings is not None  # guaranteed by SELECT type check in __init__
        for row in bindings:
            fields = [_serialize_term(row.get(v)) for v in vars]
            string_stream.write("\t".join(fields) + "\n")
