import pytest
import os

import rdflib
from rdflib import logger
from rdflib.term import BNode, Literal, URIRef, Variable
from rdflib.graph import Graph, Dataset, DATASET_DEFAULT_GRAPH_ID
from rdflib.compare import (
    isomorphic,
    graph_diff,
    similar,
    to_isomorphic,
    to_canonical_graph,
)
from rdflib.store import VALID_STORE, NO_STORE, CORRUPTED_STORE, UNKNOWN
from test.data import (
    CONSISTENT_DATA_DIR,
    context0,
    context1,
    context2,
    alice_uri,
    bob_uri,
    tarek,
    michel,
    likes,
    pizza,
)
from test.testutils import GraphHelper

# # For future reference:

# logger.debug(f"D1:\n{os.linesep.join(sorted(d1.serialize(format='nquads').split(os.linesep)))}")
# logger.debug(f"D2:\n{os.linesep.join(sorted(d2.serialize(format='nquads').split(os.linesep)))}")

# Progammatic construction


def test_with_matching_default_graphs():

    t1 = (tarek, likes, pizza)
    t2 = (michel, likes, pizza)

    ds1 = Dataset()
    ds1.bind("", URIRef("urn:example:"))
    ds1.add(t1)
    ds1.add(t2)

    ds2 = Dataset()
    ds2.bind("", URIRef("urn:example:"))
    ds2.add(t1)
    ds2.add(t2)

    assert len([t for t in ds1.quads((None, None, None, None))]) == 2
    assert len([t for t in ds2.quads((None, None, None, None))]) == 2

    assert isomorphic(ds1, ds2)


def test_negative_with_different_default_graphs():

    t1 = (tarek, likes, pizza)
    t2 = (michel, likes, pizza)

    ds1 = Dataset()
    ds1.bind("", URIRef("urn:example:"))
    ds1.add(t1)
    ds1.add(t2)

    ds2 = Dataset()
    ds2.bind("", URIRef("urn:example:"))
    ds2.add(t1)  # not tt2

    assert len([t for t in ds1.quads((None, None, None, None))]) == 2
    assert len([t for t in ds2.quads((None, None, None, None))]) == 1

    assert not isomorphic(ds1, ds2)


def test_matching_graphs_and_context_identifiers():

    t1 = (tarek, likes, pizza)
    t2 = (michel, likes, pizza)

    ds1 = Dataset()
    ds1.bind("", URIRef("urn:example:"))

    ds1g1 = ds1.graph(context1)
    ds1g1.add(t1)
    ds1g1.add(t2)

    ds1g2 = ds1.graph(context2)
    ds1g2.add(t1)
    ds1g2.add(t2)

    ds2 = Dataset()
    ds2.bind("", URIRef("urn:example:"))

    ds2g1 = ds2.graph(context1)
    ds2g1.add(t1)
    ds2g1.add(t2)

    ds2g2 = ds2.graph(context2)
    ds2g2.add(t1)
    ds2g2.add(t2)

    assert len([t for t in ds1.quads((None, None, None, None))]) == 4
    assert len([t for t in ds2.quads((None, None, None, None))]) == 4

    assert isomorphic(ds1, ds2)


def test_negative_with_mismatching_graphs_and_matching_context_identifiers():

    t1 = (tarek, likes, pizza)
    t2 = (michel, likes, pizza)

    ds1 = Dataset()
    ds1.bind("", URIRef("urn:example:"))

    ds1g1 = ds1.graph(context1)
    ds1g1.add(t1)
    ds1g1.add(t2)

    ds1g2 = ds1.graph(context2)
    ds1g2.add(t1)
    ds1g2.add(t2)

    ds2 = Dataset()
    ds2.bind("", URIRef("urn:example:"))

    ds2g1 = ds2.graph(context1)
    ds2g1.add(t1)
    ds2g1.add(t2)

    ds2g2 = ds2.graph(context2)
    ds2g2.add(t1)  # But not michel

    assert len([t for t in ds1.quads((None, None, None, None))]) == 4
    assert len([t for t in ds2.quads((None, None, None, None))]) == 3

    assert not isomorphic(ds1, ds2)


@pytest.mark.xfail(
    reason="Datasets with isomorphic graphs but different context identifers are improperly isomorphic"
)
def test_negative_with_matching_graphs_and_mismatched_context_identifiers():

    t1 = (tarek, likes, pizza)
    t2 = (michel, likes, pizza)

    ds1 = Dataset()
    ds1.bind("", URIRef("urn:example:"))

    ds1g1 = ds1.graph(context1)
    ds1g1.add(t1)
    ds1g1.add(t2)

    ds1g2 = ds1.graph(context2)
    ds1g2.add(t1)
    ds1g2.add(t2)

    ds2 = Dataset()
    ds2.bind("", URIRef("urn:example:"))

    # Different context identifiers - what *are* the semantics of dataset isomorphism here?
    ds2g1 = ds2.graph(context0)
    ds2g1.add(t1)
    ds2g1.add(t2)

    ds2g2 = ds2.graph(context1)
    ds2g2.add(t1)
    ds2g2.add(t2)

    assert len([t for t in ds1.quads((None, None, None, None))]) == 4
    assert len([t for t in ds2.quads((None, None, None, None))]) == 4

    assert isomorphic(ds1, ds2)


iso1 = os.path.join(
    CONSISTENT_DATA_DIR,
    "isomorphic",
    "example-2-default-and-two-bnode-graphs.trig",
)

iso2 = os.path.join(
    CONSISTENT_DATA_DIR,
    "isomorphic",
    "example-2-default-and-two-bnode-graphs-reordered.trig",
)

iso3 = os.path.join(
    CONSISTENT_DATA_DIR,
    "isomorphic",
    "example-2-default-and-two-named-graphs-base.trig",
)

iso4 = os.path.join(
    CONSISTENT_DATA_DIR,
    "isomorphic",
    "example-2-default-and-two-named-graphs-harry-added-to-default.trig",
)

iso5 = os.path.join(
    CONSISTENT_DATA_DIR,
    "isomorphic",
    "example-2-default-and-two-named-graphs-harry-added-to-default-and-harry-graph.trig",
)

iso6 = os.path.join(
    CONSISTENT_DATA_DIR,
    "isomorphic",
    "example-2-default-and-two-named-graphs-harry-added-to-default-and-alice-bnode-graph.trig",
)

iso7 = os.path.join(
    CONSISTENT_DATA_DIR,
    "isomorphic",
    "example-2-default-and-two-named-graphs-harry-added-to-default-and-harry-bnode-graph.trig",
)


@pytest.mark.xfail(
    reason="Inconsistent fail/pass with reordered isomorphic trig graphs"
)
def test_assert_reordered_graph_is_isomorphic():
    ds1 = Dataset().parse(data=open(iso1, "r").read(), format="trig")
    ds2 = Dataset().parse(data=open(iso2, "r").read(), format="trig")

    GraphHelper.assert_isomorphic(ds1, ds2)


def test_assert_reordered_graph_is_isomorphic_after_to_isomorphic():
    ds1 = Dataset().parse(data=open(iso1, "r").read(), format="trig")
    ds2 = Dataset().parse(data=open(iso2, "r").read(), format="trig")

    ids1 = to_isomorphic(ds1)
    ids2 = to_isomorphic(ds2)

    GraphHelper.assert_isomorphic(ids1, ids2)

    # logger.debug(f"IDS1 {ids1.serialize(format='trig')}")

    # assert ids1 == ids2

    # in_both, in_first, in_second = dataset_diff(ids1, ids2)

    # assert isinstance(in_both, Dataset)

    # assert in_both.serialize(format='trig') == "\n"

    # assert len(list(in_first.quads((None, None, None, None)))) == 7

    # assert len(list(in_second.quads((None, None, None, None)))) == 7

    # ds3 = Dataset().parse(data=open(iso3, "r").read(), format="trig")
    # assert isomorphic(ds1, ds3)

    # ds4 = Dataset().parse(data=open(iso4, "r").read(), format="trig")
    # assert isomorphic(ds1, ds4)
