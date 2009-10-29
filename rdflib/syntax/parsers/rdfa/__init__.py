# -*- coding: utf-8 -*-
"""
##########################################
RDFa Parser for RDFLib
##########################################

For details on RDFa, the reader should consult the `RDFa syntax document
<http://www.w3.org/TR/rdfa-syntax>`_.

(Simple) Usage
==============

From a Python file, expecting an RDF/XML pretty printed output::

    import rdflib.graph as g
    graph = g.Graph()
    graph.parse('filename.html', format='rdfa')
    print graph.serialize(format='pretty-xml')

Options
=======

The parser also implements some optional features that are not fully part of
the RDFa syntax. At the moment these are:

- extra warnings and information (eg, missing ``@profile, @version`` attribute
  or DTD, possibly erroneous CURIE:s) are added to the output graph
- possibility that plain literals are normalized in terms of white spaces.
  Default: false. (The RDFa specification requires keeping the white spaces and
  leave applications to normalize them, if needed)
- extra, built-in transformers are executed on the DOM tree prior to RDFa
  processing (see below)

Options are collected in an instance of the :obj:`Options` class and passed to
the processing functions as an extra argument. Eg, if extra warnings are
required, the code may be::

    graph.parse('filename.html', format='rdfa', warnings=True)
    print graph.serialize(format='pretty-xml')

Transformers
============

The package uses the concept of 'transformers': the parsed DOM tree is possibly
transformed before performing the real RDFa processing. This transformer
structure makes it possible to add additional 'services' without distoring the
core code of RDFa processing. (Ben Adida referred to these as "hGRDDL"...)

The user of the package may refer to such and pass them to the parse method via
an the ``transformers`` option. The caller of the package may also add his/her
transformer modules. Here is a possible usage with the 'openid' transformer
added to the call::

    from pyRdfa.transform.OpenID import OpenID_transform
    graph.parse('filename.html', format='rdfa',
            transformers=[OpenID_transform])
    print graph.serialize(format='pretty-xml')

Note that the current option instance is passed to all transformers as extra
parameters. Extensions of the package may make use of that to control the
transformers, if necessary.

HTML5
=====

The `RDFa syntax <http://www.w3.org/TR/rdfa-syntax>`_ is defined in terms of
XHTML. However, in future, `HTML5 <http://www.w3.org/TR/html5/>`_ may also be
considered as a carrier language for RDFa. Therefore, the distiller can be
started up in two different modes: - in a "strict" XML mode the input is parsed
by an XML parser (Python's xml minidom), and an exception is raised if the
parser experiences problems - in a "lax" mode, meaning that if the XML parser
has problems, then there is a fallback on an `HTML5 parser
<http://code.google.com/p/html5lib/>`_ to parse the input. This also covers
HTML4 "tag soup" files.

Requires: `html5lib <http://code.google.com/p/html5lib/>`_ for the HTML5
parsing. Note possible dependecies on Python's version on the project's web
site.

SVG 1.2 (and XML host languages in general)
===========================================

The `SVG 1.2 Tiny <http://www.w3.org/TR/SVGMobile12/>`_ specification has also
adopted RDFa as a means to add metadata to SVG content. This means that RDFa
attributes can also be used to express metadata. There are, however, two subtle
differences when using RDFa with XHTML or with SVG, namely:

- SVG also has a more "traditional" way of adding RDF metadata to a file,
  namely by directly including RDF/XML into SVG (as a child of a ``metadata``
  element. According to the specification of SVG, the graphs extracted from an
  SVG file and originating from such embedded contents and the graph extracted
  via RDFa attributes should be merged to yield the output RDF graph.
- XHTML1 does *not* use the ``xml:base`` functionality, whereas SVG
  (and generic XML applications) do.

By default, the distiller runs in XHTML 'mode', ie, these two extra features
are not implemented. However, if parse is given ``xhtml=False``, distiller
considers that the underlying host language is pure XML, and these two
additional features are also implemented. An example would be::

    graph.parse('filename.svg', format='rdfa', xhtml=False)

Attribution
===========================================

This is an adapted version of pyRdfa (`W3C RDFa Distiller page
<http://www.w3.org/2007/08/pyRdfa/>`_) by Ivan Herman
(<http://www.w3.org/People/Ivan/>). It replaces the previous RDFa parser by
Elias Torres (<elias@torrez.us>).

The pyRdfa package has the following relevant info:

Author: `Ivan Herman <a href="http://www.w3.org/People/Ivan/">`_.
License: This software is available for use under the `W3C® SOFTWARE NOTICE AND
LICENSE <http://www.w3.org/Consortium/Legal/2002/copyright-software-20021231>.

This package is a part of and falls under the licence of RDFLib.
"""

import sys
from xml.dom import minidom

from rdflib.graph import Graph
from rdflib.namespace import Namespace
from rdflib.term import BNode, URIRef

from rdflib.syntax.parsers import Parser

import xml.dom.minidom

from rdflib.syntax.parsers.rdfa.state import ExecutionContext
from rdflib.syntax.parsers.rdfa.parse import parse_one_node
from rdflib.syntax.parsers.rdfa.options import (Options, _add_to_comment_graph,
        DIST_NS, ERROR, GENERIC_XML, XHTML_RDFA, HTML5_RDFA)

from rdflib.syntax.parsers.rdfa.transform.headabout import head_about_transform


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
            transformers=None, xhtml=True, lax=False):
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
    parse = minidom.parse
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

        # Now try to see if and HTML5 parser is an alternative...
        try:
            from html5lib import HTMLParser, treebuilders
        except ImportError:
            # no alternative to the XHTML error, because HTML5 parser not available...
            msg2 = 'XHTML Parsing error in input file: %s. Though parsing is lax, HTML5 parser not available' % value
            raise RDFaError(msg2)

        parser = html5lib.HTMLParser(tree=treebuilders.getTreeBuilder("dom"))
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

