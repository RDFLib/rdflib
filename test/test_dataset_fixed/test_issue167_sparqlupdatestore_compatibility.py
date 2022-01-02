import pytest
import sys
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


@pytest.mark.skipif(sys.platform == "win32", reason="does not run on windows")
def test_issue167_sparqlupdatestore_compatibility():

    # STATUS: FIXED no longer an issue

    # https://github.com/RDFLib/rdflib/issues/167#issuecomment-873620457

    # Note that this is also observed when using Dataset instances. In particular,

    store = SPARQLUpdateStore(
        query_endpoint="http://localhost:3030/db/sparql",
        update_endpoint="http://localhost:3030/db/update",
    )

    ds = Dataset(store=store)
    # ds.parse(data=sportquadsnq, format="nquads")

    ds.update("CLEAR ALL")

    ds.addN(list_of_nquads)

    # assert (
    #     repr(list(ds.contexts()))
    #     == "[<Graph identifier=http://example.org/graph/students (<class 'rdflib.graph.Graph'>)>, <Graph identifier=http://example.org/graph/practise (<class 'rdflib.graph.Graph'>)>, <Graph identifier=http://example.org/graph/sports (<class 'rdflib.graph.Graph'>)>, <Graph identifier=urn:x-rdflib-default (<class 'rdflib.graph.Graph'>)>]"
    # )

    assert len(list(ds.contexts())) == 4

    # Used to be the case but no longer - fixes

    # Data from fuseki (urn:context-1 from previous update)

    # Dataset size

    # graph name:                           triples:

    # default graph                         0
    # urn:context-1                         1
    # http://example.org/graph/practise     1
    # http://example.org/graph/sports       2
    # http://example.org/graph/students     4
