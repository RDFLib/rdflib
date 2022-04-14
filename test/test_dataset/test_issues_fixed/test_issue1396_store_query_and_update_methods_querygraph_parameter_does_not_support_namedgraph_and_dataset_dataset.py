import pytest

from rdflib import Dataset
from rdflib.graph import DATASET_DEFAULT_GRAPH_ID


# @pytest.mark.skip("PENDING SPARQL PROCESSOR CHANGE")
def test_issue1396_store_query_and_update_methods_queryGraph_parameter_does_not_support_namedgraph_and_dataset_dataset():

    ds = Dataset()

    # There are no triples in any context, so dataset length == 0
    assert len(ds) == 0

    # The default graph is not treated as a context
    assert len(list(ds.graphs())) == 0

    # The default graph is not treated as a context
    assert str(list(ds.graphs())) == "[]"

    # only the default graph exists and is properly identified as DATASET_DEFAULT_GRAPH_ID
    assert ds.default_graph.identifier == DATASET_DEFAULT_GRAPH_ID

    assert (
        str(ds.default_graph)
        == "<urn:x-rdflib:default> a rdfg:Graph;rdflib:storage [a rdflib:Store;rdfs:label 'Memory']."
    )

    # INSERT into NAMED GRAPH

    ds.update(
        "INSERT DATA { GRAPH <urn:example:context1> { <urn:example:tarek> <urn:example:hates> <urn:example:pizza> . } }"
    )

    l = list(ds.graphs())

    assert len(list(ds.graphs())) == 1

    # Only the named graph exists as a context and is yielded by ds.graphs()
    assert str(sorted(list(ds.contexts()))) in [
        "[rdflib.term.URIRef('urn:example:context1')]",
    ]

    # No triples have been stored in the default graph, so dataset length == 0
    assert len(ds) == 0
