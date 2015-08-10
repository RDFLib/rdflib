from rdflib import *
from rdflib.compare import *
from io import StringIO

def get_digest_value(rdf, mimetype):
    graph = Graph()
    graph.load(StringIO(rdf),format=mimetype)
    stats = {}
    ig = to_isomorphic(graph)
    result = ig.graph_digest(stats)
    print stats
    return result

def negative_graph_match_test():
    '''Test of FRIR identifiers against tricky RDF graphs with blank nodes.'''
    testInputs = [
    [ unicode('''@prefix : <http://example.org/ns#> .
     <http://example.org> :rel
         [ :label "Same" ].
         '''),
    unicode('''@prefix : <http://example.org/ns#> .
     <http://example.org> :rel
         [ :label "Same" ],
         [ :label "Same" ].
         '''),
    False
    ],
    [ unicode('''@prefix : <http://example.org/ns#> .
     <http://example.org> :rel
         <http://example.org/a>.
         '''),
    unicode('''@prefix : <http://example.org/ns#> .
     <http://example.org> :rel
         <http://example.org/a>,
         <http://example.org/a>.
         '''),
    True
    ],
    [ unicode('''@prefix : <http://example.org/ns#> .
     :linear_two_step_symmetry_start :related [ :related [ :related :linear_two_step_symmatry_end]],
                                              [ :related [ :related :linear_two_step_symmatry_end]].'''),
    unicode('''@prefix : <http://example.org/ns#> .
     :linear_two_step_symmetry_start :related [ :related [ :related :linear_two_step_symmatry_end]],
                                              [ :related [ :related :linear_two_step_symmatry_end]].'''),
    True
    ],
    [ unicode('''@prefix : <http://example.org/ns#> .
     _:a :rel [
         :rel [
         :rel [
         :rel [
           :rel _:a;
          ];
          ];
          ];
          ].'''),
    unicode('''@prefix : <http://example.org/ns#> .
     _:a :rel [
         :rel [
         :rel [
         :rel [
         :rel [
           :rel _:a;
          ];
          ];
          ];
          ];
          ].'''),
    False
    ],
    # This test fails because the algorithm purposefully breaks the symmetry of symetric
    [ unicode('''@prefix : <http://example.org/ns#> .
     _:a :rel [
         :rel [
         :rel [
         :rel [
           :rel _:a;
          ];
          ];
          ];
          ].'''),
    unicode('''@prefix : <http://example.org/ns#> .
     _:a :rel [
         :rel [
         :rel [
         :rel [
           :rel _:a;
          ];
          ];
          ];
          ].'''),
    True
    ],
    [ unicode('''@prefix : <http://example.org/ns#> .
     _:a :rel [
         :rel [
         :label "foo";
         :rel [
         :rel [
           :rel _:a;
          ];
          ];
          ];
          ].'''),
    unicode('''@prefix : <http://example.org/ns#> .
     _:a :rel [
         :rel [
         :rel [
         :rel [
           :rel _:a;
          ];
          ];
          ];
          ].'''),
    False
    ],
    [ unicode('''@prefix : <http://example.org/ns#> .
     _:0001 :rel _:0003, _:0004.
     _:0002 :rel _:0005, _:0006.
     _:0003 :rel _:0001, _:0007, _:0010.
     _:0004 :rel _:0001, _:0009, _:0008.
     _:0005 :rel _:0002, _:0007, _:0009.
     _:0006 :rel _:0002, _:0008, _:0010.
     _:0007 :rel _:0003, _:0005, _:0009.
     _:0008 :rel _:0004, _:0006, _:0010.
     _:0009 :rel _:0004, _:0005, _:0007.
     _:0010 :rel _:0003, _:0006, _:0008.
     '''),
    unicode('''@prefix : <http://example.org/ns#> .
     _:0001 :rel _:0003, _:0004.
     _:0002 :rel _:0005, _:0006.
     _:0003 :rel _:0001, _:0007, _:0010.
     _:0008 :rel _:0004, _:0006, _:0010.
     _:0009 :rel _:0004, _:0005, _:0007.
     _:0010 :rel _:0003, _:0006, _:0008.
     _:0004 :rel _:0001, _:0009, _:0008.
     _:0005 :rel _:0002, _:0007, _:0009.
     _:0006 :rel _:0002, _:0008, _:0010.
     _:0007 :rel _:0003, _:0005, _:0009.
     '''),
    True
    ],
    ]
    def fn(rdf1, rdf2, identical):
        digest1 = get_digest_value(rdf1,"text/turtle")
        digest2 = get_digest_value(rdf2,"text/turtle")
        print rdf1
        print digest1
        print rdf2
        print digest2
        assert (digest1 == digest2) == identical
    for inputs in testInputs:
        yield fn, inputs[0], inputs[1], inputs[2]

def test_issue494_collapsing_bnodes():
    """Test for https://github.com/RDFLib/rdflib/issues/494 collapsing BNodes"""
    g = Graph()
    g += [
        (BNode('Na1a8fbcf755f41c1b5728f326be50994'),
         RDF['object'],
         URIRef(u'source')),
        (BNode('Na1a8fbcf755f41c1b5728f326be50994'),
         RDF['predicate'],
         BNode('vcb3')),
        (BNode('Na1a8fbcf755f41c1b5728f326be50994'),
         RDF['subject'],
         BNode('vcb2')),
        (BNode('Na1a8fbcf755f41c1b5728f326be50994'),
         RDF['type'],
         RDF['Statement']),
        (BNode('Na713b02f320d409c806ff0190db324f4'),
         RDF['object'],
         URIRef(u'target')),
        (BNode('Na713b02f320d409c806ff0190db324f4'),
         RDF['predicate'],
         BNode('vcb0')),
        (BNode('Na713b02f320d409c806ff0190db324f4'),
         RDF['subject'],
         URIRef(u'source')),
        (BNode('Na713b02f320d409c806ff0190db324f4'),
         RDF['type'],
         RDF['Statement']),
        (BNode('Ndb804ba690a64b3dbb9063c68d5e3550'),
         RDF['object'],
         BNode('vr0KcS4')),
        (BNode('Ndb804ba690a64b3dbb9063c68d5e3550'),
         RDF['predicate'],
         BNode('vrby3JV')),
        (BNode('Ndb804ba690a64b3dbb9063c68d5e3550'),
         RDF['subject'],
         URIRef(u'source')),
        (BNode('Ndb804ba690a64b3dbb9063c68d5e3550'),
         RDF['type'],
         RDF['Statement']),
        (BNode('Ndfc47fb1cd2d4382bcb8d5eb7835a636'),
         RDF['object'],
         URIRef(u'source')),
        (BNode('Ndfc47fb1cd2d4382bcb8d5eb7835a636'),
         RDF['predicate'],
         BNode('vcb5')),
        (BNode('Ndfc47fb1cd2d4382bcb8d5eb7835a636'),
         RDF['subject'],
         URIRef(u'target')),
        (BNode('Ndfc47fb1cd2d4382bcb8d5eb7835a636'),
         RDF['type'],
         RDF['Statement']),
        (BNode('Nec6864ef180843838aa9805bac835c98'),
         RDF['object'],
         URIRef(u'source')),
        (BNode('Nec6864ef180843838aa9805bac835c98'),
         RDF['predicate'],
         BNode('vcb4')),
        (BNode('Nec6864ef180843838aa9805bac835c98'),
         RDF['subject'],
         URIRef(u'source')),
        (BNode('Nec6864ef180843838aa9805bac835c98'),
         RDF['type'],
         RDF['Statement']),
    ]

    print 'graph length: %d, nodes: %d' % (len(g), len(g.all_nodes()))
    print 'triple_bnode degrees:'
    for triple_bnode in g.subjects(RDF['type'], RDF['Statement']):
        print len(list(g.triples([triple_bnode, None, None])))
    print 'all node degrees:'
    g_node_degs = sorted([
        len(list(g.triples([node, None, None])))
        for node in g.all_nodes()
    ], reverse=True)
    print g_node_degs

    cg = to_canonical_graph(g)
    print 'graph length: %d, nodes: %d' % (len(cg), len(cg.all_nodes()))
    print 'triple_bnode degrees:'
    for triple_bnode in cg.subjects(RDF['type'], RDF['Statement']):
        print len(list(cg.triples([triple_bnode, None, None])))
    print 'all node degrees:'
    cg_node_degs = sorted([
        len(list(cg.triples([node, None, None])))
        for node in cg.all_nodes()
    ], reverse=True)
    print cg_node_degs

    assert len(g) == len(cg), \
        'canonicalization changed number of triples in graph'
    assert len(g.all_nodes()) == len(cg.all_nodes()), \
        'canonicalization changed number of nodes in graph'
    assert len(list(g.subjects(RDF['type'], RDF['Statement']))) == \
        len(list(cg.subjects(RDF['type'], RDF['Statement']))), \
        'canonicalization changed number of statements'
    assert g_node_degs == cg_node_degs, \
        'canonicalization changed node degrees'
