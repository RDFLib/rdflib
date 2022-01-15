import os
from rdflib.plugins.sparql import prepareUpdate, prepareQuery
from rdflib.namespace import FOAF
from rdflib import (
    Graph,
    URIRef,
)


def test_prepare_update():

    q = prepareUpdate(
        """\
PREFIX dc: <http://purl.org/dc/elements/1.1/>
INSERT DATA
{ <http://example/book3> dc:title "A new book" ;
                         dc:creator "A.N.Other" .
 } ;
""",
        initNs={},
    )

    g = Graph()
    g.update(q, initBindings={})
    assert len(g) == 2


def test_prepare_query():

    q = prepareQuery(
        "SELECT ?name WHERE { ?person foaf:knows/foaf:name ?name . }",
        initNs={"foaf": FOAF},
    )

    g = Graph()
    g.parse(
        location=os.path.join(os.path.dirname(__file__), "..", "examples", "foaf.n3"),
        format="n3",
    )

    tim = URIRef("http://www.w3.org/People/Berners-Lee/card#i")

    assert len(list(g.query(q, initBindings={"person": tim}))) == 50
