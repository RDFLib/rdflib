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

example4_root = os.path.join(
    CONSISTENT_DATA_DIR, "example-4-default-plus-two-named-graphs-and-one-bnode."
)


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


context_formats = [
    "json-ld",
    "trix",
    "nquads",
    "trig",
    "hext",
]


@pytest.fixture
def xfail_selected_context_parse_data_formats(request):
    fmt = request.getfixturevalue("fmt")

    expected_failures = [
        "json-ld",
        "trix",
        "nquads",
        "trig",
        "hext",
    ]

    if fmt in expected_failures:
        request.node.add_marker(
            pytest.mark.xfail(reason=f"Expected failure with {fmt}")
        )


@pytest.mark.parametrize("fmt", context_formats)
@pytest.mark.usefixtures("xfail_selected_context_parse_data_formats")
def test_parse_example4_from_data(fmt, example4):
    d1, alice_graph, bob_graph, harry_graph = example4

    d2 = Dataset()
    with open(example4_root + fmt, "r") as fp:
        d2.parse(data=fp.read(), format=fmt)

    assert len(list(d2.contexts())) == 3
    assert len(list(d2.graphs())) == 3
    assert len(d2) == 3

    contexts = sorted(list(d2.contexts()))

    assert alice_uri in contexts
    assert bob_uri in contexts
    if fmt == "trig":
        assert isinstance(contexts[0], BNode)
    else:
        assert (
            contexts[-1].n3().startswith("<http://rdlib.net/.well-known/genid/rdflib/N")
        )

    assert len(list(d1.quads((None, None, None, None)))) == len(
        list(d2.quads((None, None, None, None)))
    )

    assert len(d1.store) == len(d2.store)

    # assert isomorphic(d1.graph(alice_uri), d2.graph(alice_uri))
    # assert isomorphic(d1.graph(bob_uri), d2.graph(bob_uri))

    d1harry = sorted(list(d1.contexts()))[0]

    if fmt == "trig":
        d2harry = sorted(list(d2.contexts()))[0]
    else:
        d2harry = sorted(list(d2.contexts()))[-1]

    # assert isomorphic(d1.graph(d1harry), d2.graph(d2harry))

    assert isomorphic(d1, d2)


@pytest.fixture
def xfail_selected_context_parse_file_formats(request):
    fmt = request.getfixturevalue("fmt")

    expected_failures = [
        "json-ld",
        "trix",
        "nquads",
        "trig",
        "hext",
    ]

    if fmt in expected_failures:
        request.node.add_marker(
            pytest.mark.xfail(reason=f"Expected failure with {fmt}")
        )


@pytest.mark.parametrize("fmt", context_formats)
@pytest.mark.usefixtures("xfail_selected_context_parse_file_formats")
def test_parse_example4_from_file(fmt, example4):
    d1, alice_graph, bob_graph, harry_graph = example4

    d2 = Dataset()

    with open(example4_root + fmt, "r") as fp:
        d2.parse(file=fp, format=fmt)

    assert len(list(d2.contexts())) == 3
    assert len(list(d2.graphs())) == 3
    assert len(d2) == 3

    contexts = sorted(list(d2.contexts()))

    assert alice_uri in contexts
    assert bob_uri in contexts
    if fmt == "trig":
        assert isinstance(contexts[0], BNode)
    else:
        assert (
            contexts[-1].n3().startswith("<http://rdlib.net/.well-known/genid/rdflib/N")
        )

    assert len(list(d1.quads((None, None, None, None)))) == len(
        list(d2.quads((None, None, None, None)))
    )

    assert len(d1.store) == len(d2.store)

    # assert isomorphic(d1.graph(alice_uri), d2.graph(alice_uri))
    # assert isomorphic(d1.graph(bob_uri), d2.graph(bob_uri))

    d1harry = sorted(list(d1.contexts()))[0]

    if fmt == "trig":
        d2harry = sorted(list(d2.contexts()))[0]
    else:
        d2harry = sorted(list(d2.contexts()))[-1]

    # assert isomorphic(d1.graph(d1harry), d2.graph(d2harry))

    assert isomorphic(d1, d2)


@pytest.fixture
def xfail_selected_context_parse_location_formats(request):
    fmt = request.getfixturevalue("fmt")

    expected_failures = [
        "json-ld",
        "trix",
        "hext",
        "trig",
        "nquads",
    ]

    if fmt in expected_failures:
        request.node.add_marker(
            pytest.mark.xfail(reason=f"Expected failure with {fmt}")
        )


@pytest.mark.parametrize("fmt", context_formats)
@pytest.mark.usefixtures("xfail_selected_context_parse_location_formats")
def test_parse_example4_from_location(fmt, example4):
    d1, alice_graph, bob_graph, harry_graph = example4

    d2 = Dataset()

    loc = example4_root + fmt
    d2.parse(location=loc, format=fmt)

    assert len(list(d2.contexts())) == 3
    assert len(list(d2.graphs())) == 3
    assert len(d2) == 3

    contexts = sorted(list(d2.contexts()))

    assert alice_uri in contexts
    assert bob_uri in contexts

    if fmt == "trig":
        assert isinstance(contexts[0], BNode)
    else:
        assert (
            contexts[-1].n3().startswith("<http://rdlib.net/.well-known/genid/rdflib/N")
        )

    assert len(list(d1.quads((None, None, None, None)))) == len(
        list(d2.quads((None, None, None, None)))
    )

    assert len(d1.store) == len(d2.store)

    # assert isomorphic(d1.graph(alice_uri), d2.graph(alice_uri))

    # assert isomorphic(d1.graph(bob_uri), d2.graph(bob_uri))

    d1harry = sorted(list(d1.contexts()))[0]

    if fmt == "trig":
        d2harry = sorted(list(d2.contexts()))[0]
    else:
        d2harry = sorted(list(d2.contexts()))[-1]

    # if fmt != "hext":
    #     assert isomorphic(d1.graph(d1harry), d2.graph(d2harry))

    assert isomorphic(d1, d2)
