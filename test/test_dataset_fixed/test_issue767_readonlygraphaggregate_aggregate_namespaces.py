from rdflib import Graph, Namespace, OWL, URIRef
from rdflib.graph import ReadOnlyGraphAggregate


def test_issue767_readonlygraphaggregate_aggregate_namespaces():
    # STATUS: Fixed - ReadOnlyGraphAggregate _doesn't_ aggregate namespaces, by design.

    g = Graph()

    h = ReadOnlyGraphAggregate([g])

    ns = Namespace("http://example.org/")
    g.bind("ex", ns)
    # g.add((rdflib.Literal("fish"), rdflib.OWL.differentFrom, rdflib.Literal("bird")))
    g.add((URIRef(ns + "fish"), OWL.differentFrom, URIRef(ns + "bird")))

    h = ReadOnlyGraphAggregate([g])

    assert len(list(h.namespaces())) == len(list(g.namespaces())) - 1
