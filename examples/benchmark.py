import sys
import os
import time
import random

import rdflib

def resource(n):
    return rdflib.URIRef("urn:resource:%d"%n)

def prop(n):
    return rdflib.URIRef("urn:property:%d"%n)


def createData(g,N, M=80):

    for x in range(N):
        g.add(( resource(random.randint(0,M)),
                prop(random.randint(0,M)),
                resource(random.randint(0,M))))

if __name__=='__main__':

    g=rdflib.Graph(sys.argv[1])

    g.open(os.tempnam(), create=True)
    start=time.time()
    #g.load("foaf890K.rdf")
    createData(g,300000)
    print len(g)
    read=time.time()
    sys.stderr.write("Reading took %.2fs\n"%(read-start))
    
    x=set(g.subjects(prop(5), resource(5)))
    t1=time.time()
    sys.stderr.write("Subjects took %.2fs\n"%(t1-read))
    
    x=set(g.predicates(resource(5), resource(5)))
    t2=time.time()
    sys.stderr.write("Predicates took %.2fs\n"%(t2-t1))

    x=set(g.objects(resource(5), prop(5)))
    t3=time.time()
    sys.stderr.write("Objects took %.2fs\n"%(t3-t2))

    x=set(g.subject_objects(prop(5)))
    t4=time.time()
    sys.stderr.write("SubjectObjects took %.2fs\n"%(t4-t3))

    x=set(g.subject_predicates(resource(5)))
    t5=time.time()
    sys.stderr.write("SubjectPredicates took %.2fs\n"%(t5-t4))

    x=set(g.predicate_objects(resource(5)))
    t6=time.time()
    sys.stderr.write("SubjectPredicates took %.2fs\n"%(t6-t5))
