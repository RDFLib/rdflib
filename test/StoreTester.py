#!/usr/bin/env python2.2
from __future__ import generators
from rdflib.store.InMemoryStore import InMemoryStore
from rdflib.store.KDTreeStore import KDTreeStore
import time, random, sys

random.seed(time.time())

def rand():
    return random.randint(-2000000, 2000000)

def buildSet(num):
    print "Building Set of %s elements"%(num,)
    s = time.clock()
    set = []
    for i in range(num):
        set.append((rand(),rand(),rand()))
    f = time.clock()
    print "Done building Set (%f)"%(f - s)
    return set

def timeAdd(store, set):
    print "Adding %d statements to %s store"%(len(set), type(store))
    s = time.clock()
    for triple in set:
        store.add(triple)


    f = time.clock()
    print "Done adding to set (%f)"%(f - s)


def timeQuery3(store, set, num):
    print "Query3 for containment of %d triples"%(num,)
    s = time.clock()
    
    for i in range(num):
        t = set[random.randint(0,len(set)-1)]
        for r in store.triples(t):
            #print ""
            pass
            
    f = time.clock()
    print "Done checking set (%f)"%(f - s)

def timeQuery2(store, set, num):
    print "Query2 for containment of %d triples"%(num,)
    s = time.clock()
    
    for i in range(num):
        t = set[random.randint(0,len(set)-1)]
        t = (t[0], t[1], None) # Copy
       
        for r in store.triples(t):
            #print r
            pass
            

    f = time.clock()
    print "Done checking set (%f)"%(f - s)

def timeQuery1(store, set, num):
    print "Query1 for containment of %d triples"%(num,)
    s = time.clock()
    
    for i in range(num):
        t = set[random.randint(0,len(set)-1)]
        t = (t[0], None, None) # Copy
       
        for r in store.triples(t):
            #print r
            pass

    f = time.clock()
    print "Done checking set (%f)"%(f - s)

def timeQuery0(store, set, num):
    print "Query0 for containment of %d triples"%(num,)
    s = time.clock()
    
    for i in range(num):
        t = (None, None, None)
       
        for r in store.triples(t):
            #print r
            pass

    f = time.clock()
    print "Done checking set (%f)"%(f - s)
    
set = buildSet(int(sys.argv[1]))
storeList = [InMemoryStore, KDTreeStore]
for storeType in storeList:
    print "\n---------------------------------------"
    
    print "Test %s"%(storeType.__name__,)
    store = storeType()
    timeAdd(store,set)
    timeQuery0(store, set, 10000)
    timeQuery1(store, set, 10000)
    timeQuery2(store, set, 10000)
    timeQuery3(store, set, 10000)
