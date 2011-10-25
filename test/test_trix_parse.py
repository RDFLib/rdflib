#!/usr/bin/env python


from rdflib.graph import ConjunctiveGraph
import unittest

class TestTrixParse(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testAperture(self): 

        g=ConjunctiveGraph()

        g.parse("test/trix/aperture.trix",format="trix")
        c=list(g.contexts())

        #print list(g.contexts())
        t=sum(map(len, g.contexts()))

        self.assertEquals(t,24)
        self.assertEquals(len(c),4)
        
        #print "Parsed %d triples"%t

    def testSpec(self): 

        g=ConjunctiveGraph()
        
        g.parse("test/trix/nokia_example.trix",format="trix")
        
        #print "Parsed %d triples"%len(g)
        



if __name__=='__main__':
    unittest.main()
                          
