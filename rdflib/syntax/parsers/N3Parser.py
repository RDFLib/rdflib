from rdflib import URIRef, BNode, Literal, RDF, Variable

from rdflib.util import from_n3

from rdflib.syntax.parsers import Parser
from rdflib.syntax.parsers.n3p.n3proc import N3Processor

from rdflib.Graph import Graph, QuotedGraph, ConjunctiveGraph


class N3Parser(Parser):

    def __init__(self):
        pass
    
    def parse(self, source, graph):
	# we're currently being handed a Graph, not a ConjunctiveGraph
	assert graph.store.context_aware # is this implied by formula_aware
	assert graph.store.formula_aware

        conj_graph = ConjunctiveGraph(store=graph.store)
        conj_graph.default_context = graph.identifier # TODO: CG __init__ should have a default_context arg
        # TODO: update N3Processor so that it can use conj_graph as the sink
        sink = Sink(conj_graph)
        if False: 
            sink.quantify = lambda *args: True
            sink.flatten = lambda *args: True
        baseURI = graph.absolutize(source.getPublicId() or source.getSystemId() or "")
        p = N3Processor("nowhere", sink, baseURI=baseURI) # pass in "nowhere" so we can set data instead
	p.userkeys = True # bah
	p.data = source.getByteStream().read() # TODO getCharacterStream?
        p.parse()


class Sink(object):
    def __init__(self, graph): 
        self.graph = graph 

    def start(self, root): 
        pass

    def statement(self, s, p, o, f): 
        f.add((s, p, o))

    def quantify(self, formula, var): 
        #print "quantify(%s, %s)" % (formula, var)
        pass

