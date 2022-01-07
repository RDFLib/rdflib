from rdflib import Dataset


def test_issue1396_store_query_and_update_methods_querygraph_parameter_does_not_support_conjunctivegraph_and_dataset_dataset():

    ds = Dataset()

    ds.update(
        "INSERT DATA {<urn:example:tarek> <urn:example:likes> <urn:example:pizza> .}"
    )

    assert len(list(ds.query("SELECT * {?s ?p ?o .}"))) == 1
