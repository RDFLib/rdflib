# -*- coding: utf-8 -*-
"""
The core parsing function of RDFa. Some details are
put into other modules to make it clearer to update/modify (eg, generation of literals, or managing the current state).

@summary: RDFa core parser processing step
@requires: U{RDFLib package<http://rdflib.net>}
@organization: U{World Wide Web Consortium<http://www.w3.org>}
@author: U{Ivan Herman<a href="http://www.w3.org/People/Ivan/">}
@license: This software is available for use under the
U{W3C® SOFTWARE NOTICE AND LICENSE<href="http://www.w3.org/Consortium/Legal/2002/copyright-software-20021231">}
"""

from rdflib.term import BNode, URIRef
from rdflib.namespace import RDF

from rdflib.plugins.parsers.rdfa.state import ExecutionContext
from rdflib.plugins.parsers.rdfa.literal import generate_literal
from rdflib.plugins.parsers.rdfa.embeddedrdf import handle_embeddedRDF
from rdflib.plugins.parsers.rdfa.options import GENERIC_XML, XHTML_RDFA, HTML5_RDFA


def parse_one_node(node, graph, parent_object, incoming_state, parent_incomplete_triples):
    """The (recursive) step of handling a single node. See the
    U{RDFa syntax document<http://www.w3.org/TR/rdfa-syntax>} for further details.

    @param node: the DOM node to handle
    @param graph: the RDF graph
    @type graph: RDFLib's Graph object instance
    @param parent_object: the parent's object, as an RDFLib URIRef
    @param incoming_state: the inherited state (namespaces, lang, etc)
    @type incoming_state: L{State.ExecutionContext}
    @param parent_incomplete_triples: list of hanging triples (the missing resource set to None) to be handled (or not)
    by the current node.
    @return: whether the caller has to complete it's parent's incomplete triples
    @rtype: Boolean
    """
    def _get_resources_for_attr(attr):
        """Get a series of resources encoded via CURIE-s for an attribute on a specific node.
        @param attr: the name of the attribute
        @return: a list of RDFLib URIRef instances
        """
        if not node.hasAttribute(attr):
            return []
        else:
            rel  = (attr == "rel") or (attr == "rev")
            prop = (attr == "property")
            return state.get_resources(node.getAttribute(attr), rel, prop)

    # Update the state. This means, for example, the possible local settings of
    # namespaces and lang
    state = ExecutionContext(node, graph, inherited_state=incoming_state)

    #---------------------------------------------------------------------------------
    # Handle the special case for embedded RDF, eg, in SVG1.2.
    # This may add some triples to the target graph that does not originate from RDFa parsing
    # If the function return TRUE, that means that an rdf:RDF has been found. No
    # RDFa parsing should be done on that subtree, so we simply return...
    if state.options.host_language == GENERIC_XML and node.nodeType == node.ELEMENT_NODE and handle_embeddedRDF(node, graph, state):
        return

    #---------------------------------------------------------------------------------
    # First, let us check whether there is anything to do at all. Ie,
    # whether there is any relevant RDFa specific attribute on the element
    #
    if not _has_one_of_attributes(node, "href", "resource", "about", "property", "rel", "rev", "typeof", "src"):
        # nop, there is nothing to do here, just go down the tree and return...
        for n in node.childNodes:
            if n.nodeType == node.ELEMENT_NODE : parse_one_node(n, graph, parent_object, state, parent_incomplete_triples)
        return


    #-----------------------------------------------------------------
    # The goal is to establish the subject and object for local processing
    # The behaviour is slightly different depending on the presense or not
    # of the @rel/@rev attributes
    current_subject = None
    current_object  = None

    if _has_one_of_attributes(node, "rel", "rev"):
        # in this case there is the notion of 'left' and 'right' of @rel/@rev
        # in establishing the new Subject and the objectResource

        # set first the subject
        if node.hasAttribute("about"):
            current_subject = state.get_Curie_ref(node.getAttribute("about"))
        elif node.hasAttribute("src"):
            current_subject = state.get_URI_ref(node.getAttribute("src"))
        elif node.hasAttribute("typeof"):
            current_subject = BNode()

        # get_URI_ref may return None in case of an illegal Curie, so
        # we have to be careful here, not use only an 'else'
        if current_subject == None:
            current_subject = parent_object

        # set the object resource
        if node.hasAttribute("resource"):
            current_object = state.get_Curie_ref(node.getAttribute("resource"))
        elif node.hasAttribute("href"):
            current_object = state.get_URI_ref(node.getAttribute("href"))
    else:
        # in this case all the various 'resource' setting attributes
        # behave identically, except that their value might be different
        # in terms of CURIE-s and they also have their own priority, of course
        if node.hasAttribute("about"):
            current_subject = state.get_Curie_ref(node.getAttribute("about"))
        elif node.hasAttribute("src"):
            current_subject = state.get_URI_ref(node.getAttribute("src"))
        elif node.hasAttribute("resource"):
            current_subject = state.get_Curie_ref(node.getAttribute("resource"))
        elif node.hasAttribute("href"):
            current_subject = state.get_URI_ref(node.getAttribute("href"))
        elif node.hasAttribute("typeof"):
            current_subject = BNode()

        # get_URI_ref may return None in case of an illegal Curie, so
        # we have to be careful here, not use only an 'else'
        if current_subject == None:
            current_subject = parent_object

        # in this case no non-literal triples will be generated, so the
        # only role of the current_objectResource is to be transferred to
        # the children node
        current_object = current_subject

    # ---------------------------------------------------------------------
    # The possible typeof indicates a number of type statements on the newSubject
    for defined_type in _get_resources_for_attr("typeof"):
        graph.add((current_subject, RDF.type, defined_type))

    # ---------------------------------------------------------------------
    # In case of @rel/@rev, either triples or incomplete triples are generated
    # the (possible) incomplete triples are collected, to be forwarded to the children
    incomplete_triples  = []
    for prop in _get_resources_for_attr("rel"):
        theTriple = (current_subject, prop, current_object)
        if current_object != None:
            graph.add(theTriple)
        else:
            incomplete_triples.append(theTriple)
    for prop in _get_resources_for_attr("rev"):
        theTriple = (current_object, prop, current_subject)
        if current_object != None:
            graph.add(theTriple)
        else:
            incomplete_triples.append(theTriple)

    # ----------------------------------------------------------------------
    # Generation of the literal values. The newSubject is the subject
    # A particularity of property is that it stops the parsing down the DOM tree if an XML Literal is generated,
    # because everything down there is part of the generated literal. For this purpose the recurse flag is set (and used later
    # in the parsing process).
    if node.hasAttribute("property"):
        # Generate the literal. It has been put it into a separate module to make it more managable
        # the overall return value should be set to true if any valid triple has been generated
        recurse = generate_literal(node, graph, current_subject, state)
    else:
        recurse = True

    # ----------------------------------------------------------------------
    # Setting the current object to a bnode is setting up a possible resource
    # for the incomplete triples downwards
    if current_object == None:
        object_to_children = BNode()
    else:
        object_to_children = current_object

    #-----------------------------------------------------------------------
    # Here is the recursion step for all the children
    if recurse:
        for n in node.childNodes:
            if n.nodeType == node.ELEMENT_NODE:
                parse_one_node(n, graph, object_to_children, state, incomplete_triples)

    # ---------------------------------------------------------------------
    # At this point, the parent's incomplete triples may be completed
    for s, p, o in parent_incomplete_triples:
        if s == None: s = current_subject
        if o == None: o = current_subject
        graph.add((s, p, o))

    # -------------------------------------------------------------------
    # This should be it...
    # -------------------------------------------------------------------
    return


def _has_one_of_attributes(node, *args):
    """
    Check whether one of the listed attributes is present on a (DOM) node.
    @param node: DOM element node
    @param args: possible attribute names
    @return: True or False
    @rtype: Boolean
    """
    return True in [ node.hasAttribute(attr) for attr in args ]


