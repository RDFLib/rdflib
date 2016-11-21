"""

A simple example showing how to use the SPARQLStore

"""

from rdflib import Graph, URIRef, Namespace

if __name__ == '__main__':

    dbo = Namespace('http://dbpedia.org/ontology/')

    graph = Graph('SPARQLStore', identifier="http://dbpedia.org")

    graph.open("http://dbpedia.org/sparql")


    pop = graph.value(
        URIRef("http://dbpedia.org/resource/Berlin"),
        dbo.populationTotal)

    print(graph.store.queryString)

    print("According to DBPedia Berlin has a population of", pop)
