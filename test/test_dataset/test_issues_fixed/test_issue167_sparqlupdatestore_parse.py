import os
import sys

import pytest

from rdflib import Dataset
from rdflib.plugins.stores.sparqlstore import SPARQLUpdateStore

sportquadsnq = open(
    os.path.join(
        os.path.dirname(__file__), "..", "..", "consistent_test_data", "sportquads.nq"
    )
).read()


try:
    from urllib.request import urlopen

    assert len(urlopen("http://localhost:3030").read()) > 0
    skip = False
except Exception:
    skip = True


@pytest.mark.skipif(skip, reason="sparql endpoint is unavailable.")
@pytest.mark.skipif(sys.platform == "win32", reason="does not run on windows")
def test_issue167_sparqlupdatestore_parse():

    store = SPARQLUpdateStore(
        query_endpoint="http://localhost:3030/db/sparql",
        update_endpoint="http://localhost:3030/db/update",
    )

    ds = Dataset(store=store)

    try:
        assert len(list(ds.graphs())) == 0
    except Exception:
        store.update("CLEAR ALL")

    ds.parse(data=sportquadsnq, format="nquads")

    store.update("CLEAR ALL")
