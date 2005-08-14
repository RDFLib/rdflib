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


