from rdflib.exceptions import ParserDispatchNameError, ParserDispatchNameClashError
import rdflib.syntax.parsers
from rdflib.URLInputSource import URLInputSource
from rdflib.URIRef import URIRef
from xml.sax.xmlreader import InputSource

from urlparse import urljoin, urldefrag
from urllib import pathname2url, url2pathname
import os

class AbstractParser(object):

    def __init__(self, store):
        self.__short_name = ""
        self.store = store
        
    def parse(self, source):
        pass


class ParserDispatcher(object):

    def __init__(self, store):
        self.store = store
        for ser in rdflib.syntax.parsers.__all__:
            module = __import__("parsers." + ser, globals(), locals(), ["parsers"])
            aParser  = getattr(module, ser)
            short_name = getattr(aParser, "short_name")
            self.add(aParser, name=short_name)
                                   
    def add(self, parser, name=None):
        #first, check if there's a name or a shortname, else throw exception
        if name != None:
            the_name = name
        elif hasattr(parser, "short_name"):
            the_name = parser.short_name
        else:
            msg = "You didn't set a short name for the parser or pass in a name to add()"
            raise ParserDispatchNameError(msg)
        #check for name clash
        if hasattr(self, the_name):
            raise ParserDispatchNameClashError("That name is already registered.")
        else:
            setattr(self, the_name, parser(self.store))

    def absolutize(self, uri, defrag=1):
        base = urljoin("file:", pathname2url(os.getcwd()))        
        uri = urljoin("%s/" % base, uri)
        if defrag:
            uri, frag = urldefrag(uri)            
        return URIRef(uri)

    def __call__(self, source, publicID=None, format="xml"):
        if isinstance(source, InputSource):
            input_source = source
        else:
            # TODO: way to detect source of string vs. location?
            input_source = URLInputSource(self.absolutize(source))
        if publicID:
            input_source.setPublicId(publicID)

        return getattr(self, format).parse(input_source)

