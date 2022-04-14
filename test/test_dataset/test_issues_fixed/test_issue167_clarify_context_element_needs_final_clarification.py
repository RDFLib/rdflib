import pytest

from rdflib import URIRef
from rdflib.graph import Dataset

michel = URIRef("urn:example:michel")
tarek = URIRef("urn:example:tarek")
bob = URIRef("urn:example:bob")
likes = URIRef("urn:example:likes")
hates = URIRef("urn:example:hates")
pizza = URIRef("urn:example:pizza")
cheese = URIRef("urn:example:cheese")

c1 = URIRef("urn:example:context-1")
c2 = URIRef("urn:example:context-2")

exa = URIRef("urn:example:a")


def test_issue167_clarify_context_element_needs_final_clarification():

    g = Dataset()

    g.graph(c1).add((bob, likes, pizza))
    g.graph(c2).add((bob, likes, pizza))

    g1 = Dataset()
    g2 = Dataset()

    g1.graph(exa).add((tarek, likes, pizza))

    # Supplying a Graph as context raises an EXception
    with pytest.raises(Exception):
        g2.addN([(bob, likes, cheese, g1.graph(exa))])

    # Supplying a URIRef as context is accepted
    g2.addN([(bob, likes, cheese, exa)])

    assert g2.store == g2.graph(exa).store

    ctx = list(sorted(g1.contexts()))[0]
    assert str(ctx) == "urn:example:a"

    ctx = list(sorted(g1.contexts()))[0]
    assert str(ctx) == "urn:example:a"

    ctx = list(g1.graph(exa))
    assert (
        str(ctx)
        == "[(rdflib.term.URIRef('urn:example:tarek'), rdflib.term.URIRef('urn:example:likes'), rdflib.term.URIRef('urn:example:pizza'))]"
    )


def test_issue167_clarify_context_element_needs_final_clarification_take2():

    g1 = Dataset()
    g1.graph(exa).add((tarek, likes, cheese))

    g2 = Dataset()
    # Supplying a Graph as context raises an EXception
    with pytest.raises(Exception):
        g2.addN([(michel, likes, pizza, g1.graph(exa))])

    # Supplying a URIRef as context is accepted
    g2.addN([(bob, likes, cheese, exa)])

    assert g2.store == g2.graph(exa).store

    assert sorted(list(g1.contexts()))[0] == exa

    assert list(g1.graph(sorted(list(g1.contexts()))[0])) == [
        (
            URIRef("urn:example:tarek"),
            URIRef("urn:example:likes"),
            URIRef("urn:example:cheese"),
        )
    ]

    assert list(g1.graph(exa)) == [
        (
            URIRef("urn:example:tarek"),
            URIRef("urn:example:likes"),
            URIRef("urn:example:cheese"),
        )
    ]
