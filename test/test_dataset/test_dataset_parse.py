import os
from pathlib import Path
from test.data import *

import pytest

from rdflib import BNode, Dataset, Graph, URIRef, logger
from rdflib.graph import DATASET_DEFAULT_GRAPH_ID

s1 = (
    URIRef("http://data.yyx.me/jack"),
    URIRef("http://onto.yyx.me/work_for"),
    URIRef("http://data.yyx.me/company_a"),
)
s2 = (
    URIRef("http://data.yyx.me/david"),
    URIRef("http://onto.yyx.me/work_for"),
    URIRef("http://data.yyx.me/company_b"),
)

n3data = """
<http://data.yyx.me/jack> <http://onto.yyx.me/work_for> <http://data.yyx.me/company_a> .
<http://data.yyx.me/david> <http://onto.yyx.me/work_for> <http://data.yyx.me/company_b> .
"""

testdata01_trig = os.path.join(CONSISTENT_DATA_DIR, "testdata01.trig")

sportquadsnq = open(os.path.join(CONSISTENT_DATA_DIR, "sportquads.nq")).read()


def test_parse_graph_into_dataset__n3():
    dataset = Dataset()

    dataset.parse(data=n3data, format="n3")

    assert len(list(dataset.graphs())) == 0
    assert len(dataset) == 2


def test_parse_graph_into_dataset_default_graph_n3():
    dataset = Dataset()

    graph = dataset.default_graph

    graph.parse(data=n3data, format="n3")

    assert len(list(dataset.graphs())) == 0
    assert len(dataset) == 2


def test_parse_graph_into_dataset_default_graph_as_publicID_n3():

    dataset = Dataset()

    dataset.add((tarek, hates, cheese))
    assert len(dataset) == 1
    assert len(list(dataset.graphs())) == 0

    dataset.parse(data=n3data, format="n3", publicID=DATASET_DEFAULT_GRAPH_ID)

    assert len(list(dataset.graphs())) == 0

    assert len(dataset) == 3


def test_parse_graph_as_new_dataset_subgraph_n3():

    dataset = Dataset()

    dataset.add((tarek, hates, cheese))
    assert len(dataset) == 1

    data = """
    <http://data.yyx.me/jack> <http://onto.yyx.me/work_for> <http://data.yyx.me/company_a> .
    <http://data.yyx.me/david> <http://onto.yyx.me/work_for> <http://data.yyx.me/company_b> .
    """

    subgraph_identifier = URIRef("urn:x-rdflib:subgraph1")

    g = dataset.graph(subgraph_identifier)

    g.parse(data=data, format="n3")

    assert len(g) == 2

    subgraph = dataset.graph(subgraph_identifier)

    assert type(subgraph) is Graph

    assert len(subgraph) == 2


def test_parse_graph_as_new_dataset_subgraph_nquads():

    dataset = Dataset()

    dataset.add((tarek, hates, cheese))

    assert len(list(dataset.graphs((tarek, None, None)))) == 0

    assert len(dataset) == 1

    dataset.parse(
        data="<urn:example:tarek> <urn:example:likes> <urn:example:pizza> <urn:example:context-a> .",
        format="nquads",
    )

    assert len(list(dataset.graphs())) == 1

    assert len(list(dataset.graphs((tarek, None, None)))) == 1

    # Confirm that the newly-created subgraph (the publicID in the above turtle) exists
    assert URIRef("urn:example:context-a") in list(dataset.contexts())

    # Confirm that the newly-created subgraph contains a triple
    assert len(dataset.graph(URIRef("urn:example:context-a"))) == 1

    # Bind the newly-created subgraph to a variable
    g = dataset.graph(URIRef("urn:example:context-a"))

    # Confirm that the newly-created subgraph contains the parsed triple
    assert (tarek, likes, pizza) in g


def test_parse_graph_as_new_dataset_subgraph_trig():
    dataset = Dataset()

    dataset.add((tarek, hates, cheese))

    # Trig default
    dataset.parse(
        Path("./test/consistent_test_data/testdata01.trig").absolute().as_uri()
    )

    assert len(list(dataset.graphs())) == 3

    for g in dataset.graphs():
        logger.debug(f"{g}:\n{g.serialize(format='nt')}")


def test_parse_graph_with_publicid_as_new_dataset_subgraph():
    dataset = Dataset()

    dataset.add((tarek, hates, cheese))

    dataset.parse(
        data="<urn:example:tarek> <urn:example:likes> <urn:example:pizza> .",
        publicID="urn:x-rdflib:context-a",
        format="ttl",
    )
    assert len(list(dataset.graphs())) == 1

    # Confirm that the newly-created subgraph (the publicID in the above turtle) exists
    assert URIRef("urn:x-rdflib:context-a") in list(dataset.contexts())

    # Confirm that the newly-created subgraph contains a triple
    assert len(dataset.graph(URIRef("urn:x-rdflib:context-a"))) == 1

    # Bind the newly-created subgraph to a variable
    g = dataset.graph(URIRef("urn:x-rdflib:context-a"))

    # Confirm that the newly-created subgraph contains the parsed triple
    assert (tarek, likes, pizza) in g
