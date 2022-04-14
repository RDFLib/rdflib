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


def test_dataset_add_graph_as_new_dataset_subgraph():

    data = """
    <http://data.yyx.me/jack> <http://onto.yyx.me/work_for> <http://data.yyx.me/company_a> .
    <http://data.yyx.me/david> <http://onto.yyx.me/work_for> <http://data.yyx.me/company_b> .
    """

    ds = Dataset()

    subgraph_identifier = URIRef("urn:x-rdflib:subgraph1")

    g = ds.graph(subgraph_identifier)

    g.add(s1)
    g.add(s2)

    assert len(g) == 2

    subgraph = ds.graph(subgraph_identifier)

    assert type(subgraph) is Graph

    assert len(subgraph) == 2


def test_parse_graph_as_new_dataset_subgraph_n3():

    dataset = Dataset()
    assert len(list(dataset.contexts())) == 0

    dataset.add((tarek, hates, cheese))
    assert len(list(dataset.contexts())) == 0
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

    assert len(list(dataset.contexts())) == 0

    dataset.add((tarek, hates, cheese))

    assert len(list(dataset.contexts())) == 0

    assert len(list(dataset.graphs((tarek, None, None)))) == 1

    assert len(dataset) == 1

    dataset.parse(
        data="<urn:example:tarek> <urn:example:likes> <urn:example:pizza> <urn:example:context-a> .",
        format="nquads",
    )

    assert len(list(dataset.contexts())) == 1

    assert len(list(dataset.graphs((tarek, None, None)))) == 1


def test_parse_graph_as_new_dataset_subgraph_nquads():

    dataset = Dataset()

    assert len(list(dataset.contexts())) == 0

    dataset.add((tarek, hates, cheese))

    assert len(list(dataset.contexts())) == 0

    with pytest.raises(AssertionError):
        assert len(list(dataset.graphs((tarek, None, None)))) == 1

    assert len(dataset) == 1

    dataset.parse(
        data="<urn:example:tarek> <urn:example:likes> <urn:example:pizza> <urn:example:context-a> .",
        format="nquads",
    )

    assert len(list(dataset.contexts())) == 1

    assert len(list(dataset.graphs((tarek, None, None)))) == 1

    # Confirm that the newly-created subgraph (the publicID in the above turtle) exists
    assert URIRef("urn:example:context-a") in list(dataset.contexts())

    # Confirm that the newly-created subgraph contains a triple
    assert len(dataset.graph(URIRef("urn:example:context-a"))) == 1

    # Bind the newly-created subgraph to a variable
    g = dataset.graph(URIRef("urn:example:context-a"))

    # Confirm that the newly-created subgraph contains the parsed triple
    assert (tarek, likes, pizza) in g


def test_parse_graph_as_new_dataset_subgraph_nquads_with_dataset_aware_store():
    import shutil
    import tempfile

    path = tempfile.mkdtemp()

    try:
        shutil.rmtree(path)
    except:
        pass

    dataset = Dataset(store="BerkeleyDB")
    dataset.open(path, create=True)

    try:

        assert len(list(dataset.contexts())) == 0

        dataset.add((tarek, hates, cheese))

        assert len(list(dataset.contexts())) == 0

        assert len(list(dataset.graphs((tarek, None, None)))) == 0

        assert len(dataset) == 1

        dataset.parse(
            data="<urn:example:tarek> <urn:example:likes> <urn:example:pizza> <urn:example:context-a> .",
            format="nquads",
        )

        assert len(list(dataset.contexts())) == 1

        assert len(list(dataset.graphs((tarek, None, None)))) == 1

        # Confirm that the newly-created subgraph (the publicID in the above turtle) exists
        assert URIRef("urn:example:context-a") in list(dataset.contexts())

        # Confirm that the newly-created subgraph contains a triple
        assert len(dataset.graph(URIRef("urn:example:context-a"))) == 1

        # Bind the newly-created subgraph to a variable
        graph = dataset.graph(URIRef("urn:example:context-a"))

        # Confirm that the newly-created subgraph contains the parsed triple
        assert (tarek, likes, pizza) in graph

        dataset.store.close()
        try:
            shutil.rmtree(path)
        except Exception:
            pass
    except Exception as e:
        try:
            shutil.rmtree(path)
        except Exception:
            pass
        raise Exception(e)


def test_parse_graph_as_new_dataset_subgraph_trig():
    dataset = Dataset()
    assert len(list(dataset.contexts())) == 0

    dataset.add((tarek, hates, cheese))
    assert len(dataset) == 1
    assert len(list(dataset.contexts())) == 0

    dataset.parse(
        data="@prefix ex: <http://example.org/graph/> . @prefix ont: <http://example.com/ontology/> . ex:practise { <http://example.com/resource/student_10> ont:practises <http://example.com/resource/sport_100> . }",
        format="trig",
    )

    assert len(list(dataset.contexts())) == 1

    # Check that the newly-created subgraph ("ex:practise" in the above trig) exists
    assert URIRef("http://example.org/graph/practise") in list(dataset.contexts())

    assert len(dataset) == 1  # Just the statement asserting tarek's dislike of cheese


def test_parse_graph_with_publicid_as_new_dataset_subgraph():
    dataset = Dataset()
    assert len(list(dataset.contexts())) == 0

    dataset.add((tarek, hates, cheese))
    assert len(dataset) == 1
    assert len(list(dataset.contexts())) == 0

    dataset.parse(
        data="<urn:example:tarek> <urn:example:likes> <urn:example:pizza> .",
        publicID="urn:x-rdflib:context-a",
        format="ttl",
    )
    assert len(list(dataset.contexts())) == 1

    # Confirm that the newly-created subgraph (the publicID in the above turtle) exists
    assert URIRef("urn:x-rdflib:context-a") in list(dataset.contexts())

    # Confirm that the newly-created subgraph contains a triple
    assert len(dataset.graph(URIRef("urn:x-rdflib:context-a"))) == 1

    # Bind the newly-created subgraph to a variable
    g = dataset.graph(URIRef("urn:x-rdflib:context-a"))

    # Confirm that the newly-created subgraph contains the parsed triple
    assert (tarek, likes, pizza) in g


def test_parse_graph_with_bnode_as_new_dataset_subgraph():
    dataset = Dataset()
    assert len(list(dataset.contexts())) == 0

    dataset.add((tarek, hates, cheese))

    assert len(dataset) == 1

    assert len(list(dataset.contexts())) == 0

    data = """_:a <urn:example:likes> <urn:example:pizza> ."""

    subgraph = dataset.graph()

    subgraph.parse(data=data, format="ttl")

    assert (
        len(list(dataset.contexts())) == 1
    )  # Now contains a context with a BNode graph

    assert subgraph.identifier in list(dataset.contexts())

    logger.debug(
        f"PARSED DATASET GRAPHS: {list(dataset.contexts())} ... {subgraph.identifier}"
    )

    # subgraph identifier is a GenID identifier
    assert (
        str(subgraph.identifier).startswith(
            "http://rdlib.net/.well-known/genid/rdflib/N"
        )
        and len(subgraph.identifier) == 75
    )


def test_add_graph_with_bnode_identifier_as_new_dataset_subgraph():
    dataset = Dataset()
    assert len(list(dataset.contexts())) == 0

    dataset.add((tarek, hates, cheese))
    assert len(dataset) == 1
    assert len(list(dataset.contexts())) == 0

    subgraph = dataset.graph(identifier=BNode())
    subgraph.parse(data="<a> <b> <c> .", format="ttl")

    assert (
        len(list(dataset.contexts())) == 1
    )  # Now contains a context with a BNode graph

    assert len(subgraph) > 0

    assert subgraph.identifier in list(dataset.contexts())

    # subgraph identifier is a BNode identifier
    assert subgraph.identifier.startswith("N") and len(subgraph.identifier) == 33
