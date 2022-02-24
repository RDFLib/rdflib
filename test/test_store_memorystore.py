import pytest

import rdflib


@pytest.fixture(scope="function", params=["SimpleMemory", "Memory"])
def get_graph(request):
    g = rdflib.Graph(request.param)
    yield g


def test_memory_store(get_graph):
    g = get_graph
    subj1 = rdflib.URIRef("http://example.org/foo#bar1")
    pred1 = rdflib.URIRef("http://example.org/foo#bar2")
    obj1 = rdflib.URIRef("http://example.org/foo#bar3")
    triple1 = (subj1, pred1, obj1)
    triple2 = (
        subj1,
        rdflib.URIRef("http://example.org/foo#bar4"),
        rdflib.URIRef("http://example.org/foo#bar5"),
    )
    g.add(triple1)
    assert len(g) == 1
    g.add(triple2)
    assert len(list(g.triples((subj1, None, None)))) == 2
    assert len(list(g.triples((None, pred1, None)))) == 1
    assert len(list(g.triples((None, None, obj1)))) == 1
    g.remove(triple1)
    assert len(g) == 1
    assert len(g.serialize()) > 0
