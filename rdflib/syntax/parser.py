from rdflib.exceptions import ParserDispatchNameError, ParserDispatchNameClashError
from rdflib.URLInputSource import URLInputSource
import rdflib.syntax.parsers

from rdflib.URIRef import URIRef
from xml.sax.xmlreader import InputSource

from urlparse import urljoin, urldefrag
from urllib import pathname2url, url2pathname
import os

_module_info = {}

def register(short_name, module_path, class_name):
    _module_info[short_name] = (module_path, class_name)

register('xml', 'rdflib.syntax.parsers.RDFXMLParser', 'RDFXMLParser')
register('nt', 'rdflib.syntax.parsers.NTParser', 'NTParser')


class AbstractParser(object):

    def __init__(self, store):
        self.__short_name = ""
        self.store = store
        
    def parse(self, source):
        pass


class ParserDispatcher(object):

    def __init__(self, store):
        self.store = store
        self.__parser = {}        
        self.__module_info = dict(_module_info)        
                                   
    # TODO: abstract common bits from this and serializer for 
    def register(self, short_name, module_path, class_name):
        self.__module_info[short_name] = (module_path, class_name)        

    def parser(self, format):
        parser = self.__parser.get(format, None)
        if parser is None:
            module_path, class_name = self.__module_info[format]
            module = __import__(module_path, globals(), locals(), True)
            parser = getattr(module, class_name)(self.store)
            self.__parser[format] = parser
        return parser

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

        return getattr(self, format).parse(input_source)


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
