import pytest

from rdflib.graph import Dataset


def test_issue1396_store_query_and_update_methods_querygraph_parameter_does_not_support_dataset_default_union_false():

    cg = Dataset()

    assert list(cg.graphs()) == []

    assert cg.default_union is not True

    cg.default_union = False

    assert cg.default_union is False

    cg.update(
        "INSERT DATA {<urn:example:tarek> <urn:example:likes> <urn:example:pizza> .}"
    )

    assert len(list(cg.query("SELECT * {?s ?p ?o .}"))) == 1


def test_issue1396_store_query_and_update_methods_querygraph_parameter_does_not_support_dataset_default_union():

    cg = Dataset(default_union=True)

    assert list(cg.graphs()) == []

    assert cg.default_union is True

    cg.default_union = False

    assert cg.default_union is False

    cg.update(
        "INSERT DATA {<urn:example:tarek> <urn:example:likes> <urn:example:pizza> .}"
    )

    assert len(list(cg.query("SELECT * {?s ?p ?o .}"))) == 1
