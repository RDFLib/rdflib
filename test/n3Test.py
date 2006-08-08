#!/usr/bin/env python2.4 

import os, traceback, sys

sys.path[:0]=[".."]

import rdflib

def crapCompare(g1,g2):
    for t in g1: 
        if not isinstance(t[0],rdflib.BNode):
            s=t[0]
        else:
            s=None
        if not isinstance(t[2],rdflib.BNode):
            o=t[2]
        else:
            o=None
        if not (s,t[1],o) in g2: 
            e="(%s,%s,%s) is not in both graphs!"%(s,t[1],o)
            raise Exception, e
        

def test(f, prt=False):
    g=rdflib.ConjunctiveGraph()
    if f.endswith('rdf'):
        g.parse(f)
    else: 
        g.parse(f, format='n3')
    if prt:
        for t in g:
            print t
        print "========================================\nParsed OK!"
    f=open('roundtrip.n3','w')
    s=g.serialize(format='n3')
    if prt: 
        print s
    f.write(s)
    f.close()
    g2=rdflib.ConjunctiveGraph()
    g2.parse('roundtrip.n3',format='n3')
    if prt: 
        print g2.serialize()
    if len(g)!=len(g2):
        raise Exception("Graphs dont have same length")
    crapCompare(g,g2)
        

if len(sys.argv)>1:
    test(sys.argv[1], True)
    sys.exit()

ok=0
error=0
failed=[]
for f in os.listdir('n3'):
    print "Testing %s"%f
    try: 
        test("n3/"+f)
        print "OK"
        ok+=1
    except:
        failed.append(f)
        error+=1
        print "FAIL!"
        traceback.print_exc()

print "Passed %d, failed %d. "%(ok,error)
print "Failed: ",failed
