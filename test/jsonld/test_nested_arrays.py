# -*- coding: UTF-8 -*-

from rdflib import Graph, Literal, URIRef
from rdflib.collection import Collection
from rdflib.plugin import Parser, register

register("json-ld", Parser, "rdflib.plugins.parsers.jsonld", "JsonLDParser")
register("application/ld+json", Parser, "rdflib.plugins.parsers.jsonld", "JsonLDParser")

prop = URIRef("http://example.com/props/a")
res = URIRef("http://example.com/res")

data_no_container = """
{
    "@context": {
        "a": {
            "@id": "_PROP_ID_"
        }
    },
    "a": [
        [[1, 2, 3], ["4", 5]],
        6,
        [7, { "@id": "_RES_ID_" }]
    ]
}
""".replace(
    "_PROP_ID_", str(prop)
).replace(
    "_RES_ID_", str(res)
)

data_list = """
{
    "@context": {
        "a": {
            "@id": "_PROP_ID_",
            "@container": "@list"
        }
    },
    "a": [
        [[1, 2, 3], ["4", 5]],
        6,
        [7, { "@id": "_RES_ID_" }]
    ]
}
""".replace(
    "_PROP_ID_", str(prop)
).replace(
    "_RES_ID_", str(res)
)


def test_container_list():
    g = Graph()
    g.parse(data=data_list, format="application/ld+json")

    outer = Collection(g, next(g.objects(predicate=prop)))
    assert len(outer) == 3
    inner1, inner2, inner3 = outer

    inner1 = Collection(g, inner1)
    inner1_1, inner1_2 = map(lambda l: Collection(g, l), inner1)
    assert list(inner1_1) == [Literal(x) for x in (1, 2, 3)]
    assert list(inner1_2) == [Literal(x) for x in ("4", 5)]

    assert inner2 == Literal(6)

    inner3 = Collection(g, inner3)
    assert list(inner3) == [Literal(7), res]


def test_no_container():
    g = Graph()
    g.parse(data=data_no_container, format="application/ld+json")

    assert len(g) == 8

    objects = set(g.objects(predicate=prop))
    assert len(objects) == 8
    assert objects == set([Literal(x) for x in (1, 2, 3, "4", 5, 6, 7)] + [res])
