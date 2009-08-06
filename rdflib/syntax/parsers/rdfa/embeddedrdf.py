# -*- coding: utf-8 -*-
"""
Extracting possible embedded RDF/XML content from the file and parse it separately into the Graph. This is used, for example
by U{SVG 1.2 Tiny<http://www.w3.org/TR/SVGMobile12/>}.

@author: U{Ivan Herman<a href="http://www.w3.org/People/Ivan/">}
@license: This software is available for use under the
U{W3C® SOFTWARE NOTICE AND LICENSE<href="http://www.w3.org/Consortium/Legal/2002/copyright-software-20021231">}
@contact: Ivan Herman, ivan@w3.org
"""

from StringIO   import StringIO

def handle_embeddedRDF(node, graph, state):
    """
    Check if the node is the top level rdf element for RDF/XML. If so, the content is parsed and added to the target graph. Note that if an separate
    base is defined in the state, the C{xml:base} attribute will be added to the C{rdf} node before parsing.
    @param node: a DOM node for the top level xml element
    @param graph: target rdf graph
    @type graph: RDFLib's Graph object instance
    @param state: the inherited state (namespaces, lang, etc)
    @type state: L{State.ExecutionContext}
    @return: whether an RDF/XML content has been detected or not. If TRUE, the RDFa processing should not occur on the node and its descendents.
    @rtype: Boolean

    """
    if node.localName == "RDF" and node.namespaceURI == "http://www.w3.org/1999/02/22-rdf-syntax-ns#":
        node.setAttribute("xml:base",state.base)
        rdf = StringIO(node.toxml())
        graph.parse(rdf)
        return True
    else:
        return False

