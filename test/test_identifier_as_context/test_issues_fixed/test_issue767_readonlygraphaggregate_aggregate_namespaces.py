from rdflib import Graph, Namespace, OWL, URIRef
from rdflib.graph import ReadOnlyGraphAggregate


def test_issue767_readonlygraphaggregate_aggregate_namespaces():

    g = Graph()

    h = ReadOnlyGraphAggregate([g])

    ns = Namespace("http://example.org/")
    g.bind("ex", ns)

    g.add((URIRef(ns + "fish"), OWL.differentFrom, URIRef(ns + "bird")))

    h = ReadOnlyGraphAggregate([g])

    assert len(list(h.namespaces())) == len(list(g.namespaces())) - 1
