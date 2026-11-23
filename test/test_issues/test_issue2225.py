from __future__ import annotations

import io

from rdflib import RDFS, BNode, Graph, Literal, Namespace
from rdflib.tools.rdf2dot import rdf2dot

TTL_ISSUE_2225 = """\
@prefix foo: <https://www.resource.org/foo/> .
@prefix bar: <https://example.com/bar/> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

foo:_1 a bar:node ;
    bar:pair_in_hoge foo:_2 .
foo:_3 a bar:node ;
    bar:pair_in_fuga foo:_2 .
"""


def test_rdf2dot_includes_namespace_prefix_in_node_labels() -> None:
    g = Graph().parse(data=TTL_ISSUE_2225, format="turtle")
    stream = io.StringIO()
    rdf2dot(g, stream)
    dot = stream.getvalue()

    assert "<B>foo:_1</B>" in dot
    assert "<B>foo:_2</B>" in dot
    assert "<B>foo:_3</B>" in dot
    assert "<B>bar:node</B>" in dot


def test_rdf2dot_label_property_and_bnode_fallback() -> None:
    ex = Namespace("http://example.org/")
    g = Graph()
    g.bind("ex", ex)
    b = BNode("blank1")
    g.add((ex.labeled, RDFS.label, Literal("Custom Label")))
    g.add((ex.labeled, ex.rel, b))
    g.add((b, ex.rel, ex.target))

    stream = io.StringIO()
    rdf2dot(g, stream)
    dot = stream.getvalue()

    assert "<B>Custom Label</B>" in dot
    assert "<B>ex:target</B>" in dot
    assert "<B>blank1</B>" in dot
