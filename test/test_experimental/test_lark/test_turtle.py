from test.data import context0

import rdflib
from rdflib import ConjunctiveGraph, Literal, URIRef

rdflib.plugin.register(
    "larkttl",
    rdflib.parser.Parser,
    "rdflib.experimental.plugins.parsers.larkturtle",
    "LarkTurtleParser",
)


def test_larkturtle_1():
    data = """@prefix dc: <http://purl.org/dc/elements/1.1/> .

<http://www.dajobe.org/>
      dc:creator "Dave Beckett" ;
      dc:description "The generic home page of Dave Beckett." ;
      dc:title "Dave Beckett's Home Page" .
"""
    ds = ConjunctiveGraph(identifier=context0)
    ds.parse(
        data=data,
        format="larkttl",
    )

    assert sorted(list(ds))[2][2] == Literal("Dave Beckett's Home Page")


def test_larkturtle_2():
    data = """@prefix : <#> .
    [] :x :y .
    """
    # data = """<http://a.example/s> a <http://a.example/o> ."""
    ds = ConjunctiveGraph(identifier=context0)
    ds.parse(
        data=data,
        format="larkttl",
        base=URIRef("http://example/"),
        preserve_bnode_ids=True,
    )

    assert len(sorted(list(ds))) == 1
