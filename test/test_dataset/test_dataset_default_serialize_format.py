from rdflib import Dataset
from test.data import TEST_DATA_DIR


def test_dataset_default_serialize_format_trig():
    ds = Dataset()
    ds.parse(source=TEST_DATA_DIR / "nquads.rdflib" / "test5.nquads", format="nquads")
    statements_count = len(ds)
    assert statements_count

    # Previously, when the default format is 'turtle', given that the dataset has no
    # statements in the default graph, the output of serialize() was empty.
    output = ds.serialize().strip()
    assert output != ""

    ds2 = Dataset()
    ds2.parse(data=output, format="trig")
    assert len(ds2) == statements_count
