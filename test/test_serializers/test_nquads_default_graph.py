from rdflib import Dataset
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

    print("\n+++++")
    ds = Dataset().parse(data=data, format="trig")
    for graph in ds.graphs():
        print(graph.identifier, len(graph))

    # The internal RDFLib default graph identifier should not appear in serialized output
    nq = ds.serialize(format="nquads")

    print("+++++")
    # Ensure dataset round-trip still works
    ds2 = Dataset().parse(data=nq, format="nquads")
    for graph in ds2.graphs():
        print(graph.identifier, len(graph))
    print("+++++")

    print("\n")
    for graph in ds.graphs():
        print(graph.identifier, len(graph), " | ", ds2.graph(graph.identifier).identifier, len(ds2.graph(graph.identifier)))

        # if len(graph) != len(ds2.graph(graph.identifier)):
        #     print("\n====")
        #     print(graph.serialize())
        #     print("====")
        #     print(ds2.graph(graph.identifier).serialize())
        #     print("====")
        # assert isomorphic(graph, ds2.graph(graph.identifier)), print(
        #     f"{graph.identifier} not isomorphic"
        # )
