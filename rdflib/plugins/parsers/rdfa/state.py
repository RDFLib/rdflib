# -*- coding: utf-8 -*-
"""
Parser's execution context (a.k.a. state) object and handling. The state includes:

  - dictionary for namespaces. Keys are the namespace prefixes, values are RDFLib Namespace instances
  - language, retrieved from C{@xml:lang}
  - URI base, determined by <base> (or set explicitly). This is a little bit superfluous, because the current RDFa syntax does not make use of C{@xml:base}; ie, this could be a global value.  But the structure is prepared to add C{@xml:base} easily, if needed.
  - options, in the form of an L{Options<pyRdfa.Options>} instance

The execution context object is also used to turn relative URI-s and CURIES into real URI references.

@summary: RDFa core parser processing step
@requires: U{RDFLib package<http://rdflib.net>}
@organization: U{World Wide Web Consortium<http://www.w3.org>}
@author: U{Ivan Herman<a href="http://www.w3.org/People/Ivan/">}
@license: This software is available for use under the
U{W3C® SOFTWARE NOTICE AND LICENSE<href="http://www.w3.org/Consortium/Legal/2002/copyright-software-20021231">}

@var XHTML_PREFIX: prefix for the XHTML vocabulary namespace
@var XHTML_URI: URI prefix of the XHTML vocabulary
@var RDFa_PROFILE: the official RDFa profile URI
@var RDFa_VERSION: the official version string of RDFa
@var usual_protocols: list of "usual" protocols (used to generate warnings when CURIES are not protected)
@var _predefined_rel: list of predefined C{@rev} and C{@rel} values that should be mapped onto the XHTML vocabulary URI-s.
@var _predefined_property: list of predefined C{@property} values that should be mapped onto the XHTML vocabulary URI-s. (At present, this list is empty, but this has been an ongoing question in the group, so the I{mechanism} of checking is still there.)
@var __bnodes: dictionary of blank node names to real blank node
@var __empty_bnode: I{The} Bnode to be associated with the CURIE of the form "C{_:}".
"""

from rdflib.namespace import Namespace, RDF, RDFS
from rdflib.term import BNode, URIRef
from rdflib.plugins.parsers.rdfa.options import Options, GENERIC_XML, XHTML_RDFA, HTML5_RDFA

import re
import random
import urlparse

RDFa_PROFILE    = "http://www.w3.org/1999/xhtml/vocab"
RDFa_VERSION    = "XHTML+RDFa 1.0"
RDFa_PublicID   = "-//W3C//DTD XHTML+RDFa 1.0//EN"
RDFa_SystemID   = "http://www.w3.org/MarkUp/DTD/xhtml-rdfa-1.dtd"

usual_protocols = ["http", "https", "mailto", "ftp", "urn", "gopher", "tel", "ldap", "doi", "news"]

####Predefined @rel/@rev/@property values
# predefined values for the @rel and @rev values. These are considered to be part of a specific
# namespace, defined by the RDFa document.
# At the moment, there are no predefined @property values, but the code is there in case
# some will be defined
XHTML_PREFIX = "xhv"
XHTML_URI    = "http://www.w3.org/1999/xhtml/vocab#"

_predefined_rel  = ['alternate', 'appendix', 'cite', 'bookmark', 'chapter', 'contents',
'copyright', 'glossary', 'help', 'icon', 'index', 'meta', 'next', 'p3pv1', 'prev',
'role', 'section', 'subsection', 'start', 'license', 'up', 'last', 'stylesheet', 'first', 'top']

_predefined_property  = []

#### Managing blank nodes for CURIE-s
__bnodes = {}
__empty_bnode = BNode()
def _get_bnode_from_Curie(var):
    """
    'Var' gives the string after the coloumn in a CURIE of the form C{_:XXX}. If this variable has been used
    before, then the corresponding BNode is returned; otherwise a new BNode is created and
    associated to that value.
    @param var: CURIE BNode identifier
    @return: BNode
    """
    if len(var) == 0:
        return __empty_bnode
    if var in __bnodes:
        return __bnodes[var]
    else:
        retval = BNode()
        __bnodes[var] = retval
        return retval

#### Quote URI-s
import urllib
# 'safe' characters for the URI quoting, ie, characters that can safely stay as they are. Other
# special characters are converted to their %.. equivalents for namespace prefixes
_unquotedChars = ':/\?=#'
_warnChars     = [' ', '\n', '\r', '\t']
def _quote(uri, options):
    """
    'quote' a URI, ie, exchange special characters for their '%..' equivalents. Some of the characters
    may stay as they are (listed in L{_unquotedChars}. If one of the characters listed in L{_warnChars}
    is also in the uri, an extra warning is also generated.
    @param uri: URI
    @param options:
    @type options: L{Options<pyRdfa.Options>}
    """
    suri = uri.strip()
    for c in _warnChars:
        if suri.find(c) != -1:
            if options != None:
                options.comment_graph.add_warning('Unusual character in uri:%s; possible error?' % suri)
            break
    return urllib.quote(suri, _unquotedChars)


#### Core Class definition
class ExecutionContext(object):
    """State at a specific node, including the current set
    of namespaces in the RDFLib sense, the
    current language, and the base. The class is also used to interpret URI-s and CURIE-s to produce
    URI references for RDFLib.

    @ivar options: reference to the overall options
    @type ivar: L{Options.Options}
    @ivar base: the 'base' URI
    @ivar defaultNS: default namespace
    @ivar lang: language tag (possibly None)
    @ivar ns: dictionary of namespaces
    @type ns: dictionary, each value is an RDFLib Namespace object

    """
    def __init__(self, node, graph, inherited_state=None, base="", options=None):
        """
        @param node: the current DOM Node
        @param graph: the RDFLib Graph
        @keyword inherited_state: the state as inherited
        from upper layers. This inherited_state is mixed with the state information
        retrieved from the current node.
        @type inherited_state: L{State.ExecutionContext}
        @keyword base: string denoting the base URI for the specific node. This overrides the possible
        base inherited from the upper layers. The
        current XHTML+RDFa syntax does not allow the usage of C{@xml:base}, but SVG1.2 does, so this is
        necessary for SVG (and other possible XML dialects that accept C{@xml:base})
        @keyword options: invocation option
        @type options: L{Options<pyRdfa.Options>}
        """
        #-----------------------------------------------------------------
        # settling the base
        # note that, strictly speaking, it is not necessary to add the base to the
        # context, because there is only one place to set it (<base> element of the <header>).
        # It is done because it is prepared for a possible future change in direction of
        # accepting xml:base on each element.
        # At the moment, it is invoked with a 'None' at the top level of parsing, that is
        # when the <base> element is looked for.
        if inherited_state:
            self.base            = inherited_state.base
            self.options         = inherited_state.options
            # for generic XML versions the xml:base attribute should be handled
            if self.options.host_language == GENERIC_XML and node.hasAttribute("xml:base"):
                self.base = node.getAttribute("xml:base")
        else:
            # this is the branch called from the very top
            self.base = ""
            for bases in node.getElementsByTagName("base"):
                if bases.hasAttribute("href"):
                    self.base = bases.getAttribute("href")
                    continue
            if self.base == "":
                self.base = base

            # this is just to play safe. I believe this branch should actually not happen...
            if options == None:
                from pyRdfa import Options
                self.options = Options()
            else:
                self.options = options

            # xml:base is not part of XHTML+RDFa, but it is a valid setting for, say, SVG1.2
            if self.options.host_language == GENERIC_XML and node.hasAttribute("xml:base"):
                self.base = node.getAttribute("xml:base")

            self.options.comment_graph.set_base_URI(URIRef(_quote(base, self.options)))

            # check the the presense of the @profile and or @version attribute for the RDFa profile...
            # This whole branch is, however, irrelevant if the host language is a generic XML one (eg, SVG)
            if self.options.host_language != GENERIC_XML:
                doctype = None
                try:
                    # I am not 100% sure the HTML5 minidom implementation has this, so let us just be
                    # cautious here...
                    doctype = node.ownerDocument.doctype
                except:
                    pass
                if doctype == None or not( doctype.publicId == RDFa_PublicID and doctype.systemId == RDFa_SystemID ):
                    # next level: check the version
                    html = node.ownerDocument.documentElement
                    if not( html.hasAttribute("version") and RDFa_VERSION == html.getAttribute("version") ):
                        # see if least the profile has been set
                        # Find the <head> element
                        head = None
                        for index in range(0, html.childNodes.length-1):
                            if html.childNodes.item(index).nodeName == "head":
                                head = html.childNodes.item(index)
                                break
                        if not( head != None and head.hasAttribute("profile") and RDFa_PROFILE in head.getAttribute("profile").strip().split() ):
                            if self.options.host_language == HTML5_RDFA:
                                self.options.comment_graph.add_info("RDFa profile or RFDa version has not been set (for a correct identification of RDFa). This is not a requirement for RDFa, but it is advised to use one of those nevertheless. Note that in the case of HTML5, the DOCTYPE setting may not work...")
                            else:
                                self.options.comment_graph.add_info("None of the RDFa DOCTYPE, RDFa profile, or RFDa version has been set (for a correct identification of RDFa). This is not a requirement for RDFa, but it is advised to use one of those nevertheless.")

        #-----------------------------------------------------------------
        # Settling the language tags
        # check first the lang or xml:lang attribute
        # RDFa does not allow the lang attribute. HTML5 relies :-( on @lang;
        # I just want to be prepared here...
        if options != None and options.host_language == HTML5_RDFA and node.hasAttribute("lang"):
            self.lang = node.getAttribute("lang")
            if len(self.lang) == 0 : self.lang = None
        elif node.hasAttribute("xml:lang"):
            self.lang = node.getAttribute("xml:lang")
            if len(self.lang) == 0 : self.lang = None
        elif inherited_state:
            self.lang = inherited_state.lang
        else:
            self.lang = None

        #-----------------------------------------------------------------
        # Handling namespaces
        # First get the local xmlns declarations/namespaces stuff.
        dict = {}
        for i in range(0, node.attributes.length):
            attr = node.attributes.item(i)
            if attr.name.find('xmlns:') == 0 :
                # yep, there is a namespace setting
                key = attr.localName
                if key != "" : # exclude the top level xmlns setting...
                    if key == "_":
                        if warning: self.options.comment_graph.add_error("The '_' local CURIE prefix is reserved for blank nodes, and cannot be changed" )
                    elif key.find(':') != -1:
                        if warning: self.options.comment_graph.add_error("The character ':' is not valid in a CURIE Prefix" )
                    else :
                        # quote the URI, ie, convert special characters into %.. This is
                        # true, for example, for spaces
                        uri = _quote(attr.value, self.options)
                        # 1. create a new Namespace entry
                        ns = Namespace(uri)
                        # 2. 'bind' it in the current graph to
                        # get a nicer output
                        graph.bind(key, uri)
                        # 3. Add an entry to the dictionary
                        dict[key] = ns

        # See if anything has been collected at all.
        # If not, the namespaces of the incoming state is
        # taken over
        self.ns = {}
        if len(dict) == 0 and inherited_state:
            self.ns = inherited_state.ns
        else:
            if inherited_state:
                for k in inherited_state.ns : self.ns[k] = inherited_state.ns[k]
                # copying the newly found namespace, possibly overwriting
                # incoming values
                for k in dict :  self.ns[k] = dict[k]
            else:
                self.ns = dict

        # see if the xhtml core vocabulary has been set
        self.xhtml_prefix = None
        for key in self.ns.keys():
            if XHTML_URI == str(self.ns[key]):
                self.xhtml_prefix = key
                break
        if self.xhtml_prefix == None:
            if XHTML_PREFIX not in self.ns:
                self.ns[XHTML_PREFIX] = Namespace(XHTML_URI)
                self.xhtml_prefix = XHTML_PREFIX
            else:
                # the most disagreeable thing, the user has used
                # the prefix for something else...
                self.xhtml_prefix = XHTML_PREFIX + '_' + ("%d" % random.randint(1, 1000))
                self.ns[self.xhtml_prefix] = Namespace(XHTML_URI)
            graph.bind(self.xhtml_prefix, XHTML_URI)

        # extra tricks for unusual usages...
        # if the 'rdf' prefix is not used, it is artificially added...
        if "rdf" not in self.ns:
            self.ns["rdf"] = RDF
        if "rdfs" not in self.ns:
            self.ns["rdfs"] = RDFS

        # Final touch: setting the default namespace...
        if node.hasAttribute("xmlns"):
            self.defaultNS = node.getAttribute("xmlns")
        elif inherited_state and inherited_state.defaultNS != None:
            self.defaultNS = inherited_state.defaultNS
        else:
            self.defaultNS = None

    def _get_predefined_rels(self, val, warning):
        """Get the predefined URI value for the C{@rel/@rev} attribute.
        @param val: attribute name
        @param warning: whether a warning should be generated or not
        @type warning: boolean
        @return: URIRef for the predefined URI (or None)
        """
        vv = val.strip().lower()
        if vv in _predefined_rel:
            return self.ns[self.xhtml_prefix][vv]
        else:
            if warning: self.options.comment_graph.add_warning("invalid @rel/@rev value: '%s'" % val)
            return None

    def _get_predefined_properties(self, val, warning):
        """Get the predefined value for the C{@property} attribute.
        @param val: attribute name
        @param warning: whether a warning should be generated or not
        @type warning: boolean
        @return: URIRef for the predefined URI (or None)
        """
        vv = val.strip().lower()
        if vv in _predefined_property:
            return self.ns[self.xhtml_prefix][vv]
        else:
            if warning: self.options.comment_graph.add_warning("invalid @property value: '%s'" % val)
            return None

    def get_resource(self, val, rel=False, prop=False, warning=True):
        """Get a resource for a CURIE.
        The input argument is a CURIE; this is interpreted
        via the current namespaces and the corresponding URI Reference is returned
        @param val: string of the form "prefix:lname"
        @keyword rel: whether the predefined C{@rel/@rev} values should also be interpreted
        @keyword prop: whether the predefined C{@property} values should also be interpreted
        @return: an RDFLib URIRef instance (or None)
        """
        if val == "":
            return None
        elif val.find(":") != -1:
            key   = val.split(":", 1)[0]
            lname = val.split(":", 1)[1]
            if key == "_":
                # A possible error: this method is invoked for property URI-s, which
                # should not refer to a blank node. This case is checked and a possible
                # error condition is handled
                self.options.comment_graph.add_error("Blank node CURIE cannot be used in property position: _:%s" % lname)
                return None
            if key == "":
                # This is the ":blabla" case
                key = self.xhtml_prefix
        else:
            # if the resources correspond to a @rel or @rev or @property, then there
            # may be one more possibility here, namely that it is one of the
            # predefined values
            if rel:
                return self._get_predefined_rels(val, warning)
            elif prop:
                return self._get_predefined_properties(val, warning)
            else:
                self.options.comment_graph.add_warning("Invalid CURIE (without prefix): '%s'" % val)
                return None

        if key not in self.ns:
            self.options.comment_graph.add_error("CURIE used with non declared prefix: %s" % key)
            return None
        else:
            if lname == "":
                return URIRef(str(self.ns[key]))
            else:
                return self.ns[key][lname]

    def get_resources(self, val, rel=False, prop=False):
        """Get a series of resources encoded in CURIE-s.
        The input argument is a list of CURIE-s; these are interpreted
        via the current namespaces and the corresponding URI References are returned.
        @param val: strings of the form prefix':'lname, separated by space
        @keyword rel: whether the predefined C{@rel/@rev} values should also be interpreted
        @keyword prop: whether the predefined C{@property} values should also be interpreted
        @return: a list of RDFLib URIRef instances (possibly empty)
        """
        val.strip()
        resources = [ self.get_resource(v, rel, prop) for v in val.split() if v != None ]
        return [ r for r in resources if r != None ]

    def get_URI_ref(self, val):
        """Create a URI RDFLib resource for a URI.
        The input argument is a URI. It is checked whether it is a local
        reference with a '#' or not. If yes, a URIRef combined with the
        stored base value is returned. In both cases a URIRef for a full URI is created
        and returned
        @param val: URI string
        @return: an RDFLib URIRef instance
        """
        if val == "":
            return URIRef(self.base)
        elif val[0] == '[' and val[-1] == ']':
            self.options.comment_graph.add_error("Illegal usage of CURIE: %s" % val)
            return None
        else:
            return URIRef(urlparse.urljoin(self.base, val))

    def get_Curie_ref(self, val):
        """Create a URI RDFLib resource for a CURIE.
        The input argument is a CURIE. This means that it is
          - either of the form [a:b] where a:b should be resolved as an 'unprotected' CURIE, or
          - it is a traditional URI (relative or absolute)

        If the second case the URI value is also compared to 'usual' URI protocols ('http', 'https', 'ftp', etc)
        (see L{usual_protocols}).
        If there is no match, a warning is generated (indeed, a frequent mistake in authoring RDFa is to forget
        the '[' and ']' characters to "protect" CURIE-s.)

        @param val: CURIE string
        @return: an RDFLib URIRef instance
        """
        if len(val) == 0:
            return URIRef(self.base)
        elif val[0] == "[":
            if val[-1] == "]":
                curie = val[1:-1]
                # A possible Blank node reference should be separated here:
                if len(curie) >= 2 and curie[0] == "_" and curie[1] == ":":
                    return _get_bnode_from_Curie(curie[2:])
                else:
                    return self.get_resource(val[1:-1])
            else:
                # illegal CURIE...
                self.options.comment_graph.add_error("Illegal CURIE: %s" % val)
                return None
        else:
            # check the value, to see if an error may have been made...
            # Usual protocol values in the URI
            v = val.strip().lower()
            protocol = urlparse.urlparse(val)[0]
            if protocol != "" and protocol not in usual_protocols:
                err = "Possible URI error with '%s'; the intention may have been to use a protected CURIE" % val
                self.options.comment_graph.add_warning(err)
            return self.get_URI_ref(val)

