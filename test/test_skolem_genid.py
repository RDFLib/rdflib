from rdflib import RDF, SDO, BNode, Graph, URIRef
from rdflib.term import _Deskolemizer


def test_skolem_genid_and_rdflib_genid():
    rdflib_genid = URIRef(
        "https://rdflib.github.io/.well-known/genid/rdflib/N97c39b957bc444949a82793519348dc2"
    )
    custom_genid = URIRef(
        "http://example.com/.well-known/genid/example/Ne864c0e3684044f381d518fdac652f2e"
    )

    _deskolemizer = _Deskolemizer()
    rdflib_bnode = _deskolemizer(rdflib_genid)
    assert isinstance(rdflib_bnode, BNode)
    assert rdflib_bnode.n3() == "_:N97c39b957bc444949a82793519348dc2"

    custom_bnode = _deskolemizer(custom_genid)
    assert isinstance(custom_bnode, BNode)
    assert custom_bnode.n3().startswith("_:")


def test_graph_de_skolemize():
    graph = Graph()

    rdflib_genid = URIRef(
        "https://rdflib.github.io/.well-known/genid/rdflib/N97c39b957bc444949a82793519348dc2"
    )
    custom_genid = URIRef(
        "http://example.com/.well-known/genid/example/Ne864c0e3684044f381d518fdac652f2e"
    )

    rdflib_statement = (rdflib_genid, RDF.type, SDO.Thing)
    custom_statement = (custom_genid, RDF.type, SDO.Person)

    graph.add(rdflib_statement)
    graph.add(custom_statement)
    graph = graph.de_skolemize(uriref=rdflib_genid)

    assert rdflib_statement not in graph
    assert (BNode("N97c39b957bc444949a82793519348dc2"), RDF.type, SDO.Thing) in graph
    assert custom_statement in graph

    graph = graph.de_skolemize(uriref=custom_genid)
    assert custom_statement not in graph
    assert isinstance(graph.value(predicate=RDF.type, object=SDO.Person), BNode)
