from rdflib import Dataset, URIRef


def test_query_on_ds_yields_no_results():

    data = """
    <http://data.yyx.me/jack> <http://onto.yyx.me/work_for> <http://data.yyx.me/company_a> .
    <http://data.yyx.me/david> <http://onto.yyx.me/work_for> <http://data.yyx.me/company_b> .
    """

    ds = Dataset()

    g = ds.add_graph(URIRef("subgraph"))

    g.parse(data=data, format="n3")

    # yields 2 results from this query
    assert (
        len(list(ds.query("""SELECT ?s ?p ?o WHERE {GRAPH <subgraph> { ?s ?p ?o }}""")))
        == 2  # noqa: W503
    )

    # also yields 2 results from this query
    assert (
        len(list(ds.query("""SELECT ?g ?s ?p ?o WHERE { GRAPH ?g { ?s ?p ?o }}""")))
        == 2  # noqa: W503
    )
