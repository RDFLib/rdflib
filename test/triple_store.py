import unittest

from rdflib import Graph, URIRef, BNode, Literal, RDFS


class GraphTest(unittest.TestCase):

    def setUp(self):
        self.store = Graph()
        self.remove_me = (BNode(), RDFS.label, Literal("remove_me"))
        self.store.add(self.remove_me)

    def testAdd(self):
        subject = BNode()
        self.store.add((subject, RDFS.label, Literal("foo")))

    def testRemove(self):
        self.store.remove(self.remove_me)
        self.store.remove((None, None, None))        
        
    def testTriples(self):
        for s, p, o in self.store:
            pass

if __name__ == "__main__":
    unittest.main()   


