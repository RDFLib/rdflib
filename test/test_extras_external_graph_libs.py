from nose import SkipTest
from rdflib import Graph, URIRef, Literal
from six import text_type

def test_rdflib_to_networkx():
    try:
        import networkx
    except ImportError:
        raise SkipTest("couldn't find networkx")
    from rdflib.extras.external_graph_libs import rdflib_to_networkx_multidigraph
    from rdflib.extras.external_graph_libs import rdflib_to_networkx_digraph
    from rdflib.extras.external_graph_libs import rdflib_to_networkx_graph
    g = Graph()
    a, b, l = URIRef('a'), URIRef('b'), Literal('l')
    p, q = URIRef('p'), URIRef('q')
    edges = [(a, p, b), (a, q, b), (b, p, a), (b, p, l)]
    for t in edges:
        g.add(t)


    mdg = rdflib_to_networkx_multidigraph(g)
    assert len(mdg.edges()) == 4
    assert mdg.has_edge(a, b)
    assert mdg.has_edge(a, b, key=p)
    assert mdg.has_edge(a, b, key=q)

    mdg = rdflib_to_networkx_multidigraph(g, edge_attrs=lambda s, p, o: {})
    assert mdg.has_edge(a, b, key=0)
    assert mdg.has_edge(a, b, key=1)


    dg = rdflib_to_networkx_digraph(g)
    assert dg[a][b]['weight'] == 2
    assert sorted(dg[a][b]['triples']) == [(a, p, b), (a, q, b)]
    assert len(dg.edges()) == 3
    assert dg.size() == 3
    assert dg.size(weight='weight') == 4.0

    dg = rdflib_to_networkx_graph(g, False, edge_attrs=lambda s, p, o:{})
    assert 'weight' not in dg[a][b]
    assert 'triples' not in dg[a][b]


    ug = rdflib_to_networkx_graph(g)
    assert ug[a][b]['weight'] == 3
    assert sorted(ug[a][b]['triples']) == [(a, p, b), (a, q, b), (b, p, a)]
    assert len(ug.edges()) == 2
    assert ug.size() == 2
    assert ug.size(weight='weight') == 4.0

    ug = rdflib_to_networkx_graph(g, False, edge_attrs=lambda s, p, o:{})
    assert 'weight' not in ug[a][b]
    assert 'triples' not in ug[a][b]


def test_rdflib_to_graphtool():
    try:
        from graph_tool import util as gt_util
    except ImportError:
        raise SkipTest("couldn't find graph_tool")
    from rdflib.extras.external_graph_libs import rdflib_to_graphtool
    g = Graph()
    a, b, l = URIRef('a'), URIRef('b'), Literal('l')
    p, q = URIRef('p'), URIRef('q')
    edges = [(a, p, b), (a, q, b), (b, p, a), (b, p, l)]
    for t in edges:
        g.add(t)

    mdg = rdflib_to_graphtool(g)
    assert len(list(mdg.edges())) == 4

    vpterm = mdg.vertex_properties['term']
    va = gt_util.find_vertex(mdg, vpterm, a)[0]
    vb = gt_util.find_vertex(mdg, vpterm, b)[0]
    vl = gt_util.find_vertex(mdg, vpterm, l)[0]
    assert (va, vb) in [(e.source(), e.target()) for e in list(mdg.edges())]

    epterm = mdg.edge_properties['term']
    assert len(list(gt_util.find_edge(mdg, epterm, p))) == 3
    assert len(list(gt_util.find_edge(mdg, epterm, q))) == 1

    mdg = rdflib_to_graphtool(
        g,
        e_prop_names=[text_type('name')],
        transform_p=lambda s, p, o: {text_type('name'): text_type(p)})
    epterm = mdg.edge_properties['name']
    assert len(list(gt_util.find_edge(mdg, epterm, text_type(p)))) == 3
    assert len(list(gt_util.find_edge(mdg, epterm, text_type(q)))) == 1

if __name__ == "__main__":
    import sys
    import nose
    nose.main(defaultTest=sys.argv[0])
