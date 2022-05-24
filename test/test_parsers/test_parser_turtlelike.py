"""
This module contains tests for the parsing of the turtle family of formats: N3,
Turtle, NTriples, NQauds and TriG.
"""

import enum
import itertools
from dataclasses import dataclass, field
from typing import Callable, Dict, Iterator, List, Set, Tuple, Union

import pytest
from _pytest.mark.structures import Mark, MarkDecorator, ParameterSet

from rdflib import XSD, Graph, Literal, Namespace
from rdflib.term import Identifier
from rdflib.util import from_n3

EGNS = Namespace("http://example.com/")


class FormatTrait(enum.Enum):
    shorthand_literals = enum.auto()
    prefixes = enum.auto()
    extended_quoting = enum.auto()  # supports additional quoting styles


@dataclass
class Format:
    name: str
    traits: Set[FormatTrait]


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
        data=f"""<{EGNS.subject}> <{EGNS.predicate}> {identifier_string} .""",
        format=format,
    )
    triples = list(g.triples((None, None, None)))
    assert len(triples) == 1
    (subj, pred, obj) = triples[0]
    assert subj == EGNS.subject
    assert pred == EGNS.predicate
    assert isinstance(obj, Identifier)
    return obj


def parse_n3_identifier(identifier_string: str, format: str) -> Identifier:
    return from_n3(identifier_string)


ParseFunction = Callable[[str, str], Identifier]


def make_literal_tests() -> Iterator[ParameterSet]:
    @dataclass
    class Case:
        expected_literal: Literal
        quoted_strings: List[str]
        shorthand_strings: List[str] = field(default_factory=list)
        xquoted_strings: List[str] = field(
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

    escapes: Dict[str, str] = {
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

    xfails: Dict[
        Tuple[str, Literal, str, Callable[[str, str], Identifier]],
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
            parse_functions: List[ParseFunction] = [parse_identifier]
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
    make_literal_tests(),
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
