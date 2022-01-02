from rdflib import ConjunctiveGraph, URIRef


michel = URIRef("urn:michel")
tarek = URIRef("urn:tarek")
bob = URIRef("urn:bob")
likes = URIRef("urn:likes")
hates = URIRef("urn:hates")
pizza = URIRef("urn:pizza")
cheese = URIRef("urn:cheese")

c1 = URIRef("urn:context-1")
c2 = URIRef("urn:context-2")


def test_issue167_clarify_context_element_needs_final_clarification_repo():

    # Works as expected these days

    g1 = ConjunctiveGraph()
    g2 = ConjunctiveGraph()

    g1.get_context("urn:a").add((tarek, likes, cheese))
    g2.addN([(michel, likes, pizza, g1.get_context("urn:a"))])

    assert g2.store == g2.get_context("urn:a").store

    assert (
        repr(list(g1.contexts())[0])
        == "<Graph identifier=urn:a (<class 'rdflib.graph.Graph'>)>"
    )

    assert list(list(g1.contexts())[0]) == [
        (URIRef("urn:tarek"), URIRef("urn:likes"), URIRef("urn:cheese"))
    ]

    assert list(g1.get_context("urn:a")) == [
        (
            URIRef("urn:tarek"),
            URIRef("urn:likes"),
            URIRef("urn:cheese"),
        )
    ]
