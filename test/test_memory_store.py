import unittest
import rdflib

rdflib.plugin.register('Memory', rdflib.store.Store, 
                'rdflib.plugins.memory', 'Memory')

class StoreTestCase(unittest.TestCase):

    def test_memory_store(self):
        g = rdflib.Graph("Memory")
        subj1 = rdflib.URIRef("http://example.org/foo#bar1")
        pred1 = rdflib.URIRef("http://example.org/foo#bar2")
        obj1 = rdflib.URIRef("http://example.org/foo#bar3")
        triple1 = (subj1, pred1, obj1)
        triple2 = (subj1, 
                   rdflib.URIRef("http://example.org/foo#bar4"),                
                   rdflib.URIRef("http://example.org/foo#bar5"))
        g.add(triple1)
        self.assertTrue(len(g) == 1)
        g.add(triple2)
        self.assertTrue(len(list(g.triples((subj1, None, None)))) == 2)
        self.assertTrue(len(list(g.triples((None, pred1, None)))) == 1)
        self.assertTrue(len(list(g.triples((None, None, obj1)))) == 1)
        g.remove(triple1)
        self.assertTrue(len(g) == 1)
        g.serialize()


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
