"""
This module is intended for tests related to quoting/escaping and
unquoting/unescaping in various formats that are related to turtle, such as
ntriples, nquads, trig and n3.
"""

from typing import Callable, Dict, Iterable, List, Tuple
import pytest
from rdflib.graph import ConjunctiveGraph

from rdflib.plugins.parsers import ntriples
from rdflib.term import Literal

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


def make_correctness_pairs() -> List[Tuple[str, str]]:
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


CORRECTNESS_PAIRS = make_correctness_pairs()


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


def make_correctness_tests(
    selectors: Iterable[str],
) -> Iterable[Tuple[str, str, str]]:
    """
    This function creates a cartesian product of the selectors and
    `CORRECTNESS_PAIRS` that is suitable for use as pytest parameters.
    """
    for selector in selectors:
        for quoted, unquoted in CORRECTNESS_PAIRS:
            yield selector, quoted, unquoted


@pytest.mark.parametrize(
    "unquoter_key, quoted, unquoted", make_correctness_tests(unquoters.keys())
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
    make_correctness_tests(["turtle", "ntriples", "nquads"]),
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
