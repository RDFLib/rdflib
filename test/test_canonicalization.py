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
        print digest1
        print digest2
        assert (digest1 == digest2) == identical
    for inputs in testInputs:
        yield fn, inputs[0], inputs[1], inputs[2]