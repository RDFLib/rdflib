import unittest
import rdflib
from rdflib import ConjunctiveGraph
from rdflib import Literal
from rdflib.namespace import SKOS
from rdflib import RDFS
from rdflib import URIRef

class TestPrefLabel(unittest.TestCase):

    def setUp(self):
        self.g = ConjunctiveGraph()
        self.u = URIRef('http://example.com/foo')
        self.g.add([self.u, RDFS.label, Literal('foo')])
        self.g.add([self.u, RDFS.label, Literal('bar')])
    
    def test_default_label_sorting(self):
        res = sorted(self.g.preferredLabel(self.u))
        tgt = [(rdflib.term.URIRef('http://www.w3.org/2000/01/rdf-schema#label'), 
                rdflib.term.Literal(u'bar')), 
                (rdflib.term.URIRef('http://www.w3.org/2000/01/rdf-schema#label'), 
                rdflib.term.Literal(u'foo'))]
        self.assertEqual(res, tgt)

    def test_default_preflabel_sorting(self):
        self.g.add([self.u, SKOS.prefLabel, Literal('bla')])
        res = self.g.preferredLabel(self.u)
        tgt = [(rdflib.term.URIRef('http://www.w3.org/2004/02/skos/core#prefLabel'),
                rdflib.term.Literal(u'bla'))]
        self.assertEqual(res, tgt)

    def test_preflabel_lang_sorting_no_lang_attr(self):
        self.g.add([self.u, SKOS.prefLabel, Literal('bla')])
        self.g.add([self.u, SKOS.prefLabel, Literal('blubb', lang='en')])
        res = sorted(self.g.preferredLabel(self.u))
        tgt = [(rdflib.term.URIRef('http://www.w3.org/2004/02/skos/core#prefLabel'),
                rdflib.term.Literal(u'bla')),
               (rdflib.term.URIRef('http://www.w3.org/2004/02/skos/core#prefLabel'),
                rdflib.term.Literal(u'blubb', lang='en'))]

        self.assertEqual(res, tgt)

    def test_preflabel_lang_sorting_empty_lang_attr(self):
        self.g.add([self.u, SKOS.prefLabel, Literal('bla')])
        self.g.add([self.u, SKOS.prefLabel, Literal('blubb', lang='en')])
        res = self.g.preferredLabel(self.u, lang='')
        tgt = [(rdflib.term.URIRef('http://www.w3.org/2004/02/skos/core#prefLabel'),
                rdflib.term.Literal(u'bla'))]
        self.assertEqual(res, tgt)

    def test_preflabel_lang_sorting_en_lang_attr(self):
        self.g.add([self.u, SKOS.prefLabel, Literal('blubb', lang='en')])
        res = self.g.preferredLabel(self.u, lang='en')
        tgt = [(rdflib.term.URIRef('http://www.w3.org/2004/02/skos/core#prefLabel'),
                rdflib.term.Literal(u'blubb', lang='en'))]
        self.assertEqual(res, tgt)

