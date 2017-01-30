#!/usr/bin/env python

import unittest

from rdflib.graph import ConjunctiveGraph
from rdflib.term import URIRef, Literal
from rdflib.graph import Graph
from six import BytesIO


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

        g1 = Graph(identifier=s1)
        g1.add((r1, label, Literal("label 1", lang="en")))
        g1.add((r1, label, Literal("label 2")))

        s2 = URIRef('store:2')
        g2 = Graph(identifier=s2)
        g2.add((r2, label, Literal("label 3")))

        g = ConjunctiveGraph()
        for s, p, o in g1.triples((None, None, None)):
            g.addN([(s, p, o, g1)])
        for s, p, o in g2.triples((None, None, None)):
            g.addN([(s, p, o, g2)])
        r3 = URIRef('resource:3')
        g.add((r3, label, Literal(4)))

        r = g.serialize(format='trix')
        g3 = ConjunctiveGraph()

        g3.parse(BytesIO(r), format='trix')

        for q in g3.quads((None, None, None)):
            # TODO: Fix once getGraph/getContext is in conjunctive graph
            if isinstance(q[3].identifier, URIRef):
                tg = Graph(store=g.store, identifier=q[3].identifier)
            else:
                # BNode, this is a bit ugly
                # we cannot match the bnode to the right graph automagically
                # here I know there is only one anonymous graph,
                # and that is the default one, but this is not always the case
                tg = g.default_context
            self.assertTrue(q[0:3] in tg)

    def test_issue_250(self):
        """

        https://github.com/RDFLib/rdflib/issues/250

        When I have a ConjunctiveGraph with the default namespace set,
        for example

        import rdflib
        g = rdflib.ConjunctiveGraph()
        g.bind(None, "http://defaultnamespace")

        then the Trix serializer binds the default namespace twice in its XML
        output, once for the Trix namespace and once for the namespace I used:

        print(g.serialize(format='trix').decode('UTF-8'))

        <?xml version="1.0" encoding="utf-8"?>
        <TriX
          xmlns:xml="http://www.w3.org/XML/1998/namespace"
          xmlns="http://defaultnamespace"
          xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
          xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"
          xmlns="http://www.w3.org/2004/03/trix/trix-1/"
        />

        """

        graph = ConjunctiveGraph()
        graph.bind(None, "http://defaultnamespace")
        sg = graph.serialize(format='trix').decode('UTF-8')
        self.assertTrue(
            'xmlns="http://defaultnamespace"' not in sg, sg)
        self.assertTrue(
            'xmlns="http://www.w3.org/2004/03/trix/trix-1/' in sg, sg)


if __name__ == '__main__':
    unittest.main()
