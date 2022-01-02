import os
import tempfile
import shutil
from rdflib import Dataset, Graph, URIRef
from rdflib.plugins.stores.berkeleydb import BerkeleyDB  # type: ignore


michel = URIRef("urn:michel")
tarek = URIRef("urn:tarek")
likes = URIRef("urn:likes")
hates = URIRef("urn:hates")
pizza = URIRef("urn:pizza")
cheese = URIRef("urn:cheese")

c1 = URIRef("urn:context-1")
c2 = URIRef("urn:context-2")


def test_store_based_creation_of_dataset():

    path = os.path.join(tempfile.gettempdir(), "test_bddbdataset")

    if os.path.exists(path):
        shutil.rmtree(path)

    store = BerkeleyDB(configuration=path)
    store.open(path, create=True)

    g1 = Graph(store=store, identifier=c1)
    g2 = Graph(store=store, identifier=c2)

    g1.add((tarek, likes, pizza))
    g1.add((tarek, likes, cheese))

    g2.add((michel, hates, pizza))
    g2.add((michel, hates, cheese))

    g = Dataset(store=store)

    assert len(list(g.contexts())) == 3
