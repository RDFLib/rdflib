import re
from rdflib.graph import DATASET_DEFAULT_GRAPH_ID


def test_issue1396_store_query_and_update_methods_queryGraph_parameter_does_not_support_conjunctivegraph_and_dataset_conjunctivegraph(
    get_conjunctivegraph,
):

    # STATUS: FIXED no longer an issue

    cg = get_conjunctivegraph

    # There are no triples in any context, so dataset length == 0
    assert len(cg) == 0

    # The default graph is a context so the length of ds.contexts() == 1
    assert len(list(cg.contexts())) == 0

    assert repr(list(cg.contexts())) == "[]"

    cg.update("INSERT DATA { <urn:tarek> <urn:hates> <urn:pizza> . }")

    assert len(list(cg.contexts())) == 1

    assert re.match(
        r"\[<Graph identifier=N(.*?) \(<class 'rdflib\.graph\.Graph'>\)>]",
        str(list(cg.contexts())),
    )

    # There is one triple in the context, so graph length == 1
    assert len(cg) == 1
