"""
Simple examples showing how to use the SPARQLStore
"""

import sys
from urllib.request import urlopen

from rdflib import Graph, Namespace, URIRef
from rdflib.namespace import RDF, SKOS
from rdflib.plugins.stores.sparqlstore import SPARQLStore, SPARQLUpdateStore
from rdflib.term import Identifier, Literal

# Shows examples of the useage of SPARQLStore and SPARQLUpdateStore against local SPARQL1.1 endpoint if
# available. This assumes SPARQL1.1 query/update endpoints running locally at
# http://localhost:3030/db/
#
# It uses the same endpoint as the test_dataset.py!
#
# For the tests here to run, you can for example start fuseki with:
# ./fuseki-server --mem --update /db

# THIS WILL ADD DATA TO THE /db dataset


HOST = "http://localhost:3030"

if __name__ == "__main__":
    try:
        assert len(urlopen(HOST).read()) > 0
    except Exception:
        print(f"{HOST} is unavailable.")
        sys.exit(126)

    dbo = Namespace("http://dbpedia.org/ontology/")
    dbr = Namespace("http://dbpedia.org/resource/")

    # EXAMPLE Update Store:
    update_store = SPARQLUpdateStore(
        query_endpoint="http://localhost:3030/db/sparql",
        update_endpoint="http://localhost:3030/db/update",
    )
    graph = Graph(store=update_store, identifier="http://dbpedia.org")
    graph.add((dbr.Berlin, dbo.populationTotal, Literal(3)))
    graph.add((dbr.Brisbane, dbo.populationTotal, Literal(2)))
    graph.add((dbr["Category:Capitals_in_Europe"], RDF.type, SKOS.Concept))
    graph.add((dbr["Category:Holy_Grail"], RDF.type, SKOS.Concept))
    graph.add((dbr["Category:Hospital_ships_of_Japan"], RDF.type, SKOS.Concept))

    # EXAMPLE Store 1: using a Graph with the Store type string set to "SPARQLStore"
    graph = Graph("SPARQLStore", identifier="http://dbpedia.org")
    graph.open("http://localhost:3030/db/sparql")

    pop = graph.value(URIRef("http://dbpedia.org/resource/Berlin"), dbo.populationTotal)
    assert isinstance(pop, Identifier)

    print(
        "According to DBPedia, Berlin has a population of {0:,}".format(
            int(pop)
        ).replace(",", ".")
    )
    print()

    # EXAMPLE Query 2: using a SPARQLStore object directly
    st = SPARQLStore(query_endpoint="http://localhost:3030/db/sparql")

    for p in st.objects(
        URIRef("http://dbpedia.org/resource/Brisbane"), dbo.populationTotal
    ):
        assert isinstance(p, Identifier)
        print("According to DBPedia, Brisbane has a population of {0}".format(int(p)))
    print()

    # EXAMPLE Query 3: doing RDFlib triple navigation using SPARQLStore as a Graph()
    print("Triple navigation using SPARQLStore as a Graph():")
    graph = Graph("SPARQLStore", identifier="http://dbpedia.org")
    graph.open("http://localhost:3030/db/sparql")
    # we are asking DBPedia for 3 skos:Concept instances
    count = 0

    for s in graph.subjects(predicate=RDF.type, object=SKOS.Concept):
        count += 1
        print(f"\t- {s}")
        if count >= 3:
            break

    # EXAMPLE Query 4: doing RDFlib triple navigation using a Graph() with a SPARQLStore backend
    print("Triple navigation using a Graph() with a SPARQLStore backend:")
    st = SPARQLStore(query_endpoint="http://localhost:3030/db/sparql")
    graph = Graph(store=st)
    # we are asking DBPedia for 3 skos:Concept instances
    count = 0

    for s in graph.subjects(predicate=RDF.type, object=SKOS.Concept):
        count += 1
        print(f"\t- {s}")
        if count >= 3:
            break

    # EXAMPLE Store 5: using a SPARQL endpoint that requires Basic HTTP authentication
    # NOTE: this example won't run since the endpoint isn't live (or real)
    sparql_store = SPARQLStore(
        query_endpoint="http://fake-sparql-endpoint.com/repository/x",
        auth=("my_username", "my_password"),
    )
    # do normal Graph things
