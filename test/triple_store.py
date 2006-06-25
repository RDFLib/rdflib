import unittest

from rdflib import Graph, URIRef, BNode, Literal, RDFS


class GraphTest(unittest.TestCase):
    backend = 'default'
    path = 'store'
    
    def setUp(self):
        self.store = Graph(backend=self.backend)
        self.store.open(self.path)
        self.remove_me = (BNode(), RDFS.label, Literal("remove_me"))
        self.store.add(self.remove_me)

    def tearDown(self):
        self.store.close()

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


