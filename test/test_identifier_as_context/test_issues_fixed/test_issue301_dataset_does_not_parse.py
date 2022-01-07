from rdflib import Dataset, URIRef


def test_issue301_dataset_does_not_parse():

    dataset = Dataset()

    g = dataset.parse(
        data="<a:a> <b:b> <c:c> .", format="turtle", publicID=URIRef("g:g")
    )

    assert str(type(g)) == "<class 'rdflib.graph.Graph'>"

    assert g == dataset.get_context(g.identifier)

    assert g in list(dataset.graphs())
