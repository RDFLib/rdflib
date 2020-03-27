"""
A simple example showing how to use the SPARQLStore
"""

import locale
from rdflib import Graph, URIRef, Namespace
from rdflib.plugins.stores.sparqlstore import SPARQLStore

if __name__ == "__main__":

    dbo = Namespace("http://dbpedia.org/ontology/")

    # using a Graph with the Store type string set to "SPARQLStore"
    graph = Graph("SPARQLStore", identifier="http://dbpedia.org")
    graph.open("http://dbpedia.org/sparql")

    pop = graph.value(
        URIRef("http://dbpedia.org/resource/Berlin"),
        dbo.populationTotal)

    print("According to DBPedia, Berlin has a population of {0:,}".format(int(pop), ',d').replace(",", "."))

    # using a SPARQLStore object directly
    s = SPARQLStore(endpoint="http://dbpedia.org/sparql")
    s.open(None)
    pop = graph.value(
        URIRef("http://dbpedia.org/resource/Brisbane"),
        dbo.populationTotal)
    print("According to DBPedia, Brisbane has a population of " "{0:,}".format(int(pop), ',d'))
