from xml.sax import make_parser
from xml.sax.saxutils import handler
from xml.sax.handler import ErrorHandler

from rdflib.syntax.parsers.RDFXMLHandler import RDFXMLHandler


def create_parser(store):
    parser = make_parser()
    # Workaround for bug in expatreader.py. Needed when
    # expatreader is trying to guess a prefix.
    parser.start_namespace_decl("xml", "http://www.w3.org/XML/1998/namespace")
    parser.setFeature(handler.feature_namespaces, 1)
    rdfxml = RDFXMLHandler(store)
    #rdfxml.setDocumentLocator(_Locator(self.url, self.parser))
    parser.setContentHandler(rdfxml)
    parser.setErrorHandler(ErrorHandler())
    return parser


class RDFXMLParser(object):
    short_name = "xml"

    def __init__(self, store):
        self.store = store
        self._parser = create_parser(store)
    
    def parse(self, source):
        #@@ reset self._parser?
        self._parser.parse(source)



