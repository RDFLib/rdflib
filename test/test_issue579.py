# test for https://github.com/RDFLib/rdflib/issues/579

from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import FOAF, RDF

def test_issue579():
    g = Graph()
    g.bind('foaf', FOAF)
    n = Namespace("http://myname/")
    g.add((n.bob, FOAF.name, Literal('bb')))
    # query is successful.
    assert len(g.query("select ?n where { ?n foaf:name 'bb' . }")) == 1
    # update is not.
    g.update("delete where { ?e foaf:name 'ss' .}")
    assert len(g) == 1
    g.update("delete where { ?e foaf:name 'bb' .}")
    assert len(g) == 0
