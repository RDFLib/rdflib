
from rdflib.syntax.serializer import SerializationDispatcher
from rdflib.syntax.parser import ParserDispatcher
from rdflib.URIRef import URIRef
#from rdflib import RDF

from urlparse import urljoin, urldefrag
from urllib import pathname2url, url2pathname
import os

class GraphLoader(object):


    def __init__(self, graph):
        self.graph = graph
        self.parser_dispatcher = ParserDispatcher(self.graph)                        
    
    def _context_id(self, uri):
        uri = uri.split("#", 1)[0]
        return URIRef("%s#context" % uri)

    def _absolutize(self, uri, defrag=1):
        base = urljoin("file:", pathname2url(os.getcwd()))
        uri = urljoin("%s/" % base, uri)
        if defrag:
            uri, frag = urldefrag(uri)            
        return URIRef(uri)

    def load(self, location, publicID=None, format="xml"):
        """ Load a URL into the graph using either the publicID or the
        location (if publicID is not provided )as the context of the
        new graph.  Removes any information in the old context,
        returns the new context."""
        location = self._absolutize(location)
        id = self._context_id(publicID or location)
        self.graph.remove_context(id)
        context = self.graph.get_context(id)
#        context.add((id, RDF.type, CONTEXT))
#        context.add((id, SOURCE, location))
        context.graphLoader().parse(source=location, publicID=publicID, format=format)
        return context

    def parse(self, source, publicID=None, format="xml"):
        """ Parses the given source into the graph. """
        return self.parser_dispatcher(source=source, publicID=publicID, format=format)

class GraphUnloader(object):

    def __init__(self, graph):
        self.graph = graph
        self.serialization_dispatcher = SerializationDispatcher(self.graph)

    def save(self, location, format="xml"):
        """ Serializes the store to a given location """
        return self.serialize(destination=location, format=format)

    def serialize(self, destination=None, format="xml"):
        """ Serializes the store to a given location.  Exactly how is this different from save? ;) """        
        return self.serialization_dispatcher(destination=destination, format=format)            

    
