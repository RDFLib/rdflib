from __future__ import annotations

from rdflib import Graph, Literal
from rdflib.collection import Collection
from test.utils.namespace import EGDC

prop = EGDC["props/a"]
res = EGDC["res"]

DATA_NO_CONTAINER = """
{
    "@context": {
        "egdc": "http://example.com/",
        "a": {
            "@id": "egdc:props/a"
        }
    },
    "a": [
        [[1, 2, 3], ["4", 5]],
        6,
        [7, { "@id": "egdc:res" }]
    ]
}
"""

DATA_LIST = """
{
    "@context": {
        "egdc": "http://example.com/",
        "a": {
            "@id": "egdc:props/a",
            "@container": "@list"
        }
    },
    "a": [
        [[1, 2, 3], ["4", 5]],
        6,
        [7, { "@id": "egdc:res" }]
    ]
}
"""


def test_container_list():
    g = Graph()
    g.parse(data=DATA_LIST, format="application/ld+json")

    outer = Collection(g, next(g.objects(predicate=prop)))
    assert len(outer) == 3
    inner1, inner2, inner3 = outer

    inner1 = Collection(g, inner1)
    inner1_1, inner1_2 = map(lambda l: Collection(g, l), inner1)  # noqa: E741
    assert list(inner1_1) == [Literal(x) for x in (1, 2, 3)]
    assert list(inner1_2) == [Literal(x) for x in ("4", 5)]

    assert inner2 == Literal(6)

    inner3 = Collection(g, inner3)
    assert list(inner3) == [Literal(7), res]


def test_no_container():
    g = Graph()
    g.parse(data=DATA_NO_CONTAINER, format="application/ld+json")

    assert len(g) == 8

    objects = set(g.objects(predicate=prop))
    assert len(objects) == 8
    assert objects == set([Literal(x) for x in (1, 2, 3, "4", 5, 6, 7)] + [res])
