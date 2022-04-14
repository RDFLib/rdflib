import pytest

from rdflib import Dataset, URIRef


def test_issue301_dataset_does_not_parse():

    dataset = Dataset()

    g = dataset.parse(
        data="<a:a> <b:b> <c:c> .", format="turtle", publicID=URIRef("g:g")
    )

    assert type(g) is Dataset

    assert g == dataset.graph(g.identifier)

    assert g.identifier == dataset.default_graph.identifier

    assert str(list(dataset.contexts())) == "[rdflib.term.URIRef('g:g')]"

    assert len(list(dataset.graphs())) == 1

    # NB, default context does not contain statement
    assert len(dataset) == 0

    # The returned g is the dataset
    assert len(g) == 0

    # The statement is in the context URIRef("g:g")
    assert len(dataset.graph(URIRef("g:g"))) == 1
