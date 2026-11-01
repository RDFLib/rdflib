from rdflib import Dataset, Graph, Literal, URIRef
from rdflib.compare import isomorphic


def test_nquads_default_graph():
    data = """
        @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
        @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
        @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

        {
            <urn:test> <http://www.w3.org/ns/prov#generatedAtTime> "2012-04-09"^^xsd:date .
        }

        <urn:test> {
            <http://greggkellogg.net/foaf#me> a <http://xmlns.com/foaf/0.1/Person> ;
                <http://xmlns.com/foaf/0.1/knows> "http://manu.sporny.org/about#manu" ;
                <http://xmlns.com/foaf/0.1/name> "Gregg Kellogg" .

            <http://manu.sporny.org/about#manu> a <http://xmlns.com/foaf/0.1/Person> ;
                <http://xmlns.com/foaf/0.1/knows> "http://greggkellogg.net/foaf#me" ;
                <http://xmlns.com/foaf/0.1/name> "Manu Sporny" .
        }
    """

    ds = Dataset()
    ds.parse(data=data, format="trig")
    output = ds.serialize(format="nquads")

    # The internal RDFLib default graph identifier should not appear in the output.
    assert "<urn:x-rdflib:default>" not in output

    # Ensure dataset round-trip still works.
    ds2 = Dataset()
    ds2.parse(data=output, format="nquads")
    for graph in ds.graphs():
        assert isomorphic(graph, ds2.graph(graph.identifier)), print(
            f"{graph.identifier} not isomorphic"
        )


def test_nquads_serializes_plain_graph():
    """N-Quads must accept a non-context-aware Graph (issue #1892)."""
    g = Graph()
    g.add(
        (
            URIRef("http://example.org/s"),
            URIRef("http://example.org/p"),
            Literal("o"),
        )
    )
    data = g.serialize(format="nquads")
    assert "<http://example.org/s>" in data
    assert '"o"' in data
    parsed = Graph()
    parsed.parse(data=data, format="nquads")
    assert len(parsed) == 1


def test_trix_serializes_plain_graph():
    """TriX must accept a non-context-aware Graph (issue #1892)."""
    g = Graph()
    g.add(
        (
            URIRef("http://example.org/s"),
            URIRef("http://example.org/p"),
            Literal("o"),
        )
    )
    data = g.serialize(format="trix")
    assert "http://example.org/s" in data
    parsed = Dataset()
    parsed.parse(data=data, format="trix")
    assert len(parsed) == 1
