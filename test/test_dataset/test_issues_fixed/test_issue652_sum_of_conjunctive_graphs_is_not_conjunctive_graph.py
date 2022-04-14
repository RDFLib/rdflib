from rdflib import Dataset


def test_issue652_sum_of_conjunctive_graphs_is_not_conjunctive_graph():

    # Sum of conjunctive graphs is not conjunctive graph #652
    g1 = Dataset()
    g2 = Dataset()

    assert type(g1 + g2) == Dataset
