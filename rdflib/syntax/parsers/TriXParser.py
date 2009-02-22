from rdflib.syntax.parsers import Parser
from rdflib.graph import ConjunctiveGraph

from xml.sax import make_parser
from xml.sax.saxutils import handler
from xml.sax.handler import ErrorHandler

from rdflib.syntax.parsers.TriXHandler import TriXHandler


def create_parser(store):
    parser = make_parser()
    # Workaround for bug in expatreader.py. Needed when
    # expatreader is trying to guess a prefix.
    parser.start_namespace_decl("xml", "http://www.w3.org/XML/1998/namespace")
    parser.setFeature(handler.feature_namespaces, 1)
    trix = TriXHandler(store)
    parser.setContentHandler(trix)
    parser.setErrorHandler(ErrorHandler())
    return parser


class TriXParser(Parser):
    """A parser for TriX. See http://swdev.nokia.com/trix/TriX.html"""

    def __init__(self):
        pass

    def parse(self, source, sink, **args):
        assert sink.store.context_aware
        g=ConjunctiveGraph(store=sink.store)
        
        self._parser = create_parser(g)
        content_handler = self._parser.getContentHandler()
        preserve_bnode_ids = args.get("preserve_bnode_ids", None)
        if preserve_bnode_ids is not None:
            content_handler.preserve_bnode_ids = preserve_bnode_ids
        # We're only using it once now
        #content_handler.reset()
        #self._parser.reset()
        self._parser.parse(source)



