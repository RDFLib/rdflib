from rdflib import SDO, RDFS, URIRef
from rdflib.plugins import sparql as rdflib_sparql_module


def test_issue1275_clear_default(get_conjunctivegraph):

    # STATUS: FIXED no longer an issue if SPARQL_DEFAULT_GRAPH_UNION = False

    # CLEAR DEFAULT statement erases named graphs #1275
    # DEFAULT graph is the default unnamed graph, so the triple we store
    # in the named graph before should not be removed, but it apparently is.

    graph = get_conjunctivegraph

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
