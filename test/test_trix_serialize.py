#!/usr/bin/env python

import unittest

from rdflib.graph import ConjunctiveGraph
from rdflib.term import URIRef, Literal
from rdflib.graph import Graph


class TestTrixSerialize(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testSerialize(self):

      s1 = URIRef('store:1')
      r1 = URIRef('resource:1')
      r2 = URIRef('resource:2')

      label = URIRef('predicate:label')

      g1 = Graph(identifier = s1)
      g1.add((r1, label, Literal("label 1", lang="en")))
      g1.add((r1, label, Literal("label 2")))

      s2 = URIRef('store:2')
      g2 = Graph(identifier = s2)
      g2.add((r2, label, Literal("label 3")))

      g = ConjunctiveGraph()
      for s,p,o in g1.triples((None, None, None)):
        g.addN([(s,p,o,g1)])
      for s,p,o in g2.triples((None, None, None)):
        g.addN([(s,p,o,g2)])
      r3 = URIRef('resource:3')
      g.add((r3, label, Literal(4)))
      
      
      r = g.serialize(format='trix')
      g3 = ConjunctiveGraph()
      from StringIO import StringIO

      g3.parse(StringIO(r), format='trix')

      for q in g3.quads((None,None,None)):
        # TODO: Fix once getGraph/getContext is in conjunctive graph
        if isinstance(q[3].identifier, URIRef): 
          tg=Graph(store=g.store, identifier=q[3].identifier)
        else:
          # BNode, this is a bit ugly
          # we cannot match the bnode to the right graph automagically
          # here I know there is only one anonymous graph, 
          # and that is the default one, but this is not always the case
          tg=g.default_context
        self.assertTrue(q[0:3] in tg)

if __name__=='__main__':
    unittest.main()
