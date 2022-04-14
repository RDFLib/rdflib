import os
import shutil
import tempfile

import pytest

from rdflib import Dataset, URIRef, plugin

"""
Just a fixture template for iterating over plugin stores
"""


def get_plugin_stores():
    pluginstores = []

    for s in plugin.plugins(None, plugin.Store):
        if s.name in (
            "default",
            "Memory",
            "Auditable",
            "Concurrent",
            "SimpleMemory",
            "SPARQLStore",
            "SPARQLUpdateStore",
            "BerkeleyDB",
            "LevelDB",
            "SQLiteLSM",
            "SQLiteDBStore",
        ):
            continue  # exclude store from test

        pluginstores.append(s.name)
    return pluginstores


@pytest.fixture(
    scope="function",
    params=get_plugin_stores(),
)
def get_dataset(request):
    store = request.param
    # TBD create according to different Store requirements
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
