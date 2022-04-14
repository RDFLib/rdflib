from rdflib.graph import DATASET_DEFAULT_GRAPH_ID, Dataset, Graph


def test_issue319_add_graph_as_dataset_default_1():

    ds = Dataset()
    assert len(list(ds.graphs())) == 0

    ds.parse(data="<a> <b> <c>.", format="turtle")

    assert len(ds) == 1
    assert len(list(ds.graphs())) == 0


def test_issue319_add_graph_as_dataset_default_2():

    ds = Dataset()
    assert len(list(ds.graphs())) == 0
    assert len(ds) == 0

    g = Graph(store=ds.store, identifier=DATASET_DEFAULT_GRAPH_ID)

    g.parse(data="<a> <b> <c>.", format="turtle")

    assert len(ds) == 1
    assert len(list(ds.graphs())) == 0
