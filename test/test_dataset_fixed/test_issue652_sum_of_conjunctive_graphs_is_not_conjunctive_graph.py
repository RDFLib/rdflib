from rdflib import ConjunctiveGraph


def test_issue652_sum_of_conjunctive_graphs_is_not_conjunctive_graph(
    get_conjunctivegraph,
):
    # STATUS: FIXED no longer an issue

    # Sum of conjunctive graphs is not conjunctive graph #652
    g1 = get_conjunctivegraph
    g2 = get_conjunctivegraph

    assert type(g1 + g2) == ConjunctiveGraph
