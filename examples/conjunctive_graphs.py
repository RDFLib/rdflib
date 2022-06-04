"""
An RDFLib ConjunctiveGraph is an (unnamed) aggregation of all the Named Graphs
within a Store. The :meth:`~rdflib.graph.ConjunctiveGraph.get_context`
method can be used to get a particular named graph for use, such as to add
triples to, or the default graph can be used.

This example shows how to create Named Graphs and work with the
conjunction (union) of all the graphs.
"""

from rdflib import Namespace, Literal, URIRef
from rdflib.graph import Graph, ConjunctiveGraph
from rdflib.plugins.stores.memory import Memory

if __name__ == "__main__":

    LOVE = Namespace("http://love.com#")
    LOVERS = Namespace("http://love.com/lovers/")

    mary = URIRef("http://love.com/lovers/mary")
    john = URIRef("http://love.com/lovers/john")

    cmary = URIRef("http://love.com/lovers/mary")
    cjohn = URIRef("http://love.com/lovers/john")

    store = Memory()

    g = ConjunctiveGraph(store=store)
    g.bind("love", LOVE)
    g.bind("lovers", LOVERS)

    # Add a graph containing Mary's facts to the Conjunctive Graph
    gmary = Graph(store=store, identifier=cmary)
    # Mary's graph only contains the URI of the person she loves, not his cute name
    gmary.add((mary, LOVE.hasName, Literal("Mary")))
    gmary.add((mary, LOVE.loves, john))

    # Add a graph containing John's facts to the Conjunctive Graph
    gjohn = Graph(store=store, identifier=cjohn)
    # John's graph contains his cute name
    gjohn.add((john, LOVE.hasCuteName, Literal("Johnny Boy")))

    # Enumerate contexts
    print("Contexts:")
    for c in g.contexts():
        print(f"-- {c.identifier} ")
    print("===================")
    # Separate graphs
    print("John's Graph:")
    print(gjohn.serialize())
    print("===================")
    print("Mary's Graph:")
    print(gmary.serialize())
    print("===================")

    print("Full Graph")
    print(g.serialize())
    print("===================")

    print("Query the conjunction of all graphs:")
    xx = None
    for x in g[mary : LOVE.loves / LOVE.hasCuteName]:
        xx = x
    print("Q: Who does Mary love?")
    print("A: Mary loves {}".format(xx))
