from rdflib import ConjunctiveGraph, Graph, Literal, RDFS, URIRef


def test_issue1188_with_conjunctivegraph_and_graph():
    g1 = ConjunctiveGraph()
    g2 = Graph()
    u = URIRef("http://example.com/foo")
    g1.add([u, RDFS.label, Literal("foo")])
    g1.add([u, RDFS.label, Literal("bar")])

    g2.add([u, RDFS.label, Literal("foo")])
    g2.add([u, RDFS.label, Literal("bing")])

    assert len(g1 + g2) == 3  # adds bing as label
    assert len(g1 - g2) == 1  # removes foo
    assert len(g1 * g2) == 1  # only foo

    g1 += g2  # now g1 contains everything
    assert len(g1) == 3
