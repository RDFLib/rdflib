#!/usr/bin/env python2.4 

import os, traceback, sys, unittest

#sys.path[:0]=[".."]

from rdflib import term
from rdflib.graph import ConjunctiveGraph

def crapCompare(g1,g2):
    "A really crappy way to 'check' if two graphs are equal. It ignores blank nodes completely"
    if len(g1)!=len(g2):
        raise Exception("Graphs dont have same length")
    for t in g1: 
        if not isinstance(t[0], term.BNode):
            s=t[0]
        else:
            s=None
        if not isinstance(t[2], term.BNode):
            o=t[2]
        else:
            o=None
        if not (s,t[1],o) in g2: 
            e="(%s,%s,%s) is not in both graphs!"%(s,t[1],o)
            raise Exception, e
        

def check(f, prt=False):
    g=ConjunctiveGraph()
    if f.endswith('rdf'):
        g.parse(f)
    else: 
        g.parse(f, format='n3')
    if prt:
        for t in g:
            print t
        print "========================================\nParsed OK!"
    s=g.serialize(format='n3')
    if prt: 
        print s
    g2=ConjunctiveGraph()
    g2.parse(data=s, format='n3')
    if prt: 
        print g2.serialize()

    crapCompare(g,g2)
        

class TestN3Writing(unittest.TestCase):
    def testWriting(self): 
        for f in os.listdir('test/n3'):
            if f!='.svn':
                check("test/n3/"+f)
        
if __name__ == "__main__":
    if len(sys.argv)>1:
        check(sys.argv[1], True)
        sys.exit()
    else:
        unittest.main()
