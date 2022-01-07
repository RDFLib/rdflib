import pytest
import sys
import os
from rdflib import Dataset
from rdflib.plugins.stores.sparqlstore import SPARQLUpdateStore


sportquadsnq = open(
    os.path.join(
        os.path.dirname(__file__), "..", "..", "consistent_test_data", "sportquads.nq"
    )
).read()


@pytest.mark.skipif(sys.platform == "win32", reason="does not run on windows")
def test_issue167_sparqlupdatestore_parse():

    store = SPARQLUpdateStore(
        query_endpoint="http://localhost:3031/db/sparql",
        update_endpoint="http://localhost:3031/db/update",
    )

    ds = Dataset(store=store)

    assert len(list(ds.contexts())) == 1

    ds.parse(data=sportquadsnq, format="nquads")

    store.update("CLEAR ALL")
