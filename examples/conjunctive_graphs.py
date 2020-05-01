"""
An RDFLib ConjunctiveGraph is an (unnamed) aggregation of all the named graphs
within a Store. The :meth:`~rdflib.graph.ConjunctiveGraph.get_context`
method can be used to get a particular named graph for use such as to add
triples to, or the default graph can be used

This example shows how to create named graphs and work with the
conjunction (union) of all the graphs.
"""

from rdflib import Namespace, Literal, URIRef
from rdflib.graph import Graph, ConjunctiveGraph
from rdflib.plugins.memory import IOMemory

if __name__ == "__main__":

    ns = Namespace("http://love.com#")

    mary = URIRef("http://love.com/lovers/mary")
    john = URIRef("http://love.com/lovers/john")

    cmary = URIRef("http://love.com/lovers/mary")
    cjohn = URIRef("http://love.com/lovers/john")

    store = IOMemory()

    g = ConjunctiveGraph(store=store)
    g.bind("love", ns)

    # add a graph for Mary's facts to the Conjunctive Graph
    gmary = Graph(store=store, identifier=cmary)
    # Mary's graph only contains the URI of the person she love, not his cute name
    gmary.add((mary, ns["hasName"], Literal("Mary")))
    gmary.add((mary, ns["loves"], john))

    # add a graph for Mary's facts to the Conjunctive Graph
    gjohn = Graph(store=store, identifier=cjohn)
    # John's graph contains his cute name
    gjohn.add((john, ns["hasCuteName"], Literal("Johnny Boy")))

    # enumerate contexts
    for c in g.contexts():
        print("-- %s " % c)

    # separate graphs
    print(gjohn.serialize(format="n3").decode("utf-8"))
    print("===================")
    print(gmary.serialize(format="n3").decode("utf-8"))
    print("===================")

    # full graph
    print(g.serialize(format="n3").decode("utf-8"))

    # query the conjunction of all graphs
    xx = None
    for x in g[mary: ns.loves / ns.hasCuteName]:
        xx = x
    print("Q: Who does Mary love?")
    print("A: Mary loves {}".format(xx))
