from rdflib import *

input = """
#  Definitions of terms describing the n3 model
#

@keywords a.

@prefix n3: <#>.
@prefix log: <log.n3#> .
@prefix rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix : <#> .

@forAll :s, :p, :x, :y, :z.

n3:Statement    a rdf:Class .
n3:StatementSet a rdf:Class .

n3:includes     a rdfs:Property .   # Cf rdf:li

n3:predicate    a rdf:Property; rdfs:domain n3:statement .
n3:subject      a rdf:Property; rdfs:domain n3:statement .
n3:object       a rdf:Property; rdfs:domain n3:statement .

n3:context      a rdf:Property; rdfs:domain n3:statement;
                rdfs:range n3:StatementSet .



########### Rules

{ :x :p :y . } log:means { [
                n3:subject :x;
                n3:predicate :p;
                n3:object :y ] a log:Truth}.

# Needs more thought ... ideally, we have the implcit AND rules of
# juxtaposition (introduction and elimination)

{
    {
        {  :x n3:includes :s. } log:implies { :y n3:includes :s. } .
    } forall :s1 .
} log:implies { :x log:implies :y } .

{
    {
        {  :x n3:includes :s. } log:implies { :y n3:includes :s. } .
    } forall :s1
} log:implies { :x log:implies :y } .

# I think n3:includes has to be axiomatic builtin. - unless you go to syntax description.
# syntax.n3?
"""



import unittest

import rdflib
from rdflib.Graph import Graph

class N3TestCase(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testModel(self):
	g = rdflib.Graph()
        g.parse(StringInputSource(input), format="n3")

	for s, p, o in g:
	    print s, p, o
	    if isinstance(s, Graph):
		print "Found a graph!", len(s)
		for t in s:
		    print t

	self.assertEquals(len(list(g.contexts())), 13)
	
	for cid in g.contexts():
	    c = g.get_context(cid)
	    print len(c)

        if False:
            print g.serialize(format="pretty-xml")
	    print "CONTEXTS:", list(g.contexts())
	    for cid in g.contexts():
		print cid
		c = g.get_context(cid)
		print c.serialize(format="pretty-xml")
        g.close()
            

if __name__ == '__main__':
    unittest.main()    
