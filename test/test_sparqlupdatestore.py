# -*- coding: utf-8 -*-
import unittest
import re

from rdflib import ConjunctiveGraph, URIRef, Literal
from rdflib.util import from_n3

HOST = 'http://localhost:3031'
DB = '/db/'

# this assumes SPARQL1.1 query/update endpoints running locally at
# http://localhost:3031/db/
#
# The ConjunctiveGraph tests below require that the SPARQL endpoint renders its
# default graph as the union of all known graphs! This is incompatible with the
# endpoint behavior required by our Dataset tests in test_dataset.py, so you
# need to run a second SPARQL endpoint on a non standard port,
# e.g. fuseki started with:
# ./fuseki-server --port 3031 --memTDB --update --set tdb:unionDefaultGraph=true /db

# THIS WILL DELETE ALL DATA IN THE /db dataset

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

        root = HOST + DB
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

        # the following are actually bad tests as they depend on your endpoint,
        # as pointed out in the sparqlstore.py code:
        #
        ## For ConjunctiveGraphs, reading is done from the "default graph" Exactly
        ## what this means depends on your endpoint, because SPARQL does not offer a
        ## simple way to query the union of all graphs as it would be expected for a
        ## ConjuntiveGraph.
        ##
        ## Fuseki/TDB has a flag for specifying that the default graph
        ## is the union of all graphs (tdb:unionDefaultGraph in the Fuseki config).
        self.assertEquals(3, len(self.graph),
            'default union graph should contain three triples but contains:\n'
            '%s' % list(self.graph))

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

        # Strings with unbalanced curly braces
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

        # Complicated Strings
        r4strings = []
        r4strings.append(ur'''"1: adfk { ' \\\" \" { "''')
        r4strings.append(ur'''"2: adfk } <foo> #éï \\"''')

        r4strings.append(ur"""'3: adfk { " \\\' \' { '""")
        r4strings.append(ur"""'4: adfk } <foo> #éï \\'""")

        r4strings.append(ur'''"""5: adfk { ' \\\" \" { """''')
        r4strings.append(ur'''"""6: adfk } <foo> #éï \\"""''')
        r4strings.append(u'"""7: ad adsfj \n { \n sadfj"""')

        r4strings.append(ur"""'''8: adfk { " \\\' \' { '''""")
        r4strings.append(ur"""'''9: adfk } <foo> #éï \\'''""")
        r4strings.append(u"'''10: ad adsfj \n { \n sadfj'''")

        r4 = "\n".join([
            u'INSERT DATA { <urn:michel> <urn:says> %s } ;' % s
            for s in r4strings
        ])
        g.update(r4)
        values = set()
        for v in g.objects(michel, says):
            values.add(unicode(v))
        self.assertEquals(values, set([re.sub(ur"\\(.)", ur"\1", re.sub(ur"^'''|'''$|^'|'$|" + ur'^"""|"""$|^"|"$', ur"", s)) for s in r4strings]))

        # IRI Containing ' or #
        # The fragment identifier must not be misinterpreted as a comment
        # (commenting out the end of the block).
        # The ' must not be interpreted as the start of a string, causing the }
        # in the literal to be identified as the end of the block.
        r5 = u"""INSERT DATA { <urn:michel> <urn:hates> <urn:foo'bar?baz;a=1&b=2#fragment>, "'}" }"""

        g.update(r5)
        values = set()
        for v in g.objects(michel, hates):
            values.add(unicode(v))
        self.assertEquals(values, set([u"urn:foo'bar?baz;a=1&b=2#fragment", u"'}"]))

        # Comments
        r6 = u"""
            INSERT DATA {
                <urn:bob> <urn:hates> <urn:bob> . # No closing brace: }
                <urn:bob> <urn:hates> <urn:michel>.
            }
        #Final { } comment"""

        g.update(r6)
        values = set()
        for v in g.objects(bob, hates):
            values.add(v)
        self.assertEquals(values, set([bob, michel]))

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

    def testEmptyNamedGraph(self):
        empty_graph_iri = u"urn:empty-graph-1"
        self.graph.update(u"CREATE GRAPH <%s>" % empty_graph_iri)
        named_graphs = [unicode(r[0]) for r in self.graph.query(
            "SELECT ?name WHERE { GRAPH ?name {} }")]
        # Some SPARQL endpoint backends (like TDB) are not able to find empty named graphs
        # (at least with this query)
        if empty_graph_iri in named_graphs:
            self.assertTrue(empty_graph_iri in [unicode(g.identifier)
                                                for g in self.graph.contexts()])

    def testEmptyLiteral(self):
        # test for https://github.com/RDFLib/rdflib/issues/457
        # also see test_issue457.py which is sparql store independent!
        g = self.graph.get_context(graphuri)
        g.add((
            URIRef('http://example.com/s'),
            URIRef('http://example.com/p'),
            Literal('')))

        o = tuple(g)[0][2]
        self.assertEquals(o, Literal(''), repr(o))

from nose import SkipTest
import urllib2
try:
    assert len(urllib2.urlopen(HOST).read()) > 0
except:
    raise SkipTest(HOST + " is unavailable.")


if __name__ == '__main__':
    unittest.main()
