
from rdflib import Graph, URIRef
import unittest

class GraphSlice(unittest.TestCase):

    def testSlice(self):
        """
         We pervert the slice object, 
         and use start, stop, step as subject, predicate, object

         all operations return generators over full triples 
        """

        sl=lambda x,y: self.assertEqual(len(list(x)),y)
        soe=lambda x,y: self.assertEqual(set([a[2] for a in x]),set(y)) # equals objects
        g=self.graph
         
        # Single terms are all trivial:

        # single index slices by subject, i.e. return triples((x,None,None))
        # tell me everything about "tarek"
        sl(g[self.tarek],2)
        
        # single slice slices by s,p,o, with : used to split
        # tell me everything about "tarek" (same as above)
        sl(g[self.tarek::],2)

        # give me every "likes" relationship
        sl(g[:self.likes:],5)

        # give me every relationship to pizza
        sl(g[::self.pizza],3)

        # give me everyone who likes pizza
        sl(g[:self.likes:self.pizza],2)
       
        # does tarek like pizza?
        self.assertTrue(g[self.tarek:self.likes:self.pizza])

        # More intesting is using paths

        # everything hated or liked
        sl(g[:self.hates|self.likes], 7)
        
        

        

    def setUp(self):
        self.graph = Graph()

        self.michel = URIRef(u'michel')
        self.tarek = URIRef(u'tarek')
        self.bob = URIRef(u'bob')
        self.likes = URIRef(u'likes')
        self.hates = URIRef(u'hates')
        self.pizza = URIRef(u'pizza')
        self.cheese = URIRef(u'cheese')

        self.addStuff()

    def addStuff(self):
        tarek = self.tarek
        michel = self.michel
        bob = self.bob
        likes = self.likes
        hates = self.hates
        pizza = self.pizza
        cheese = self.cheese

        self.graph.add((tarek, likes, pizza))
        self.graph.add((tarek, likes, cheese))
        self.graph.add((michel, likes, pizza))
        self.graph.add((michel, likes, cheese))
        self.graph.add((bob, likes, cheese))
        self.graph.add((bob, hates, pizza))
        self.graph.add((bob, hates, michel)) # gasp!


if __name__ == '__main__':
    unittest.main()
