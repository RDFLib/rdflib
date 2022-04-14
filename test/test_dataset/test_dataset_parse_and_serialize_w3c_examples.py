import os
from test.data import CONSISTENT_DATA_DIR, alice_uri, bob_uri

import pytest

import rdflib
from rdflib import logger
from rdflib.compare import (
    graph_diff,
    isomorphic,
    similar,
    to_canonical_graph,
    to_isomorphic,
)
from rdflib.graph import DATASET_DEFAULT_GRAPH_ID, Dataset, Graph
from rdflib.namespace import DC, DCTERMS, FOAF, RDF, SKOS, XSD, Namespace
from rdflib.term import BNode, Literal, URIRef

example2_root = os.path.join(
    CONSISTENT_DATA_DIR, "example-2-default-and-two-named-graphs."
)
example3_root = os.path.join(CONSISTENT_DATA_DIR, "example-3-three-named-graphs.")
example4_root = os.path.join(
    CONSISTENT_DATA_DIR, "example-4-default-plus-two-named-graphs-and-one-bnode."
)


@pytest.fixture
def example2(request):
    d = Dataset()
    d.bind("ex", Namespace("http://example.org/"))

    alice = BNode()  # Alice
    bob = BNode()  # Bob

    alice_graph = d.graph(alice_uri)
    bob_graph = d.graph(bob_uri)

    d.add((alice_uri, DCTERMS.publisher, Literal("Alice")))
    d.add((bob_uri, DCTERMS.publisher, Literal("Bob")))

    alice_graph.add((alice, FOAF.mbox, URIRef("mailto:alice@work.example.org")))
    alice_graph.add((alice, FOAF.name, Literal("Alice")))

    bob_graph.add((bob, FOAF.name, Literal("Bob")))
    bob_graph.add((bob, FOAF.mbox, URIRef("mailto:bob@oldcorp.example.org")))
    bob_graph.add((bob, FOAF.knows, alice))

    yield d, alice_graph, bob_graph


@pytest.fixture
def example3(request):
    d = Dataset()

    EX = Namespace("http://www.example.org/vocabulary#")
    EXDOC = Namespace("http://www.example.org/exampleDocument#")
    SWP = Namespace("http://www.w3.org/2004/03/trix/swp-1/")
    d.bind("ex", EX)
    d.bind("", EXDOC)
    d.bind("swp", SWP)

    G1 = d.graph(EXDOC.G1)
    G2 = d.graph(EXDOC.G2)
    G3 = d.graph(EXDOC.G3)

    monica = EXDOC.Monica
    G1.add((monica, EX.name, Literal("Monica Murphy")))
    G1.add((monica, EX.homepage, URIRef("http://www.monicamurphy.org")))
    G1.add((monica, EX.email, URIRef("mailto:monica@monicamurphy.org")))
    G1.add((monica, EX.hasSkill, EX.management))

    G2.add((monica, RDF.type, EX.Person))
    G2.add((monica, EX.hasSkill, EX.Programming))

    w1 = BNode()
    w2 = BNode()

    G3.add((EXDOC.G1, SWP.assertedBy, w1))
    G3.add((w1, SWP.authority, EXDOC.Chris))
    G3.add((w1, DC.date, Literal("2003-10-02", datatype=XSD.date)))

    G3.add((EXDOC.G2, SWP.quotedBy, w2))
    G3.add((EXDOC.G3, SWP.assertedBy, w2))
    G3.add((w2, DC.date, Literal("2003-09-03", datatype=XSD.date)))
    G3.add((w2, SWP.authority, EXDOC.Chris))
    G3.add((EXDOC.Chris, RDF.type, EX.Person))
    G3.add((EXDOC.Chris, EX.email, URIRef("mailto:chris@bizer.de")))

    yield d


@pytest.fixture
def example4(request):

    d = Dataset()
    d.bind("ex", Namespace("http://example.org/"))
    d.bind("genid", Namespace("http://rdlib.net/.well-known/genid/rdflib/"))

    alice = BNode()  # Alice
    bob = BNode()  # Bob
    harry = BNode()  # Harry

    alice_graph = d.graph(alice_uri)
    bob_graph = d.graph(bob_uri)
    harry_graph = d.graph(harry)

    d.add((alice_uri, DCTERMS.publisher, Literal("Alice")))
    d.add((bob_uri, DCTERMS.publisher, Literal("Bob")))
    d.add((harry_graph.identifier, DCTERMS.publisher, Literal("Harry")))

    alice_graph.add((alice, FOAF.mbox, URIRef("mailto:alice@work.example.org")))
    alice_graph.add((alice, FOAF.name, Literal("Alice")))

    bob_graph.add((bob, FOAF.name, Literal("Bob")))
    bob_graph.add((bob, FOAF.mbox, URIRef("mailto:bob@oldcorp.example.org")))
    bob_graph.add((bob, FOAF.knows, alice))

    harry_graph.add((harry, FOAF.name, Literal("Harry")))
    harry_graph.add((harry, FOAF.mbox, URIRef("mailto:harry@work.example.org")))

    yield d, alice_graph, bob_graph, harry_graph


@pytest.fixture
def xfail_selected_triples_serialization_formats(request):
    fmt = request.getfixturevalue("fmt")

    expected_failures = [
        # "n3",
        # "turtle",
        # "xml",
        "nt",
    ]

    if fmt in expected_failures:
        request.node.add_marker(
            pytest.mark.xfail(reason=f"Expected failure with {fmt}")
        )


triples_formats = ["n3", "turtle", "xml", "nt"]


@pytest.mark.parametrize("fmt", triples_formats)
@pytest.mark.usefixtures("xfail_selected_triples_serialization_formats")
def test_default_graph_parse_and_serialize_triples_example2(fmt, example2):
    d, _, _ = example2

    g = Graph().parse(data=d.serialize(format=fmt), format=fmt)

    gser = g.serialize(format=fmt)
    dser = d.default_graph.serialize(format=fmt)

    assert isomorphic(g, d.default_graph), [gser, dser]


@pytest.mark.parametrize("fmt", triples_formats)
@pytest.mark.usefixtures("xfail_selected_triples_serialization_formats")
def test_default_graph_parse_and_serialize_triples_example3(fmt, example3):
    d = example3

    g = Graph().parse(data=d.serialize(format=fmt), format=fmt)

    assert isomorphic(g, d.default_graph)


@pytest.mark.parametrize("fmt", triples_formats)
@pytest.mark.usefixtures("xfail_selected_triples_serialization_formats")
def test_default_graph_parse_and_serialize_triples_example4(fmt, example4):
    d, _, _, _ = example4

    g = Graph().parse(data=d.serialize(format=fmt), format=fmt)

    assert isomorphic(g, d.default_graph)


quad_formats = ["json-ld", "trix", "nquads", "trig", "hext"]


@pytest.fixture
def xfail_selected_quads_serialization_formats_example2(request):
    fmt = request.getfixturevalue("fmt")

    expected_failures = [
        # "json-ld",
        # "trix",
        # "nquads",
        # "trig",
        # "hext"
    ]

    if fmt in expected_failures:
        request.node.add_marker(
            pytest.mark.xfail(reason=f"Expected failure with {fmt}")
        )


@pytest.mark.parametrize("fmt", quad_formats)
@pytest.mark.usefixtures("xfail_selected_quads_serialization_formats_example2")
def test_parse_and_serialize_contexts_example2(fmt, example2):
    d1, alice_graph, bob_graph = example2

    d2 = Dataset().parse(data=d1.serialize(format=fmt), format=fmt)

    assert len(list(d2.contexts())) == 2
    assert len(list(d2.graphs())) == 2
    assert len(d2) == 2

    assert alice_uri in d2.contexts()
    assert bob_uri in d2.contexts()

    assert len(list(d1.quads((None, None, None, None)))) == len(
        list(d2.quads((None, None, None, None)))
    )

    assert len(d1.store) == len(d2.store)

    d1sk = d1.skolemize()
    d2sk = d2.skolemize()

    if fmt == "hext":
        with pytest.raises(AssertionError):
            assert isomorphic(d1sk, d2sk)
    else:
        assert isomorphic(d1sk, d2sk)


@pytest.fixture
def xfail_selected_quads_serialization_formats_example3(request):
    fmt = request.getfixturevalue("fmt")

    expected_failures = [
        # "json-ld",
        # "trix",
        # "nquads",
        # "trig",
        # "hext"
    ]

    if fmt in expected_failures:
        request.node.add_marker(
            pytest.mark.xfail(reason=f"Expected failure with {fmt}")
        )


@pytest.mark.parametrize("fmt", quad_formats)
@pytest.mark.usefixtures("xfail_selected_quads_serialization_formats_example3")
def test_parse_and_serialize_contexts_example3(fmt, example3):
    d1 = example3

    d2 = Dataset().parse(data=d1.serialize(format=fmt), format=fmt)

    assert len(list(d2.contexts())) == 3
    assert len(list(d2.graphs())) == 3
    assert len(d2) == 0

    assert len(list(d1.quads((None, None, None, None)))) == len(
        list(d2.quads((None, None, None, None)))
    )

    assert len(d1.store) == len(d2.store)

    d1sk = d1.skolemize()
    d2sk = d2.skolemize()

    assert isomorphic(d1sk, d2sk)


@pytest.fixture
def xfail_selected_quads_serialization_formats_example4(request):
    fmt = request.getfixturevalue("fmt")

    expected_failures = [
        # "json-ld",
        # "trix",
        "nquads",
        "trig",
        # "hext"
    ]

    if fmt in expected_failures:
        request.node.add_marker(
            pytest.mark.xfail(reason=f"Expected failure with {fmt}")
        )


@pytest.mark.parametrize(
    "fmt",
    [
        "json-ld",
        "nquads",
        "trig",
        "hext",
        "trix",
    ],
)
@pytest.mark.usefixtures("xfail_selected_quads_serialization_formats_example4")
def test_parse_and_serialize_contexts_example4(fmt, example4):
    d1, alice_graph, bob_graph, harry_graph = example4

    d2 = Dataset().parse(data=d1.serialize(format=fmt), format=fmt)

    assert len(list(d2.contexts())) == 3
    assert len(list(d2.graphs())) == 3
    assert len(d2) == 3

    assert alice_uri in d2.contexts()
    assert bob_uri in d2.contexts()

    assert len(list(d1.quads((None, None, None, None)))) == len(
        list(d2.quads((None, None, None, None)))
    )

    assert len(d1.store) == len(d2.store)

    d1sk = d1.skolemize()
    d2sk = d2.skolemize()

    if fmt == "hext":
        with pytest.raises(AssertionError):
            assert isomorphic(d1sk, d2sk)
    else:
        assert isomorphic(d1sk, d2sk)


def test_parse_serialize_roundtrip():
    formats = [
        "json-ld",
        "trix",
        "nquads",
        "trig",
    ]
    for example in [example2_root, example3_root, example4_root]:
        for input_format in formats:
            ds1 = Dataset()
            with open(example + input_format, 'r') as fp:
                ds1.parse(data=fp.read(), format=input_format)
            for output_format in formats:
                ds2 = Dataset()
                ds2.parse(
                    data=ds1.serialize(format=output_format), format=output_format
                )

                d1sk = ds1.skolemize()
                d2sk = ds2.skolemize()

                assert isomorphic(d1sk, d2sk)


# # For future reference:

# logger.debug(f"D1:\n{os.linesep.join(sorted(d1.serialize(format='nquads').split(os.linesep)))}")
# logger.debug(f"D2:\n{os.linesep.join(sorted(d2.serialize(format='nquads').split(os.linesep)))}")
