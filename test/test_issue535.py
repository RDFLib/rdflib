from rdflib import ConjunctiveGraph, URIRef

def test_nquads_default_graph():
    ds = ConjunctiveGraph()

    data = """
    <http://example.org/s1> <http://example.org/p1> <http://example.org/o1> .
    <http://example.org/s2> <http://example.org/p2> <http://example.org/o2> .
    <http://example.org/s3> <http://example.org/p3> <http://example.org/o3> <http://example.org/g3> .
    """

    publicID = URIRef("http://example.org/g0")
    
    ds.parse(data=data, format="nquads", publicID=publicID)

    assert len(ds) == 3, len(g)
    assert len(list(ds.contexts())) == 2, len(list(ds.contexts()))
    assert len(ds.get_context(publicID)) == 2, len(ds.get_context(publicID))
