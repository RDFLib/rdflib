from rdflib.graph import DATASET_DEFAULT_GRAPH_ID


def test_issue1396_store_query_and_update_methods_queryGraph_parameter_does_not_support_conjunctivegraph_and_dataset_dataset(
    get_dataset,
):
    # STATUS: FIXED no longer an issue - probably

    ds = get_dataset

    # There are no triples in any context, so dataset length == 0
    assert len(ds) == 0

    # The default graph is a context so the length of ds.contexts() == 1
    assert len(list(ds.contexts())) == 1

    # Only the default graph exists and is yielded by ds.contexts()
    assert (
        repr(list(ds.contexts()))
        == "[<Graph identifier=urn:x-rdflib-default (<class 'rdflib.graph.Graph'>)>]"
    )

    # only the default graph exists and is properly identified as DATASET_DEFAULT_GRAPH_ID
    assert set(x.identifier for x in ds.contexts()) == set([DATASET_DEFAULT_GRAPH_ID])

    dataset_default_graph = ds.get_context(DATASET_DEFAULT_GRAPH_ID)
    # logger.debug(f"\n\nDATASET_DEFAULT_GRAPH\n{repr(dataset_default_graph)}")
    assert (
        repr(dataset_default_graph)
        == "<Graph identifier=urn:x-rdflib-default (<class 'rdflib.graph.Graph'>)>"
    )

    ds.update("INSERT DATA { <urn:tarek> <urn:hates> <urn:pizza> . }")

    assert len(list(ds.contexts())) == 1

    # Only the default graph exists and is yielded by ds.contexts()
    assert (
        repr(list(ds.contexts()))
        == "[<Graph identifier=urn:x-rdflib-default (<class 'rdflib.graph.Graph'>)>]"
    )

    # There is one triple in the context, so dataset length == 1
    assert len(ds) == 1
