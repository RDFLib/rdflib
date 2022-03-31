"""
This module contains tests for the parsing of the turtle family of formats: N3,
Turtle, NTriples, NQauds and TriG.
"""

from dataclasses import dataclass
from typing import Iterator, List, NamedTuple, Set

from rdflib import Namespace, Literal, XSD, Graph
import enum

import pytest
from _pytest.mark.structures import ParameterSet

EGNS = Namespace("http://example.com/")


class FormatTrait(enum.Enum):
    shorthand_literals = enum.auto()
    prefixes = enum.auto()


@dataclass
class Format:
    name: str
    traits: Set[FormatTrait]


FORMATS = [
    Format("ntriples", set()),
    Format("nquads", set()),
    Format("turtle", {FormatTrait.shorthand_literals, FormatTrait.prefixes}),
    Format("trig", {FormatTrait.shorthand_literals, FormatTrait.prefixes}),
    Format("n3", {FormatTrait.shorthand_literals, FormatTrait.prefixes}),
]


def make_literal_tests() -> Iterator[ParameterSet]:
    class RawCase(NamedTuple):
        expected_literal: Literal
        shorthand_strings: List[str]
        quoted_strings: List[str]

    raw_cases = [
        RawCase(
            Literal("-5", None, XSD.integer),
            ["-5"],
            [f'"-5"^^<{XSD}integer>'],
        ),
        RawCase(
            Literal("-5.0", None, XSD.decimal),
            ["-5.0"],
            [f'"-5.0"^^<{XSD}decimal>'],
        ),
        RawCase(
            Literal("4.2E9", None, XSD.double),
            ["4.2E9"],
            [f'"4.2E9"^^<{XSD}double>'],
        ),
        RawCase(
            Literal("false", None, XSD.boolean),
            ["false"],
            [f'"false"^^<{XSD}boolean>'],
        ),
        RawCase(
            Literal("true", None, XSD.boolean),
            ["true"],
            [f'"true"^^<{XSD}boolean>'],
        ),
    ]

    for raw_case in raw_cases:
        for format in FORMATS:
            if FormatTrait.shorthand_literals in format.traits:
                for shorthand_string in raw_case.shorthand_strings:
                    yield pytest.param(
                        format.name, raw_case.expected_literal, shorthand_string
                    )
            for quoted_string in raw_case.quoted_strings:
                yield pytest.param(
                    format.name, raw_case.expected_literal, quoted_string
                )


@pytest.mark.parametrize(
    ["format", "expected_literal", "literal_string"], make_literal_tests()
)
def test_literals(format: str, expected_literal: Literal, literal_string: str) -> None:
    """
    Literal strings parse to the expected literal.
    """
    g = Graph()
    g.parse(
        data=f"""<{EGNS.subject}> <{EGNS.predicate}> {literal_string} .""",
        format=format,
    )
    triples = list(g.triples((None, None, None)))
    assert len(triples) == 1
    assert expected_literal == triples[0][2]
