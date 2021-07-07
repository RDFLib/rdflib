# -*- coding: UTF-8 -*-

import re
import json
import itertools
from rdflib import Graph
from rdflib.plugin import register, Serializer

register("json-ld", Serializer, "rdflib.plugins.serializers.jsonld", "JsonLDSerializer")


cases = []


def case(*args):
    cases.append(args)


case(
    """
@prefix dc: <http://purl.org/dc/terms/> .
<http://example.org/>
    dc:title "Homepage"@en .
""",
    {
        "@context": {"@vocab": "http://purl.org/dc/terms/", "@language": "en"},
        "@id": "http://example.org/",
        "title": "Homepage",
    },
)


case(
    """
@prefix dc: <http://purl.org/dc/terms/> .
<http://example.org/>
    dc:title "Homepage"@en, "Hemsida"@sv .
""",
    {
        "@context": {
            "@vocab": "http://purl.org/dc/terms/",
            "title": {"@container": "@language"},
        },
        "@id": "http://example.org/",
        "title": {"en": "Homepage", "sv": "Hemsida"},
    },
)


case(
    """
@prefix dc: <http://purl.org/dc/terms/> .
<http://example.org/>
    dc:title "Homepage"@en, "Hemsida"@sv .
""",
    {
        "@context": {
            "@vocab": "http://purl.org/dc/terms/",
            "@language": "sv",
            "title_en": {"@id": "title", "@language": "en"},
        },
        "@id": "http://example.org/",
        "title_en": "Homepage",
        "title": "Hemsida",
    },
)


# .. Requires set values to be sorted to be predictable
# case("""
# @prefix dc: <http://purl.org/dc/terms/> .
# <http://example.org/>
#    dc:title "Homepage"@en, "Home Page"@en, "Home Page"@en-GB, "Hemsida"@sv .
# """,
# {
#    "@context": "-||-",
#    "@id": "http://example.org/",
#    "title_en": ["Homepage", "Home Page"],
#    "title": [{"@language": "en-GB", "@value": "Home Page"}, "Hemsida"]
# }
# )


case(
    """
@prefix dc: <http://purl.org/dc/terms/> .
<http://example.org/easter_island>
    dc:title "Påskön"@sv .
""",
    {
        "@context": {"@vocab": "http://purl.org/dc/terms/", "@language": "sv"},
        "@id": "http://example.org/easter_island",
        "title": "Påskön",
    },
)


case(
    """
@prefix : <http://example.org/ns#> .
<http://example.org/> :has _:blank-1 .
""",
    {
        "@context": {"has": {"@type": "@id", "@id": "http://example.org/ns#has"}},
        "@id": "http://example.org/",
        "has": "_:blank-1",
    },
)


case(
    """
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix : <http://example.org/ns#> .
:Something rdfs:subClassOf :Thing .
""",
    {
        "@context": {
            "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
            "v": "http://example.org/ns#",
            "rdfs:subClassOf": {"@container": "@set"},
        },
        "@id": "v:Something",
        "rdfs:subClassOf": [{"@id": "v:Thing"}],
    },
)


case(
    """
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix : <http://example.org/ns#> .
:Something rdfs:subClassOf :Thing .
""",
    {
        "@context": {
            "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
            "v": "http://example.org/ns#",
            "subClassOf": {
                "@id": "rdfs:subClassOf",
                "@type": "@id",
                "@container": "@set",
            },
        },
        "@id": "v:Something",
        "subClassOf": ["v:Thing"],
    },
)


case(
    """
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix : <http://example.org/ns#> .
:World owl:unionOf (:Everyhing :Nothing) .
""",
    {
        "@context": {
            "owl": "http://www.w3.org/2002/07/owl#",
            "v": "http://example.org/ns#",
        },
        "@id": "v:World",
        "owl:unionOf": {"@list": [{"@id": "v:Everyhing"}, {"@id": "v:Nothing"}]},
    },
)


case(
    """
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix : <http://example.org/ns#> .
:World owl:unionOf (:Everyhing :Nothing) .
""",
    {
        "@context": {
            "owl": "http://www.w3.org/2002/07/owl#",
            "v": "http://example.org/ns#",
            "unionOf": {"@id": "owl:unionOf", "@container": "@list"},
        },
        "@id": "v:World",
        "unionOf": [{"@id": "v:Everyhing"}, {"@id": "v:Nothing"}],
    },
)


case(
    """
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix : <http://example.org/ns#> .
:World owl:unionOf (:Everyhing :Nothing) .
""",
    {
        "@context": {
            "owl": "http://www.w3.org/2002/07/owl#",
            "v": "http://example.org/ns#",
            "unionOf": {"@id": "owl:unionOf", "@type": "@id", "@container": "@list"},
        },
        "@id": "v:World",
        "unionOf": ["v:Everyhing", "v:Nothing"],
    },
)


# Shorten result IRIs by using @base
case(
    """
BASE <http://example.org/>
PREFIX : <http://example.org/vocab/>
<Thing> a :Class .
<Work> a :Class; :subClassOf <Thing> .
</some/path/> a :Thing .
</some/path/#this> a :Thing .
</some/path/#other> a :Thing .
""",
    {
        "@context": {
            "@base": "http://example.org/some/path/#other",
            "@vocab": "http://example.org/vocab/",
        },
        "@graph": [
            {"@id": "/Thing", "@type": "Class"},
            {"@id": "/Work", "@type": "Class", "subClassOf": {"@id": "/Thing"}},
            {"@id": "", "@type": "Thing"},
            {"@id": "/some/path/#this", "@type": "Thing"},
            {"@id": "/some/path/#other", "@type": "Thing"},
        ],
    },
)


json_kwargs = dict(indent=2, separators=(",", ": "), sort_keys=True, ensure_ascii=False)


def run(data, expected):
    g = Graph().parse(data=data, format="turtle")
    result = g.serialize(format="json-ld", context=expected["@context"])
    result = json.loads(result)

    sort_graph(result)
    result = json.dumps(result, **json_kwargs)
    incr = itertools.count(1)
    result = re.sub(r'"_:[^"]+"', lambda m: '"_:blank-%s"' % next(incr), result)

    sort_graph(expected)
    expected = json.dumps(expected, **json_kwargs)

    assert result == expected, "Expected not equal to result: %s" % result


def sort_graph(data):
    if "@graph" in data:
        data["@graph"].sort(key=lambda node: node.get("@id"))


def test_cases():
    for data, expected in cases:
        yield run, data, expected
