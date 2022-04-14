from rdflib import Dataset
from rdflib.graph import DATASET_DEFAULT_GRAPH_ID


def test_issue1396_store_query_and_update_methods_queryGraph_parameter_does_not_support_conjunctivegraph_and_dataset_dataset():

    ds = Dataset()

    # There are no triples in any context, so dataset length == 0
    assert len(ds) == 0

    # The default graph is not treated as a context
    assert len(list(ds.graphs())) == 0

    # The default graph is not treated as a context
    assert str(list(ds.graphs())) == "[]"

    # only the default graph exists and is properly identified as DATASET_DEFAULT_GRAPH_ID
    assert ds.default_graph.identifier == DATASET_DEFAULT_GRAPH_ID

    dataset_default_graph = ds.graph(DATASET_DEFAULT_GRAPH_ID)

    assert (
        str(dataset_default_graph)
        == "<urn:x-rdflib:default> a rdfg:Graph;rdflib:storage [a rdflib:Store;rdfs:label 'Memory']."
    )

    ds.update(
        "INSERT DATA { <urn:example:tarek> <urn:example:hates> <urn:example:pizza> . }"
    )

    assert len(list(ds.graphs())) == 0

    # Only the default graph exists and is not yielded by ds.graphs()
    assert str(list(ds.graphs())) == "[]"

    # There is one triple in the context, so dataset length == 1
    assert len(ds) == 1

    assert len(list(ds.query("SELECT * {?s ?p ?o .}"))) == 1
