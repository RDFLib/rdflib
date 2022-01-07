from rdflib import ConjunctiveGraph, URIRef

michel = URIRef("urn:example:michel")
tarek = URIRef("urn:example:tarek")
bob = URIRef("urn:example:bob")
likes = URIRef("urn:example:likes")
hates = URIRef("urn:example:hates")
pizza = URIRef("urn:example:pizza")
cheese = URIRef("urn:example:cheese")

c1 = URIRef("urn:example:context-1")
c2 = URIRef("urn:example:context-2")


def test_issue167_clarify_context_element_needs_final_clarification():

    g = ConjunctiveGraph()

    g.get_context(c1).add((bob, likes, pizza))
    g.get_context(c2).add((bob, likes, pizza))

    g1 = ConjunctiveGraph()
    g2 = ConjunctiveGraph()

    g1.get_context("urn:example:a").add((tarek, likes, pizza))

    g2.addN([(bob, likes, cheese, g1.get_context("urn:example:a"))])

    assert g2.store == g2.get_context("urn:example:a").store

    ctx = list(g1.contexts())[0]
    assert (
        str(ctx)
        == "<urn:example:a> a rdfg:Graph;rdflib:storage [a rdflib:Store;rdfs:label 'Memory']."
    )

    ctx = list(list(g1.contexts())[0])
    assert (
        str(ctx)
        == "[(rdflib.term.URIRef('urn:example:tarek'), rdflib.term.URIRef('urn:example:likes'), rdflib.term.URIRef('urn:example:pizza'))]"
    )

    ctx = list(g1.get_context("urn:example:a"))
    assert (
        str(ctx)
        == "[(rdflib.term.URIRef('urn:example:tarek'), rdflib.term.URIRef('urn:example:likes'), rdflib.term.URIRef('urn:example:pizza'))]"
    )


def test_issue167_clarify_context_element_needs_final_clarification_take2():

    g1 = ConjunctiveGraph()
    g1.get_context("urn:example:a").add((tarek, likes, cheese))

    g2 = ConjunctiveGraph()
    g2.addN([(michel, likes, pizza, g1.get_context("urn:example:a"))])

    assert g2.store == g2.get_context("urn:example:a").store

    assert (
        str(list(g1.contexts())[0])
        == "<urn:example:a> a rdfg:Graph;rdflib:storage [a rdflib:Store;rdfs:label 'Memory']."
    )

    assert list(list(g1.contexts())[0]) == [
        (
            URIRef("urn:example:tarek"),
            URIRef("urn:example:likes"),
            URIRef("urn:example:cheese"),
        )
    ]

    assert list(g1.get_context("urn:example:a")) == [
        (
            URIRef("urn:example:tarek"),
            URIRef("urn:example:likes"),
            URIRef("urn:example:cheese"),
        )
    ]
