"""
This module contains tests for the parsing of the turtle family of formats: N3,
Turtle, NTriples, NQauds and TriG.
"""

from __future__ import annotations

import enum
import itertools
import traceback
from collections.abc import Callable, Iterator
from dataclasses import dataclass, field
from typing import Union

import pytest
from _pytest.mark.structures import Mark, MarkDecorator, ParameterSet

from rdflib import XSD, Graph, Literal
from rdflib.plugins.parsers.notation3 import BadSyntax
from rdflib.term import Identifier
from rdflib.util import from_n3
from test.utils.namespace import EGDC


class FormatTrait(enum.Enum):
    shorthand_literals = enum.auto()
    prefixes = enum.auto()
    extended_quoting = enum.auto()  # supports additional quoting styles


@dataclass
class Format:
    name: str
    traits: set[FormatTrait]


FORMATS = [
    Format("ntriples", set()),
    Format("nquads", set()),
    Format(
        "turtle",
        {
            FormatTrait.shorthand_literals,
            FormatTrait.prefixes,
            FormatTrait.extended_quoting,
        },
    ),
    Format(
        "trig",
        {
            FormatTrait.shorthand_literals,
            FormatTrait.prefixes,
            FormatTrait.extended_quoting,
        },
    ),
    Format(
        "n3",
        {
            FormatTrait.shorthand_literals,
            FormatTrait.prefixes,
            # NOTE: it is not clear from n3 "spec" if it supports extended
            # quoting, but the spec is not that well fleshed out. RDFLib n3
            # does not support extended quoting.
        },
    ),
]


def parse_identifier(identifier_string: str, format: str) -> Identifier:
    g = Graph()
    g.parse(
        data=f"""<{EGDC.subject}> <{EGDC.predicate}> {identifier_string} .""",
        format=format,
    )
    triples = list(g.triples((None, None, None)))
    assert len(triples) == 1
    (subj, pred, obj) = triples[0]
    assert subj == EGDC.subject
    assert pred == EGDC.predicate
    assert isinstance(obj, Identifier)
    return obj


def parse_n3_identifier(identifier_string: str, format: str) -> Identifier:
    # type error: Incompatible return value type (got "Union[Node, str, None]", expected "Identifier")
    return from_n3(identifier_string)  # type: ignore[return-value]


ParseFunction = Callable[[str, str], Identifier]


def make_literal_tests() -> Iterator[ParameterSet]:
    @dataclass
    class Case:
        expected_literal: Literal
        quoted_strings: list[str]
        shorthand_strings: list[str] = field(default_factory=list)
        xquoted_strings: list[str] = field(
            default_factory=list
        )  # strings using extended quoting styles

    cases = [
        Case(
            Literal("-5", None, XSD.integer),
            [f'"-5"^^<{XSD}integer>'],
            ["-5"],
        ),
        Case(
            Literal("-5.0", None, XSD.decimal),
            [f'"-5.0"^^<{XSD}decimal>'],
            ["-5.0"],
        ),
        Case(
            Literal("-5.5", None, XSD.decimal),
            [f'"-5.5"^^<{XSD}decimal>'],
            ["-5.5"],
        ),
        Case(
            Literal("4.2E9", None, XSD.double),
            [f'"4.2E9"^^<{XSD}double>', f'"4.2e9"^^<{XSD}double>'],
            ["4.2E9", "4.2e9"],
        ),
        Case(
            Literal("1.23E-7", None, XSD.double),
            [f'"1.23E-7"^^<{XSD}double>', f'"1.23e-7"^^<{XSD}double>'],
            ["1.23E-7", "1.23e-7"],
        ),
        Case(
            Literal("-4.1E-7", None, XSD.double),
            [f'"-4.1E-7"^^<{XSD}double>', f'"-4.1e-7"^^<{XSD}double>'],
            ["-4.1E-7", "-4.1e-7"],
        ),
        Case(
            Literal("false", None, XSD.boolean),
            [f'"false"^^<{XSD}boolean>'],
            ["false"],
        ),
        Case(
            Literal("true", None, XSD.boolean),
            [f'"true"^^<{XSD}boolean>'],
            ["true"],
        ),
        Case(
            Literal("true", None, XSD.boolean),
            [f'"true"^^<{XSD}boolean>'],
            ["true"],
        ),
        Case(
            Literal("example"),
            ['"example"'],
            [],
            ["'example'", "'''example'''", '"""example"""'],
        ),
    ]

    escapes: dict[str, str] = {
        "\t": "\\t",
        "\b": "\\b",
        "\n": "\\n",
        "\r": "\\r",
        "\f": "\\f",
        '"': '\\"',
        "'": "\\'",
        "\\": "\\\\",
    }

    for literal, escaped in escapes.items():
        cases.append(
            Case(
                Literal(f"prefix {literal} suffix"),
                [],
                [f'"prefix {escaped} suffix"'],
                [
                    f"'prefix {escaped} suffix'",
                    f"'''prefix {escaped} suffix'''",
                    f'"""prefix {escaped} suffix"""',
                ],
            )
        )

    xfails: dict[
        tuple[str, Literal, str, Callable[[str, str], Identifier]],
        Union[MarkDecorator, Mark],
    ] = {
        (
            "n3",
            Literal("-4.1E-7", None, XSD.double),
            "-4.1E-7",
            parse_n3_identifier,
        ): pytest.mark.xfail(reason="bug in from_n3", raises=AssertionError),
        (
            "n3",
            Literal("-4.1E-7", None, XSD.double),
            "-4.1e-7",
            parse_n3_identifier,
        ): pytest.mark.xfail(reason="bug in from_n3", raises=AssertionError),
    }

    for case in cases:
        for format in FORMATS:
            parse_functions: list[ParseFunction] = [parse_identifier]
            literal_strings = [*case.quoted_strings]
            if FormatTrait.shorthand_literals in format.traits:
                literal_strings.extend(case.shorthand_strings)
            if FormatTrait.extended_quoting in format.traits:
                literal_strings.extend(case.xquoted_strings)

            if format.name == "n3":
                parse_functions.append(parse_n3_identifier)

            parse_function: ParseFunction
            literal_string: str
            for literal_string, parse_function in itertools.product(
                literal_strings, parse_functions
            ):
                args = (
                    format.name,
                    case.expected_literal,
                    literal_string,
                    parse_function,
                )
                xfail = xfails.get(args)
                marks = [xfail] if xfail is not None else ()
                yield pytest.param(
                    *args,
                    marks=marks,
                )


@pytest.mark.parametrize(
    ["format_name", "expected_literal", "literal_string", "parse_function"],
    list(make_literal_tests()),
)
def test_literals(
    format_name: str,
    expected_literal: Literal,
    literal_string: str,
    parse_function: Callable[[str, str], Identifier],
) -> None:
    """
    Literal strings parse to the expected literal.
    """
    identifier = parse_function(literal_string, format_name)
    assert expected_literal == identifier


@pytest.mark.parametrize(
    ["format_name", "pname", "local_name"],
    [
        (format.name, pname, local_name)
        for format in FORMATS
        if FormatTrait.prefixes in format.traits
        for pname, local_name in [
            ("eg:a\\.", "a."),
            ("eg:a.\\.", "a.."),
            ("eg:\\..\\.", "..."),
            ("eg:a\\.b", "a.b"),
        ]
    ],
)
def test_prefixed_name_with_escaped_dot(
    format_name: str, pname: str, local_name: str
) -> None:
    """
    A prefixed name can end with an escaped dot, which is part of the local
    name, unlike an unescaped one.
    """
    g = Graph()
    g.parse(
        data=f"@prefix eg: <{EGDC}> .\n{pname} <{EGDC.predicate}> {pname} .",
        format=format_name,
    )
    assert list(g) == [(EGDC[local_name], EGDC.predicate, EGDC[local_name])]


@pytest.mark.parametrize("format_name", ["turtle", "trig"])
@pytest.mark.parametrize(
    "data",
    [
        r"_:a\. <urn:p> <urn:o> .",
        r"<urn:s> <urn:p> _:a\. .",
    ],
    ids=["subject", "object"],
)
def test_blank_node_label_with_escaped_trailing_dot(
    format_name: str, data: str
) -> None:
    """Blank-node labels cannot end in a dot, even if escaped."""
    with pytest.raises(BadSyntax):
        Graph().parse(data=data, format=format_name)


def test_badsyntax_msg_matches_rendered_detail() -> None:
    """SyntaxError.msg keeps the diagnostic BadSyntax already renders.

    Regression for https://github.com/RDFLib/rdflib/issues/3540.
    """
    uri = "http://example.org/doc"
    source = "<s> <p>"
    reason = "expected '.'"
    error = BadSyntax(uri, 2, source, 4, reason)

    assert error.args == (uri, 2, source, 4, reason)
    assert error.msg == str(error)

    for formatted in (
        "".join(traceback.format_exception_only(error)),
        "".join(traceback.format_exception(error)),
    ):
        assert reason in formatted
        assert "<s>" in formatted
        assert "at line 3" in formatted
        assert "<no detail available>" not in formatted


@pytest.mark.parametrize(
    ("format_name", "data", "reason", "source_context"),
    [
        pytest.param(
            "turtle",
            "<http://example.org/s> <http://example.org/p> <http://example.org/o> "
            "<http://example.org/s2> <http://example.org/p2> <http://example.org/o2> .",
            "expected '.' or '}' or ']' at end of statement",
            "<http://example.org/o>",
            id="turtle-missing-dot",
        ),
        pytest.param(
            "turtle",
            "<http://example.org/s> <http://example.org/p> .",
            "objectList expected",
            "<http://example.org/p>",
            id="turtle-missing-object",
        ),
        pytest.param(
            "n3",
            "<http://example.org/s> <http://example.org/p> <http://example.org/o> "
            "<http://example.org/s2> <http://example.org/p2> <http://example.org/o2> .",
            "expected '.' or '}' or ']' at end of statement",
            "<http://example.org/o>",
            id="n3-missing-dot",
        ),
        pytest.param(
            "trig",
            "<http://example.org/s> <http://example.org/p> [",
            "EOF after '['",
            "<http://example.org/p>",
            id="trig-eof",
        ),
    ],
)
def test_parse_badsyntax_traceback_includes_details(
    format_name: str,
    data: str,
    reason: str,
    source_context: str,
) -> None:
    """Malformed Turtle-family input keeps its syntax reason in tracebacks."""
    graph = Graph()
    with pytest.raises(BadSyntax) as caught:
        graph.parse(
            data=data,
            format=format_name,
            publicID="http://example.org/doc",
        )

    error = caught.value
    for formatted in (
        "".join(traceback.format_exception_only(error)),
        "".join(traceback.format_exception(error)),
    ):
        assert reason in formatted
        assert source_context in formatted
        assert "at line 1" in formatted
        assert "<no detail available>" not in formatted
