from rdflib.parser import Parser
from rdflib.plugins.parsers.ntriples import NTriplesParser

__all__ = ["NTSink", "NTParser"]


class NTSink(object):
    def __init__(self, graph):
        self.graph = graph

    def triple(self, s, p, o):
        self.graph.add((s, p, o))


class NTParser(Parser):
    """parser for the ntriples format, often stored with the .nt extension

    See http://www.w3.org/TR/rdf-testcases/#ntriples"""

    def __init__(self):
        super(NTParser, self).__init__()

    def parse(self, source, sink, **kwargs):
        '''
        Parse the NT format

        :type source: `rdflib.parser.InputSource`
        :param source: the source of NT-formatted data
        :type sink: `rdflib.graph.Graph`
        :param sink: where to send parsed triples
        :param kwargs: Additional arguments to pass to `.NTriplesParser.parse`
        '''
        f = source.getByteStream()  # TODO getCharacterStream?
        parser = NTriplesParser(NTSink(sink))
        parser.parse(f, **kwargs)
        f.close()
