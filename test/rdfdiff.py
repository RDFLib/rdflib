#!/usr/bin/env python
"""
RDF Graph Isomorphism Tester
Author: Sean B. Palmer, inamidst.com
Uses the pyrple algorithm
Requirements: 
   Python2.4+
   http://inamidst.com/proj/rdf/ntriples.py
Usage: ./rdfdiff.py <ntriplesP> <ntriplesQ>
"""

import sys, re, urllib
import ntriples
from ntriples import bNode

ntriples.r_uriref = re.compile(r'<([^\s"<>]+)>')

class Graph(object): 
   def __init__(self, uri=None, content=None): 
      self.triples = set()
      if uri:
          self.parse(uri)
      elif content:
          self.parse_string(content)

   def parse(self, uri): 
      class Sink(object): 
         def triple(sink, s, p, o): 
            self.triples.add((s, p, o))

      p = ntriples.NTriplesParser(sink=Sink())
      u = urllib.urlopen(uri)
      p.parse(u)
      u.close()

   def parse_string(self, content):
      class Sink(object): 
         def triple(sink, s, p, o): 
            self.triples.add((s, p, o))

      p = ntriples.NTriplesParser(sink=Sink())
      p.parsestring(content)

   def __hash__(self): 
      return hash(tuple(sorted(self.hashtriples())))

   def hashtriples(self): 
      for triple in self.triples: 
         g = ((isinstance(t, bNode) and self.vhash(t)) or t for t in triple)
         yield hash(tuple(g))

   def vhash(self, term, done=False): 
      return tuple(sorted(self.vhashtriples(term, done)))

   def vhashtriples(self, term, done): 
      for t in self.triples: 
         if term in t: yield tuple(self.vhashtriple(t, term, done))

   def vhashtriple(self, triple, term, done): 
      for p in xrange(3): 
         if not isinstance(triple[p], bNode): yield triple[p]
         elif done or (triple[p] == term): yield p
         else: yield self.vhash(triple[p], done=True)

def compare(p, q): 
   return hash(Graph(p)) == hash(Graph(q))

def compare_from_string(p, q):
   return hash(Graph(content=p)) == hash(Graph(content=q))

def main(): 
   result = compare(sys.argv[1], sys.argv[2])
   print ('no', 'yes')[result]

if __name__=="__main__": 
   main()
