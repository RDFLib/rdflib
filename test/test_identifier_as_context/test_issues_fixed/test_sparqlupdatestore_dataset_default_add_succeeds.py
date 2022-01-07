from rdflib import Dataset, URIRef
from rdflib.graph import DATASET_DEFAULT_GRAPH_ID


tarek = URIRef("urn:example:tarek")
likes = URIRef("urn:example:likes")
pizza = URIRef("urn:example:pizza")


def test_sparqlupdatestore_dataset_default_add_succeeds():
    ds = Dataset(store="SPARQLUpdateStore")
    ds.open(
        configuration=(
            "http://localhost:3031/db/sparql",
            "http://localhost:3031/db/update",
        )
    )
    ds.add((tarek, likes, pizza))

    assert len(ds) == 0

    g = ds.get_context(DATASET_DEFAULT_GRAPH_ID)

    assert len(g) == 1

    ds.update("CLEAR ALL")
