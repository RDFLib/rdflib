import unittest
import rdflib

class TestTrig(unittest.TestCase):
    
    def testEmpty(self): 
        g=rdflib.Graph()
        s=g.serialize(format='trig')
    
    def testRepeatTriples(self): 
        g=rdflib.ConjunctiveGraph()
        g.get_context('urn:a').add(( rdflib.URIRef('urn:1'), 
                                     rdflib.URIRef('urn:2'), 
                                     rdflib.URIRef('urn:3') ))

        g.get_context('urn:b').add(( rdflib.URIRef('urn:1'), 
                                     rdflib.URIRef('urn:2'), 
                                     rdflib.URIRef('urn:3') ))
        
        self.assertEqual(len(g.get_context('urn:a')),1)
        self.assertEqual(len(g.get_context('urn:b')),1)

        s=g.serialize(format='trig')
        self.assert_('{}' not in s) # no empty graphs!

    
