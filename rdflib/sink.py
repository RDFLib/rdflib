from collections import Counter

from rdflib.parser import Parser
from rdflib import plugin

class Sink(object):
    """
    A Sink that accepts triples/quads
    """

    context_aware = False
    formula_aware = False

    def __init__(self, namespace_manager):
        self.counter = Counter()

        self.namespace_manager = namespace_manager


    def parse(self, source=None, format=None, **args):

        if format is None:
            format = source.content_type
        if format is None:
            # raise Exception("Could not determine format for %r. You can" + \
            # "expicitly specify one with the format argument." % source)
            format = "application/rdf+xml"
        parser = plugin.get(format, Parser)()
        parser.parse(source, self, **args)
        return self

    def bind(self, prefix, namespace, override=True):
        self.namespace_manager.bind(prefix, namespace, override)


    def triple(self, triple, context = None):
        pass # abstract

class GraphSink(Sink):
    """
    A Sink that writes triples to a graph

    any context is ignored
    """

    def __init__(self, graph):
        Sink.__init__(self, graph.namespace_manager)
        self.store = graph.store
        self.context = graph.identifier

    def triple(self, triple, context=None):
        assert not context, "GraphSink cannot handle triples with context!"
        self.store.add(triple, self.context)

class ContextGraphSink(Sink):
    """
    A Sink that writes quads to a graph
    """

    context_aware = True

    def __init__(self, graph):
        Sink.__init__(self, graph.namespace_manager)
        self.store = graph.store
        self.default_context = graph.identifier

    def triple(self, triple, context=None):
        print 'C', context, self.default_context
        self.store.add(triple, context or self.default_context)



def create_graph_sink(graph):
    if graph.store.context_aware:
        return ContextGraphSink(graph)
    else:
        return GraphSink(graph)
