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
        # "json-ld",
        # "trix",
        # "nquads",
        # "trig",
        # "hext",
    ]
    if fmt in expected_failures:
        request.node.add_marker(
            pytest.mark.xfail(reason=f"Expected failure with {fmt}")
        )


@pytest.mark.parametrize("fmt", context_formats)
@pytest.mark.usefixtures("xfail_selected_context_parse_data_formats")
def test_parse_example2_from_data(fmt, example2):
    # Use programmatically-created graphs as standard to be checked against
    d1, alice_graph, bob_graph = example2

    d2 = Dataset()
    d2.bind("ex", Namespace("http://example.org/"))
    with open(example2_root + fmt, "r") as fp:
        d2.parse(data=fp.read(), format=fmt)

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

    # d1skser = d1sk.serialize(format="nquads")
    # d2skser = d2sk.serialize(format="nquads")
    # if fmt == "hext":
    #     with pytest.raises(AssertionError):
    #         assert d1skser == d2skser
    # else:
    #     assert d1skser == d2skser

    if fmt == "hext":
        with pytest.raises(AssertionError):
            assert isomorphic(d1sk, d2sk)
    else:
        assert isomorphic(d1sk, d2sk)

    # d1contexts = sorted(list(d1.contexts())) + [DATASET_DEFAULT_GRAPH_ID]
    # d2contexts = sorted(list(d2.contexts())) + [DATASET_DEFAULT_GRAPH_ID]
    # for cid, c in enumerate(d1contexts):
    #     assert isomorphic(d1.graph(c), d2.graph(d2contexts[cid]))


@pytest.fixture
def xfail_selected_context_parse_file_formats(request):
    fmt = request.getfixturevalue("fmt")

    expected_failures = [
        # "trix",
        # "trig",
        # "nquads",
        # "json-ld",
        # "hext",
    ]

    if fmt in expected_failures:
        request.node.add_marker(
            pytest.mark.xfail(reason=f"Expected failure with {fmt}")
        )


@pytest.mark.parametrize("fmt", context_formats)
@pytest.mark.usefixtures("xfail_selected_context_parse_file_formats")
def test_parse_example2_from_file(fmt, example2):
    d1, _, _ = example2

    d2 = Dataset()
    d2.bind("ex", Namespace("http://example.org/"))
    with open(example2_root + fmt, "r") as fp:
        d2.parse(file=fp, format=fmt)

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
def xfail_selected_context_parse_location_formats(request):
    fmt = request.getfixturevalue("fmt")

    expected_failures = [
        # "trix",
        "trig",
        # "nquads",
        # "json-ld",
        # "hext",
    ]

    if fmt in expected_failures:
        request.node.add_marker(
            pytest.mark.xfail(reason=f"Expected failure with {fmt}")
        )


@pytest.mark.parametrize("fmt", context_formats)
@pytest.mark.usefixtures("xfail_selected_context_parse_location_formats")
def test_parse_example2_from_location(fmt, example2):
    d1, _, _ = example2

    d2 = Dataset()
    d2.bind("ex", Namespace("http://example.org/"))
    loc = example2_root + fmt
    d2.parse(location=loc, format=fmt)

    contexts = list(d2.contexts())

    if fmt in ["trig"]:
        assert len(list(d2.contexts())) == 3
        assert len(list(d2.graphs())) == 3
        assert len(d2) == 0
    else:
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
