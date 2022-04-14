import os
from pprint import pformat
from test.data import CONSISTENT_DATA_DIR

import pytest

from rdflib import URIRef, logger
from rdflib.graph import (
    DATASET_DEFAULT_GRAPH_ID,
    Dataset,
    Graph,
    UnSupportedDatasetOperation,
    UnSupportedGraphOperation,
)

sportquadsnq = open(os.path.join(CONSISTENT_DATA_DIR, "sportquads.nq")).read()
sportquadsextranq = open(os.path.join(CONSISTENT_DATA_DIR, "sportquadsextra.nq")).read()


sportsextras = """@prefix exgraph: <http://example.org/graph/> .
@prefix ex: <http://example.com/resource/> .
@prefix sports: <http://example.com/ontology/> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix foaf: <http://xmlns.com/foaf/0.1/> .

ex:sport_200 rdfs:label "Table Tennis" .

ex:student_30 a sports:Student ;
    foaf:name "Tom Hanks" ;
    sports:practises ex:sport_200 .

ex:student_20 a sports:Student ;
    foaf:name "Demi Moore" ;
    sports:practises ex:sport_100 .
"""


def bind_standard_namespaces(obj):
    obj.bind("rl", URIRef("urn:x-rdflib:"))
    obj.bind("sports", URIRef("http://example.com/ontology/"))
    obj.bind("ex", URIRef("http://example.com/resource/"))
    obj.bind("exgraph", URIRef("http://example.org/graph/"))


def test_operators_with_dataset_and_graph():

    dataset = Dataset()
    bind_standard_namespaces(dataset)
    dataset.parse(data=sportquadsnq, format="nquads")

    assert len(dataset) == 0

    assert len(dataset.graph(DATASET_DEFAULT_GRAPH_ID)) == 0

    graph = Graph()
    bind_standard_namespaces(graph)
    graph.parse(data=sportsextras, format="n3")

    assert len(graph) == 7

    assert (
        len(dataset + graph) == 7
    )  # adds student_30, "Tom Hanks", "Table Tennis", "practises"

    dataset1 = dataset + graph

    assert len(dataset1) == len(dataset) + len(graph)

    logger.debug(
        f"DS1:\n{pformat([(graph.identifier, len(graph)) for graph in dataset1.graphs()])}\n\n"
    )

    datasett = list(dataset.quads((None, None, None, None)))

    grapht = list(graph.triples((None, None, None)))

    assert len(datasett) == 7

    assert len(grapht) == 7

    assert len(dataset - graph) == 0

    with pytest.raises(UnSupportedDatasetOperation):
        assert len(dataset * graph) == 0

    with pytest.raises(UnSupportedDatasetOperation):
        assert len(dataset ^ graph) == 2


def test_reversed_operators_with_dataset_and_graph():

    dataset = Dataset()
    dataset.parse(data=sportquadsnq, format="nquads")

    graph = Graph()
    graph.parse(data=sportsextras, format="n3")

    with pytest.raises(UnSupportedGraphOperation):
        assert len(graph + dataset) == 3

    with pytest.raises(UnSupportedGraphOperation):
        assert len(graph - dataset) == 1

    with pytest.raises(UnSupportedGraphOperation):
        assert len(graph * dataset) == 1

    with pytest.raises(UnSupportedGraphOperation):
        assert len(graph ^ dataset) == 2


def test_operators_with_two_datasets():

    dataset1 = Dataset()
    dataset1.parse(data=sportquadsnq, format="nquads")
    assert len(dataset1) == 0
    assert len(list(dataset1.quads())) == 7

    dataset2 = Dataset()
    dataset2.parse(data=sportquadsextranq, format="nquads")
    assert len(dataset2) == 0
    assert len(list(dataset2.quads())) == 10

    dataset3 = dataset1 + dataset2
    assert len(list(dataset3.quads())) == 13

    dataset3 = dataset1 - dataset2
    assert len(list(dataset3.quads())) == 3

    dataset3 = dataset1 * dataset2
    assert len(list(dataset3.quads())) == 4

    dataset3 = dataset1 ^ dataset2
    assert len(list(dataset3.quads())) == 9


def test_operators_with_two_datasets_default_union():

    dataset1 = Dataset(default_union=True)
    dataset1.parse(data=sportquadsnq, format="nquads")
    assert len(dataset1) == 7
    assert len(list(dataset1.quads())) == 7

    dataset2 = Dataset(default_union=True)
    dataset2.parse(data=sportquadsextranq, format="nquads")
    assert len(dataset2) == 10
    assert len(list(dataset2.quads())) == 10

    dataset3 = dataset1 + dataset2
    assert len(list(dataset3.quads())) == 13

    dataset3 = dataset1 - dataset2
    assert len(list(dataset3.quads())) == 3

    dataset3 = dataset1 * dataset2
    assert len(list(dataset3.quads())) == 4

    dataset3 = dataset1 ^ dataset2
    assert len(list(dataset3.quads())) == 9


def test_inplace_operators_with_dataset_and_graph():

    dataset = Dataset()
    dataset.parse(data=sportquadsnq, format="nquads")

    graph = Graph(identifier=URIRef("urn:example:context-1"))
    graph.parse(data=sportsextras, format="n3")

    dataset += graph  # now dataset contains everything

    assert len(list(dataset.quads())) == 14

    dataset.remove((None, None, None, None))
    assert len(dataset) == 0
    dataset.parse(data=sportquadsnq, format="nquads")

    dataset -= graph

    assert len(list(dataset.quads())) == 5

    dataset.remove((None, None, None, None))
    assert len(dataset) == 0
    dataset.parse(data=sportquadsnq, format="nquads")

    with pytest.raises(UnSupportedDatasetOperation):
        dataset *= graph

    with pytest.raises(UnSupportedDatasetOperation):
        dataset ^= graph


def test_inplace_operators_with_two_datasets():

    dataset1 = Dataset()
    dataset1.parse(data=sportquadsnq, format="nquads")
    assert len(dataset1) == 0
    assert len(list(dataset1.quads())) == 7

    dataset2 = Dataset()
    dataset2.parse(data=sportquadsextranq, format="nquads")
    assert len(dataset2) == 0
    assert len(list(dataset2.quads())) == 10

    dataset1 += dataset2  # now dataset1 contains everything
    assert len(list(dataset1.quads())) == 13

    dataset1.remove((None, None, None, None))
    assert len(dataset1) == 0
    for graph in dataset1.graphs():
        assert len(graph) == 0  # All gone

    dataset1.parse(data=sportquadsnq, format="nquads")

    dataset1 -= dataset2

    assert len(list(dataset1.quads())) == 3

    dataset1.parse(data=sportquadsnq, format="nquads")

    dataset1 *= dataset2

    assert len(list(dataset1.quads())) == 4
