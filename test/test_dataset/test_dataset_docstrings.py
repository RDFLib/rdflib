import re

import pytest

from rdflib.graph import Dataset, Graph
from rdflib.term import BNode, Literal, RDFLibGenid, URIRef

n3_data = """
<http://data.yyx.me/jack> <http://onto.yyx.me/work_for> <http://data.yyx.me/company_a> .
<http://data.yyx.me/david> <http://onto.yyx.me/work_for> <http://data.yyx.me/company_b> .
"""

trig_data = """
# This document contains a default graph and two named graphs.

@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix dc: <http://purl.org/dc/terms/> .
@prefix foaf: <http://xmlns.com/foaf/0.1/> .

# default graph
    {
      <http://example.org/bob> dc:publisher "Bob" .
      <http://example.org/alice> dc:publisher "Alice" .
    }

<http://example.org/bob>
    {
       _:a foaf:name "Bob" .
       _:a foaf:mbox <mailto:bob@oldcorp.example.org> .
       _:a foaf:knows _:b .
    }

<http://example.org/alice>
    {
       _:b foaf:name "Alice" .
       _:b foaf:mbox <mailto:alice@work.example.org> .
    }
"""


def test_docstrings():
    # Examples of usage:

    # Create a new Dataset
    ds = Dataset()
    assert re.match(
        r"<Graph identifier=urn:x-rdflib:default \(<class 'rdflib\.graph\.Dataset'>\)>",
        str(repr(ds)),
    )
    assert (
        str(ds)
        == "[a rdflib:Dataset;rdflib:storage [a rdflib:Store;rdfs:label 'Memory']]"
    )

    assert len(ds) == 0
    assert len(ds.default_graph) == 0
    assert (
        str(repr(ds.default_graph))
        == "<Graph identifier=urn:x-rdflib:default (<class 'rdflib.graph.Graph'>)>"
    )
    assert (
        str(ds.default_graph)
        == "<urn:x-rdflib:default> a rdfg:Graph;rdflib:storage [a rdflib:Store;rdfs:label 'Memory']."
    )

    assert len(list(ds.contexts())) == 0
    assert list(ds.contexts()) == []

    # simple triples goes to default graph

    r = ds.add(
        (
            URIRef("http://example.org/a"),
            URIRef("http://www.example.org/b"),
            Literal("foo"),
        )
    )  # doctest: +ELLIPSIS
    """<Graph identifier=... (<class 'rdflib.graph.Dataset'>)>"""

    assert r == ds

    # "simple triples goes to default graph"
    # CORRECT
    assert len(ds) == 1
    assert len(list(ds.contexts())) == 0
    assert list(ds.contexts()) == []

    assert len(ds.default_graph) == 1

    # Create a graph in the dataset, if the graph name has already been
    # used, the corresponding graph will be returned
    # (ie, the Dataset keeps track of the constituent graphs)

    g = ds.graph(URIRef("http://www.example.com/gr"))

    assert len(g) == 0
    assert (
        str(repr(g))
        == "<Graph identifier=http://www.example.com/gr (<class 'rdflib.graph.Graph'>)>"
    )
    assert (
        str(g)
        == "<http://www.example.com/gr> a rdfg:Graph;rdflib:storage [a rdflib:Store;rdfs:label 'Memory']."
    )

    # "Create a graph in the dataset"
    # CORRECT
    assert len(list(ds.contexts())) == 1
    assert (
        str(list(ds.graphs()))
        == "[<Graph identifier=http://www.example.com/gr (<class 'rdflib.graph.Graph'>)>]"
    )
    assert list(ds.contexts()) == [URIRef('http://www.example.com/gr')]

    # add triples to the new graph as usual
    g.add(
        (URIRef("http://example.org/x"), URIRef("http://example.org/y"), Literal("bar"))
    )  # doctest: +ELLIPSIS
    """<Graph identifier=... (<class 'rdflib.graph.Graph'>)>"""

    # "add triples to the new graph as usual"
    # CORRECT
    assert len(g) == 1
    assert len(ds) == 1

    # alternatively: add a quad to the dataset -> goes to the graph
    ds.add(
        (
            URIRef("http://example.org/x"),
            URIRef("http://example.org/z"),
            Literal("foo-bar"),
            g.identifier,
        )
    )

    # "alternatively: add a quad to the dataset -> goes to the graph"
    # CORRECT
    assert len(g) == 2
    assert len(ds) == 1

    # querying triples return them all regardless of the graph
    for t in ds.triples((None, None, None)):  # doctest: +SKIP
        print(t)  # doctest: +NORMALIZE_WHITESPACE

    """
    (rdflib.term.URIRef("http://example.org/a"),
     rdflib.term.URIRef("http://www.example.org/b"),
     rdflib.term.Literal("foo"))
    (rdflib.term.URIRef("http://example.org/x"),
     rdflib.term.URIRef("http://example.org/z"),
     rdflib.term.Literal("foo-bar"))
    (rdflib.term.URIRef("http://example.org/x"),
     rdflib.term.URIRef("http://example.org/y"),
     rdflib.term.Literal("bar"))
    """

    # "querying triples return them all regardless of the graph"
    # INCORRECT, generator only yields triples in the default graph

    assert len(list(ds.triples((None, None, None)))) == 1
    assert (
        URIRef("http://example.org/a"),
        URIRef("http://www.example.org/b"),
        Literal("foo"),
    ) in list(ds.triples((None, None, None)))

    # querying quads() return quads; the fourth argument can be unrestricted
    # (None) or restricted to a graph
    for q in ds.quads((None, None, None, None)):  # doctest: +SKIP
        print(q)  # doctest: +NORMALIZE_WHITESPACE

    """
    (rdflib.term.URIRef("http://example.org/a"),
     rdflib.term.URIRef("http://www.example.org/b"),
     rdflib.term.Literal("foo"),
     None)
    (rdflib.term.URIRef("http://example.org/x"),
     rdflib.term.URIRef("http://example.org/y"),
     rdflib.term.Literal("bar"),
     rdflib.term.URIRef("http://www.example.com/gr"))
    (rdflib.term.URIRef("http://example.org/x"),
     rdflib.term.URIRef("http://example.org/z"),
     rdflib.term.Literal("foo-bar"),
     rdflib.term.URIRef("http://www.example.com/gr"))
    """

    # "querying quads() return quads; the fourth argument can be unrestricted"
    # CORRECT
    assert len(list(ds.quads((None, None, None, None)))) == 3

    assert (
        str(sorted(list(ds.quads((None, None, None, None))))[0])
        == "(rdflib.term.URIRef('http://example.org/a'), "
        + "rdflib.term.URIRef('http://www.example.org/b'), "
        + "rdflib.term.Literal('foo'), "
        + "None)"
    )

    # unrestricted looping is equivalent to iterating over the entire Dataset
    for q in ds:  # doctest: +SKIP
        print(q)  # doctest: +NORMALIZE_WHITESPACE
    """
    (rdflib.term.URIRef("http://example.org/a"),
     rdflib.term.URIRef("http://www.example.org/b"),
     rdflib.term.Literal("foo"),
     None)
    (rdflib.term.URIRef("http://example.org/x"),
     rdflib.term.URIRef("http://example.org/y"),
     rdflib.term.Literal("bar"),
     rdflib.term.URIRef("http://www.example.com/gr"))
    (rdflib.term.URIRef("http://example.org/x"),
     rdflib.term.URIRef("http://example.org/z"),
     rdflib.term.Literal("foo-bar"),
     rdflib.term.URIRef("http://www.example.com/gr"))
    """

    # "unrestricted looping is equivalent to iterating over the entire Dataset"
    # CORRECT
    assert len([q for q in ds]) == len(list(ds.quads()))
    assert len(ds) == 1

    # restricting iteration to a graph:
    for q in ds.quads((None, None, None, g.identifier)):  # doctest: +SKIP
        print(q)  # doctest: +NORMALIZE_WHITESPACE
    """
    (rdflib.term.URIRef("http://example.org/x"),
     rdflib.term.URIRef("http://example.org/y"),
     rdflib.term.Literal("bar"),
     rdflib.term.URIRef("http://www.example.com/gr"))
    (rdflib.term.URIRef("http://example.org/x"),
     rdflib.term.URIRef("http://example.org/z"),
     rdflib.term.Literal("foo-bar"),
     rdflib.term.URIRef("http://www.example.com/gr"))
    """

    # "restricting iteration to a graph:"
    # CORRECT
    assert len(list(ds.quads((None, None, None, g.identifier)))) == 2

    # Note that in the call above -
    # ds.quads((None,None,None,"http://www.example.com/gr"))
    # would have been accepted, too

    # CORRECT
    assert (
        len(list(ds.quads((None, None, None, URIRef("http://www.example.com/gr")))))
        == 2
    )

    # graph names in the dataset can be queried:
    for c in ds.graphs():  # doctest: +SKIP
        print(c)  # doctest:
    """
    DEFAULT
    http://www.example.com/gr
    """

    # "graph names in the dataset can be queried:"
    # CORRECT except that Graph objects are yielded
    assert (
        str(sorted(list(ds.graphs())))
        == "[<Graph identifier=http://www.example.com/gr (<class 'rdflib.graph.Graph'>)>]"
    )

    assert sorted(list(ds.contexts())) == [URIRef('http://www.example.com/gr')]
    # A graph can be created without specifying a name; a skolemized genid
    # is created on the fly
    h = ds.graph()

    for c in ds.graphs():  # doctest: +SKIP
        print(c)  # doctest: +NORMALIZE_WHITESPACE +ELLIPSIS
    """
    DEFAULT
    http://rdlib.net/.well-known/genid/rdflib/N...
    http://www.example.com/gr
    """

    # "A graph can be created without specifying a name; a skolemized genid"
    # CORRECT

    assert re.match(
        r"\[RDFLibGenid\('http://rdlib\.net/\.well-known/genid/rdflib/N(.*?)'\), rdflib\.term\.URIRef\('http://www\.example\.com/gr'\)\]",
        str(sorted(list(ds.contexts()))),
    )

    # Note that the Dataset.graphs() call returns names of empty graphs,
    # too. This can be restricted:

    for c in ds.graphs(empty=False):  # doctest: +SKIP
        print(c)  # doctest: +NORMALIZE_WHITESPACE

    """
    DEFAULT
    http://www.example.com/gr
    """
    # a graph can also be removed from a dataset via ds.remove_graph(g)

    assert len(list(ds.graphs())) == 2

    r = ds.remove_graph(h)

    # "a graph can also be removed from a dataset via ds.remove_graph(g)"
    # CORRECT
    assert len(list(ds.graphs())) == 1

    # OMITTED

    # DESIRED unless otherwise-specified, triples should be parsed into the default graph

    assert len(ds) == 1
    assert len(list(ds.contexts())) == 1
    assert len(ds.default_graph) == 1

    ds.parse(data=n3_data, format="n3")

    # ACTUAL they're parsed into a new BNode-identified graph

    assert len(ds.default_graph) == 3

    assert len(ds) == 3

    assert len(list(ds.graphs())) == 1

    assert list(ds.contexts()) == [URIRef('http://www.example.com/gr')]

    # DESIRED RDF serializations of quads are parsed into the defined graphs

    assert len(ds) == 3
    assert len(list(ds.contexts())) == 1
    assert len(ds.default_graph) == 3

    ds.parse(data=trig_data, format="trig")

    # ACTUAL Failed to parse triples into default graph
    assert len(ds.default_graph) == 5

    assert len(ds) == 5

    assert len(list(ds.contexts())) == 3

    assert sorted(list(ds.contexts())) == [
        URIRef('http://example.org/alice'),
        URIRef('http://example.org/bob'),
        URIRef('http://www.example.com/gr'),
    ]

    bobgraph = ds.graph(URIRef("http://example.org/bob"))
    assert len(bobgraph) == 3

    # DESIRED serializatio preserves BNodes
    # ACTUAL serialization fails to preserve BNodes

    assert (
        bobgraph.serialize(format="n3")
        == """@prefix foaf: <http://xmlns.com/foaf/0.1/> .

[] foaf:knows [ ] ;
    foaf:mbox <mailto:bob@oldcorp.example.org> ;
    foaf:name "Bob" .

"""
    )

    # ditto with trig serializer:

    """
     @prefix dcterms: <http://purl.org/dc/terms/> .
     @prefix foaf: <http://xmlns.com/foaf/0.1/> .
     @prefix ns1: <http://example.org/> .
     @prefix ns2: <http://www.example.com/> .
     @prefix ns3: <urn:x-rdflib:> .
     @prefix ns4: <http://www.example.org/> .
     @prefix ns5: <http://onto.yyx.me/> .
     
     _:N2d8d1777d6034aa38f32d0b73f1ba0b2 {
         ns1:alice dcterms:publisher "Alice" .
     
         ns1:bob dcterms:publisher "Bob" .
     }
     
     ns1:alice {
         [] foaf:mbox <mailto:alice@work.example.org> ;
             foaf:name "Alice" .
     }
     
     ns2:gr {
         ns1:x ns1:y "bar" ;
             ns1:z "foo-bar" .
     }
     
     {
         ns1:a ns4:b "foo" .
     }
     
     _:N8dac373f5b584d3fb82c09dc9ae87180 {
         <http://data.yyx.me/david> ns5:work_for <http://data.yyx.me/company_b> .
     
         <http://data.yyx.me/jack> ns5:work_for <http://data.yyx.me/company_a> .
     }
     
     ns1:bob {
         [] foaf:knows [ ] ;
             foaf:mbox <mailto:bob@oldcorp.example.org> ;
             foaf:name "Bob" .
     }

    """
