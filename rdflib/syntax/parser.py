from rdflib.exceptions import ParserDispatchNameError, ParserDispatchNameClashError
from rdflib.URLInputSource import URLInputSource
import rdflib.syntax.parsers

from rdflib.URIRef import URIRef
from xml.sax.xmlreader import InputSource
from xml.sax.saxutils import prepare_input_source 


class Parser(object):

    def __init__(self, parser):
        self.parser = parser

    def _get_store(self):
        return self.parser.store

    def _set_store(self, store):
        self.parser.store = store
        
    store = property(_get_store, _set_store)

    def parse(self, source, publicID=None, format="xml"):
        if isinstance(source, InputSource):
            input_source = source
        else:
            # TODO: way to detect source of string vs. location?            
            if hasattr(source, "read"):
                input_source = prepare_input_source(source)
            else:
                input_source = URLInputSource(self.store.absolutize(source))
        if publicID:
            input_source.setPublicId(publicID)

        return self.parser.parse(input_source)


    def _context_id(self, uri):
        uri = uri.split("#", 1)[0]
        return URIRef("%s#context" % uri)

    def load(self, location, publicID=None, format="xml"):
        """ Load a URL into the graph using either the publicID or the
        location (if publicID is not provided )as the context of the
        new graph.  Removes any information in the old context,
        returns the new context."""
        if self.store.context_aware:
            location = self.store.absolutize(location)
            id = self._context_id(publicID or location)
            self.store.remove_context(id)
            context = self.store.get_context(id)
            # context.add((id, RDF.type, CONTEXT))
            # context.add((id, SOURCE, location))
        else:
            context = self.store
        context.parse(source=location, publicID=publicID, format=format)
        return context
