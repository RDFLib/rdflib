import pytest
from rdflib import (
    Graph,
    ConjunctiveGraph,
    Dataset,
    URIRef,
)


michel = URIRef("urn:example:michel")
tarek = URIRef("urn:example:tarek")
bob = URIRef("urn:example:bob")
likes = URIRef("urn:example:likes")
hates = URIRef("urn:example:hates")
pizza = URIRef("urn:example:pizza")
cheese = URIRef("urn:example:cheese")

c1 = URIRef("urn:example:context-1")
c2 = URIRef("urn:example:context-2")


def test_operators_with_dataset_and_graph():

    ds = Dataset()
    ds.add((tarek, likes, pizza))
    ds.add((tarek, likes, michel))

    g = Graph()
    g.add([tarek, likes, pizza])
    g.add([tarek, likes, cheese])

    with pytest.raises(
        Exception
    ):  # Trying to add to a context that isn't an identifier: None
        assert len(ds + g) == 3  # adds cheese as liking

    with pytest.raises(ValueError):  # too many values to unpack (expected 3)
        assert len(ds - g) == 1  # removes pizza

    assert len(ds * g) == 1  # only pizza

    with pytest.raises(ValueError):  # too many values to unpack (expected 3)
        assert len(ds ^ g) == 2  # removes pizza, adds cheese


def test_operators_with_dataset_and_conjunctivegraph():

    ds = Dataset()
    ds.add((tarek, likes, pizza))
    ds.add((tarek, likes, michel))

    cg = ConjunctiveGraph()
    cg.add([tarek, likes, pizza])
    cg.add([tarek, likes, cheese])

    with pytest.raises(
        Exception
    ):  # Trying to add to a context that isn't an identifier: None
        assert len(ds + cg) == 3  # adds cheese as liking

    with pytest.raises(
        Exception
    ):  # Trying to add to a context that isn't an identifier: None
        assert len(ds - cg) == 1  # removes pizza

    assert len(ds * cg) == 1  # only pizza


def test_operators_with_dataset_and_namedgraph():

    ds = Dataset()
    ds.add((tarek, likes, pizza))
    ds.add((tarek, likes, michel))

    ng = ConjunctiveGraph(identifier=URIRef("context-1"))
    ng.add([tarek, likes, pizza])
    ng.add([tarek, likes, cheese])

    with pytest.raises(
        Exception
    ):  # Trying to add to a context that isn't an identifier: None
        assert len(ds + ng) == 3  # adds cheese as liking

    with pytest.raises(
        Exception
    ):  # Trying to add to a context that isn't an identifier: None
        assert len(ds - ng) == 1  # removes pizza

    assert len(ds * ng) == 1  # only pizza


def test_reversed_operators_with_dataset_and_graph():

    ds = Dataset()
    ds.add((tarek, likes, pizza))
    ds.add((tarek, likes, michel))

    g = Graph()
    g.add([tarek, likes, pizza])
    g.add([tarek, likes, cheese])

    with pytest.raises(ValueError):  # too many values to unpack (expected 3)
        assert len(g + ds) == 3  # adds cheese as liking

    assert len(g - ds) == 1  # removes pizza

    with pytest.raises(ValueError):  # too many values to unpack (expected 3)
        assert len(g * ds) == 1  # only pizza

    with pytest.raises(ValueError):  # too many values to unpack (expected 3)
        assert len(g ^ ds) == 2  # removes pizza, adds cheese


def test_operators_with_two_datasets():

    ds1 = Dataset()
    ds1.add((tarek, likes, pizza))
    ds1.add((tarek, likes, michel))

    ds2 = Dataset()
    ds2.add((tarek, likes, pizza))
    ds2.add((tarek, likes, cheese))

    with pytest.raises(
        Exception
    ):  # Trying to add to a context that isn't an identifier: None
        assert len(ds1 + ds2) == 3  # adds cheese as liking

    with pytest.raises(
        Exception
    ):  # Trying to add to a context that isn't an identifier: None
        assert len(ds1 - ds2) == 1  # removes pizza

    with pytest.raises(
        Exception
    ):  # Trying to add to a context that isn't an identifier: None
        assert len(ds1 * ds2) == 1  # only pizza

    with pytest.raises(
        Exception
    ):  # Trying to add to a context that isn't an identifier: None
        assert len(ds1 ^ ds2) == 1  # only pizza


def test_operators_with_two_datasets_default_union():

    ds1 = Dataset(default_union=True)
    ds1.add((tarek, likes, pizza))
    ds1.add((tarek, likes, michel))

    ds2 = Dataset()
    ds2.add((tarek, likes, pizza))
    ds2.add((tarek, likes, cheese))

    with pytest.raises(
        Exception
    ):  # Trying to add to a context that isn't an identifier: None
        assert len(ds1 + ds2) == 3  # adds cheese as liking

    with pytest.raises(
        Exception
    ):  # Trying to add to a context that isn't an identifier: None
        assert len(ds1 - ds2) == 1  # removes pizza

    with pytest.raises(
        Exception
    ):  # Trying to add to a context that isn't an identifier: None
        assert len(ds1 * ds2) == 1  # only pizza

    with pytest.raises(
        Exception
    ):  # Trying to add to a context that isn't an identifier: None
        assert len(ds1 ^ ds2) == 1  # only pizza


def test_inplace_operators_with_conjunctivegraph_and_graph():

    cg = ConjunctiveGraph()
    cg.add((tarek, likes, pizza))
    cg.add((tarek, likes, michel))

    g = Graph()
    g.add([tarek, likes, pizza])
    g.add([tarek, likes, cheese])

    cg += g  # now cg contains everything

    assert len(cg) == 3

    cg.remove((None, None, None, None))
    assert len(cg) == 0

    cg -= g

    with pytest.raises(AssertionError):  # 0 == 1
        assert len(cg) == 1  # removes pizza

    cg.remove((None, None, None, None))
    assert len(cg) == 0

    cg *= g

    with pytest.raises(AssertionError):  # 0 == 1
        assert len(cg) == 1  # only pizza


def test_inplace_operators_with_two_conjunctivegraphs():

    cg1 = ConjunctiveGraph()
    cg1.add((tarek, likes, pizza))
    cg1.add((tarek, likes, michel))

    cg2 = ConjunctiveGraph()
    cg2.add((tarek, likes, pizza))
    cg2.add((tarek, likes, cheese))

    cg1 += cg2  # now cg1 contains everything

    assert len(cg1) == 3

    cg1.remove((None, None, None, None))
    assert len(cg1) == 0

    cg1 -= cg2

    with pytest.raises(AssertionError):
        assert len(cg1) == 1  # removes pizza

    cg1.remove((None, None, None, None))
    assert len(cg1) == 0

    cg1 *= cg2

    with pytest.raises(AssertionError):
        assert len(cg1) == 1  # only pizza


def test_inplace_operators_with_dataset_and_graph():

    ds = Dataset()
    ds.add((tarek, likes, pizza))
    ds.add((tarek, likes, michel))

    g = Graph()
    g.add([tarek, likes, pizza])
    g.add([tarek, likes, cheese])

    ds += g  # now ds contains everything

    assert len(ds) == 3

    ds.remove((None, None, None, None))
    assert len(ds) == 0

    ds -= g

    with pytest.raises(AssertionError):  # 0 == 1
        assert len(ds) == 1  # removes pizza

    ds.remove((None, None, None, None))
    assert len(ds) == 0

    ds *= g

    with pytest.raises(AssertionError):  # 0 == 1
        assert len(ds) == 1  # only pizza


def test_inplace_operators_with_dataset_and_conjunctivegraph():

    ds = Dataset()
    ds.add((tarek, likes, pizza))
    ds.add((tarek, likes, michel))

    cg = ConjunctiveGraph()
    cg.add([tarek, likes, pizza])
    cg.add([tarek, likes, cheese])

    ds += cg  # now ds contains everything

    assert len(ds) == 3

    ds.remove((None, None, None, None))
    assert len(ds) == 0

    ds -= cg

    with pytest.raises(AssertionError):  # 0 == 1
        assert len(ds) == 1  # removes pizza

    ds.remove((None, None, None, None))
    assert len(ds) == 0

    ds *= cg

    with pytest.raises(AssertionError):  # 0 == 1
        assert len(ds) == 1  # only pizza


def test_inplace_operators_with_dataset_and_namedgraph():

    ds = Dataset()
    ds.add((tarek, likes, pizza))
    ds.add((tarek, likes, michel))

    cg = ConjunctiveGraph(identifier=URIRef("context-1"))
    cg.add((tarek, likes, pizza))
    cg.add((tarek, likes, cheese))

    ds += cg  # now ds contains everything

    assert len(ds) == 3

    ds.remove((None, None, None, None))
    assert len(ds) == 0

    ds -= cg

    with pytest.raises(AssertionError):  # 0 == 1
        assert len(ds) == 1  # removes pizza

    ds.remove((None, None, None, None))
    assert len(ds) == 0

    ds *= cg

    with pytest.raises(AssertionError):  # 0 == 1
        assert len(ds) == 1  # only pizza


def test_inplace_operators_with_two_datasets():

    ds1 = Dataset()
    ds1.add((tarek, likes, pizza))
    ds1.add((tarek, likes, michel))

    ds2 = Dataset()
    ds2.add((tarek, likes, pizza))
    ds2.add((tarek, likes, cheese))

    with pytest.raises(ValueError):  # too many values to unpack (expected 3)
        ds1 += ds2  # now ds1 contains everything

    ds1.remove((None, None, None, None))
    assert len(ds1) == 0

    ds1 -= ds2

    with pytest.raises(AssertionError):  # 0 == 1
        assert len(ds1) == 1  # removes pizza

    ds1.remove((None, None, None, None))
    assert len(ds1) == 0

    ds1 *= ds2

    with pytest.raises(AssertionError):  # 0 == 1
        assert len(ds1) == 1  # only pizza
