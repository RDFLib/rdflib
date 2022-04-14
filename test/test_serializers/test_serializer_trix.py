#!/usr/bin/env python

from io import BytesIO

import pytest

from rdflib.graph import DATASET_DEFAULT_GRAPH_ID, Dataset, Graph
from rdflib.term import BNode, Literal, URIRef


def test_serialize():

    s1 = URIRef("store:1")
    r1 = URIRef("resource:1")
    r2 = URIRef("resource:2")

    label = URIRef("predicate:label")

    g1 = Graph(identifier=s1)
    g1.add((r1, label, Literal("label 1", lang="en")))
    g1.add((r1, label, Literal("label 2")))

    s2 = URIRef("store:2")
    g2 = Graph(identifier=s2)
    g2.add((r2, label, Literal("label 3")))

    ds1 = Dataset()
    for s, p, o in g1.triples((None, None, None)):
        ds1.addN([(s, p, o, g1.identifier)])
    for s, p, o in g2.triples((None, None, None)):
        ds1.addN([(s, p, o, g2.identifier)])
    r3 = URIRef("resource:3")
    ds1.add((r3, label, Literal(4)))

    r = ds1.serialize(format="trix", encoding="utf-8")
    ds2 = Dataset()

    ds2.parse(BytesIO(r), format="trix")

    for q in ds2.quads((None, None, None)):
        if q[3] == ds2.default_graph.identifier:
            tg = ds1.default_graph
        elif isinstance(q[3], (BNode, URIRef, type(None))):
            tg = ds2.graph(q[3] if q[3] is not None else DATASET_DEFAULT_GRAPH_ID)
        else:
            raise Exception(f"Unrecognised identifier {q[3]}")

        assert q[0:3] in tg


def test_issue_250():
    """

    https://github.com/RDFLib/rdflib/issues/250

    When I have a ConjunctiveGraph with the default namespace set,
    for example

    import rdflib
    g = rdflib.ConjunctiveGraph()
    g.bind(None, "http://defaultnamespace")

    then the Trix serializer binds the default namespace twice in its XML
    output, once for the Trix namespace and once for the namespace I used:

    print(g.serialize(format='trix').decode('UTF-8'))

    <?xml version="1.0" encoding="utf-8"?>
    <TriX
      xmlns:xml="http://www.w3.org/XML/1998/namespace"
      xmlns="http://defaultnamespace"
      xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
      xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"
      xmlns="http://www.w3.org/2004/03/trix/trix-1/"
    />

    """

    graph = Dataset()
    graph.bind(None, "http://defaultnamespace")
    sg = graph.serialize(format="trix")
    assert 'xmlns="http://defaultnamespace"' not in sg, sg
    assert 'xmlns="http://www.w3.org/2004/03/trix/trix-1/' in sg, sg
