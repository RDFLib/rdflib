from rdflib.exceptions import ParserDispatchNameError, ParserDispatchNameClashError
from rdflib.URLInputSource import URLInputSource
import rdflib.syntax.parsers

from rdflib.URIRef import URIRef
from xml.sax.xmlreader import InputSource

from urlparse import urljoin, urldefrag
from urllib import pathname2url, url2pathname
import os


class Parser(object):

    def __init__(self, parser):
        self.parser = parser

    def _get_store(self):
        return self.parser.store

    def _set_store(self, store):
        self.parser.store = store
        
    store = property(_get_store, _set_store)

    def absolutize(self, uri, defrag=1):
        base = urljoin("file:", pathname2url(os.getcwd()))        
        uri = urljoin("%s/" % base, uri)
        if defrag:
            uri, frag = urldefrag(uri)            
        return URIRef(uri)

    def parse(self, source, publicID=None, format="xml"):
        if isinstance(source, InputSource):
            input_source = source
        else:
            # TODO: way to detect source of string vs. location?
            input_source = URLInputSource(self.absolutize(source))
        if publicID:
            input_source.setPublicId(publicID)

        return self.parser.parse(input_source)


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
        if self.store.context_aware:
            location = self._absolutize(location)
            id = self._context_id(publicID or location)
            self.store.remove_context(id)
            context = self.store.get_context(id)
            # context.add((id, RDF.type, CONTEXT))
            # context.add((id, SOURCE, location))
        else:
            context = self.store
        context.parse(source=location, publicID=publicID, format=format)
        return context
