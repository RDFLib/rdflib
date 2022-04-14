"""
An RDFLib Dataset is a means of working with a set of Named Graphs
within a Store. The :meth:`~rdflib.graph.Dataset.graph`
method can be used to get a particular named graph for use, such as to add
triples to, or the default graph can be used.

This example shows how to create Named Graphs and work with the
conjunction (union) of all the graphs.
"""

from rdflib import Namespace, Literal, URIRef, logger
from rdflib.graph import Graph, Dataset
from rdflib.plugins.stores.memory import Memory


def test_dataset_example():

    LOVE = Namespace("http://love.com#")
    LOVERS = Namespace("http://love.com/lovers/")

    mary = URIRef("http://love.com/lovers/mary")
    john = URIRef("http://love.com/lovers/john")

    cmary = URIRef("http://love.com/lovers/mary")
    cjohn = URIRef("http://love.com/lovers/john")

    store = Memory()

    g = Dataset(store=store, default_union=True)
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
    logger.debug("Contexts:")
    for c in g.contexts():
        logger.debug(f"-- {c} ")
    logger.debug("===================")
    # Separate graphs
    logger.debug("John's Graph:")
    logger.debug(gjohn.serialize())
    logger.debug("===================")
    logger.debug("Mary's Graph:")
    logger.debug(gmary.serialize())
    logger.debug("===================")

    logger.debug("Full Graph")
    logger.debug(g.serialize())
    logger.debug("===================")

    logger.debug("Query the conjunction of all graphs:")
    xx = None
    for x in g[mary : LOVE.loves / LOVE.hasCuteName]:
        xx = x
    logger.debug("Q: Who does Mary love?")
    logger.debug("A: Mary loves {}".format(xx))
