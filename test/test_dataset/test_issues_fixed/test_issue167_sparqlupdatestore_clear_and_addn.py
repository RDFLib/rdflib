import sys

import pytest

from rdflib import Dataset, Literal, URIRef
from rdflib.plugins.stores.sparqlstore import SPARQLUpdateStore

list_of_nquads = [
    (
        URIRef("http://example.com/resource/student_10"),
        URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),
        URIRef("http://example.com/ontology/Student"),
        URIRef("http://example.org/graph/students"),
    ),
    (
        URIRef("http://example.com/resource/student_10"),
        URIRef("http://xmlns.com/foaf/0.1/name"),
        Literal("Venus Williams"),
        URIRef("http://example.org/graph/students"),
    ),
    (
        URIRef("http://example.com/resource/student_20"),
        URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),
        URIRef("http://example.com/ontology/Student"),
        URIRef("http://example.org/graph/students"),
    ),
    (
        URIRef("http://example.com/resource/student_20"),
        URIRef("http://xmlns.com/foaf/0.1/name"),
        Literal("Demi Moore"),
        URIRef("http://example.org/graph/students"),
    ),
    (
        URIRef("http://example.com/resource/sport_100"),
        URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),
        URIRef("http://example.com/ontology/Sport"),
        URIRef("http://example.org/graph/sports"),
    ),
    (
        URIRef("http://example.com/resource/sport_100"),
        URIRef("http://www.w3.org/2000/01/rdf-schema#label"),
        Literal("Tennis"),
        URIRef("http://example.org/graph/sports"),
    ),
    (
        URIRef("http://example.com/resource/student_10"),
        URIRef("http://example.com/ontology/practises"),
        URIRef("http://example.com/resource/sport_100"),
        URIRef("http://example.org/graph/practise"),
    ),
]


try:
    from urllib.request import urlopen

    assert len(urlopen("http://localhost:3030").read()) > 0
    skip = False
except Exception:
    skip = True


@pytest.mark.skipif(skip, reason="sparql endpoint is unavailable.")
@pytest.mark.skipif(sys.platform == "win32", reason="does not run on windows")
def test_issue167_sparqlupdatestore_clear():

    store = SPARQLUpdateStore(
        query_endpoint="http://localhost:3030/db/sparql",
        update_endpoint="http://localhost:3030/db/update",
    )

    ds = Dataset(store=store)

    ds.update("CLEAR ALL")

    assert len(list(ds.graphs())) == 0


@pytest.mark.skipif(skip, reason="sparql endpoint is unavailable.")
@pytest.mark.skipif(sys.platform == "win32", reason="does not run on windows")
def test_issue167_sparqlupdatestore_addN():

    store = SPARQLUpdateStore(
        query_endpoint="http://localhost:3030/db/sparql",
        update_endpoint="http://localhost:3030/db/update",
    )

    ds = Dataset(store=store)

    assert len(list(ds.graphs())) == 0

    ds.addN(list_of_nquads)

    assert len(list(ds.graphs())) == 3  # 3 added

    store.update("CLEAR ALL")
