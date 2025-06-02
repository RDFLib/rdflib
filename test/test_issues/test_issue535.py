from rdflib import Dataset, URIRef


def test_nquads_default_graph():
    ds = Dataset(default_union=True)

    data = """
    <http://example.org/s1> <http://example.org/p1> <http://example.org/o1> .
    <http://example.org/s2> <http://example.org/p2> <http://example.org/o2> .
    <http://example.org/s3> <http://example.org/p3> <http://example.org/o3> <http://example.org/g3> .
    """

    publicID = URIRef("http://example.org/g0")  # noqa: N806

    ds.parse(data=data, format="nquads", publicID=publicID)

    assert len(ds) == 3, len(g)  # noqa: F821
    assert len(list(ds.contexts())) == 2, len(list(ds.contexts()))
    assert len(ds.default_context) == 2, len(ds.get_context(publicID))
