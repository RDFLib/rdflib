from rdflib.graph import ConjunctiveGraph
from rdflib.syntax.parsers import Parser
#from rdflib.syntax.parsers.n3p.n3proc import N3Processor

from rdflib.syntax.parsers.notation3 import SinkParser, RDFSink


class N3Parser(Parser):

    def __init__(self):
        pass

    def parse(self, source, graph):
        # we're currently being handed a Graph, not a ConjunctiveGraph
        assert graph.store.context_aware # is this implied by formula_aware
        assert graph.store.formula_aware

        conj_graph = ConjunctiveGraph(store=graph.store)
        conj_graph.default_context = graph # TODO: CG __init__ should have a default_context arg
        # TODO: update N3Processor so that it can use conj_graph as the sink
        conj_graph.namespace_manager = graph.namespace_manager
        sink = RDFSink(conj_graph)

        baseURI = graph.absolutize(source.getPublicId() or source.getSystemId() or "")
        p = SinkParser(sink, baseURI=baseURI) 
        
        p.loadStream(source.getByteStream())

        for prefix, namespace in p._bindings.items():
             conj_graph.bind(prefix, namespace)



