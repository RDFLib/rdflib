
from rdflib import Graph, URIRef
import unittest

class GraphSlice(unittest.TestCase):

    def testSlice(self):
        """
         Slicing in python supports:
         Slicing a range, i.e element 2-5, with a step 
         slicing in more than one dimension with comma

         normal lists only let you do ranges or single items
        
         scipy lets you slice multidimensional arrays like this: 
         array[(2,5),10:20]  returns the 10-20th column of the 2nd and 5th row 
         in python slice syntax
         You can combine tuples and ranges, but not vice versa, i.e. 
         i.e 
         a[(0,1):2] is ok, although what is means is not defined for scipy 

         a[(0:1),2] is NOT ok. 

         In theory, a graph could be seen as a 3-dimensional array of booleans,
         i.e. one dimension for subject, predicate, object, and bools whether 
         this triple is contained in the graph. 

         So we could use slice dimensions for each triple element, however, this
         leaves us with range-slices unused, since there is no concept or order
         for rdflib nodes (or there is lexical order, but it's not very useful)
         
         Better is perhaps to pervert the slice object, 
         and use start, stop, step as subject, predicate, object

         This leaves us with several dimensions, i.e. several objects
         And also with tuples used for start, stop, step...
         
         Functions that would be interesting would be:
         * disjunction - matching either of the patterns given
         * conjunction - matching all of the patterns given
         * property-paths - going further in the graph

         Gut feeling tells me that conjunction is least useful, 
         i.e. neither of these strike me as very useful:
         [(bob,bill):likes] - everything bob AND bill likes
         [bob:(likes,hates)] - everything bob likes AND hates
         [::(pizza,cheese)] - everything about pizza AND cheese

         but the disjunction case does seem useful:
         [resource:(SKOS.prefLabel,RDFS.label)] -  
             give me either of the two label properties
         [:RDF.type:(RDFS.Class,OWL.Class)] - 
             give me all RDFS classes or OWL classes

         I think having paths would very nice - i.e.:
         g[resource:RDF.type,:RDFS.label] -> get me all labels of the types of this thing

         I have implemented disjunction and paths.

         One problem with using slices and :: notation for the s,p,o part is that 
         this does not generalize to ConjunctiveGraphs, as slices can only have 3 parts. 
         However, maybe one does not want to mix and match contexts very often, so having 
         a simple __getitem__ which is the same as get_graph on ConjunctiveGraphs is probably enough: 
         cg[mycontext][:RDF.type,:RDFS.label] 
         This is not implemented atm.

         Below are some examples - that should make it much clearer
        
         all operations return generators over full triples - 
         although one could try to be clever, and match subject_predicates 
         and related functions, and only return tuples - depending on what was given
         I think this would be too confusing
        """

        sl=lambda x,y: self.assertEquals(len(list(x)),y)
        soe=lambda x,y: self.assertEquals(set([a[2] for a in x]),set(y)) # equals objects
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
        sl(g[self.tarek:self.likes:self.pizza],1)

        # Much more intesting is using tuples:

        # tuples in slices
        #   give me everything bob OR tarek like 

        # (alternative could be:
        #   give me everything both bob AND tarek like)
        sl(g[(self.tarek, self.bob):self.likes],3)

        # everything hated or liked
        sl(g[:(self.hates,self.likes)], 7)
        
        # hated or liked, pizza or cheese
        sl(g[:(self.hates,self.likes):(self.pizza,self.cheese)], 6)

        
        # give everything tarek OR bob, likes OR hates

        # two alternatives:
        #   give everything tarek AND bob, likes AND hates
        # or pair-wise matching:
        #   give everything tarek likes OR bob hates
        sl(g[(self.tarek, self.bob):(self.likes,self.hates)],5)

        

        # several slices, i.e. several patterns
        #
        #   a nested path, ignore the subject of the second pattern
        #    "give me everything liked by something bob hates"
        
        ## (alternatives could be:
        ##   give me everything tarek likes AND hates
        ## or 
        ##   give me everything tarek likes OR hates )
        sl(g[self.bob:self.hates,:self.likes], 2)
        soe(g[self.bob:self.hates,:self.likes], [self.pizza,self.cheese])
        

        

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
