import pytest
import rdflib


@pytest.mark.xfail(reason="Some issue with handling base URI that does not end with a slash")
def test_trig_default_graph_with_dataset_default_id_as_identifier():
    ds = rdflib.Dataset()
    data = """
    @prefix : <http://example.com/> .

    <> <b> <c> .
    { <d> <e> <f> . }

    <g1> { <d> <e> <f> . }
    <g2> { <g> <h> <i> . }
    """
    ds.parse(data=data, format="trig", publicID=ds.default_graph.identifier)

    assert len(list(ds.contexts())) == 2
    assert len(list(ds.default_graph)) == 2


def test_trig_default_graph():
    ds = rdflib.Dataset()
    data = """
    @prefix : <http://example.com/> .

    <> <b> <c> .
    { <d> <e> <f> . }

    <g1> { <d> <e> <f> . }
    <g2> { <g> <h> <i> . }
    """
    ds.parse(data=data, format="trig")

    assert len(list(ds.contexts())) == 2
    assert len(list(ds.default_graph)) == 2
