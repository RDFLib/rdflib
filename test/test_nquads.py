import unittest
from rdflib import ConjunctiveGraph, URIRef, Namespace
from six import b

TEST_BASE = 'test/nquads.rdflib'

class NQuadsParserTest(unittest.TestCase):

    def _load_example(self):
        g = ConjunctiveGraph()
        with open("test/nquads.rdflib/example.nquads", "rb") as data:
            g.parse(data, format="nquads")
        return g

    def test_01_simple_open(self):
        g = self._load_example()
        assert len(g.store) == 449

    def test_02_contexts(self):
        # There should be 16 separate contexts
        g = self._load_example()
        assert len([x for x in g.store.contexts()]) == 16

    def test_03_get_value(self):
        # is the name of entity E10009 "Arco Publications"?
        # (in graph http://bibliographica.org/entity/E10009)
        # Looking for:
        # <http://bibliographica.org/entity/E10009>
        #       <http://xmlns.com/foaf/0.1/name>
        #       "Arco Publications"
        #       <http://bibliographica.org/entity/E10009>

        g = self._load_example()
        s = URIRef("http://bibliographica.org/entity/E10009")
        FOAF = Namespace("http://xmlns.com/foaf/0.1/")
        self.assertTrue(g.value(s, FOAF.name).eq("Arco Publications"))

    def test_context_is_optional(self):
        g = ConjunctiveGraph()
        with open("test/nquads.rdflib/test6.nq", "rb") as data:
            g.parse(data, format="nquads")
        assert len(g) > 0

    def test_serialize(self):
        g = ConjunctiveGraph()
        uri1 = URIRef("http://example.org/mygraph1")
        uri2 = URIRef("http://example.org/mygraph2")

        bob = URIRef(u'urn:bob')
        likes = URIRef(u'urn:likes')
        pizza = URIRef(u'urn:pizza')

        g.get_context(uri1).add((bob, likes, pizza))
        g.get_context(uri2).add((bob, likes, pizza))

        s = g.serialize(format='nquads')
        self.assertEqual(len([x for x in s.split(b("\n")) if x.strip()]), 2)

        g2 = ConjunctiveGraph()
        g2.parse(data=s, format='nquads')

        self.assertEqual(len(g), len(g2))
        self.assertEqual(sorted(x.identifier for x in g.contexts()),
                         sorted(x.identifier for x in g2.contexts()))


if __name__ == "__main__":
    unittest.main()
