# -*- coding: utf-8 -*-
from rdflib import ConjunctiveGraph, URIRef

import unittest

# this assumed SPARQL1.1 query/update endpoints
# running locally at localhost:3030/data
# for instance fuseki started with ./fuseki-server --mem --update /data

# THIS WILL DELETE ALL DATA IN THE /data dataset

michel = URIRef(u'urn:michel')
tarek = URIRef(u'urn:tarek')
bob = URIRef(u'urn:bob')
likes = URIRef(u'urn:likes')
hates = URIRef(u'urn:hates')
pizza = URIRef(u'urn:pizza')
cheese = URIRef(u'urn:cheese')

graphuri = URIRef('urn:graph')
othergraphuri = URIRef('urn:othergraph')


class TestSparql11(unittest.TestCase):

    def setUp(self):
        self.longMessage = True
        self.graph = ConjunctiveGraph('SPARQLUpdateStore')

        root = "http://localhost:3030/ukpp/"
        self.graph.open((root + "sparql", root + "update"))

        # clean out the store
        for c in self.graph.contexts():
            c.remove((None, None, None))
            assert len(c) == 0

    def tearDown(self):
        self.graph.close()

    def testSimpleGraph(self):
        g = self.graph.get_context(graphuri)
        g.add((tarek, likes, pizza))
        g.add((bob, likes, pizza))
        g.add((bob, likes, cheese))

        g2 = self.graph.get_context(othergraphuri)
        g2.add((michel, likes, pizza))

        self.assertEquals(3, len(g), 'graph contains 3 triples')
        self.assertEquals(1, len(g2), 'other graph contains 1 triple')

        r = g.query("SELECT * WHERE { ?s <urn:likes> <urn:pizza> . }")
        self.assertEquals(2, len(list(r)), "two people like pizza")

        r = g.triples((None, likes, pizza))
        self.assertEquals(2, len(list(r)), "two people like pizza")

        # Test initBindings
        r = g.query("SELECT * WHERE { ?s <urn:likes> <urn:pizza> . }",
                    initBindings={'s': tarek})
        self.assertEquals(1, len(list(r)), "i was asking only about tarek")

        r = g.triples((tarek, likes, pizza))
        self.assertEquals(1, len(list(r)), "i was asking only about tarek")

        r = g.triples((tarek, likes, cheese))
        self.assertEquals(0, len(list(r)), "tarek doesn't like cheese")

        g2.add((tarek, likes, pizza))
        g.remove((tarek, likes, pizza))
        r = g.query("SELECT * WHERE { ?s <urn:likes> <urn:pizza> . }")
        self.assertEquals(1, len(list(r)), "only bob likes pizza")

    def testConjunctiveDefault(self):
        g = self.graph.get_context(graphuri)
        g.add((tarek, likes, pizza))
        g2 = self.graph.get_context(othergraphuri)
        g2.add((bob, likes, pizza))
        g.add((tarek, hates, cheese))

        self.assertEquals(2, len(g), 'graph contains 2 triples')
        self.assertEquals(3, len(self.graph),
                          'default union graph contains three triples')

        r = self.graph.query("SELECT * WHERE { ?s <urn:likes> <urn:pizza> . }")
        self.assertEquals(2, len(list(r)), "two people like pizza")

        r = self.graph.query("SELECT * WHERE { ?s <urn:likes> <urn:pizza> . }",
                             initBindings={'s': tarek})
        self.assertEquals(1, len(list(r)), "i was asking only about tarek")

        r = self.graph.triples((tarek, likes, pizza))
        self.assertEquals(1, len(list(r)), "i was asking only about tarek")

        r = self.graph.triples((tarek, likes, cheese))
        self.assertEquals(0, len(list(r)), "tarek doesn't like cheese")

        g2.remove((bob, likes, pizza))

        r = self.graph.query("SELECT * WHERE { ?s <urn:likes> <urn:pizza> . }")
        self.assertEquals(1, len(list(r)), "only tarek likes pizza")

    def testUpdate(self):
        self.graph.update("INSERT DATA { GRAPH <urn:graph> { <urn:michel> <urn:likes> <urn:pizza> . } }")
        
        g = self.graph.get_context(graphuri)
        self.assertEquals(1, len(g), 'graph contains 1 triples')
        
    def testUpdateWithInitNs(self):
        self.graph.update(
            "INSERT DATA { GRAPH ns:graph { ns:michel ns:likes ns:pizza . } }",
            initNs={'ns': URIRef('urn:')}
        )
        
        g = self.graph.get_context(graphuri)
        self.assertEquals(
            set(g.triples((None,None,None))),
            set([(michel,likes,pizza)]),
            'only michel likes pizza'
        )
        
    def testUpdateWithInitBindings(self):
        self.graph.update(
            "INSERT { GRAPH <urn:graph> { ?a ?b ?c . } } WherE { }",
            initBindings={
                'a': URIRef('urn:michel'),
                'b': URIRef('urn:likes'),
                'c': URIRef('urn:pizza'),
            }
        )
        
        g = self.graph.get_context(graphuri)
        self.assertEquals(
            set(g.triples((None,None,None))),
            set([(michel,likes,pizza)]),
            'only michel likes pizza'
        )

    def testMultipleUpdateWithInitBindings(self):
        self.graph.update(
            "INSERT { GRAPH <urn:graph> { ?a ?b ?c . } } WHERE { };"
            "INSERT { GRAPH <urn:graph> { ?d ?b ?c . } } WHERE { }",
            initBindings={
                'a': URIRef('urn:michel'),
                'b': URIRef('urn:likes'),
                'c': URIRef('urn:pizza'),
                'd': URIRef('urn:bob'),
            }
        )
        
        g = self.graph.get_context(graphuri)
        self.assertEquals(
            set(g.triples((None,None,None))),
            set([(michel,likes,pizza), (bob,likes,pizza)]),
            'michel and bob like pizza'
        )

    def testNamedGraphUpdate(self):
        g = self.graph.get_context(graphuri)
        r1 = "INSERT DATA { <urn:michel> <urn:likes> <urn:pizza> }"
        g.update(r1)
        self.assertEquals(
            set(g.triples((None,None,None))),
            set([(michel,likes,pizza)]),
            'only michel likes pizza'
        )

        r2 = "DELETE { <urn:michel> <urn:likes> <urn:pizza> } " + \
             "INSERT { <urn:bob> <urn:likes> <urn:pizza> } WHERE {}"
        g.update(r2)
        self.assertEquals(
            set(g.triples((None, None, None))),
            set([(bob, likes, pizza)]),
            'only bob likes pizza'
        )
        says = URIRef("urn:says")
        tricky_strs = ["With an unbalanced curly brace %s " % brace
                       for brace in ["{", "}"]]

        for tricky_str in tricky_strs:
            r3 = """INSERT { ?b <urn:says> "%s" }
            WHERE { ?b <urn:likes> <urn:pizza>} """ % tricky_str
            g.update(r3)

        values = set()
        for v in g.objects(bob, says):
            values.add(str(v))
        self.assertEquals(values, set(tricky_strs))

        bio = u"éï }"
        r4 = u'INSERT DATA { <urn:michel> <urn:says> "%s" }' % bio
        g.update(r4)
        values = set()
        for v in g.objects(michel, says):
            values.add(unicode(v))
        self.assertEquals(values, set([bio]))

    def testNamedGraphUpdateWithInitBindings(self):
        g = self.graph.get_context(graphuri)
        r = "INSERT { ?a ?b ?c } WHERE {}"
        g.update(r, initBindings={
                'a': michel,
                'b': likes,
                'c': pizza
            })
        self.assertEquals(
            set(g.triples((None, None, None))),
            set([(michel, likes, pizza)]),
            'only michel likes pizza'
        )


from nose import SkipTest
import urllib2
try:
    assert len(urllib2.urlopen("http://localhost:3030/").read()) > 0
except:
    raise SkipTest("http://localhost:3030/ is unavailable.")


if __name__ == '__main__':
    unittest.main()
