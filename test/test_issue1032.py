from rdflib import Graph
graph = Graph(store="SPARQLStore")
graph.update("insert data {graph <urn:ex> {<urn:s> <urn:p> <urn:o>}}")