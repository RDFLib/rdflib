import logging

from xml.sax.saxutils import XMLGenerator
from xml.dom import XML_NAMESPACE
from xml.sax.xmlreader import AttributesNSImpl

from rdflib.compat import etree

from rdflib import Literal, URIRef, BNode, Variable
from rdflib.query import Result, ResultParser, ResultSerializer, ResultException


SPARQL_XML_NAMESPACE = "http://www.w3.org/2005/sparql-results#"
RESULTS_NS_ET = "{%s}" % SPARQL_XML_NAMESPACE

log = logging.getLogger(__name__)


"""A Parser for SPARQL results in XML:

http://www.w3.org/TR/rdf-sparql-XMLres/

Bits and pieces borrowed from:
http://projects.bigasterisk.com/sparqlhttp/

Authors: Drew Perttula, Gunnar Aastrand Grimnes
"""


class XMLResultParser(ResultParser):
    def parse(self, source, content_type=None):
        return XMLResult(source)


class XMLResult(Result):
    def __init__(self, source, content_type=None):

        try:
            parser = etree.XMLParser(huge_tree=True)
            tree = etree.parse(source, parser)
        except TypeError:
            tree = etree.parse(source)

        boolean = tree.find(RESULTS_NS_ET + "boolean")
        results = tree.find(RESULTS_NS_ET + "results")

        if boolean is not None:
            type_ = "ASK"
        elif results is not None:
            type_ = "SELECT"
        else:
            raise ResultException("No RDF result-bindings or boolean answer found!")

        Result.__init__(self, type_)

        if type_ == "SELECT":
            self.bindings = []
            for result in results:
                r = {}
                for binding in result:
                    r[Variable(binding.get("name"))] = parseTerm(binding[0])
                self.bindings.append(r)

            self.vars = [
                Variable(x.get("name"))
                for x in tree.findall(
                    "./%shead/%svariable" % (RESULTS_NS_ET, RESULTS_NS_ET)
                )
            ]

        else:
            self.askAnswer = boolean.text.lower().strip() == "true"


def parseTerm(element):
    """rdflib object (Literal, URIRef, BNode) for the given
    elementtree element"""
    tag, text = element.tag, element.text
    if tag == RESULTS_NS_ET + "literal":
        if text is None:
            text = ""
        datatype = None
        lang = None
        if element.get("datatype", None):
            datatype = URIRef(element.get("datatype"))
        elif element.get("{%s}lang" % XML_NAMESPACE, None):
            lang = element.get("{%s}lang" % XML_NAMESPACE)

        ret = Literal(text, datatype=datatype, lang=lang)

        return ret
    elif tag == RESULTS_NS_ET + "uri":
        return URIRef(text)
    elif tag == RESULTS_NS_ET + "bnode":
        return BNode(text)
    else:
        raise TypeError("unknown binding type %r" % element)


class XMLResultSerializer(ResultSerializer):
    def __init__(self, result):
        ResultSerializer.__init__(self, result)

    def serialize(self, stream, encoding="utf-8"):

        writer = SPARQLXMLWriter(stream, encoding)
        if self.result.type == "ASK":
            writer.write_header([])
            writer.write_ask(self.result.askAnswer)
        else:
            writer.write_header(self.result.vars)
            writer.write_results_header()
            for b in self.result.bindings:
                writer.write_start_result()
                for key, val in b.items():
                    writer.write_binding(key, val)

                writer.write_end_result()

        writer.close()


# TODO: Rewrite with ElementTree?
class SPARQLXMLWriter:
    """
    Python saxutils-based SPARQL XML Writer
    """

    def __init__(self, output, encoding="utf-8"):
        writer = XMLGenerator(output, encoding)
        writer.startDocument()
        writer.startPrefixMapping("", SPARQL_XML_NAMESPACE)
        writer.startPrefixMapping("xml", XML_NAMESPACE)
        writer.startElementNS(
            (SPARQL_XML_NAMESPACE, "sparql"), "sparql", AttributesNSImpl({}, {})
        )
        self.writer = writer
        self._output = output
        self._encoding = encoding
        self._results = False

    def write_header(self, allvarsL):
        self.writer.startElementNS(
            (SPARQL_XML_NAMESPACE, "head"), "head", AttributesNSImpl({}, {})
        )
        for i in range(0, len(allvarsL)):
            attr_vals = {
                (None, "name"): str(allvarsL[i]),
            }
            attr_qnames = {
                (None, "name"): "name",
            }
            self.writer.startElementNS(
                (SPARQL_XML_NAMESPACE, "variable"),
                "variable",
                AttributesNSImpl(attr_vals, attr_qnames),
            )
            self.writer.endElementNS((SPARQL_XML_NAMESPACE, "variable"), "variable")
        self.writer.endElementNS((SPARQL_XML_NAMESPACE, "head"), "head")

    def write_ask(self, val):
        self.writer.startElementNS(
            (SPARQL_XML_NAMESPACE, "boolean"), "boolean", AttributesNSImpl({}, {})
        )
        self.writer.characters(str(val).lower())
        self.writer.endElementNS((SPARQL_XML_NAMESPACE, "boolean"), "boolean")

    def write_results_header(self):
        self.writer.startElementNS(
            (SPARQL_XML_NAMESPACE, "results"), "results", AttributesNSImpl({}, {})
        )
        self._results = True

    def write_start_result(self):
        self.writer.startElementNS(
            (SPARQL_XML_NAMESPACE, "result"), "result", AttributesNSImpl({}, {})
        )
        self._resultStarted = True

    def write_end_result(self):
        assert self._resultStarted
        self.writer.endElementNS((SPARQL_XML_NAMESPACE, "result"), "result")
        self._resultStarted = False

    def write_binding(self, name, val):
        assert self._resultStarted

        attr_vals = {
            (None, "name"): str(name),
        }
        attr_qnames = {
            (None, "name"): "name",
        }
        self.writer.startElementNS(
            (SPARQL_XML_NAMESPACE, "binding"),
            "binding",
            AttributesNSImpl(attr_vals, attr_qnames),
        )

        if isinstance(val, URIRef):
            self.writer.startElementNS(
                (SPARQL_XML_NAMESPACE, "uri"), "uri", AttributesNSImpl({}, {})
            )
            self.writer.characters(val)
            self.writer.endElementNS((SPARQL_XML_NAMESPACE, "uri"), "uri")
        elif isinstance(val, BNode):
            self.writer.startElementNS(
                (SPARQL_XML_NAMESPACE, "bnode"), "bnode", AttributesNSImpl({}, {})
            )
            self.writer.characters(val)
            self.writer.endElementNS((SPARQL_XML_NAMESPACE, "bnode"), "bnode")
        elif isinstance(val, Literal):
            attr_vals = {}
            attr_qnames = {}
            if val.language:
                attr_vals[(XML_NAMESPACE, "lang")] = val.language
                attr_qnames[(XML_NAMESPACE, "lang")] = "xml:lang"
            elif val.datatype:
                attr_vals[(None, "datatype")] = val.datatype
                attr_qnames[(None, "datatype")] = "datatype"

            self.writer.startElementNS(
                (SPARQL_XML_NAMESPACE, "literal"),
                "literal",
                AttributesNSImpl(attr_vals, attr_qnames),
            )
            self.writer.characters(val)
            self.writer.endElementNS((SPARQL_XML_NAMESPACE, "literal"), "literal")

        else:
            raise Exception("Unsupported RDF term: %s" % val)

        self.writer.endElementNS((SPARQL_XML_NAMESPACE, "binding"), "binding")

    def close(self):
        if self._results:
            self.writer.endElementNS((SPARQL_XML_NAMESPACE, "results"), "results")
        self.writer.endElementNS((SPARQL_XML_NAMESPACE, "sparql"), "sparql")
        self.writer.endDocument()
