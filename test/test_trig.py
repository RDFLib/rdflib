import re

import rdflib

TRIPLE = (
    rdflib.URIRef("http://example.com/s"),
    rdflib.RDFS.label,
    rdflib.Literal("example 1"),
)


def test_empty():
    g = rdflib.Graph()
    s = g.serialize(format="trig")
    assert s is not None


def test_repeat_triples():
    g = rdflib.Dataset()
    g.get_context("urn:a").add(
        (rdflib.URIRef("urn:1"), rdflib.URIRef("urn:2"), rdflib.URIRef("urn:3"))
    )

    g.get_context("urn:b").add(
        (rdflib.URIRef("urn:1"), rdflib.URIRef("urn:2"), rdflib.URIRef("urn:3"))
    )

    assert len(g.get_context("urn:a")) == 1
    assert len(g.get_context("urn:b")) == 1

    s = g.serialize(format="trig", encoding="latin-1")
    assert b"{}" not in s  # no empty graphs!


def test_same_subject():
    g = rdflib.Dataset()
    g.get_context("urn:a").add(
        (rdflib.URIRef("urn:1"), rdflib.URIRef("urn:p1"), rdflib.URIRef("urn:o1"))
    )

    g.get_context("urn:b").add(
        (rdflib.URIRef("urn:1"), rdflib.URIRef("urn:p2"), rdflib.URIRef("urn:o2"))
    )

    assert len(g.get_context("urn:a")) == 1
    assert len(g.get_context("urn:b")) == 1

    s = g.serialize(format="trig", encoding="latin-1")

    assert len(re.findall(b"p1", s)) == 1
    assert len(re.findall(b"p2", s)) == 1

    assert b"{}" not in s  # no empty graphs!


def test_remember_namespace():
    g = rdflib.Dataset()
    g.add(TRIPLE + (rdflib.URIRef("http://example.com/graph1"),))
    # In 4.2.0 the first serialization would fail to include the
    # prefix for the graph but later serialize() calls would work.
    first_out = g.serialize(format="trig", encoding="latin-1")
    second_out = g.serialize(format="trig", encoding="latin-1")
    assert b"@prefix ns1: <http://example.com/> ." not in second_out
    assert b"@prefix ns1: <http://example.com/> ." not in first_out


def test_graph_qname_syntax():
    g = rdflib.Dataset()
    g.add(TRIPLE + (rdflib.URIRef("http://example.com/graph1"),))
    out = g.serialize(format="trig", encoding="latin-1")
    assert b"ns1:graph1 {" not in out


def test_graph_uri_syntax():
    g = rdflib.Dataset()
    # getQName will not abbreviate this, so it should serialize as
    # a '<...>' term.
    g.add(TRIPLE + (rdflib.URIRef("http://example.com/foo."),))
    out = g.serialize(format="trig", encoding="latin-1")
    assert b"<http://example.com/foo.> {" in out


def test_blank_graph_identifier():
    g = rdflib.Dataset()
    g.add(TRIPLE + (rdflib.BNode(),))
    out = g.serialize(format="trig", encoding="latin-1")
    graph_label_line = out.splitlines()[-4]

    assert re.match(rb"^_:[a-zA-Z0-9]+ \{", graph_label_line)


def test_graph_parsing():
    # should parse into single default graph context
    data = """
<http://example.com/thing#thing_a> <http://example.com/knows> <http://example.com/thing#thing_b> .
"""
    g = rdflib.Dataset()
    g.parse(data=data, format="trig")
    assert len(list(g.contexts())) == 1

    # should parse into single default graph context
    data = """
<http://example.com/thing#thing_a> <http://example.com/knows> <http://example.com/thing#thing_b> .

{ <http://example.com/thing#thing_c> <http://example.com/knows> <http://example.com/thing#thing_d> . }
"""
    g = rdflib.Dataset()
    g.parse(data=data, format="trig")
    assert len(list(g.contexts())) == 1

    # should parse into 2 contexts, one default, one named
    data = """
<http://example.com/thing#thing_a> <http://example.com/knows> <http://example.com/thing#thing_b> .

{ <http://example.com/thing#thing_c> <http://example.com/knows> <http://example.com/thing#thing_d> . }

<http://example.com/graph#graph_a> {
    <http://example.com/thing/thing_e> <http://example.com/knows> <http://example.com/thing#thing_f> .
}
"""
    g = rdflib.Dataset()
    g.parse(data=data, format="trig")
    assert len(list(g.contexts())) == 2


def test_round_trips():
    data = """
<http://example.com/thing#thing_a> <http://example.com/knows> <http://example.com/thing#thing_b> .

{ <http://example.com/thing#thing_c> <http://example.com/knows> <http://example.com/thing#thing_d> . }

<http://example.com/graph#graph_a> {
    <http://example.com/thing/thing_e> <http://example.com/knows> <http://example.com/thing#thing_f> .
}
"""
    g = rdflib.Dataset()
    for i in range(5):
        g.parse(data=data, format="trig")
        data = g.serialize(format="trig")

    # output should only contain 1 mention of each resource/graph name
    assert data.count("thing_a") == 1
    assert data.count("thing_b") == 1
    assert data.count("thing_c") == 1
    assert data.count("thing_d") == 1
    assert data.count("thing_e") == 1
    assert data.count("thing_f") == 1
    assert data.count("graph_a") == 1


def test_default_graph_serializes_without_name():
    data = """
<http://example.com/thing#thing_a> <http://example.com/knows> <http://example.com/thing#thing_b> .

{ <http://example.com/thing#thing_c> <http://example.com/knows> <http://example.com/thing#thing_d> . }
"""
    g = rdflib.Dataset()
    g.parse(data=data, format="trig")
    data = g.serialize(format="trig", encoding="latin-1")

    assert b"None" not in data


def test_prefixes():
    data = """
    @prefix ns1: <http://ex.org/schema#> .
    <http://ex.org/docs/document1> = {
        ns1:Person_A a ns1:Person ;
            ns1:TextSpan "Simon" .
    }
    <http://ex.org/docs/document2> = {
        ns1:Person_C a ns1:Person ;
            ns1:TextSpan "Agnes" .
    }
    """

    cg = rdflib.Dataset()
    cg.parse(data=data, format="trig")
    data = cg.serialize(format="trig", encoding="latin-1")

    assert "ns2: <http://ex.org/docs/".encode("latin-1") not in data, data
    assert "<ns2:document1>".encode("latin-1") not in data, data
    assert "ns2:document1".encode("latin-1") not in data, data


def test_issue_2154():
    ds = rdflib.Dataset()
    sg = ds.serialize(format="trig")
    assert "prefix" not in sg, sg
