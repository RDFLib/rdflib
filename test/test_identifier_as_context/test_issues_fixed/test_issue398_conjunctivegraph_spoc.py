from rdflib import (
    Dataset,
    Graph,
    RDF,
    FOAF,
    URIRef,
    plugin,
)
from rdflib.plugin import Store


def test_issue398():

    store = plugin.get("Memory", Store)()

    g1 = Graph(store=store, identifier="http://example.com/graph#1")
    g2 = Graph(store=store, identifier="http://example.com/graph#2")
    g3 = Graph(store=store, identifier="http://example.com/graph#3")

    donna = URIRef("http://example.org/donna")

    g1.addN([(donna, RDF.type, FOAF.Person, g1)])
    g2.addN([(donna, RDF.type, FOAF.Person, g2)])
    g3.addN([(donna, RDF.type, FOAF.Person, g3)])

    dataset = Dataset(store)

    assert len(list(dataset.quads((None, None, None, None)))) == 3

    assert len(list(dataset.quads((None, None, None, g1.identifier)))) == 1

    assert len(list(dataset.quads((donna, None, None, g1.identifier)))) == 1

    assert len(list(dataset.quads((donna, RDF.type, None, g1.identifier)))) == 1

    assert len(list(dataset.quads((donna, RDF.type, FOAF.Person, g1.identifier)))) == 1
