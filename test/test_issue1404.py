from rdflib import Graph, URIRef, FOAF
from rdflib.term import RDFLibGenid
from rdflib.compare import isomorphic


def test_skolem_de_skolem_roundtrip():
    """Test round-trip of skolemization/de-skolemization of data.

    Issue: https://github.com/RDFLib/rdflib/issues/1404
    """

    ttl = '''
    @prefix wd: <http://www.wikidata.org/entity/> .
    @prefix foaf: <http://xmlns.com/foaf/0.1/> .

    wd:Q1203 foaf:knows [ a foaf:Person;
        foaf:name "Ringo" ].
    '''

    graph = Graph()
    graph.parse(data=ttl, format='turtle')

    query = {"subject": URIRef("http://www.wikidata.org/entity/Q1203"), "predicate": FOAF.knows}

    # Save the original bnode id.
    bnode_id = graph.value(**query)

    skolemized_graph = graph.skolemize()

    # Check the BNode is now an RDFLibGenid after skolemization.
    skolem_bnode = skolemized_graph.value(**query)
    assert type(skolem_bnode) == RDFLibGenid

    # Check that the original bnode id exists somewhere in the uri.
    assert bnode_id in skolem_bnode

    # Check that the original data is not isomorphic with the skolemized data.
    assert not isomorphic(graph, skolemized_graph)

    # Check that the original graph data is the same as the de-skolemized data.
    de_skolemized_graph = skolemized_graph.de_skolemize()
    assert isomorphic(graph, de_skolemized_graph)
