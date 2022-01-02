from rdflib import Graph


def test_issue000_query_on_ds_yields_no_results(get_dataset):

    # STATUS: FIXED no longer an issue

    data = """
    <http://data.yyx.me/jack> <http://onto.yyx.me/work_for> <http://data.yyx.me/company_a> .
    <http://data.yyx.me/david> <http://onto.yyx.me/work_for> <http://data.yyx.me/company_b> .
    """

    ds = get_dataset
    g = Graph(identifier="subgraph")
    g.parse(data=data, format="n3")
    ds.add_graph(g)

    # yields 2 results from this query
    assert (
        len(list(ds.query("""SELECT ?s ?p ?o WHERE {GRAPH <subgraph> { ?s ?p ?o }}""")))
        == 2  # noqa: W503
    )

    # yields 2 results from this query
    assert (
        len(list(ds.query("""SELECT ?g ?s ?p ?o WHERE { GRAPH ?g { ?s ?p ?o }}""")))
        == 2  # noqa: W503
    )
