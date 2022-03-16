"""
This module is intended for tests related to unquoting/unescaping in various
formats that are related to turtle, such as ntriples, nquads, trig and n3.
"""

import itertools
import logging
from typing import Callable, Dict, Iterable, List, Tuple
import pytest
from rdflib.graph import ConjunctiveGraph, Graph

from rdflib.plugins.parsers import ntriples
from rdflib.term import Literal, URIRef
from rdflib import Namespace
from .testutils import GraphHelper

# https://www.w3.org/TR/turtle/#string
string_escape_map = {
    "t": "\t",
    "b": "\b",
    "n": "\n",
    "r": "\r",
    "f": "\f",
    '"': '"',
    "'": "'",
    "\\": "\\",
}

import re


def make_unquote_correctness_pairs() -> List[Tuple[str, str]]:
    """
    Creates pairs of quoted and unquoted strings.
    """
    result = []

    def add_pair(escape: str, unescaped: str) -> None:
        result.append((f"\\{escape}", unescaped))
        result.append((f"\\\\{escape}", f"\\{escape}"))
        result.append((f"\\\\\\{escape}", f"\\{unescaped}"))

    chars = "A1a\\\nøæå"
    for char in chars:
        code_point = ord(char)
        add_pair(f"u{code_point:04x}", char)
        add_pair(f"u{code_point:04X}", char)
        add_pair(f"U{code_point:08x}", char)
        add_pair(f"U{code_point:08X}", char)

    string_escapes = "tbnrf'"
    for char in string_escapes:
        add_pair(f"{char}", string_escape_map[char])

    # special handling because «"» should not appear in string, and add_pair
    # will add it.
    result.append(('\\"', '"'))
    result.append(('\\\\\\"', '\\"'))

    # special handling because «\» should not appear in string, and add_pair
    # will add it.
    result.append(("\\\\", "\\"))
    result.append(("\\\\\\\\", "\\\\"))

    return result


UNQUOTE_CORRECTNESS_PAIRS = make_unquote_correctness_pairs()


def ntriples_unquote_validate(input: str) -> str:
    """
    This function wraps `ntriples.unquote` in a way that ensures that `ntriples.validate` is always ``True`` when it runs.
    """
    old_validate = ntriples.validate
    try:
        ntriples.validate = True
        return ntriples.unquote(input)
    finally:
        ntriples.validate = old_validate


def ntriples_unquote(input: str) -> str:
    """
    This function wraps `ntriples.unquote` in a way that ensures that `ntriples.validate` is always ``False`` when it runs.
    """
    old_validate = ntriples.validate
    try:
        ntriples.validate = False
        return ntriples.unquote(input)
    finally:
        ntriples.validate = old_validate


unquoters: Dict[str, Callable[[str], str]] = {
    "ntriples_unquote": ntriples_unquote,
    "ntriples_unquote_validate": ntriples_unquote_validate,
}


def make_unquote_correctness_tests(
    selectors: Iterable[str],
) -> Iterable[Tuple[str, str, str]]:
    """
    This function creates a cartesian product of the selectors and
    `CORRECTNESS_PAIRS` that is suitable for use as pytest parameters.
    """
    for selector in selectors:
        for quoted, unquoted in UNQUOTE_CORRECTNESS_PAIRS:
            yield selector, quoted, unquoted


@pytest.mark.parametrize(
    "unquoter_key, quoted, unquoted", make_unquote_correctness_tests(unquoters.keys())
)
def test_unquote_correctness(
    unquoter_key: str,
    quoted: str,
    unquoted: str,
) -> None:
    """
    Various unquote functions work correctly.
    """
    unquoter = unquoters[unquoter_key]
    assert unquoted == unquoter(quoted)


QUAD_FORMATS = {"nquads"}


@pytest.mark.parametrize(
    "format, quoted, unquoted",
    make_unquote_correctness_tests(["turtle", "ntriples", "nquads"]),
)
def test_parse_correctness(
    format: str,
    quoted: str,
    unquoted: str,
) -> None:
    """
    Quoted strings parse correctly
    """
    if format in QUAD_FORMATS:
        data = f'<example:Subject> <example:Predicate> "{quoted}" <example:Graph>.'
    else:
        data = f'<example:Subject> <example:Predicate> "{quoted}".'
    graph = ConjunctiveGraph()
    graph.parse(data=data, format=format)
    objs = list(graph.objects())
    assert len(objs) == 1
    obj = objs[0]
    assert isinstance(obj, Literal)
    assert isinstance(obj.value, str)
    assert obj.value == unquoted


EGNS = Namespace("http://example.com/")


@pytest.mark.parametrize(
    "format, char, escaped",
    [
        (format, char, escaped)
        for format, (char, escaped) in itertools.product(
            ["turtle"],
            [
                (r"x", r"x"),
                (r"(", r"\("),
                (r")", r"\)"),
            ],
        )
    ],
)
def test_pname_escaping(format: str, char: str, escaped: str) -> None:
    graph = Graph()
    triple = (
        URIRef(EGNS["prefix/John_Doe"]),
        URIRef(EGNS[f"prefix/prop{char}"]),
        Literal("foo", lang="en"),
    )
    graph.bind("egns", EGNS["prefix/"])
    graph.add(triple)
    data = graph.serialize(format=format)
    pattern = re.compile(f"\\segns:prop{re.escape(escaped)}\\s")
    logging.debug(
        "format = %s, char = %r, escaped = %r, pattern = %r, data = %s",
        format,
        char,
        escaped,
        pattern,
        data,
    )
    assert re.search(pattern, data) is not None


# https://www.w3.org/TR/turtle/#grammar-production-PN_LOCAL_ESC
# Not including %, as % should be used for percent encoding.
PN_LOCAL_ESC_CHARS = r"_~.-!$&'()*+,;=/?#@"


@pytest.mark.parametrize(
    "format, char",
    itertools.product(["turtle", "ntriples"], "A2c" + PN_LOCAL_ESC_CHARS),
)
def test_serialize_roundtrip(format: str, char: str) -> None:
    graph = Graph()
    triple = (
        URIRef(EGNS["prefix/John_Doe"]),
        URIRef(EGNS[f"prefix/prop{char}"]),
        Literal("foo", lang="en"),
    )
    graph.add(triple)
    graph.bind("egns", EGNS["prefix/"])
    data = graph.serialize(format=format)
    logging.debug("format = %s, char = %s, data = %s", format, char, data)
    parsed_graph = Graph()
    parsed_graph.parse(data=data, format=format)
    GraphHelper.assert_sets_equals(graph, parsed_graph)
