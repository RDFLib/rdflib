import unittest

from rdflib.TripleStore import TripleStore

from rdflib.URIRef import URIRef
from rdflib.BNode import BNode
from rdflib.Literal import Literal

from rdflib.constants import RDFS_LABEL

class TripleStoreTest(unittest.TestCase):
    def setUp(self):
        self.store = TripleStore()
        self.remove_me = (BNode(), RDFS_LABEL, Literal("remove_me"))
        self.store.add(self.remove_me)

    def testAdd(self):
        subject = BNode()
        self.store.add((subject, RDFS_LABEL, Literal("foo")))

    def testRemove(self):
        self.store.remove(self.remove_me)
        
    def testTriples(self):
        for s, p, o in self.store:
            pass

if __name__ == "__main__":
    unittest.main()   


