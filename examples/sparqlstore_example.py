"""
Simple examples showing how to use the SPARQLStore
"""

from rdflib import Graph, URIRef, Namespace
from rdflib.plugins.stores.sparqlstore import SPARQLStore

if __name__ == "__main__":

    dbo = Namespace("http://dbpedia.org/ontology/")

    # EXAMPLE 1: using a Graph with the Store type string set to "SPARQLStore"
    graph = Graph("SPARQLStore", identifier="http://dbpedia.org")
    graph.open("http://dbpedia.org/sparql")

    pop = graph.value(URIRef("http://dbpedia.org/resource/Berlin"), dbo.populationTotal)

    print(
        "According to DBPedia, Berlin has a population of {0:,}".format(
            int(pop)
        ).replace(",", ".")
    )
    print()

    # EXAMPLE 2: using a SPARQLStore object directly
    st = SPARQLStore(query_endpoint="http://dbpedia.org/sparql")

    for p in st.objects(
        URIRef("http://dbpedia.org/resource/Brisbane"), dbo.populationTotal
    ):
        print(
            "According to DBPedia, Brisbane has a population of "
            "{0:,}".format(int(p), ",d")
        )
    print()

    # EXAMPLE 3: doing RDFlib triple navigation using SPARQLStore as a Graph()
    print("Triple navigation using SPARQLStore as a Graph():")
    graph = Graph("SPARQLStore", identifier="http://dbpedia.org")
    graph.open("http://dbpedia.org/sparql")
    # we are asking DBPedia for 3 skos:Concept instances
    count = 0
    from rdflib.namespace import RDF, SKOS

    for s in graph.subjects(predicate=RDF.type, object=SKOS.Concept):
        count += 1
        print(f"\t- {s}")
        if count >= 3:
            break

    # EXAMPLE 4: using a SPARQL endpoint that requires Basic HTTP authentication
    # NOTE: this example won't run since the endpoint isn't live (or real)
    s = SPARQLStore(
        query_endpoint="http://fake-sparql-endpoint.com/repository/x",
        auth=("my_username", "my_password"),
    )
    # do normal Graph things
