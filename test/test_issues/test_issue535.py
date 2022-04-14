import pytest
from rdflib import URIRef
from rdflib.graph import Dataset


def test_nquads_default_graph():
    ds = Dataset()

    data = """
    <http://example.org/s1> <http://example.org/p1> <http://example.org/o1> .
    <http://example.org/s2> <http://example.org/p2> <http://example.org/o2> .
    <http://example.org/s3> <http://example.org/p3> <http://example.org/o3> <http://example.org/g3> .
    """

    publicID = URIRef("http://example.org/g0")

    ds.parse(data=data, format="nquads", publicID=publicID)

    assert len(ds) == 0
    assert len(list(ds.graphs())) == 2
    assert len(ds.graph(publicID)) == 2

def test_nquads_default_graph_default_union():
    ds = Dataset(default_union=True)

    data = """
    <http://example.org/s1> <http://example.org/p1> <http://example.org/o1> .
    <http://example.org/s2> <http://example.org/p2> <http://example.org/o2> .
    <http://example.org/s3> <http://example.org/p3> <http://example.org/o3> <http://example.org/g3> .
    """

    publicID = URIRef("http://example.org/g0")

    ds.parse(data=data, format="nquads", publicID=publicID)

    assert len(ds) == 3
    assert len(list(ds.contexts())) == 2
    assert len(ds.get_context(publicID)) == 2
