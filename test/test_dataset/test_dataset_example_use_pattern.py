import pytest

from rdflib import FOAF, Dataset, Graph, URIRef

# https://github.com/RDFLib/rdflib/issues/698#issuecomment-577776652


def test_intuition_698_comment_577776652():

    foaf = Graph(identifier=FOAF)
    foaf.parse("http://xmlns.com/foaf/spec/index.rdf", format="xml")

    ds = Dataset()

    assert len(list(ds.graphs())) == 0

    try:
        ds.graph(foaf)
    except Exception as e:
        assert (
            str(e) == "identifer can be URIRef, BNode, Literal or None (but not Graph)"
        )

    assert len(list(ds.graphs())) == 0

    dsfoaf = ds.graph(foaf.identifier)
    assert foaf == dsfoaf  # identifier equality only

    assert len(dsfoaf) == 0

    assert len(foaf) == 631


def test_actualité_698_comment_577776652():

    ds = Dataset()
    assert len(list(ds.graphs())) == 0

    try:
        ds.graph(FOAF)
    except Exception as e:
        assert (
            str(e)
            == "identifer can be URIRef, BNode, Literal or None (but not DefinedNamespaceMeta)"
        )

    foaf = ds.graph(
        URIRef(FOAF)
    )  # Create empty, identified graph in Dataset, return it

    assert type(foaf) is Graph

    assert len(list(ds.graphs())) == 1  # Dataset now has one context

    # Operations on foaf == operations on the Dataset graph

    foaf.parse("http://xmlns.com/foaf/spec/index.rdf", format="xml")

    assert len(foaf) == 631

    # Dataset still has handle on the graph, so we can delete the referent

    del foaf

    with pytest.raises(UnboundLocalError):
        assert foaf is None

    # Get the graph from the Dataset
    foaf = ds.graph(URIRef(FOAF))

    assert len(foaf) == 631
