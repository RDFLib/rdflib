import os


def test_issue436_ds_capable_parse(get_dataset):

    # STATUS: FIXED no longer an issue

    ds = get_dataset
    trigfile = os.path.join(
        os.path.dirname(__file__), "..", "consistent_test_data", "testdata01.trig"
    )
    ds.parse(location=trigfile)  # RDF file type worked out by guess_format()
    assert len(list(ds.quads((None, None, None, None)))) == 2
    assert len(list(ds.contexts())) == 3
    assert (
        str(sorted(list(ds.contexts())))
        == "[<Graph identifier=file:///home/gjh/PyBench/rdflib-github-identifier-as-context/"
        "test/consistent_test_data/testdata01.trig (<class 'rdflib.graph.Graph'>)>, "
        "<Graph identifier=http://example.org/b/ (<class 'rdflib.graph.Graph'>)>, "
        "<Graph identifier=urn:x-rdflib-default (<class 'rdflib.graph.Graph'>)>]"
    )
