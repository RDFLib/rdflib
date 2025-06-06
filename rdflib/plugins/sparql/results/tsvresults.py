"""
This implements the Tab Separated SPARQL Result Format

It is implemented with pyparsing, reusing the elements from the SPARQL Parser
"""

from __future__ import annotations

import codecs
from typing import IO, Union

from pyparsing import (
    FollowedBy,
    LineEnd,
    Literal,
    Optional,
    ParserElement,
    Suppress,
    ZeroOrMore,
)

from rdflib import IdentifiedNode
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
from rdflib.query import Result, ResultParser
from rdflib.term import BNode, URIRef, Variable
from rdflib.term import Literal as RDFLiteral

ParserElement.setDefaultWhitespaceChars(" \n")


String = STRING_LITERAL1 | STRING_LITERAL2

RDFLITERAL = Comp(
    "literal",
    Param("string", String)
    + Optional(
        Param("lang", LANGTAG.leaveWhitespace())
        | Literal("^^").leaveWhitespace() + Param("datatype", IRIREF).leaveWhitespace()
    ),
)

NONE_VALUE = object()

EMPTY = FollowedBy(LineEnd()) | FollowedBy("\t")
EMPTY.setParseAction(lambda x: NONE_VALUE)

TERM = RDFLITERAL | IRIREF | BLANK_NODE_LABEL | NumericLiteral | BooleanLiteral

ROW = (EMPTY | TERM) + ZeroOrMore(Suppress("\t") + (EMPTY | TERM))
ROW.parseWithTabs()

HEADER = Var + ZeroOrMore(Suppress("\t") + Var)
HEADER.parseWithTabs()


class TSVResultParser(ResultParser):
    """Parses SPARQL TSV results into a Result object."""

    # type error: Signature of "parse" incompatible with supertype "ResultParser"  [override]
    def parse(self, source: IO, content_type: str | None = None) -> Result:  # type: ignore[override]
        if isinstance(source.read(0), bytes):
            # if reading from source returns bytes do utf-8 decoding
            # type error: Incompatible types in assignment (expression has type "StreamReader", variable has type "IO[Any]")
            source = codecs.getreader("utf-8")(source)  # type: ignore[assignment]

        r = Result("SELECT")

        header = source.readline()

        r.vars = list(HEADER.parseString(header.strip(), parseAll=True))
        r.bindings = []
        while True:
            line = source.readline()
            if not line:
                break
            line = line.strip("\n")
            if line == "":
                continue

            row = ROW.parseString(line, parseAll=True)
            this_row_dict: dict[Variable, IdentifiedNode | RDFLiteral] = {}
            for var, val_read in zip(r.vars, row):
                val = self.convertTerm(val_read)
                if val is None:
                    # Skip unbound vars
                    continue
                this_row_dict[var] = val
            if len(this_row_dict) > 0:
                r.bindings.append(this_row_dict)
        return r

    def convertTerm(
        self, t: Union[object, RDFLiteral, BNode, CompValue, URIRef]
    ) -> BNode | URIRef | RDFLiteral | None:
        if t is NONE_VALUE:
            return None
        elif isinstance(t, CompValue):
            if t.name == "literal":
                return RDFLiteral(t.string, lang=t.lang, datatype=t.datatype)
            else:
                raise Exception("I dont know how to handle this: %s" % (t,))
        elif isinstance(t, (RDFLiteral, BNode, URIRef)):
            return t
        else:
            raise ValueError(f"Unexpected type {type(t)} found in TSV result")
