import pytest
import os
import shutil
import tempfile
from rdflib import (
    Dataset,
    URIRef,
)

michel = URIRef("urn:example:michel")
tarek = URIRef("urn:example:tarek")
bob = URIRef("urn:example:bob")
likes = URIRef("urn:example:likes")
hates = URIRef("urn:example:hates")
pizza = URIRef("urn:example:pizza")
cheese = URIRef("urn:example:cheese")

c1 = URIRef("urn:example:context-1")
c2 = URIRef("urn:example:context-2")


@pytest.fixture(
    # scope="function", params=["default", "BerkeleyDB", "SQLiteLSM", "LevelDB", "SQLAlchemy"]
    scope="function",
    params=["default"],
)
def get_dataset(request):
    store = request.param
    tmppath = os.path.join(tempfile.gettempdir(), f"test_{store.lower()}")
    dataset = Dataset(store=store)
    dataset.open(tmppath, create=True)
    # tmppath = mkdtemp()
    if store != "default" and dataset.store.is_open():
        # delete the graph for each test!
        dataset.remove((None, None, None))
        for c in dataset.contexts():
            c.remove((None, None, None))
            assert len(c) == 0
            dataset.remove_graph(c)
    # logger.debug(f"Using store {dataset.store}")

    yield dataset

    dataset.close()
    if os.path.isdir(tmppath):
        shutil.rmtree(tmppath)
    else:
        try:
            os.remove(tmppath)
        except Exception:
            pass
