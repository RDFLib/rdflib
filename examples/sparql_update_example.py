"""
SPARQL Update statements can be applied with :meth:`rdflib.graph.Graph.update`
"""

import rdflib

if __name__ == "__main__":

    g = rdflib.Graph()
    g.load("foaf.n3", format="n3")

    print(f"Initially there are {len(g)} triples in the graph")

    g.update(
        """
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        PREFIX dbpedia: <http://dbpedia.org/resource/>
        INSERT { 
            ?s a dbpedia:Human . 
        }
        WHERE {
            ?s a foaf:Person .
        }
        """
    )

    print(f"After the UPDATE, there are {len(g)} triples in the graph")
