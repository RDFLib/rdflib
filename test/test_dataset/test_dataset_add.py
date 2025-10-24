from textwrap import dedent

from rdflib import RDF, RDFS, Dataset, Graph, Literal, URIRef
from rdflib.compare import isomorphic
from rdflib.graph import DATASET_DEFAULT_GRAPH_ID
from test.data import TEST_DATA_DIR


def test_behaviour_where_graph_is_created_via_dataset():
    """
    Test that the dataset store state is intact when graphs are created from the dataset.
    """
    ds = Dataset(default_union=True)
    graph_name = URIRef("urn:graph")
    graph = ds.graph(graph_name)

    graph.add((URIRef("urn:class"), RDF.type, RDFS.Class))
    assert len(graph) == 1
    assert len(ds) == 1

    ds.add_graph(graph)
    assert any(g.identifier == graph_name for g in ds.graphs())
    assert len(list(ds.objects(None, None))) == 1

    retrieved_graph = ds.get_graph(graph_name)
    assert retrieved_graph.identifier == graph_name
    assert isinstance(retrieved_graph, Graph)

    assert len(retrieved_graph) == 1
    assert len(ds) == 1

    ds.remove_graph(retrieved_graph)
    assert len(retrieved_graph) == 0
    assert len(ds) == 0


def test_behaviour_where_graph_is_created_separately():
    """
    Test that the graphs created externally from the dataset are added to the dataset
    store.
    """
    ds = Dataset(default_union=True)
    graph_name = URIRef("urn:graph")
    graph = Graph(identifier=graph_name)

    graph.add((URIRef("urn:class"), RDF.type, RDFS.Class))
    assert len(graph) == 1
    assert len(ds) == 0

    ds.add_graph(graph)
    assert any(g.identifier == graph_name for g in ds.graphs())

    assert len(list(ds.objects(None, None))) == 1

    retrieved_graph = ds.get_graph(graph_name)
    assert retrieved_graph.identifier == graph_name
    assert isinstance(retrieved_graph, Graph)

    assert len(retrieved_graph) == 1
    assert len(ds) == 1

    ds.remove_graph(retrieved_graph)
    assert len(retrieved_graph) == 0
    assert len(ds) == 0


def test_adding_appends_to_dataset_graph():
    """
    Test that external graphs added to the dataset have their triples appended if
    the graph identifier already exists.
    """
    ds = Dataset(default_union=True)
    graph_name = URIRef("urn:graph")
    graph = Graph(identifier=graph_name)

    graph.add((URIRef("urn:class"), RDF.type, RDFS.Class))
    assert len(graph) == 1
    assert len(ds) == 0

    # Make sure to use the returned graph object with the same dataset store.
    graph = ds.add_graph(graph)
    assert len(ds) == 1

    graph.add((URIRef("urn:instance"), RDF.type, URIRef("urn:class")))
    assert len(graph) == 2
    assert len(ds) == 2

    # Another graph, same identifier
    another_graph = Graph(identifier=graph_name)
    another_graph.add((URIRef("urn:another_instance"), RDF.type, URIRef("urn:class")))
    graph = ds.add_graph(another_graph)
    assert len(graph) == 3
    assert len(ds) == 3


def test_dataset_parse_return_value():
    """
    Test that the return value of ds.parse has the same reference as ds.
    """
    ds = Dataset()
    return_value = ds.parse(
        source=TEST_DATA_DIR / "nquads.rdflib/example.nquads", format="nquads"
    )
    assert len(ds)
    assert return_value is ds


def test_dataset_iadd():
    ds = Dataset()
    ds.add(
        (
            URIRef("https://example.com/subject"),
            URIRef("https://example.com/p/predicate"),
            Literal("object"),
        )
    )

    ds2 = Dataset()
    ds2.add(
        (
            URIRef("https://example.com/subject"),
            URIRef("https://example.com/p/predicate"),
            Literal("object"),
            URIRef("https://example.com/graph"),
        )
    )

    data = """
    {
        <https://example.com/subject2> <https://example.com/p/predicate2> "object2" .
    }

    <https://example.com/graph> {
        <https://example.com/subject-other> <https://example.com/p/predicate-other> "Triple-Other" .
    }

    <https://example.com/graph2> {
        <https://example.com/subject-y> <https://example.com/predicate-y> "Triple Y" .
    }

    """
    ds3 = Dataset().parse(data=data, format="trig")

    # Combine the datasets
    ds += ds2 + ds3

    expected_default_graph_data = dedent(
        """
        @prefix ns2: <https://example.com/> .
        @prefix ns3: <https://example.com/p/> .
        ns2:subject2 ns3:predicate2 "object2" .
        ns2:subject ns3:predicate "object" .
    """
    )
    expected_default_graph = Graph(identifier=DATASET_DEFAULT_GRAPH_ID).parse(
        data=expected_default_graph_data, format="turtle"
    )

    expected_graph1_data = dedent(
        """
        @prefix ns2: <https://example.com/> .
        @prefix ns3: <https://example.com/p/> .
        ns2:subject ns3:predicate "object" .
        ns2:subject-other ns3:predicate-other "Triple-Other" .
    """
    )
    expected_graph1 = Graph(identifier=URIRef("https://example.com/graph")).parse(
        data=expected_graph1_data, format="turtle"
    )

    expected_graph2 = dedent(
        """
        @prefix ns2: <https://example.com/> .
        ns2:subject-y ns2:predicate-y "Triple Y" .
    """
    )
    expected_graph2 = Graph(identifier=URIRef("https://example.com/graph2")).parse(
        data=expected_graph2, format="turtle"
    )

    assert isomorphic(expected_default_graph, ds.default_graph)
    assert isomorphic(
        expected_graph1, ds.get_graph(URIRef("https://example.com/graph"))
    )
    assert isomorphic(
        expected_graph2, ds.get_graph(URIRef("https://example.com/graph2"))
    )
