"""
From a Python file, expecting an RDF/XML pretty printed output::

    import rdflib.graph as g
    graph = g.Graph()
    graph.parse('filename.html', format='rdfa')
    print graph.serialize(format='pretty-xml')

For details on RDFa, the reader should consult the `RDFa syntax document
<http://www.w3.org/TR/rdfa-syntax>`_.

This is an adapted version of pyRdfa (`W3C RDFa Distiller page
<http://www.w3.org/2007/08/pyRdfa/>`_) by Ivan Herman
"""

import sys
import urllib
import xml.dom.minidom

from rdflib.graph import Graph
from rdflib.namespace import Namespace
from rdflib.term import BNode, URIRef
from rdflib.parser import Parser
from rdflib.plugins.parsers.rdfa.state import ExecutionContext
from rdflib.plugins.parsers.rdfa.parse import parse_one_node
from rdflib.plugins.parsers.rdfa.options import (Options, _add_to_comment_graph,
        DIST_NS, ERROR, GENERIC_XML, XHTML_RDFA, HTML5_RDFA)

from rdflib.plugins.parsers.rdfa.transform.headabout import head_about_transform


# These are part of the RDFa spec.
BUILT_IN_TRANSFORMERS = [
    head_about_transform
]

# Exception handling. Essentially, all the different exceptions are re-packaged
# into separate exception class, to allow for an easier management on the user
# level
class RDFaError(Exception) :
    """Just a wrapper around the local exceptions. It does not add any new
    functionality to the Exception class."""
    pass

# For some doctype and element name combinations an automatic switch to an
# input mode is done
_HOST_LANG = {
    ("http://www.w3.org/1999/xhtml", "html"): XHTML_RDFA,
    ("http://www.w3.org/2000/svg", "svg"): GENERIC_XML
}


class RDFaParser(Parser):

    def parse(self, source, sink,
            warnings=False, space_preserve=True,
            transformers=None, xhtml=True, lax=True):
        if transformers is None:
            transformers = []
        options = Options(warnings, space_preserve, transformers, xhtml, lax)
        baseURI = source.getPublicId()
        stream = source.getByteStream()
        dom = _try_process_source(stream, options)
        _process_DOM(dom, baseURI, sink, options)


def _process_DOM(dom, base, graph, options=None):
    """
    Core processing. The transformers ("pre-processing") is done on the DOM
    tree, the state is initialized, and the "real" RDFa parsing is done.
    The result is put into the provided Graph.

    The real work is done in the parser function :obj:`parse_one_node`.

    :param dom: XML DOM Tree node (for the top level)
    :param base: URI for the default "base" value (usually the URI of the file to be processed)
    :param options: :obj:`Options` for the distiller
    :raise RDFaError: when called via CGI, this encapsulates the possible exceptions raised by the RDFLib serializer or the processing itself
    """
    html = dom.documentElement
    # Perform the built-in and external transformations on the HTML tree. This is,
    # in simulated form, the hGRDDL approach of Ben Adida.
    for trans in options.transformers + BUILT_IN_TRANSFORMERS:
        trans(html, options)
    # Collect the initial state. This takes care of things
    # like base, top level namespace settings, etc.
    # Ensure the proper initialization.
    state = ExecutionContext(html, graph, base=base, options=options)
    # The top level subject starts with the current document; this
    # is used by the recursion
    subject = URIRef(state.base)
    # Parse the whole thing recursively and fill the graph.
    parse_one_node(html, graph, subject, state, [])
    if options.comment_graph.graph != None:
        # Add the content of the comment graph to the output.
        graph.bind("dist", DIST_NS)
        for t in options.comment_graph.graph:
            graph.add(t)

def _try_process_source(stream, options):
    """
    Tries to parse input as xhtml, xml (e.g. svg) or html(5), modifying options
    while figuring out input..

    Returns a DOM tree.
    """
    parse = xml.dom.minidom.parse
    try:
        dom = parse(stream)
        # Try to second-guess the input type
        # This is _not_ really kosher, but the minidom is not really namespace aware...
        # In practice the goal is to have the system recognize svg content automatically
        # First see if there is a default namespace defined for the document:
        top = dom.documentElement
        if top.hasAttribute("xmlns"):
            key = (top.getAttribute("xmlns"), top.nodeName)
            if key in _HOST_LANG:
                options.host_language = _HOST_LANG[key]
    except:
        # XML Parsing error in the input
        type, value, traceback = sys.exc_info()
        if options.host_language == GENERIC_XML or options.lax == False:
            raise RDFaError('Parsing error in input file: "%s"' % value)

        # XML Parsing error in the input
        msg = "XHTML Parsing error in input file: %s. Falling back on the HTML5 parser" % value
        if options != None and options.warnings:
            options.comment_graph.add_warning(msg)

        # in Ivan's original code he reopened the stream if it was from urllib 
        if isinstance(stream, urllib.addinfourl):
            stream = urllib.urlopen(stream.url)

        # Now try to see if and HTML5 parser is an alternative...
        try:
            from html5lib import HTMLParser, treebuilders
        except ImportError:
            # no alternative to the XHTML error, because HTML5 parser not available...
            msg2 = 'XHTML Parsing error in input file: %s. Though parsing is lax, HTML5 parser not available. Try installing html5lib <http://code.google.com/p/html5lib>' % value
            raise RDFaError(msg2)

        parser = HTMLParser(tree=treebuilders.getTreeBuilder("dom"))
        parse = parser.parse
        try:
            dom = parse(stream)
            # The host language has changed
            options.host_language = HTML5_RDFA
        except:
            # Well, even the HTML5 parser could not do anything with this...
            (type, value, traceback) = sys.exc_info()
            msg2 = 'Parsing error in input file as HTML5: "%s"' % value
            msg3 = msg + '\n' + msg2
            raise RDFaError, msg3

    return dom
