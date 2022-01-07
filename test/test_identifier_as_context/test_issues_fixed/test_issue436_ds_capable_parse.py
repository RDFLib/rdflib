import os
from rdflib import Dataset


def test_issue436_ds_capable_parse():

    ds = Dataset()

    trigfile = os.path.join(
        os.path.dirname(__file__), "..", "..", "consistent_test_data", "testdata01.trig"
    )

    ds.parse(location=trigfile)  # RDF file type worked out by guess_format()

    assert len(list(ds.quads((None, None, None, None)))) == 4

    assert len(list(ds.contexts())) == 3

    assert "identifier=http://example.org/b/" in str(list(ds.contexts()))
