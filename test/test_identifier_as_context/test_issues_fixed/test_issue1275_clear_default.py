from rdflib import ConjunctiveGraph, SDO, RDFS, URIRef
from rdflib.plugins import sparql as rdflib_sparql_module


def test_issue1275_clear_default():

    graph = ConjunctiveGraph()

    graph.add(
        (
            SDO.title,
            RDFS.subPropertyOf,
            RDFS.label,
            URIRef("https://example.org"),
        )
    )

    rdflib_sparql_module.SPARQL_DEFAULT_GRAPH_UNION = False

    assert list(graph)

    graph.update("CLEAR DEFAULT")

    assert (
        str(list(graph))
        == "[(rdflib.term.URIRef('https://schema.org/title'), rdflib.term.URIRef('http://www.w3.org/2000/01/rdf-schema#subPropertyOf'), rdflib.term.URIRef('http://www.w3.org/2000/01/rdf-schema#label'))]"
    )
