import os
from test.data import *

import pytest

from rdflib import URIRef
from rdflib.graph import (
    Dataset,
    Graph,
    UnSupportedDatasetOperation,
    UnSupportedGraphOperation,
)

sportquadsnq = open(os.path.join(CONSISTENT_DATA_DIR, "sportquads.nq")).read()


def test_operators_with_dataset_and_graph():

    dataset = Dataset()
    dataset.add((tarek, likes, pizza))
    dataset.add((tarek, likes, michel))

    graph = Graph()
    graph.add([tarek, likes, pizza])
    graph.add([tarek, likes, cheese])

    assert len(dataset + graph) == 3  # addataset cheese as liking

    assert len(dataset - graph) == 1  # removes pizza

    with pytest.raises(UnSupportedDatasetOperation):
        assert len(dataset * graph) == 1

    assert len(dataset.default_graph * graph) == 1

    with pytest.raises(UnSupportedDatasetOperation):
        dataset *= graph

    dataset.default_graph *= graph

    with pytest.raises(UnSupportedDatasetOperation):
        assert len(dataset ^ graph) == 2

    assert len(dataset.default_graph ^ graph) == 1

    with pytest.raises(UnSupportedDatasetOperation):
        dataset ^= graph

    dataset.default_graph ^= graph

    assert len(dataset) == 2


def test_operators_with_dataset_and_namedgraph():

    dataset = Dataset()
    dataset.add((tarek, likes, pizza))
    dataset.add((tarek, likes, michel))

    graph = Graph(identifier=URIRef("context-1"))
    graph.add([tarek, likes, pizza])
    graph.add([tarek, likes, cheese])

    assert len(dataset + graph) == 3  # addataset cheese as liking

    assert len(dataset - graph) == 1  # removes pizza

    with pytest.raises(UnSupportedDatasetOperation):
        assert len(dataset * graph) == 1  # only pizza


def test_reversed_operators_with_dataset_and_graph():

    dataset = Dataset()
    dataset.add((tarek, likes, pizza))
    dataset.add((tarek, likes, michel))

    g = Graph()
    g.add([tarek, likes, pizza])
    g.add([tarek, likes, cheese])

    with pytest.raises(UnSupportedGraphOperation):
        assert len(g + dataset) == 3  # addataset cheese as liking

    with pytest.raises(UnSupportedGraphOperation):
        assert len(g - dataset) == 1  # removes pizza

    with pytest.raises(UnSupportedGraphOperation):
        assert len(g * dataset) == 1  # only pizza

    with pytest.raises(
        UnSupportedGraphOperation
    ):  # too many values to unpack (expected 3)
        assert len(g ^ dataset) == 2  # removes pizza, addataset cheese


def test_operators_with_two_datasets():

    dataset1 = Dataset()
    dataset1.add((tarek, likes, pizza))
    dataset1.add((tarek, likes, michel))

    dataset2 = Dataset()
    dataset2.add((tarek, likes, pizza))
    dataset2.add((tarek, likes, cheese))

    assert len(dataset1 + dataset2) == 3  # addataset cheese as liking

    assert len(dataset1 - dataset2) == 1  # removes pizza

    assert len(dataset1 * dataset2) == 1  # only pizza

    assert len(dataset1 ^ dataset2) == 2  # only pizza


def test_operators_with_two_datasets_one_default_union():

    dataset1 = Dataset(default_union=True)
    dataset1.add((tarek, likes, pizza))
    dataset1.add((tarek, likes, michel))

    dataset2 = Dataset()
    dataset2.add((tarek, likes, pizza))
    dataset2.add((tarek, likes, cheese))

    assert len(dataset1 + dataset2) == 3  # adds cheese as liking

    assert len(dataset1 - dataset2) == 1  # removes pizza

    assert len(dataset1 * dataset2) == 1  # only pizza

    assert len(dataset1 ^ dataset2) == 2  # only pizza


def test_inplace_operators_with_dataset_and_graph():

    dataset = Dataset()
    dataset.add((tarek, likes, pizza))
    dataset.add((tarek, likes, michel))

    g = Graph()
    g.add([tarek, likes, pizza])
    g.add([tarek, likes, cheese])

    dataset += g  # now dataset contains everything

    assert len(dataset) == 3

    dataset.remove((None, None, None, None))
    assert len(dataset) == 0

    dataset -= g

    with pytest.raises(AssertionError):  # 0 == 1
        assert len(dataset) == 1  # removes pizza

    dataset.remove((None, None, None, None))
    assert len(dataset) == 0

    with pytest.raises(UnSupportedDatasetOperation):
        dataset *= g


def test_inplace_operators_with_two_datasets():

    dataset1 = Dataset()

    dataset1.add((tarek, likes, pizza))
    dataset1.add((tarek, likes, michel))

    dataset2 = Dataset()
    dataset2.add((tarek, likes, pizza))
    dataset2.add((tarek, likes, cheese))

    dataset1 += dataset2  # now dataset1 contains everything

    dataset1.remove((None, None, None, None))

    assert len(dataset1) == 0

    dataset1.add((tarek, likes, pizza))
    dataset1.add((tarek, likes, michel))

    dataset1 -= dataset2

    assert len(dataset1) == 1  # removes pizza

    dataset1.remove((None, None, None, None))
    assert len(dataset1) == 0

    dataset1.add((tarek, likes, pizza))
    dataset1.add((tarek, likes, michel))

    dataset1 *= dataset2

    assert len(dataset1) == 1  # only pizza


def test_inplace_operators_with_dataset_and_datasetunion():

    dataset1 = Dataset()
    dataset1.add((tarek, likes, pizza))
    dataset1.add((tarek, likes, michel))

    dataset2 = Dataset(default_union=True)
    dataset2.add((tarek, likes, pizza))
    dataset2.add((tarek, likes, cheese))

    dataset1 += dataset2  # now dataset1 contains everything

    dataset1.remove((None, None, None, None))
    assert len(dataset1) == 0
    dataset1.add((tarek, likes, pizza))
    dataset1.add((tarek, likes, michel))

    dataset1 -= dataset2

    assert len(dataset1) == 1  # removes pizza

    dataset1.remove((None, None, None, None))
    assert len(dataset1) == 0
    dataset1.add((tarek, likes, pizza))
    dataset1.add((tarek, likes, michel))

    dataset1 *= dataset2

    assert len(dataset1) == 1  # only pizza
