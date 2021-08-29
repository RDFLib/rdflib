"""
RDFLib Graphs (and Resources) can be "sliced" with [] syntax

This is a short-hand for iterating over triples.

Combined with SPARQL paths (see ``foafpaths.py``) - quite complex queries
can be realised.

See :meth:`rdflib.graph.Graph.__getitem__` for details
"""

from rdflib import Graph, RDF
from rdflib.namespace import FOAF

if __name__ == "__main__":

    graph = Graph()
    graph.load("foaf.n3", format="n3")

    for person in graph[: RDF.type : FOAF.Person]:
        friends = list(graph[person : FOAF.knows * "+" / FOAF.name])
        if friends:
            print(f"{graph.value(person, FOAF.name)}'s circle of friends:")
            for name in friends:
                print(name)
