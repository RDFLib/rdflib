from rdflib import ConjunctiveGraph


def test_issue319_add_graph_as_conjunctivegraph_default():

    cg = ConjunctiveGraph()
    assert len(list(cg.contexts())) == 0

    cg.parse(data="<a> <b> <c>.", format="turtle")

    assert len(list(cg.contexts())) == 1
