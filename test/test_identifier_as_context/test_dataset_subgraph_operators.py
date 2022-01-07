import os
import pytest
from pprint import pformat
from rdflib import (
    Graph,
    ConjunctiveGraph,
    Dataset,
    URIRef,
    logger,
)
from rdflib.graph import DATASET_DEFAULT_GRAPH_ID

sportquadsnq = open(
    os.path.join(
        os.path.dirname(__file__), "..", "consistent_test_data", "sportquads.nq"
    )
).read()


sportquadsextranq = open(
    os.path.join(
        os.path.dirname(__file__), "..", "consistent_test_data", "sportquadsextra.nq"
    )
).read()


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

c1 = URIRef("urn:example:context-1")
c2 = URIRef("urn:example:context-2")


def bind_standard_namespaces(obj):
    obj.bind("rl", URIRef("urn:x-rdflib:"))
    obj.bind("sports", URIRef("http://example.com/ontology/"))
    obj.bind("ex", URIRef("http://example.com/resource/"))
    obj.bind("exgraph", URIRef("http://example.org/graph/"))


def test_operators_with_dataset_and_graph():

    ds = Dataset()
    bind_standard_namespaces(ds)
    ds.parse(data=sportquadsnq, format="nquads")
    assert len(ds) == 0
    assert len(ds.get_context(DATASET_DEFAULT_GRAPH_ID)) == 0
    logger.debug(f"DS:\n{pformat([(g.identifier, len(g)) for g in ds.contexts()])}\n\n")

    g = Graph()
    bind_standard_namespaces(g)
    g.parse(data=sportsextras, format="n3")
    assert len(g) == 7
    # logger.debug(f"G:\n{g.serialize(format='ttl')}")

    assert len(ds + g) == 7  # adds student_30, "Tom Hanks", "Table Tennis", "practises"

    ds1 = ds + g
    assert len(ds1) == 7

    logger.debug(
        f"DS1:\n{pformat([(g.identifier, len(g)) for g in ds1.contexts()])}\n\n"
    )
    logger.debug(f"DS1:\n{ds1.serialize(format='nquads')}")

    with pytest.raises(ValueError):  # too many values to unpack (expected 3)
        assert len(ds - g) == 1  # removes pizza

    with pytest.raises(AssertionError):  # 0 != 1
        assert len(ds * g) == 1  # only pizza

    with pytest.raises(ValueError):  # too many values to unpack (expected 3)
        assert len(ds ^ g) == 2  # removes pizza, adds cheese


def test_operators_with_dataset_and_conjunctivegraph():

    ds = Dataset()
    ds.parse(data=sportquadsnq, format="nquads")

    cg = ConjunctiveGraph()
    cg.parse(data=sportquadsextranq, format="nquads")

    with pytest.raises(
        Exception
    ):  # Trying to add to a context that isn't an identifier: None
        assert len(ds + cg) == 3  # adds cheese as liking

    with pytest.raises(
        Exception
    ):  # Trying to add to a context that isn't an identifier: None
        assert len(ds - cg) == 1  # removes pizza

    with pytest.raises(AssertionError):  # 0 != 1
        assert len(ds * cg) == 1  # only pizza


def test_operators_with_dataset_and_namedgraph():

    ds = Dataset()
    ds.parse(data=sportquadsnq, format="nquads")

    ng = ConjunctiveGraph(identifier=URIRef("urn:example:context-1"))
    ng.parse(data=sportquadsextranq, format="nquads")

    with pytest.raises(
        Exception
    ):  # Trying to add to a context that isn't an identifier: None
        assert len(ds + ng) == 3  # adds cheese as liking

    with pytest.raises(
        Exception
    ):  # Trying to add to a context that isn't an identifier: None
        assert len(ds - ng) == 1  # removes pizza

    with pytest.raises(AssertionError):  # 0 != 1
        assert len(ds * ng) == 1  # only pizza


def test_reversed_operators_with_dataset_and_graph():

    ds = Dataset()
    ds.parse(data=sportquadsnq, format="nquads")

    g = Graph()
    g.parse(data=sportsextras, format="n3")

    with pytest.raises(ValueError):  # too many values to unpack (expected 3)
        assert len(g + ds) == 3  # adds cheese as liking

    with pytest.raises(AssertionError):  # 0 != 1
        assert len(g - ds) == 1  # removes pizza

    with pytest.raises(ValueError):  # too many values to unpack (expected 3)
        assert len(g * ds) == 1  # only pizza

    with pytest.raises(ValueError):  # too many values to unpack (expected 3)
        assert len(g ^ ds) == 2  # removes pizza, adds cheese


def test_operators_with_two_datasets():

    ds1 = Dataset()
    ds1.parse(data=sportquadsnq, format="nquads")

    ds2 = Dataset()
    ds1.parse(data=sportquadsextranq, format="nquads")

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
    ds1.parse(data=sportquadsnq, format="nquads")

    ds2 = Dataset()
    ds1.parse(data=sportquadsextranq, format="nquads")

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


def test_inplace_operators_with_dataset_and_named_graph():

    ds = Dataset()
    ds.parse(data=sportquadsnq, format="nquads")

    g = Graph(identifier=URIRef("urn:example:context-1"))
    g.parse(data=sportsextras, format="n3")

    ds += g  # now ds contains everything

    assert len(ds) == 7

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
    ds.parse(data=sportquadsnq, format="nquads")

    cg = ConjunctiveGraph()
    cg.parse(data=sportquadsextranq, format="nquads")

    ds += cg  # now ds contains everything

    assert len(ds) == 10

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
    ds.parse(data=sportquadsnq, format="nquads")

    cg = ConjunctiveGraph(identifier=URIRef("urn:example:context-1"))
    cg.parse(data=sportquadsextranq, format="nquads")

    ds += cg  # now ds contains everything

    assert len(ds) == 10

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
    ds1.parse(data=sportquadsnq, format="nquads")

    ds2 = Dataset()
    ds1.parse(data=sportquadsextranq, format="nquads")

    ds1 += ds2  # now ds1 contains everything
    assert len(ds1) == 0

    ds1.remove((None, None, None, None))
    assert len(ds1) == 0
    for context in ds1.contexts():
        assert len(ds1.get_context(context)) == 0  # All gone

    ds1.parse(data=sportquadsnq, format="nquads")

    ds1 -= ds2

    assert len(ds1) == 0  # removes extras

    ds1.parse(data=sportquadsnq, format="nquads")

    ds1 *= ds2

    assert len(ds1) == 0  # only pizza

    for g in ds1.graphs():
        logger.debug(
            f"G:{g.identifier}\n{ds1.get_context(g.identifier).serialize(format='trig')}"
        )
