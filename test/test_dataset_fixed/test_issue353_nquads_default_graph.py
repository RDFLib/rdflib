from rdflib import URIRef


def test_issue353_nquads_default_graph(get_conjunctivegraph):

    # STATUS: FIXED

    data = """
    <http://example.org/s1> <http://example.org/p1> <http://example.org/o1> .
    <http://example.org/s2> <http://example.org/p2> <http://example.org/o2> .
    <http://example.org/s3> <http://example.org/p3> <http://example.org/o3> <http://example.org/g3> .
    """
    publicID = URIRef("http://example.org/g0")

    cg = get_conjunctivegraph
    cg.parse(data=data, format="nquads", publicID=publicID)

    assert len([q for q in cg.quads((None, None, None, None))]) == 3
    assert len([q for q in cg.quads((None, None, None, publicID))]) == 2
    assert (
        len([q for q in cg.quads((None, None, None, URIRef("http://example.org/g3")))])
        == 1
    )
