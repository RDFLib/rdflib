from xml.sax import make_parser
from xml.sax.saxutils import handler
from xml.sax.handler import ErrorHandler

from rdflib.syntax.parsers.RDFXMLHandler import RDFXMLHandler


class RDFXMLParser(object):
    short_name = "xml"

    def __init__(self, store):
        self.store = store
    
    def parse(self, source):
        parser = make_parser()
        # Workaround for bug in expatreader.py. Needed when
        # expatreader is trying to guess a prefix.
        parser.start_namespace_decl("xml", "http://www.w3.org/XML/1998/namespace")
        parser.setFeature(handler.feature_namespaces, 1)
        parser.setContentHandler(RDFXMLHandler(self.store))
        parser.setErrorHandler(ErrorHandler())
        parser.parse(source)
