import rdflib

def test_trig_default_graph():
    ds = rdflib.ConjunctiveGraph()
    data = """
    @prefix : <http://example.com/> .

    <> <b> <c> .
    { <d> <e> <f> . }

    <g1> { <d> <e> <f> . }
    <g2> { <g> <h> <i> . }
    """
    ds.parse(data=data, format='trig', publicID=ds.default_context.identifier)

    assert len(list(ds.contexts())) == 3
    assert len(list(ds.default_context)) == 2
