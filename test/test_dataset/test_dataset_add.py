from rdflib import RDF, RDFS, Dataset, Graph, URIRef


def test_working():
    """
    This test passes because the graph is created through the Dataset.graph method.
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


def test_broken():
    """
    This test fails because the graph is created first and then added to the Dataset.
    """
    ds = Dataset(default_union=True)
    graph_name = URIRef("urn:graph")
    graph = Graph(identifier=graph_name)

    graph.add((URIRef("urn:class"), RDF.type, RDFS.Class))
    assert len(graph) == 1
    assert len(ds) == 0

    # Adding an existing graph doesn’t necessarily use the same store, and therefore its contents are not copied over.
    ds.add_graph(graph)
    assert any(g.identifier == graph_name for g in ds.graphs())

    # This fails
    assert len(list(ds.objects(None, None))) == 1

    retrieved_graph = ds.get_graph(graph_name)
    assert retrieved_graph.identifier == graph_name
    assert isinstance(retrieved_graph, Graph)

    # This prints correctly
    ds.print(format="trig")

    # These fail with 0
    assert len(retrieved_graph) == 1
    assert len(ds) == 1

    ds.remove_graph(retrieved_graph)
    assert len(retrieved_graph) == 0
    assert len(ds) == 0


def test_adding_appends_to_dataset_graph():
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
