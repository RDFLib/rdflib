from rdflib import Dataset, Graph


def test_issue698_len_ds():
    """

    # STATUS: FIXED no longer an issue

    Dataset.graph should not allow adding random graphs to the store #698
    gromgull commented on 24 Jan 2017

    You can pass an existing graph into the dataset. This will then be
    added directly.

    But there is no guarantee this new graph has the same store, and the
    triples will not be copied over.

    """
    from rdflib.namespace import FOAF

    # Create dissociated graph
    foaf = Graph(identifier=FOAF)
    foaf.parse("http://xmlns.com/foaf/spec/index.rdf", format="xml")

    ds = Dataset()

    # NONONO
    ds.add_graph(foaf)

    assert len(list(ds.contexts())) == 2
    assert len(foaf) == 631
    # with pytest.raises(AssertionError):
    #     assert len(ds) == 631
    assert len(ds) == 631
    # logger.debug(
    #     f" CONTEXT IDENTIFIERS\n{pformat([c.identifier for c in list(ds.contexts())])}"
    # )
