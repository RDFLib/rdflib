from rdflib.exceptions import ParserDispatchNameError, ParserDispatchNameClashError
from rdflib.URLInputSource import URLInputSource
import rdflib.syntax.parsers

from rdflib.URIRef import URIRef
from rdflib.Namespace import Namespace
from xml.sax.xmlreader import InputSource
from xml.sax.saxutils import prepare_input_source 

import logging

class Parser(object):

    def __init__(self, parser):
        self.parser = parser

    def parse(self, sink, source):
	self.parser.parse(source, sink)


