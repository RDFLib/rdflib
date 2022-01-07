from rdflib import Dataset
from rdflib.graph import DATASET_DEFAULT_GRAPH_ID


def test_issue1396_store_query_and_update_methods_queryGraph_parameter_does_not_support_namedgraph_and_dataset_dataset():

    ds = Dataset()

    # There are no triples in any context, so dataset length == 0
    assert len(ds) == 0

    # The default graph is a context so the length of ds.contexts() == 1
    assert len(list(ds.contexts())) == 1

    # Only the default graph exists and is yielded by ds.contexts()
    assert (
        str(list(ds.contexts()))
        == "[<Graph identifier=urn:x-rdflib:default (<class 'rdflib.graph.Graph'>)>]"
    )

    # only the default graph exists and is properly identified as DATASET_DEFAULT_GRAPH_ID
    assert set(x.identifier for x in ds.contexts()) == set([DATASET_DEFAULT_GRAPH_ID])

    dataset_default_graph = ds.get_context(DATASET_DEFAULT_GRAPH_ID)

    assert (
        str(dataset_default_graph)
        == "<urn:x-rdflib:default> a rdfg:Graph;rdflib:storage [a rdflib:Store;rdfs:label 'Memory']."
    )

    # INSERT into NAMED GRAPH

    ds.update(
        "INSERT DATA { GRAPH <urn:example:context1> { <urn:example:tarek> <urn:example:hates> <urn:example:pizza> . } }"
    )

    assert len(list(ds.contexts())) == 2

    # Only the default graph exists and is yielded by ds.contexts()
    assert str(list(ds.contexts())) in [
        "[<Graph identifier=urn:x-rdflib:default (<class 'rdflib.graph.Graph'>)>, <Graph identifier=urn:context1 (<class 'rdflib.graph.Graph'>)>]",
        "[<Graph identifier=urn:x-rdflib:default (<class 'rdflib.graph.Graph'>)>, <Graph identifier=urn:example:context1 (<class 'rdflib.graph.Graph'>)>]",
        "[<Graph identifier=urn:example:context1 (<class 'rdflib.graph.Graph'>)>, <Graph identifier=urn:x-rdflib:default (<class 'rdflib.graph.Graph'>)>]",
    ]

    # There is one triple in the context, so dataset length == 1
    assert len(ds) == 1
