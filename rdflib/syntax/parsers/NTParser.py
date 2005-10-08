from rdflib.syntax.parsers import Parser
from rdflib.syntax.parsers.ntriples import NTriplesParser


class NTSink(object):
    def __init__(self, graph):
        self.graph = graph

    def triple(self, s, p, o):
        self.graph.add((s, p, o))


import codecs

class NTParser(Parser):
    
    def __init__(self):
        super(NTParser, self).__init__()

    def parse(self, source, sink, baseURI=None):
	f = source.getByteStream() # TODO getCharacterStream?
        parser = NTriplesParser(NTSink(sink))
        parser.parse(f)
        f.close()
       

