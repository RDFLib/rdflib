import sys
from typing import Optional

import pytest

from rdflib import Graph, Literal, URIRef, Variable

EX = "http://example.org/"


def _query_values(size: int, modifiers: str) -> list[int]:
    g = Graph()
    for i in range(size):
        g.add((URIRef(f"{EX}s{i}"), URIRef(f"{EX}p"), Literal(i)))
    query = f"SELECT ?o WHERE {{ ?s ?p ?o }} ORDER BY ?o {modifiers}"
    return [int(row[Variable("o")]) for row in g.query(query).bindings]


@pytest.mark.parametrize("size", [0, 3])
@pytest.mark.parametrize(
    ("offset", "limit"),
    [
        (sys.maxsize + 1, None),
        (sys.maxsize, 1),
        (1, sys.maxsize),
        (0, sys.maxsize + 1),
        (sys.maxsize + 1, sys.maxsize + 1),
    ],
)
def test_slice_bounds_above_maxsize(
    size: int, offset: int, limit: Optional[int]
) -> None:
    modifiers = f"OFFSET {offset}"
    stop = None
    if limit is not None:
        modifiers += f" LIMIT {limit}"
        stop = offset + limit
    assert _query_values(size, modifiers) == list(range(size))[offset:stop]


@pytest.mark.parametrize(
    ("modifiers", "expected"),
    [
        ("LIMIT 2", [0, 1]),
        ("OFFSET 3", [3, 4]),
        ("LIMIT 2 OFFSET 1", [1, 2]),
        ("LIMIT 0", []),
        ("OFFSET 5", []),
    ],
)
def test_slice_bounds_normal_paging(modifiers: str, expected: list[int]) -> None:
    assert _query_values(5, modifiers) == expected
