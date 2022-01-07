from rdflib import ConjunctiveGraph


def test_issue1396_store_query_and_update_methods_querygraph_parameter_does_not_support_conjunctivegraph_and_dataset_conjunctivegraph_default_union_true():

    cg = ConjunctiveGraph()

    assert list(cg.contexts()) == []

    assert cg.default_union is True

    cg.update(
        "INSERT DATA {<urn:example:tarek> <urn:example:likes> <urn:example:pizza> .}"
    )

    assert len(list(cg.query("SELECT * {?s ?p ?o .}"))) == 1


def test_issue1396_store_query_and_update_methods_querygraph_parameter_does_not_support_conjunctivegraph_and_dataset_conjunctivegraph_default_union_false():

    cg = ConjunctiveGraph()

    assert list(cg.contexts()) == []

    assert cg.default_union is True

    cg.default_union = False

    assert cg.default_union is False

    cg.update(
        "INSERT DATA {<urn:example:tarek> <urn:example:likes> <urn:example:pizza> .}"
    )

    assert len(list(cg.query("SELECT * {?s ?p ?o .}"))) == 1
