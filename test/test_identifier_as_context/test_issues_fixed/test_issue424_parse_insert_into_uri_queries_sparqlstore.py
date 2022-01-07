import pytest
from rdflib.plugins.stores.sparqlstore import SPARQLUpdateStore


try:
    from urllib.request import urlopen

    assert len(urlopen("http://localhost:3030").read()) > 0
    skip = False
except Exception:
    skip = True


@pytest.mark.skipif(skip, reason="sparql endpoint is unavailable.")
def test_issue424_parse_insert_into_uri_queries_sparqlstore():

    store = SPARQLUpdateStore(
        query_endpoint="http://localhost:3030/db/sparql",
        update_endpoint="http://localhost:3030/db/update",
    )

    store.update(
        "INSERT DATA { GRAPH <urn:example:context-1> { <urn:example:tarek> <urn:example:likes> <urn:example:pizza> } }"
    )

    assert len(store) == 0

    assert (
        len(
            list(
                store.query(
                    """SELECT ?s ?p ?o WHERE {GRAPH <urn:example:context-1> { ?s ?p ?o }}"""
                )
            )
        )
        == 1  # noqa: W503
    )
