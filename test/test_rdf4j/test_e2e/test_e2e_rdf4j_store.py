
from rdflib import RDF, SKOS, Dataset, Graph, Literal, URIRef
from rdflib.contrib.rdf4j.client import Repository
from rdflib.graph import DATASET_DEFAULT_GRAPH_ID


def test_rdf4j_store_add(ds: Dataset):
    assert len(ds) == 0
    ds.add((URIRef("http://example.com/s"), RDF.type, SKOS.Concept))
    assert len(ds) == 1


def test_rdf4j_store_addn(ds: Dataset):
    assert len(ds) == 0
    ds.addN(
        [
            (
                URIRef("http://example.com/s"),
                RDF.type,
                SKOS.Concept,
                URIRef("urn:graph:a"),
            ),
            (
                URIRef("http://example.com/s"),
                SKOS.prefLabel,
                Literal("Label"),
                DATASET_DEFAULT_GRAPH_ID,
            ),
            (
                URIRef("http://example.com/s"),
                SKOS.definition,
                Literal("Definition"),
                URIRef("urn:graph:b"),
            ),
        ]
    )
    assert len(ds) == 3


def test_graphs_method_default_graph(ds: Dataset):
    repo: Repository = ds.store.repo
    data = f"""
        <http://example.com/s> <{RDF.type}> <{SKOS.Concept}> .
    """
    # This returns 1 graph, the default graph, even when there are no triples.
    graphs = list(ds.graphs())
    assert len(graphs) == 1
    assert graphs[0].identifier == DATASET_DEFAULT_GRAPH_ID
    repo.upload(data)
    graphs = list(ds.graphs())
    assert len(graphs) == 1
    graph = graphs[0]
    assert graph.identifier == DATASET_DEFAULT_GRAPH_ID
    assert len(graph) == 1


def test_graphs_method_default_and_named_graphs(ds: Dataset):
    repo: Repository = ds.store.repo
    data = f"""
            <http://example.com/s> <{RDF.type}> <{SKOS.Concept}> <urn:graph:a> .
            <http://example.com/s> <{SKOS.prefLabel}> "Label" <urn:graph:a> .
            <http://example.com/s> <{SKOS.prefLabel}> "Label" <urn:graph:b> .
            <http://example.com/s> <{SKOS.definition}> "Definition" .
        """
    # This returns 1 graph, the default graph, even when there are no triples.
    graphs = list(ds.graphs())
    assert len(graphs) == 1
    assert graphs[0].identifier == DATASET_DEFAULT_GRAPH_ID
    repo.upload(data)

    # Retrieve graphs with no triple pattern.
    graphs = list(ds.graphs())
    assert len(graphs) == 3

    graph_a = graphs[0]
    assert graph_a.identifier == URIRef("urn:graph:b")
    assert len(graph_a) == 1

    graph_b = graphs[1]
    assert graph_b.identifier == URIRef("urn:graph:a")
    assert len(graph_b) == 2

    default_graph = graphs[2]
    assert default_graph.identifier == DATASET_DEFAULT_GRAPH_ID
    assert len(default_graph) == 1

    # Retrieve graphs with a triple pattern.
    graphs = list(
        ds.graphs(triple=(URIRef("http://example.com/s"), RDF.type, SKOS.Concept))
    )
    # Note: it's returning 2 graphs instead of 1 because the Dataset class always
    # includes the default graph.
    # I don't think this is the correct behaviour. TODO: raise a ticket for this.
    # What should happen is, ds.graphs() includes the default graph if the triple
    # pattern is None. Otherwise, it should only include graphs that contain the triple.
    assert len(graphs) == 2
    graph_a = graphs[0]
    assert graph_a.identifier == URIRef("urn:graph:a")
    assert len(graph_a) == 2


def test_add_graph(ds: Dataset):
    assert len(ds) == 0
    graphs = list(ds.graphs())
    assert len(graphs) == 1
    assert graphs[0].identifier == DATASET_DEFAULT_GRAPH_ID

    graph_name = URIRef("urn:graph:a")

    # Add a graph to the dataset using a URIRef.
    # Note, this is a no-op since RDF4J doesn't support named graphs with no statements,
    # which is why the length of the graphs is 1 (the default graph).
    ds.add_graph(graph_name)
    graphs = list(ds.graphs())
    assert len(graphs) == 1
    assert graphs[0].identifier == DATASET_DEFAULT_GRAPH_ID

    # Add a graph object to the dataset.
    # This will create a new graph in RDF4J, along with the statements.
    graph = Graph(identifier=graph_name)
    graph.add((URIRef("http://example.com/s"), RDF.type, SKOS.Concept))
    graph.add((URIRef("http://example.com/s"), SKOS.prefLabel, Literal("Label")))
    ds.add_graph(graph)
    # Verify that the graph was added.
    graphs = list(ds.graphs())
    assert len(graphs) == 2
    graph_a = graphs[0]
    assert graphs[1].identifier == DATASET_DEFAULT_GRAPH_ID
    assert graph_a.identifier == graph_name
    assert len(graph_a) == 2


def test_remove_graph(ds: Dataset):
    repo: Repository = ds.store.repo
    data = f"""
            <http://example.com/s> <{RDF.type}> <{SKOS.Concept}> <urn:graph:a> .
            <http://example.com/s> <{SKOS.prefLabel}> "Label" <urn:graph:a> .
            <http://example.com/s> <{SKOS.prefLabel}> "Label" <urn:graph:b> .
            <http://example.com/s> <{SKOS.definition}> "Definition" .
        """
    # This returns 1 graph, the default graph, even when there are no triples.
    graphs = list(ds.graphs())
    assert len(graphs) == 1
    assert graphs[0].identifier == DATASET_DEFAULT_GRAPH_ID
    repo.upload(data)
    assert len(ds) == 4

    ds.remove_graph(URIRef("urn:graph:a"))
    assert len(ds) == 2
    graphs = list(ds.graphs())
    assert len(graphs) == 2
    assert graphs[0].identifier == URIRef("urn:graph:b")
    assert graphs[1].identifier == DATASET_DEFAULT_GRAPH_ID
