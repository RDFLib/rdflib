import unittest

from rdflib.TripleStore import TripleStore
from rdflib.URIRef import URIRef
from rdflib.Literal import Literal
from rdflib.BNode import BNode
from rdflib import exception

class TypeCheckCase(unittest.TestCase):

    def testA(self):
        store = TripleStore()
        store.load("bnode.rdf", None, 1)
        store.remove_triples(None, None, None)        
        b1 = BNode()
        b2 = BNode()
        store.add(b1, URIRef("foo"), b2)
        store.add(b1, URIRef("foo"), Literal("123"))
        self.assertNotEquals(b1, b2)        
        print b1, b2
        store.save()

if __name__ == "__main__":
    unittest.main()   
