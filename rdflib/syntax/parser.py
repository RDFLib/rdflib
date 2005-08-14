from rdflib.exceptions import ParserDispatchNameError, ParserDispatchNameClashError
from rdflib.URLInputSource import URLInputSource
import rdflib.syntax.parsers

from rdflib.URIRef import URIRef
from xml.sax.xmlreader import InputSource
from xml.sax.saxutils import prepare_input_source 

import logging

class Parser(object):

    def __init__(self, parser):
        self.parser = parser

    def _get_store(self):
        return self.parser.store

    def _set_store(self, store):
        self.parser.store = store
        
    store = property(_get_store, _set_store)

    def prepare_input_source(self, source, publicID=None):
        if isinstance(source, InputSource):
            input_source = source
        else:
            if hasattr(source, "read") and not isinstance(source, Namespace): # we need to make sure it's not an instance of Namespace since Namespace instances have a read attr
                input_source = prepare_input_source(source)
            else:
		location = self.store.absolutize(source)
                input_source = URLInputSource(location)
		publicID = publicID or location
        if publicID:
            input_source.setPublicId(publicID)
	id = input_source.getPublicId()
	if id is None:
	    logging.info("no publicID set for source. Using '' for publicID.")
	    input_source.setPublicId("")
	return input_source

    def parse(self, source, publicID=None, format="xml"):
	input_source = self.prepare_input_source(source, publicID)
        return self.parser.parse(input_source)


