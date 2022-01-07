from rdflib import ConjunctiveGraph


def test_issue652_sum_of_conjunctive_graphs_is_not_conjunctive_graph():

    # Sum of conjunctive graphs is not conjunctive graph #652
    g1 = ConjunctiveGraph()
    g2 = ConjunctiveGraph()

    assert type(g1 + g2) == ConjunctiveGraph
