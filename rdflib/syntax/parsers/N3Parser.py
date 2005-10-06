from rdflib import URIRef, BNode, Literal, RDF

from rdflib.util import from_n3

from rdflib.syntax.parsers import Parser
from rdflib.syntax.parsers.n3p.n3proc import N3Processor#, NTriplesSink

class N3Parser(Parser):

    def __init__(self):
        pass
    
    def parse(self, source, graph):
        source = source.url
        baseURI = source
        #sink = NTriplesSink()
        sink = Sink(graph)
        if False: 
            sink.quantify = lambda *args: True
            sink.flatten = lambda *args: True
        #if ':' not in source: 
        #    uri = 'file://' + os.path.join(os.getcwd(), source)
        #if baseURI and (':' not in baseURI): 
        #    baseURI = 'file://' + os.path.join(os.getcwd(), baseURI)
        baseURI = source # TODO absolutize
        p = N3Processor(source, sink, baseURI=baseURI)
        p.parse()



def convert(t):
    if t.startswith("_"):
        return BNode(unicode(t[2:]))
    elif t.startswith("<"):
	return URIRef(unicode(t[1:-1]))
    elif t.startswith("?"):
	return URIRef("TODO:var/%s" % unicode(t)) # TODO: var term type
    elif t.startswith('"'):
        return from_n3(t)
    else:
        raise "NYI:", t
    return 

class Sink(object):
   def __init__(self, sink): 
      self.sink = sink 
      self.counter = 0

   def absolutize(self, u):
       return URIRef("%s" % unicode(u[2:]))

   def start(self, root): 
       self.root = convert(root) #self.absolutize(root)

   def statement(self, s, p, o, f): 
       s, p, o  = convert(s), convert(p), convert(o)
       f = convert(f) #self.absolutize(f)
       quoted = (f != self.root) 
       #print " adding:", (f, RDF.type, URIRef("Formula")), self.root
       #self.sink.add((f, RDF.type, URIRef("http://example.org/Formula")), self.root)

       #print " adding:", s, p, o, f, quoted
       self.sink.add((s, p, o), f, quoted=quoted)    

   def quantify(self, formula, var): 
       pass

    

# from rdflib import *

# 
# import os

# def parse(uri): 

# parse("model.n3")
# #parse("log.n3")
# #parse("log_implies1.n3")
# #parse("t1.n3")
