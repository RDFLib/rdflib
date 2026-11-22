from rdflib import Graph
from rdflib.term import BNode, URIRef, rdflib_skolem_genid


def test():
    """Test skolemised URI query retrieves expected results.

    Issue: https://github.com/RDFLib/rdflib/issues/1808
    """

    g = Graph()
    g.parse(data='[] <urn:prop> "val" .', format="turtle")
    for s, p, o in g:
        assert isinstance(s, BNode)

    gs = g.skolemize()
    for s, p, o in gs:
        assert isinstance(s, URIRef) and s.__contains__(rdflib_skolem_genid)

    query_with_iri = "select ?p ?o {{ <{}> ?p ?o }}".format(s)
    query_for_all = "select ?s ?p ?o { ?s ?p ?o }"

    count = 0
    for row in gs.query(query_with_iri):
        count += 1
    assert count == 1

    count = 0
    for row in gs.query(query_for_all):
        count += 1
    assert count == 1

    gp = Graph()
    gp.parse(data=gs.serialize(format="turtle"), format="turtle")

    count = 0
    for row in gp.query(query_with_iri):
        count += 1
    assert count == 1

    count = 0
    for row in gp.query(query_for_all):
        count += 1
    assert count == 1
