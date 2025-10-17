from rdflib import RDF, RDFS, Dataset, Graph, URIRef
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
