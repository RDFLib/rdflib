from rdflib import logger, Dataset, Graph, URIRef
from rdflib.plugins.stores.sparqlstore import SPARQLUpdateStore


michel = URIRef("urn:michel")
tarek = URIRef("urn:tarek")
likes = URIRef("urn:likes")
pizza = URIRef("urn:pizza")
cheese = URIRef("urn:cheese")

c1 = URIRef("urn:context-1")
c2 = URIRef("urn:context-2")


def test_issue371_validation_of_quads_at_graph_addN_does_not_work_as_expected():

    # STATUS: FIXED

    # https://github.com/RDFLib/rdflib/issues/167#issuecomment-873620457

    # Note that this is also observed when using Dataset instances. In particular,

    ds = Dataset()

    ds.addN([(tarek, likes, pizza, c1), (michel, likes, cheese, c2)])

    quads = ds.quads((None, None, None, None))  # Fourth term is identifier

    store = SPARQLUpdateStore(
        query_endpoint="http://localhost:3030/db/sparql",
        update_endpoint="http://localhost:3030/db/update",
    )

    store.addN(quads)  # Fourth term is identifier

    store.update("CLEAR ALL")
