# -*- coding: utf-8 -*-
"""
Implementation of the Literal handling. Details of the algorithm are described on
U{RDFa Task Force's wiki page<http://www.w3.org/2006/07/SWD/wiki/RDFa/LiteralObject>}.

@summary: RDFa Literal generation
@requires: U{RDFLib package<http://rdflib.net>}
@organization: U{World Wide Web Consortium<http://www.w3.org>}
@author: U{Ivan Herman<a href="http://www.w3.org/People/Ivan/">}
@license: This software is available for use under the
U{W3C® SOFTWARE NOTICE AND LICENSE<href="http://www.w3.org/Consortium/Legal/2002/copyright-software-20021231">}
"""

import re
from rdflib.namespace import RDF
from rdflib.term import Literal

XMLLiteral = RDF.XMLLiteral


def __putBackEntities(str):
    """Put 'back' entities for the '&', '<', and '>' characters, to produce kosher XML string.
    Used by XML Literal
    @param str: string to be converted
    @return: string with entities
    @rtype: string
    """
    return str.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

#### The real meat...
def generate_literal(node, graph, subject, state):
    """Generate the literal the C{@property}, taking into account datatype, etc.
    Note: this method is called only if the C{@property} is indeed present, no need to check.

    This method is an encoding of the algorithm documented
    U{task force's wiki page<http://www.w3.org/2006/07/SWD/wiki/RDFa/LiteralObject>}.

    The method returns a value whether the literal is a 'normal' literal (regardless of its datatype)
    or an XML Literal. The return value is True or False, respectively. This value is used to control whether
    the parser should stop recursion. This also means that that if the literal is generated from @content,
    the return value is False, regardless of the possible @datatype value.

    @param node: DOM element node
    @param graph: the (RDF) graph to add the properies to
    @param subject: the RDFLib URIRef serving as a subject for the generated triples
    @param state: the current state to be used for the CURIE-s
    @type state: L{State.ExecutionContext}
    @return: whether the literal is a 'normal' or an XML Literal (return value is True or False, respectively). Note that if the literal is generated from @content, the return value is False, regardless of the possible @datatype value.
    @rtype: Boolean
    """
    def _get_literal(Pnode):
        """
        Get (recursively) the full text from a DOM Node.

        @param Pnode: DOM Node
        @return: string
        """
        rc = ""
        for node in Pnode.childNodes:
            if node.nodeType == node.TEXT_NODE:
                rc = rc + node.data
            elif node.nodeType == node.ELEMENT_NODE:
                rc = rc + _get_literal(node)

        # The decision of the group in February 2008 is not to normalize the result by default.
        # This is reflected in the default value of the option
        if state.options.space_preserve:
            return rc
        else:
            return re.sub(r'(\r| |\n|\t)+', " ", rc).strip()
    # end getLiteral

    def _get_XML_literal(Pnode):
        """
        Get (recursively) the XML Literal content of a DOM Node. (Most of the processing is done
        via a C{node.toxml} call of the xml minidom implementation.)

        @param Pnode: DOM Node
        @return: string
        """
        def collectPrefixes(prefixes, node):
            def addPf(prefx, string):
                pf = string.split(':')[0]
                if pf != string and pf not in prefx : prefx.append(pf)
            # edn addPf

            # first the local name of the node
            addPf(prefixes, node.tagName)
            # get all the attributes and children
            for child in node.childNodes:
                if child.nodeType == node.ELEMENT_NODE:
                    collectPrefixes(prefixes, child)
                elif child.nodeType == node.ATTRIBUTE_NODE:
                    addPf(prefixes, node.child.name)
        # end collectPrefixes

        rc = ""
        prefixes = []
        for node in Pnode.childNodes:
            if node.nodeType == node.ELEMENT_NODE:
                collectPrefixes(prefixes, node)

        for node in Pnode.childNodes:
            if node.nodeType == node.TEXT_NODE:
                rc = rc + __putBackEntities(node.data)
            elif node.nodeType == node.ELEMENT_NODE:
                # Decorate the element with namespaces and lang values
                for prefix in prefixes:
                    if prefix in state.ns and not node.hasAttribute("xmlns:%s" % prefix):
                        node.setAttribute("xmlns:%s" % prefix, "%s" % state.ns[prefix])
                # Set the default namespace, if not done (and is available)
                if not node.getAttribute("xmlns") and state.defaultNS != None:
                    node.setAttribute("xmlns", state.defaultNS)
                # Get the lang, if necessary
                if not node.getAttribute("xml:lang") and state.lang != None:
                    node.setAttribute("xml:lang", state.lang)
                rc = rc + node.toxml()
        return rc
        # If XML Literals must be canonicalized for space, then this is the return line:
        #return re.sub(r'(\r| |\n|\t)+', " ", rc).strip()
    # end getXMLLiteral

    # Most of the times the literal is a 'normal' one, ie, not an XML Literal
    retval = True

    # Get the Property URI-s
    props = state.get_resources(node.getAttribute("property"), prop=True)

    # Get, if exists, the value of @datatype, and figure out the language
    datatype = None
    dtset    = False
    lang     = state.lang
    if node.hasAttribute("datatype"):
        dtset = True
        dt = node.getAttribute("datatype")
        if dt != "":
            datatype = state.get_resource(dt)
            lang = None

    # The simple case: separate @content attribute
    if node.hasAttribute("content"):
        val = node.getAttribute("content")
        object = Literal(node.getAttribute("content"), datatype=datatype, lang=lang)
        # The value of datatype has been set, and the keyword paramaters take care of the rest
    else:
        # see if there *is* a datatype (even if it is empty!)
        if dtset:
            # yep. The Literal content is the pure text part of the current element:
            # We have to check whether the specified datatype is, in fact, and
            # explicit XML Literal
            if datatype == XMLLiteral:
                object = Literal(_get_XML_literal(node), datatype=XMLLiteral)
                retval = False
            else:
                object = Literal(_get_literal(node), datatype=datatype, lang=lang)
        else:
            # no controlling @datatype. We have to see if there is markup in the contained
            # element
            if True in [ n.nodeType == node.ELEMENT_NODE for n in node.childNodes ]:
                # yep, and XML Literal should be generated
                object = Literal(_get_XML_literal(node), datatype=XMLLiteral)
                retval = False
            else:
                val = _get_literal(node)
                # At this point, there might be entities in the string that are returned as real characters by the dom
                # implementation. That should be turned back
                object = Literal(_get_literal(node), lang=lang)

    # NOTE: rdflib<2.5 didn't equal Literal with lang="", hence this check
    # proably always passed?
    # All tests pass with this check removed; going with that..
    ## The object may be empty, for example in an ill-defined <meta> element...
    if True:#object != "":
        for prop in props:
            graph.add((subject, prop, object))

    return retval

