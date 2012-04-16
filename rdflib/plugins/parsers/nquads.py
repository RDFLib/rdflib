"""
This is a rdflib plugin for parsing NQuad files into Conjunctive 
graphs that can be used and queried. The store that backs the graph 
*must* be able to handle contexts.

>>> from rdflib import ConjunctiveGraph, URIRef, Namespace
>>> g = ConjunctiveGraph()
>>> data = open("test/example.nquads", "rb")
>>> g.parse(data, format="nquads") # doctest:+ELLIPSIS
<Graph identifier=... (<class 'rdflib.graph.Graph'>)>
>>> assert len(g.store) == 449
>>> # There should be 16 separate contexts
>>> assert len([x for x in g.store.contexts()]) == 16
>>> # is the name of entity E10009 "Arco Publications"? (in graph http://bibliographica.org/entity/E10009)
>>> # Looking for:
>>> # <http://bibliographica.org/entity/E10009> <http://xmlns.com/foaf/0.1/name> "Arco Publications" <http://bibliographica.org/entity/E10009>
>>> s = URIRef("http://bibliographica.org/entity/E10009")
>>> FOAF = Namespace("http://xmlns.com/foaf/0.1/")
>>> assert(g.value(s, FOAF.name) == "Arco Publications")
"""

from rdflib.py3compat import b

# Build up from the NTriples parser:
from rdflib.plugins.parsers.ntriples import NTriplesParser
from rdflib.plugins.parsers.ntriples import ParseError
from rdflib.plugins.parsers.ntriples import r_tail
from rdflib.plugins.parsers.ntriples import r_wspace
from rdflib.plugins.parsers.ntriples import r_wspaces

__all__ = ['QuadSink', 'NQuadsParser']

class QuadSink(object):
    def __init__(self):
        class FakeStore(object):
            def __init__(self, addn):
                self.addN = addn
        self.length = 0
        self.__quads = []
        self.__store = FakeStore(self.addN)
        
    def addN(self, quads):
        self.length += 1
        self.__quads.append(quads)
        
    def quads(self, (s,p,o)):
        for s,p,o,ctx in self.__quads:
            yield s,p,o,ctx

class NQuadsParser(NTriplesParser):
    def __init__(self, sink=None):
        if sink is not None:
            assert sink.store.context_aware, ("NQuadsParser must be given"
                                          " a context aware store.")
            self.sink = sink
        else: self.sink = QuadSink()

    def parse(self, inputsource, sink, **kwargs):
        """Parse f as an N-Triples file."""
        assert sink.store.context_aware, ("NQuadsParser must be given"
                                          " a context aware store.")
        self.sink = sink
        
        source = inputsource.getByteStream()
        
        if not hasattr(source, 'read'):
            raise ParseError("Item to parse must be a file-like object.")

        self.file = source
        self.buffer = ''
        while True:
            self.line = self.readline()
            if self.line is None: break
            try: self.parseline()
            except ParseError:
               raise ParseError("Invalid line: %r" % self.line)
        return self.sink
  
    def context(self):
        context = self.uriref()
        if not context:
            raise ParseError("Context must be a uriref")
        return context
  
    def parseline(self):
        self.eat(r_wspace)
        if (not self.line) or self.line.startswith(b('#')):
            return # The line is empty or a comment

        subject = self.subject()
        self.eat(r_wspaces)

        predicate = self.predicate()
        self.eat(r_wspaces)

        obj = self.object()
        self.eat(r_wspaces)
      
        context = self.context()
        self.eat(r_tail)

        if self.line:
            raise ParseError("Trailing garbage")
        # Must have a context aware store - add on a normal Graph
        # discards anything where the ctx != graph.identifier
        self.sink.store.add((subject, predicate, obj), context)

