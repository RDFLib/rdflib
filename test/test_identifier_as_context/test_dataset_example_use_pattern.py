import pytest
from rdflib import (
    Dataset,
    FOAF,
    Graph,
)

# https://github.com/RDFLib/rdflib/issues/698#issuecomment-577776652


def test_intuition_698_comment_577776652():

    foaf = Graph(identifier=FOAF)
    foaf.parse("http://xmlns.com/foaf/spec/index.rdf", format="xml")

    ds = Dataset()
    assert len(list(ds.contexts())) == 1

    ds.graph(foaf)
    assert len(list(ds.contexts())) == 2

    dsfoaf = ds.graph(foaf.identifier)
    assert foaf == dsfoaf  # identifier equality only

    assert len(dsfoaf) == 0

    assert len(foaf) == 631


def test_actualité_698_comment_577776652():

    ds = Dataset()
    assert len(list(ds.graphs())) == 1  # Only the default graph exists at this point

    foaf = ds.graph(FOAF)  # Create empty, identified graph in Dataset, return it
    assert type(foaf) is Graph
    assert len(list(ds.graphs())) == 2  # Dataset now has two graphs

    # Operations on foaf == operations on the Dataset graph

    foaf.parse("http://xmlns.com/foaf/spec/index.rdf", format="xml")

    assert len(foaf) == 631

    # Dataset still has handle on the graph, so we can delete the referent

    del foaf

    with pytest.raises(UnboundLocalError):
        assert foaf is None

    # Get the graph from the Dataset
    foaf = ds.graph(FOAF)

    assert len(foaf) == 631
