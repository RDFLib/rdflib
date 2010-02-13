#!/usr/bin/env python
u"""
notation3.py - Standalone Notation3 Parser
Derived from CWM, the Closed World Machine

Authors of the original suite:

* Dan Connolly <@@>
* Tim Berners-Lee <@@>
* Yosi Scharf <@@>
* Joseph M. Reagle Jr. <reagle@w3.org>
* Rich Salz <rsalz@zolera.com>

http://www.w3.org/2000/10/swap/notation3.py

Copyright 2000-2007, World Wide Web Consortium.
Copyright 2001, MIT.
Copyright 2001, Zolera Systems Inc.

License: W3C Software License
http://www.w3.org/Consortium/Legal/copyright-software

Modified by Sean B. Palmer
Copyright 2007, Sean B. Palmer. \u32E1

Modified to work with rdflib by Gunnar Aastrand Grimnes
Copyright 2010, Gunnar A. Grimnes

"""

# Python standard libraries
import types
import sys
import os
import string
import re
import time
import StringIO

from string import find, rfind
from decimal import Decimal

from rdflib.term import URIRef, BNode, Literal, Variable, _XSD_PFX
from rdflib.graph import QuotedGraph, ConjunctiveGraph

from rdflib.parser import Parser

# Incestuous.. would be nice to separate N3 and XML
# from sax2rdf import XMLtoDOM
def XMLtoDOM(*args, **kargs): 
   # print >> sys.stderr, args, kargs
   pass

# SWAP http://www.w3.org/2000/10/swap
# from diag import verbosity, setVerbosity, progress
def verbosity(*args, **kargs):
   # print >> sys.stderr, args, kargs
   pass
def setVerbosity(*args, **kargs):
   # print >> sys.stderr, args, kargs
   pass
def progress(*args, **kargs):
   # print >> sys.stderr, args, kargs
   pass



def splitFrag(uriref):
    """split a URI reference between the fragment and the rest.

    Punctuation is thrown away.

    e.g.
    
    >>> splitFrag("abc#def")
    ('abc', 'def')

    >>> splitFrag("abcdef")
    ('abcdef', None)

    """

    i = rfind(uriref, "#")
    if i>= 0: return uriref[:i], uriref[i+1:]
    else: return uriref, None

def splitFragP(uriref, punct=0):
    """split a URI reference before the fragment

    Punctuation is kept.
    
    e.g.

    >>> splitFragP("abc#def")
    ('abc', '#def')

    >>> splitFragP("abcdef")
    ('abcdef', '')

    """

    i = rfind(uriref, "#")
    if i>= 0: return uriref[:i], uriref[i:]
    else: return uriref, ''


def join(here, there):
    """join an absolute URI and URI reference
    (non-ascii characters are supported/doctested;
    haven't checked the details of the IRI spec though)

    here is assumed to be absolute.
    there is URI reference.

    >>> join('http://example/x/y/z', '../abc')
    'http://example/x/abc'

    Raise ValueError if there uses relative path
    syntax but here has no hierarchical path.

    >>> join('mid:foo@example', '../foo')
    Traceback (most recent call last):
        raise ValueError, here
    ValueError: Base <mid:foo@example> has no slash after colon - with relative '../foo'.

    >>> join('http://example/x/y/z', '')
    'http://example/x/y/z'
    
    >>> join('mid:foo@example', '#foo')
    'mid:foo@example#foo'
    
    We grok IRIs

    >>> len(u'Andr\\xe9')
    5
    
    >>> join('http://example.org/', u'#Andr\\xe9')
    u'http://example.org/#Andr\\xe9'
    """

    assert(find(here, "#") < 0), "Base may not contain hash: '%s'"% here # caller must splitFrag (why?)

    slashl = find(there, '/')
    colonl = find(there, ':')

    # join(base, 'foo:/') -- absolute
    if colonl >= 0 and (slashl < 0 or colonl < slashl):
        return there

    bcolonl = find(here, ':')
    assert(bcolonl >= 0), "Base uri '%s' is not absolute" % here # else it's not absolute

    path, frag = splitFragP(there)
    if not path: return here + frag
    
    # join('mid:foo@example', '../foo') bzzt
    if here[bcolonl+1:bcolonl+2] <> '/':
        raise ValueError ("Base <%s> has no slash after colon - with relative '%s'." %(here, there))

    if here[bcolonl+1:bcolonl+3] == '//':
        bpath = find(here, '/', bcolonl+3)
    else:
        bpath = bcolonl+1

    # join('http://xyz', 'foo')
    if bpath < 0:
        bpath = len(here)
        here = here + '/'

    # join('http://xyz/', '//abc') => 'http://abc'
    if there[:2] == '//':
        return here[:bcolonl+1] + there

    # join('http://xyz/', '/abc') => 'http://xyz/abc'
    if there[:1] == '/':
        return here[:bpath] + there

    slashr = rfind(here, '/')

    while 1:
        if path[:2] == './':
            path = path[2:]
        if path == '.':
            path = ''
        elif path[:3] == '../' or path == '..':
            path = path[3:]
            i = rfind(here, '/', bpath, slashr)
            if i >= 0:
                here = here[:i+1]
                slashr = i
        else:
            break

    return here[:slashr+1] + path + frag

commonHost = re.compile(r'^[-_a-zA-Z0-9.]+:(//[^/]*)?/[^/]*$')

def refTo(base, uri):
    """figure out a relative URI reference from base to uri

    >>> refTo('http://example/x/y/z', 'http://example/x/abc')
    '../abc'

    >>> refTo('file:/ex/x/y', 'file:/ex/x/q/r#s')
    'q/r#s'
    
    >>> refTo(None, 'http://ex/x/y')
    'http://ex/x/y'

    >>> refTo('http://ex/x/y', 'http://ex/x/y')
    ''

    Note the relationship between refTo and join:
    join(x, refTo(x, y)) == y
    which points out certain strings which cannot be URIs. e.g.
    >>> x='http://ex/x/y';y='http://ex/x/q:r';join(x, refTo(x, y)) == y
    0

    So 'http://ex/x/q:r' is not a URI. Use 'http://ex/x/q%3ar' instead:
    >>> x='http://ex/x/y';y='http://ex/x/q%3ar';join(x, refTo(x, y)) == y
    1
    
    This one checks that it uses a root-realtive one where that is
    all they share.  Now uses root-relative where no path is shared.
    This is a matter of taste but tends to give more resilience IMHO
    -- and shorter paths

    Note that base may be None, meaning no base.  In some situations, there
    just ain't a base. Slife. In these cases, relTo returns the absolute value.
    The axiom abs(,rel(b,x))=x still holds.
    This saves people having to set the base to "bogus:".

    >>> refTo('http://ex/x/y/z', 'http://ex/r')
    '/r'

    """

#    assert base # don't mask bugs -danc # not a bug. -tim
    if not base: return uri
    if base == uri: return ""
    
    # Find how many path segments in common
    i=0
    while i<len(uri) and i<len(base):
        if uri[i] == base[i]: i = i + 1
        else: break
    # print "# relative", base, uri, "   same up to ", i
    # i point to end of shortest one or first difference

    m = commonHost.match(base[:i])
    if m:
        k=uri.find("//")
        if k<0: k=-2 # no host
        l=uri.find("/", k+2)
        if uri[l+1:l+2] != "/" and base[l+1:l+2] != "/" and uri[:l]==base[:l]:
            return uri[l:]

    if uri[i:i+1] =="#" and len(base) == i: return uri[i:] # fragment of base

    while i>0 and uri[i-1] != '/' : i=i-1  # scan for slash

    if i < 3: return uri  # No way.
    if string.find(base, "//", i-2)>0 \
       or string.find(uri, "//", i-2)>0: return uri # An unshared "//"
    if string.find(base, ":", i)>0: return uri  # An unshared ":"
    n = string.count(base, "/", i)
    if n == 0 and i<len(uri) and uri[i] == '#':
        return "./" + uri[i:]
    elif n == 0 and i == len(uri):
        return "./"
    else:
        return ("../" * n) + uri[i:]


def base():
        """The base URI for this process - the Web equiv of cwd
        
        Relative or abolute unix-standard filenames parsed relative to
        this yeild the URI of the file.
        If we had a reliable way of getting a computer name,
        we should put it in the hostname just to prevent ambiguity

        """
#       return "file://" + hostname + os.getcwd() + "/"
        return "file://" + _fixslash(os.getcwd()) + "/"


def _fixslash(str):
    """ Fix windowslike filename to unixlike - (#ifdef WINDOWS)"""
    s = str
    for i in range(len(s)):
        if s[i] == "\\": s = s[:i] + "/" + s[i+1:]
    if s[0] != "/" and s[1] == ":": s = s[2:]  # @@@ Hack when drive letter present
    return s

URI_unreserved = "ABCDEFGHIJJLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~"
    # unreserved  = ALPHA / DIGIT / "-" / "." / "_" / "~"
    
def canonical(str_in):
    """Convert equivalent URIs (or parts) to the same string
    
    There are many differenet levels of URI canonicalization
    which are possible.  See http://www.ietf.org/rfc/rfc3986.txt
    Done:
    - Converfting unicode IRI to utf-8
    - Escaping all non-ASCII
    - De-escaping, if escaped, ALPHA (%41-%5A and %61-%7A), DIGIT (%30-%39),
      hyphen (%2D), period (%2E), underscore (%5F), or tilde (%7E) (Sect 2.4) 
    - Making all escapes uppercase hexadecimal
    Not done:
    - Making URI scheme lowercase
    - changing /./ or  /foo/../ to / with care not to change host part
    
    
    >>> canonical("foo bar")
    'foo%20bar'
    
    >>> canonical(u'http:')
    'http:'
    
    >>> canonical('fran%c3%83%c2%a7ois')
    'fran%C3%83%C2%A7ois'
    
    >>> canonical('a')
    'a'
    
    >>> canonical('%4e')
    'N'

    >>> canonical('%9d')
    '%9D'
    
    >>> canonical('%2f')
    '%2F'

    >>> canonical('%2F')
    '%2F'

    """
    if type(str_in) == type(u''):
        s8 = str_in.encode('utf-8')
    else:
        s8 = str_in
    s = ''
    i = 0
    while i < len(s8):
        ch = s8[i]; n = ord(ch)
        if (n > 126) or (n < 33) :   # %-encode controls, SP, DEL, and utf-8
            s += "%%%02X" % ord(ch)
        elif ch == '%' and i+2 < len(s8):
            ch2 = s8[i+1:i+3].decode('hex')
            if ch2 in URI_unreserved: s += ch2
            else: s += "%%%02X" % ord(ch2)
            i = i+3
            continue
        else:
            s += ch
        i = i +1
    return s






CONTEXT = 0
PRED = 1  
SUBJ = 2
OBJ = 3

PARTS =  PRED, SUBJ, OBJ
ALL4 = CONTEXT, PRED, SUBJ, OBJ

SYMBOL = 0
FORMULA = 1
LITERAL = 2
LITERAL_DT = 21
LITERAL_LANG = 22
ANONYMOUS = 3
XMLLITERAL = 25

Logic_NS = "http://www.w3.org/2000/10/swap/log#"
NODE_MERGE_URI = Logic_NS + "is"  # Pseudo-property indicating node merging
forSomeSym = Logic_NS + "forSome"
forAllSym = Logic_NS + "forAll"

RDF_type_URI = "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
RDF_NS_URI = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
OWL_NS = "http://www.w3.org/2002/07/owl#"
DAML_sameAs_URI = OWL_NS+"sameAs"
parsesTo_URI = Logic_NS + "parsesTo"
RDF_spec = "http://www.w3.org/TR/REC-rdf-syntax/"

List_NS = RDF_NS_URI     # From 20030808
_Old_Logic_NS = "http://www.w3.org/2000/10/swap/log.n3#"

N3_first = (SYMBOL, List_NS + "first")
N3_rest = (SYMBOL, List_NS + "rest")
N3_li = (SYMBOL, List_NS + "li")
N3_nil = (SYMBOL, List_NS + "nil")
N3_List = (SYMBOL, List_NS + "List")
N3_Empty = (SYMBOL, List_NS + "Empty")



runNamespaceValue = None

def runNamespace():
    "Return a URI suitable as a namespace for run-local objects"
    # @@@ include hostname (privacy?) (hash it?)
    global runNamespaceValue
    if runNamespaceValue == None:
        try:
            runNamespaceValue = os.environ["CWM_RUN_NS"]
        except KeyError:
            runNamespaceValue = join(
                base(), ".run-" + `time.time()` + "p"+ `os.getpid()` +"#")
                                # was uripath.join, and uripath.base
        runNamespaceValue = join(base(), runNamespaceValue) # absolutize
    return runNamespaceValue

nextu = 0
def uniqueURI():
    "A unique URI"
    global nextu
    nextu += 1
    return runNamespace() + "u_" + `nextu`
    
class URISyntaxError(ValueError):
    """A parameter is passed to a routine that requires a URI reference"""
    pass


tracking = False
chatty_flag = 50


from xml.dom import Node
try:
    from xml.ns import XMLNS
except:
    class XMLNS:
        BASE = "http://www.w3.org/2000/xmlns/"
        XML = "http://www.w3.org/XML/1998/namespace"


_attrs = lambda E: (E.attributes and E.attributes.values()) or []
_children = lambda E: E.childNodes or []
_IN_XML_NS = lambda n: n.namespaceURI == XMLNS.XML
_inclusive = lambda n: n.unsuppressedPrefixes == None

# Does a document/PI has lesser/greater document order than the
# first element?
_LesserElement, _Element, _GreaterElement = range(3)

def _sorter(n1,n2):
    '''_sorter(n1,n2) -> int
    Sorting predicate for non-NS attributes.'''

    i = cmp(n1.namespaceURI, n2.namespaceURI)
    if i: return i
    return cmp(n1.localName, n2.localName)


def _sorter_ns(n1,n2):
    '''_sorter_ns((n,v),(n,v)) -> int
    "(an empty namespace URI is lexicographically least)."'''

    if n1[0] == 'xmlns': return -1
    if n2[0] == 'xmlns': return 1
    return cmp(n1[0], n2[0])

def _utilized(n, node, other_attrs, unsuppressedPrefixes):
    '''_utilized(n, node, other_attrs, unsuppressedPrefixes) -> boolean
    Return true if that nodespace is utilized within the node'''

    if n.startswith('xmlns:'):
        n = n[6:]
    elif n.startswith('xmlns'):
        n = n[5:]
    if (n=="" and node.prefix in ["#default", None]) or \
        n == node.prefix or n in unsuppressedPrefixes: 
            return 1
    for attr in other_attrs:
        if n == attr.prefix: return 1
    return 0

#_in_subset = lambda subset, node: not subset or node in subset
_in_subset = lambda subset, node: subset is None or node in subset # rich's tweak

class _implementation:
    '''Implementation class for C14N. This accompanies a node during it's
    processing and includes the parameters and processing state.'''

    # Handler for each node type; populated during module instantiation.
    handlers = {}

    def __init__(self, node, write, **kw):
        '''Create and run the implementation.'''
        self.write = write
        self.subset = kw.get('subset')
        self.comments = kw.get('comments', 0)
        self.unsuppressedPrefixes = kw.get('unsuppressedPrefixes')
        nsdict = kw.get('nsdict', { 'xml': XMLNS.XML, 'xmlns': XMLNS.BASE })
        
        # Processing state.
        self.state = (nsdict, {'xml':''}, {}) #0422
        
        if node.nodeType == Node.DOCUMENT_NODE:
            self._do_document(node)
        elif node.nodeType == Node.ELEMENT_NODE:
            self.documentOrder = _Element        # At document element
            if not _inclusive(self):
                self._do_element(node)
            else:
                inherited = self._inherit_context(node)
                self._do_element(node, inherited)
        elif node.nodeType == Node.DOCUMENT_TYPE_NODE:
            pass
        elif node.nodeType == Node.TEXT_NODE:
            self._do_text(node)
        else:
            raise TypeError, str(node)


    def _inherit_context(self, node):
        '''_inherit_context(self, node) -> list
        Scan ancestors of attribute and namespace context.  Used only
        for single element node canonicalization, not for subset
        canonicalization.'''

        # Collect the initial list of xml:foo attributes.
        xmlattrs = filter(_IN_XML_NS, _attrs(node))

        # Walk up and get all xml:XXX attributes we inherit.
        inherited, parent = [], node.parentNode
        while parent and parent.nodeType == Node.ELEMENT_NODE:
            for a in filter(_IN_XML_NS, _attrs(parent)):
                n = a.localName
                if n not in xmlattrs:
                    xmlattrs.append(n)
                    inherited.append(a)
            parent = parent.parentNode
        return inherited


    def _do_document(self, node):
        '''_do_document(self, node) -> None
        Process a document node. documentOrder holds whether the document
        element has been encountered such that PIs/comments can be written
        as specified.'''

        self.documentOrder = _LesserElement
        for child in node.childNodes:
            if child.nodeType == Node.ELEMENT_NODE:
                self.documentOrder = _Element        # At document element
                self._do_element(child)
                self.documentOrder = _GreaterElement # After document element
            elif child.nodeType == Node.PROCESSING_INSTRUCTION_NODE:
                self._do_pi(child)
            elif child.nodeType == Node.COMMENT_NODE:
                self._do_comment(child)
            elif child.nodeType == Node.DOCUMENT_TYPE_NODE:
                pass
            else:
                raise TypeError, str(child)
    handlers[Node.DOCUMENT_NODE] = _do_document


    def _do_text(self, node):
        '''_do_text(self, node) -> None
        Process a text or CDATA node.  Render various special characters
        as their C14N entity representations.'''
        if not _in_subset(self.subset, node): return
        s = string.replace(node.data, "&", "&amp;")
        s = string.replace(s, "<", "&lt;")
        s = string.replace(s, ">", "&gt;")
        s = string.replace(s, "\015", "&#xD;")
        if s: self.write(s)
    handlers[Node.TEXT_NODE] = _do_text
    handlers[Node.CDATA_SECTION_NODE] = _do_text


    def _do_pi(self, node):
        '''_do_pi(self, node) -> None
        Process a PI node. Render a leading or trailing #xA if the
        document order of the PI is greater or lesser (respectively)
        than the document element.
        '''
        if not _in_subset(self.subset, node): return
        W = self.write
        if self.documentOrder == _GreaterElement: W('\n')
        W('<?')
        W(node.nodeName)
        s = node.data
        if s:
            W(' ')
            W(s)
        W('?>')
        if self.documentOrder == _LesserElement: W('\n')
    handlers[Node.PROCESSING_INSTRUCTION_NODE] = _do_pi


    def _do_comment(self, node):
        '''_do_comment(self, node) -> None
        Process a comment node. Render a leading or trailing #xA if the
        document order of the comment is greater or lesser (respectively)
        than the document element.
        '''
        if not _in_subset(self.subset, node): return
        if self.comments:
            W = self.write
            if self.documentOrder == _GreaterElement: W('\n')
            W('<!--')
            W(node.data)
            W('-->')
            if self.documentOrder == _LesserElement: W('\n')
    handlers[Node.COMMENT_NODE] = _do_comment


    def _do_attr(self, n, value):
        ''''_do_attr(self, node) -> None
        Process an attribute.'''

        W = self.write
        W(' ')
        W(n)
        W('="')
        s = string.replace(value, "&", "&amp;")
        s = string.replace(s, "<", "&lt;")
        s = string.replace(s, '"', '&quot;')
        s = string.replace(s, '\011', '&#x9')
        s = string.replace(s, '\012', '&#xA')
        s = string.replace(s, '\015', '&#xD')
        W(s)
        W('"')


    def _do_element(self, node, initial_other_attrs = []):
        '''_do_element(self, node, initial_other_attrs = []) -> None
        Process an element (and its children).'''

        # Get state (from the stack) make local copies.
        #   ns_parent -- NS declarations in parent
        #   ns_rendered -- NS nodes rendered by ancestors
        #        ns_local -- NS declarations relevant to this element
        #   xml_attrs -- Attributes in XML namespace from parent
        #       xml_attrs_local -- Local attributes in XML namespace.
        ns_parent, ns_rendered, xml_attrs = \
                self.state[0], self.state[1].copy(), self.state[2].copy() #0422
        ns_local = ns_parent.copy()
        xml_attrs_local = {}

	# progress("_do_element node.nodeName=", node.nodeName)
	# progress("_do_element node.namespaceURI", node.namespaceURI)
	# progress("_do_element node.tocml()", node.toxml())
        # Divide attributes into NS, XML, and others.
        other_attrs = initial_other_attrs[:]
        in_subset = _in_subset(self.subset, node)
        for a in _attrs(node):
	    # progress("\t_do_element a.nodeName=", a.nodeName)
            if a.namespaceURI == XMLNS.BASE:
                n = a.nodeName
                if n == "xmlns:": n = "xmlns"        # DOM bug workaround
                ns_local[n] = a.nodeValue
            elif a.namespaceURI == XMLNS.XML:
                if _inclusive(self) or in_subset:
                    xml_attrs_local[a.nodeName] = a #0426
            else:
                other_attrs.append(a)
            #add local xml:foo attributes to ancestor's xml:foo attributes
            xml_attrs.update(xml_attrs_local)

        # Render the node
        W, name = self.write, None
        if in_subset: 
            name = node.nodeName
            W('<')
            W(name)

            # Create list of NS attributes to render.
            ns_to_render = []
            for n,v in ns_local.items():

                # If default namespace is XMLNS.BASE or empty,
                # and if an ancestor was the same
                if n == "xmlns" and v in [ XMLNS.BASE, '' ] \
                and ns_rendered.get('xmlns') in [ XMLNS.BASE, '', None ]:
                    continue

                # "omit namespace node with local name xml, which defines
                # the xml prefix, if its string value is
                # http://www.w3.org/XML/1998/namespace."
                if n in ["xmlns:xml", "xml"] \
                and v in [ 'http://www.w3.org/XML/1998/namespace' ]:
                    continue


                # If not previously rendered
                # and it's inclusive  or utilized
                if (n,v) not in ns_rendered.items() \
                  and (_inclusive(self) or \
                  _utilized(n, node, other_attrs, self.unsuppressedPrefixes)):
                    ns_to_render.append((n, v))

            # Sort and render the ns, marking what was rendered.
            ns_to_render.sort(_sorter_ns)
            for n,v in ns_to_render:
                self._do_attr(n, v)
                ns_rendered[n]=v    #0417

            # If exclusive or the parent is in the subset, add the local xml attributes
            # Else, add all local and ancestor xml attributes
            # Sort and render the attributes.
            if not _inclusive(self) or _in_subset(self.subset,node.parentNode):  #0426
                other_attrs.extend(xml_attrs_local.values())
            else:
                other_attrs.extend(xml_attrs.values())
            other_attrs.sort(_sorter)
            for a in other_attrs:
                self._do_attr(a.nodeName, a.value)
            W('>')

        # Push state, recurse, pop state.
        state, self.state = self.state, (ns_local, ns_rendered, xml_attrs)
        for c in _children(node):
            _implementation.handlers[c.nodeType](self, c)
        self.state = state

        if name: W('</%s>' % name)
    handlers[Node.ELEMENT_NODE] = _do_element


def Canonicalize(node, output=None, **kw):
    '''Canonicalize(node, output=None, **kw) -> UTF-8

    Canonicalize a DOM document/element node and all descendents.
    Return the text; if output is specified then output.write will
    be called to output the text and None will be returned
    Keyword parameters:
        nsdict: a dictionary of prefix:uri namespace entries
                assumed to exist in the surrounding context
        comments: keep comments if non-zero (default is 0)
        subset: Canonical XML subsetting resulting from XPath
                (default is [])
        unsuppressedPrefixes: do exclusive C14N, and this specifies the
                prefixes that should be inherited.
    '''
    if output:
        apply(_implementation, (node, output.write), kw)
    else:
        s = StringIO.StringIO()
        apply(_implementation, (node, s.write), kw)
        return s.getvalue()

# end of xmlC14n.py

# from why import BecauseOfData, becauseSubexpression
def BecauseOfData(*args, **kargs): 
   # print args, kargs
   pass
def becauseSubexpression(*args, **kargs): 
   # print args, kargs
   pass

N3_forSome_URI = forSomeSym
N3_forAll_URI = forAllSym

# Magic resources we know about



ADDED_HASH = "#"  # Stop where we use this in case we want to remove it!
# This is the hash on namespace URIs

RDF_type = ( SYMBOL , RDF_type_URI )
DAML_sameAs = ( SYMBOL, DAML_sameAs_URI )

LOG_implies_URI = "http://www.w3.org/2000/10/swap/log#implies"

BOOLEAN_DATATYPE = _XSD_PFX + "boolean"
DECIMAL_DATATYPE = _XSD_PFX + "decimal"
DOUBLE_DATATYPE = _XSD_PFX + "double"
FLOAT_DATATYPE = _XSD_PFX + "float"
INTEGER_DATATYPE = _XSD_PFX + "integer"

option_noregen = 0   # If set, do not regenerate genids on output

# @@ I18n - the notname chars need extending for well known unicode non-text
# characters. The XML spec switched to assuming unknown things were name
# characaters.
# _namechars = string.lowercase + string.uppercase + string.digits + '_-'
_notQNameChars = "\t\r\n !\"#$%&'()*.,+/;<=>?@[\\]^`{|}~" # else valid qname :-/
_notNameChars = _notQNameChars + ":"  # Assume anything else valid name :-/
_rdfns = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#'


N3CommentCharacter = "#"     # For unix script #! compatabilty

########################################## Parse string to sink
#
# Regular expressions:
eol = re.compile(r'[ \t]*(#[^\n]*)?\r?\n')      # end  of line, poss. w/comment
eof = re.compile(r'[ \t]*(#[^\n]*)?$')          # end  of file, poss. w/comment
ws = re.compile(r'[ \t]*')                      # Whitespace not including NL
signed_integer = re.compile(r'[-+]?[0-9]+')     # integer
number_syntax = re.compile(r'(?P<integer>[-+]?[0-9]+)(?P<decimal>\.[0-9]+)?(?P<exponent>e[-+]?[0-9]+)?')
digitstring = re.compile(r'[0-9]+')             # Unsigned integer      
interesting = re.compile(r'[\\\r\n\"]')
langcode = re.compile(r'[a-zA-Z0-9]+(-[a-zA-Z0-9]+)?')
#"



class SinkParser:
    def __init__(self, store, openFormula=None, thisDoc="", baseURI=None,
                 genPrefix = "", flags="",
                 why=None):
        """ note: namespace names should *not* end in #;
        the # will get added during qname processing """

        self._bindings = {}
        self._flags = flags
        if thisDoc != "":
            assert ':' in thisDoc, "Document URI not absolute: <%s>" % thisDoc
            self._bindings[""] = thisDoc + "#"  # default

        self._store = store
        if genPrefix: store.setGenPrefix(genPrefix) # pass it on
        
        self._thisDoc = thisDoc
        self.lines = 0              # for error handling
        self.startOfLine = 0        # For calculating character number
        self._genPrefix = genPrefix
        self.keywords = ['a', 'this', 'bind', 'has', 'is', 'of', 'true', 'false' ]
        self.keywordsSet = 0    # Then only can others be considerd qnames
        self._anonymousNodes = {} # Dict of anon nodes already declared ln: Term
        self._variables  = {}
        self._parentVariables = {}
        self._reason = why      # Why the parser was asked to parse this

        self._reason2 = None    # Why these triples
        # was: diag.tracking
        if tracking: self._reason2 = BecauseOfData(
                        store.newSymbol(thisDoc), because=self._reason) 

        if baseURI: self._baseURI = baseURI
        else:
            if thisDoc:
                self._baseURI = thisDoc
            else:
                self._baseURI = None

        assert not self._baseURI or ':' in self._baseURI

        if not self._genPrefix:
            if self._thisDoc: self._genPrefix = self._thisDoc + "#_g"
            else: self._genPrefix = uniqueURI()

        if openFormula ==None:
            if self._thisDoc:
                self._formula = store.newFormula(thisDoc + "#_formula")
            else:
                self._formula = store.newFormula()
        else:
            self._formula = openFormula
        

        self._context = self._formula
        self._parentContext = None
        

    def here(self, i):
        """String generated from position in file
        
        This is for repeatability when refering people to bnodes in a document.
        This has diagnostic uses less formally, as it should point one to which 
        bnode the arbitrary identifier actually is. It gives the
        line and character number of the '[' charcacter or path character
        which introduced the blank node. The first blank node is boringly _L1C1.
        It used to be used only for tracking, but for tests in general
        it makes the canonical ordering of bnodes repeatable."""

        return "%s_L%iC%i" % (self._genPrefix , self.lines,
                                            i - self.startOfLine + 1) 
        
    def formula(self):
        return self._formula
    
    def loadStream(self, stream):
        return self.loadBuf(stream.read())   # Not ideal

    def loadBuf(self, buf):
        """Parses a buffer and returns its top level formula"""
        self.startDoc()

        self.feed(buf)
        return self.endDoc()    # self._formula


    def feed(self, octets):
        """Feed an octet stream tothe parser
        
        if BadSyntax is raised, the string
        passed in the exception object is the
        remainder after any statements have been parsed.
        So if there is more data to feed to the
        parser, it should be straightforward to recover."""

        if not isinstance(octets, unicode):        
           str = octets.decode('utf-8')
        else: 
           str=octets

        i = 0
        while i >= 0:
            j = self.skipSpace(str, i)
            if j<0: return

            i = self.directiveOrStatement(str,j)
            if i<0:
                print "# next char: ", `str[j]` 
                raise BadSyntax(self._thisDoc, self.lines, str, j,
                                    "expected directive or statement")

    def directiveOrStatement(self, str,h):
    
            i = self.skipSpace(str, h)
            if i<0: return i   # EOF

            j = self.directive(str, i)
            if j>=0: return  self.checkDot(str,j)
            
            j = self.statement(str, i)
            if j>=0: return self.checkDot(str,j)
            
            return j


    #@@I18N
    global _notNameChars
    #_namechars = string.lowercase + string.uppercase + string.digits + '_-'
        
    def tok(self, tok, str, i):
        """Check for keyword.  Space must have been stripped on entry and
        we must not be at end of file."""
        
        assert tok[0] not in _notNameChars # not for punctuation
        if str[i:i+1] == "@":
            i = i+1
        else:
            if tok not in self.keywords:
                return -1   # No, this has neither keywords declaration nor "@"

        if (str[i:i+len(tok)] == tok
            and (str[i+len(tok)] in  _notQNameChars )): 
            i = i + len(tok)
            return i
        else:
            return -1

    def directive(self, str, i):
        j = self.skipSpace(str, i)
        if j<0: return j # eof
        res = []
        
        j = self.tok('bind', str, i)        # implied "#". Obsolete.
        if j>0: raise BadSyntax(self._thisDoc, self.lines, str, i,
                                "keyword bind is obsolete: use @prefix")

        j = self.tok('keywords', str, i)
        if j>0:
            i = self.commaSeparatedList(str, j, res, self.bareWord)
            if i < 0:
                raise BadSyntax(self._thisDoc, self.lines, str, i,
                    "'@keywords' needs comma separated list of words")
            self.setKeywords(res[:])
            # was: diag.chatty_flag
            if chatty_flag > 80: progress("Keywords ", self.keywords)
            return i


        j = self.tok('forAll', str, i)
        if j > 0:
            i = self.commaSeparatedList(str, j, res, self.uri_ref2)
            if i <0: raise BadSyntax(self._thisDoc, self.lines, str, i,
                        "Bad variable list after @forAll")
            for x in res:
                #self._context.declareUniversal(x)
                if x not in self._variables or x in self._parentVariables:
                    self._variables[x] =  self._context.newUniversal(x)
            return i

        j = self.tok('forSome', str, i)
        if j > 0:
            i = self. commaSeparatedList(str, j, res, self.uri_ref2)
            if i <0: raise BadSyntax(self._thisDoc, self.lines, str, i,
                    "Bad variable list after @forSome")
            for x in res:
                self._context.declareExistential(x)
            return i


        j=self.tok('prefix', str, i)   # no implied "#"
        if j>=0:
            t = []
            i = self.qname(str, j, t)
            if i<0: raise BadSyntax(self._thisDoc, self.lines, str, j,
                                "expected qname after @prefix")
            j = self.uri_ref2(str, i, t)
            if j<0: raise BadSyntax(self._thisDoc, self.lines, str, i,
                                "expected <uriref> after @prefix _qname_")
            ns = self.uriOf(t[1])

            if self._baseURI:
                ns = join(self._baseURI, ns)
            elif ":" not in ns:
                 raise BadSyntax(self._thisDoc, self.lines, str, j,
                    "With no base URI, cannot use relative URI in @prefix <"+ns+">")
            assert ':' in ns # must be absolute
            self._bindings[t[0][0]] = ns
            self.bind(t[0][0], hexify(ns))
            return j

        j=self.tok('base', str, i)      # Added 2007/7/7
        if j >= 0:
            t = []
            i = self.uri_ref2(str, j, t)
            if i<0: raise BadSyntax(self._thisDoc, self.lines, str, j,
                                "expected <uri> after @base ")
            ns = self.uriOf(t[0])

            if self._baseURI:
                ns = join(self._baseURI, ns)
            else:
                raise BadSyntax(self._thisDoc, self.lines, str, j,
                    "With no previous base URI, cannot use relative URI in @base  <"+ns+">")
            assert ':' in ns # must be absolute
            self._baseURI = ns
            return i

        return -1  # Not a directive, could be something else.

    def bind(self, qn, uri):
        assert isinstance(uri,
                    types.StringType), "Any unicode must be %x-encoded already"
        if qn == "":
            self._store.setDefaultNamespace(uri)
        else:
            self._store.bind(qn, uri)

    def setKeywords(self, k):
        "Takes a list of strings"
        if k == None:
            self.keywordsSet = 0
        else:
            self.keywords = k
            self.keywordsSet = 1


    def startDoc(self):
        # was: self._store.startDoc()
        self._store.startDoc(self._formula)

    def endDoc(self):
        """Signal end of document and stop parsing. returns formula"""
        self._store.endDoc(self._formula)  # don't canonicalize yet
        return self._formula

    def makeStatement(self, quadruple):
        #$$$$$$$$$$$$$$$$$$$$$
#        print "# Parser output: ", `quadruple`
        self._store.makeStatement(quadruple, why=self._reason2)



    def statement(self, str, i):
        r = []

        i = self.object(str, i, r)  #  Allow literal for subject - extends RDF 
        if i<0: return i

        j = self.property_list(str, i, r[0])

        if j<0: raise BadSyntax(self._thisDoc, self.lines,
                                    str, i, "expected propertylist")
        return j

    def subject(self, str, i, res):
        return self.item(str, i, res)

    def verb(self, str, i, res):
        """ has _prop_
        is _prop_ of
        a
        =
        _prop_
        >- prop ->
        <- prop -<
        _operator_"""

        j = self.skipSpace(str, i)
        if j<0:return j # eof
        
        r = []

        j = self.tok('has', str, i)
        if j>=0:
            i = self.prop(str, j, r)
            if i < 0: raise BadSyntax(self._thisDoc, self.lines,
                                str, j, "expected property after 'has'")
            res.append(('->', r[0]))
            return i

        j = self.tok('is', str, i)
        if j>=0:
            i = self.prop(str, j, r)
            if i < 0: raise BadSyntax(self._thisDoc, self.lines, str, j,
                                "expected <property> after 'is'")
            j = self.skipSpace(str, i)
            if j<0:
                raise BadSyntax(self._thisDoc, self.lines, str, i,
                            "End of file found, expected property after 'is'")
                return j # eof
            i=j
            j = self.tok('of', str, i)
            if j<0: raise BadSyntax(self._thisDoc, self.lines, str, i,
                                "expected 'of' after 'is' <prop>")
            res.append(('<-', r[0]))
            return j

        j = self.tok('a', str, i)
        if j>=0:
            res.append(('->', RDF_type))
            return j

            
        if str[i:i+2] == "<=":
            res.append(('<-', self._store.newSymbol(Logic_NS+"implies")))
            return i+2

        if str[i:i+1] == "=":
            if str[i+1:i+2] == ">":
                res.append(('->', self._store.newSymbol(Logic_NS+"implies")))
                return i+2
            res.append(('->', DAML_sameAs))
            return i+1

        if str[i:i+2] == ":=":
            # patch file relates two formulae, uses this    @@ really?
            res.append(('->', Logic_NS+"becomes")) 
            return i+2

        j = self.prop(str, i, r)
        if j >= 0:
            res.append(('->', r[0]))
            return j

        if str[i:i+2] == ">-" or str[i:i+2] == "<-":
            raise BadSyntax(self._thisDoc, self.lines, str, j,
                                        ">- ... -> syntax is obsolete.")

        return -1

    def prop(self, str, i, res):
        return self.item(str, i, res)

    def item(self, str, i, res):
        return self.path(str, i, res)

    def blankNode(self, uri=None):
        if "B" not in self._flags:
            return self._context.newBlankNode(uri, why=self._reason2)
        x = self._context.newSymbol(uri)
        self._context.declareExistential(x)
        return x
        
    def path(self, str, i, res):
        """Parse the path production.
        """
        j = self.nodeOrLiteral(str, i, res)
        if j<0: return j  # nope

        while str[j:j+1] in "!^.":  # no spaces, must follow exactly (?)
            ch = str[j:j+1]     # @@ Allow "." followed IMMEDIATELY by a node.
            if ch == ".":
                ahead = str[j+1:j+2]
                if not ahead or (ahead in _notNameChars
                            and ahead not in ":?<[{("): break
            subj = res.pop()
            obj = self.blankNode(uri=self.here(j))
            j = self.node(str, j+1, res)
            if j<0: raise BadSyntax(self._thisDoc, self.lines, str, j,
                            "EOF found in middle of path syntax")
            pred = res.pop()
            if ch == "^": # Reverse traverse
                self.makeStatement((self._context, pred, obj, subj)) 
            else:
                self.makeStatement((self._context, pred, subj, obj)) 
            res.append(obj)
        return j

    def anonymousNode(self, ln):
        """Remember or generate a term for one of these _: anonymous nodes"""
        term = self._anonymousNodes.get(ln, None)
        if term != None: return term
        term = self._store.newBlankNode(self._context, why=self._reason2)
        self._anonymousNodes[ln] = term
        return term

    def node(self, str, i, res, subjectAlready=None):
        """Parse the <node> production.
        Space is now skipped once at the beginning
        instead of in multipe calls to self.skipSpace().
        """
        subj = subjectAlready

        j = self.skipSpace(str,i)
        if j<0: return j #eof
        i=j
        ch = str[i:i+1]  # Quick 1-character checks first:

        if ch == "[":
            bnodeID = self.here(i)
            j=self.skipSpace(str,i+1)
            if j<0: raise BadSyntax(self._thisDoc,
                                    self.lines, str, i, "EOF after '['")
            if str[j:j+1] == "=":     # Hack for "is"  binding name to anon node
                i = j+1
                objs = []
                j = self.objectList(str, i, objs);
                if j>=0:
                    subj = objs[0]
                    if len(objs)>1:
                        for obj in objs:
                            self.makeStatement((self._context,
                                                DAML_sameAs, subj, obj))
                    j = self.skipSpace(str, j)
                    if j<0: raise BadSyntax(self._thisDoc, self.lines, str, i,
                        "EOF when objectList expected after [ = ")
                    if str[j:j+1] == ";":
                        j=j+1
                else:
                    raise BadSyntax(self._thisDoc, self.lines, str, i,
                                        "objectList expected after [= ")

            if subj is None:
                subj=self.blankNode(uri= bnodeID)

            i = self.property_list(str, j, subj)
            if i<0: raise BadSyntax(self._thisDoc, self.lines, str, j,
                                "property_list expected")

            j = self.skipSpace(str, i)
            if j<0: raise BadSyntax(self._thisDoc, self.lines, str, i,
                "EOF when ']' expected after [ <propertyList>")
            if str[j:j+1] != "]":
                raise BadSyntax(self._thisDoc,
                                    self.lines, str, j, "']' expected")
            res.append(subj)
            return j+1

        if ch == "{":
            ch2 = str[i+1:i+2]
            if ch2 == '$':
                i += 1
                j = i + 1
                List = []
                first_run = True
                while 1:
                    i = self.skipSpace(str, j)
                    if i<0: raise BadSyntax(self._thisDoc, self.lines, str, i,
                                                    "needed '$}', found end.")                    
                    if str[i:i+2] == '$}':
                        j = i+2
                        break

                    if not first_run:
                        if str[i:i+1] == ',':
                            i+=1
                        else:
                            raise BadSyntax(self._thisDoc, self.lines,
                                                str, i, "expected: ','")
                    else: first_run = False
                    
                    item = []
                    j = self.item(str,i, item) #@@@@@ should be path, was object
                    if j<0: raise BadSyntax(self._thisDoc, self.lines, str, i,
                                            "expected item in set or '$}'")
                    List.append(self._store.intern(item[0]))
                res.append(self._store.newSet(List, self._context))
                return j
            else:
                j=i+1
                oldParentContext = self._parentContext
                self._parentContext = self._context
                parentAnonymousNodes = self._anonymousNodes
                grandParentVariables = self._parentVariables
                self._parentVariables = self._variables
                self._anonymousNodes = {}
                self._variables = self._variables.copy()
                reason2 = self._reason2
                self._reason2 = becauseSubexpression
                if subj is None: subj = self._store.newFormula()
                self._context = subj
                
                while 1:
                    i = self.skipSpace(str, j)
                    if i<0: raise BadSyntax(self._thisDoc, self.lines,
                                    str, i, "needed '}', found end.")
                    
                    if str[i:i+1] == "}":
                        j = i+1
                        break
                    
                    j = self.directiveOrStatement(str,i)
                    if j<0: raise BadSyntax(self._thisDoc, self.lines,
                                    str, i, "expected statement or '}'")

                self._anonymousNodes = parentAnonymousNodes
                self._variables = self._parentVariables
                self._parentVariables = grandParentVariables
                self._context = self._parentContext
                self._reason2 = reason2
                self._parentContext = oldParentContext
                res.append(subj.close())   #  No use until closed
                return j

        if ch == "(":
            thing_type = self._store.newList
            ch2 = str[i+1:i+2]
            if ch2 == '$':
                thing_type = self._store.newSet
                i += 1
            j=i+1

            List = []
            while 1:
                i = self.skipSpace(str, j)
                if i<0: raise BadSyntax(self._thisDoc, self.lines,
                                    str, i, "needed ')', found end.")                    
                if str[i:i+1] == ')':
                    j = i+1
                    break

                item = []
                j = self.item(str,i, item) #@@@@@ should be path, was object
                if j<0: raise BadSyntax(self._thisDoc, self.lines, str, i,
                                        "expected item in list or ')'")
                List.append(self._store.intern(item[0]))
            res.append(thing_type(List, self._context))
            return j

        j = self.tok('this', str, i)   # This context
        if j>=0:
            raise BadSyntax(self._thisDoc, self.lines, str, i,
                "Keyword 'this' was ancient N3. Now use @forSome and @forAll keywords.")
            res.append(self._context)
            return j

        #booleans
        j = self.tok('true', str, i)
        if j>=0:
            res.append(True)
            return j
        j = self.tok('false', str, i)
        if j>=0:
            res.append(False)
            return j

        if subj is None:   # If this can be a named node, then check for a name.
            j = self.uri_ref2(str, i, res)
            if j >= 0:
                return j

        return -1
        
    def property_list(self, str, i, subj):
        """Parse property list
        Leaves the terminating punctuation in the buffer
        """
        while 1:
            j = self.skipSpace(str, i)
            if j<0:
                raise BadSyntax(self._thisDoc, self.lines, str, i,
                            "EOF found when expected verb in property list")
                return j #eof

            if str[j:j+2] ==":-":
                i = j + 2
                res = []
                j = self.node(str, i, res, subj)
                if j<0: raise BadSyntax(self._thisDoc, self.lines, str, i,
                                        "bad {} or () or [] node after :- ")
                i=j
                continue
            i=j
            v = []
            j = self.verb(str, i, v)
            if j<=0:
                return i # void but valid

            objs = []
            i = self.objectList(str, j, objs)
            if i<0: raise BadSyntax(self._thisDoc, self.lines, str, j,
                                                        "objectList expected")
            for obj in objs:
                dir, sym = v[0]
                if dir == '->':
                    self.makeStatement((self._context, sym, subj, obj))
                else:
                    self.makeStatement((self._context, sym, obj, subj))

            j = self.skipSpace(str, i)
            if j<0:
                raise BadSyntax(self._thisDoc, self.lines, str, j,
                                                "EOF found in list of objects")
                return j #eof
            if str[i:i+1] != ";":
                return i
            i = i+1 # skip semicolon and continue

    def commaSeparatedList(self, str, j, res, what):
        """return value: -1 bad syntax; >1 new position in str
        res has things found appended
        """
        i = self.skipSpace(str, j)
        if i<0:
            raise BadSyntax(self._thisDoc, self.lines, str, i,
                                    "EOF found expecting comma sep list")
            return i
        if str[i] == ".": return j  # empty list is OK
        i = what(str, i, res)
        if i<0: return -1
        
        while 1:
            j = self.skipSpace(str, i)
            if j<0: return j # eof
            ch = str[j:j+1]  
            if ch != ",":
                if ch != ".":
                    return -1
                return j    # Found  but not swallowed "."
            i = what(str, j+1, res)
            if i<0:
                raise BadSyntax(self._thisDoc, self.lines, str, i,
                                                "bad list content")
                return i

    def objectList(self, str, i, res):
        i = self.object(str, i, res)
        if i<0: return -1
        while 1:
            j = self.skipSpace(str, i)
            if j<0:
                raise BadSyntax(self._thisDoc, self.lines, str, j,
                                    "EOF found after object")
                return j #eof
            if str[j:j+1] != ",":
                return j    # Found something else!
            i = self.object(str, j+1, res)
            if i<0: return i

    def checkDot(self, str, i):
            j = self.skipSpace(str, i)
            if j<0: return j #eof
            if str[j:j+1] == ".":
                return j+1  # skip
            if str[j:j+1] == "}":
                return j     # don't skip it
            if str[j:j+1] == "]":
                return j
            raise BadSyntax(self._thisDoc, self.lines,
                    str, j, "expected '.' or '}' or ']' at end of statement")
            return i


    def uri_ref2(self, str, i, res):
        """Generate uri from n3 representation.

        Note that the RDF convention of directly concatenating
        NS and local name is now used though I prefer inserting a '#'
        to make the namesapces look more like what XML folks expect.
        """
        qn = []
        j = self.qname(str, i, qn)
        if j>=0:
            pfx, ln = qn[0]
            if pfx is None:
                assert 0, "not used?"
                ns = self._baseURI + ADDED_HASH
            else:
                try:
                    ns = self._bindings[pfx]
                except KeyError:
                    if pfx == "_":  # Magic prefix 2001/05/30, can be overridden
                        res.append(self.anonymousNode(ln))
                        return j
                    raise BadSyntax(self._thisDoc, self.lines, str, i,
                                "Prefix \"%s:\" not bound" % (pfx))
            symb = self._store.newSymbol(ns + ln)
            if symb in self._variables:
                res.append(self._variables[symb])
            else:
                res.append(symb) # @@@ "#" CONVENTION
            if not string.find(ns, "#"):progress(
                        "Warning: no # on namespace %s," % ns)
            return j

        
        i = self.skipSpace(str, i)
        if i<0: return -1

        if str[i] == "?":
            v = []
            j = self.variable(str,i,v)
            if j>0:              #Forget varibles as a class, only in context.
                res.append(v[0])
                return j
            return -1

        elif str[i]=="<":
            i = i + 1
            st = i
            while i < len(str):
                if str[i] == ">":
                    uref = str[st:i] # the join should dealt with "":
                    if self._baseURI:
                        uref = join(self._baseURI, uref) # was: uripath.join
                    else:
                        assert ":" in uref, \
                            "With no base URI, cannot deal with relative URIs"
                    if str[i-1:i]=="#" and not uref[-1:]=="#":
                        uref = uref + "#" # She meant it! Weirdness in urlparse?
                    symb = self._store.newSymbol(uref)
                    if symb in self._variables:
                        res.append(self._variables[symb])
                    else:
                        res.append(symb)
                    return i+1
                i = i + 1
            raise BadSyntax(self._thisDoc, self.lines, str, j,
                            "unterminated URI reference")

        elif self.keywordsSet:
            v = []
            j = self.bareWord(str,i,v)
            if j<0: return -1      #Forget varibles as a class, only in context.
            if v[0] in self.keywords:
                raise BadSyntax(self._thisDoc, self.lines, str, i,
                    'Keyword "%s" not allowed here.' % v[0])
            res.append(self._store.newSymbol(self._bindings[""]+v[0]))
            return j
        else:
            return -1

    def skipSpace(self, str, i):
        """Skip white space, newlines and comments.
        return -1 if EOF, else position of first non-ws character"""
        while 1:
            m = eol.match(str, i)
            if m == None: break
            self.lines = self.lines + 1
            i = m.end()   # Point to first character unmatched
            self.startOfLine = i
        m = ws.match(str, i)
        if m != None:
            i = m.end()
        m = eof.match(str, i)
        if m != None: return -1
        return i

    def variable(self, str, i, res):
        """     ?abc -> variable(:abc)
        """

        j = self.skipSpace(str, i)
        if j<0: return -1

        if str[j:j+1] != "?": return -1
        j=j+1
        i = j
        if str[j] in "0123456789-":
            raise BadSyntax(self._thisDoc, self.lines, str, j,
                            "Varible name can't start with '%s'" % str[j])
            return -1
        while i <len(str) and str[i] not in _notNameChars:
            i = i+1
        if self._parentContext == None:
            varURI = self._store.newSymbol(self._baseURI + "#" +str[j:i])
            if varURI not in self._variables:
                self._variables[varURI] = self._context.newUniversal(varURI
                                , why=self._reason2) 
            res.append(self._variables[varURI])
            return i
            # @@ was: 
            # raise BadSyntax(self._thisDoc, self.lines, str, j,
            #     "Can't use ?xxx syntax for variable in outermost level: %s"
            #     % str[j-1:i])
        varURI = self._store.newSymbol(self._baseURI + "#" +str[j:i])
        if varURI not in self._parentVariables:
            self._parentVariables[varURI] = self._parentContext.newUniversal(varURI
                            , why=self._reason2) 
        res.append(self._parentVariables[varURI])
        return i

    def bareWord(self, str, i, res):
        """     abc -> :abc
        """
        j = self.skipSpace(str, i)
        if j<0: return -1

        if str[j] in "0123456789-" or str[j] in _notNameChars: return -1
        i = j
        while i <len(str) and str[i] not in _notNameChars:
            i = i+1
        res.append(str[j:i])
        return i

    def qname(self, str, i, res):
        """
        xyz:def -> ('xyz', 'def')
        If not in keywords and keywordsSet: def -> ('', 'def')
        :def -> ('', 'def')    
        """

        i = self.skipSpace(str, i)
        if i<0: return -1

        c = str[i]
        if c in "0123456789-+": return -1
        if c not in _notNameChars:
            ln = c
            i = i + 1
            while i < len(str):
                c = str[i]
                if c not in _notNameChars:
                    ln = ln + c
                    i = i + 1
                else: break
        else: # First character is non-alpha
            ln = ''   # Was:  None - TBL (why? useful?)

        if i<len(str) and str[i] == ':':
            pfx = ln
            i = i + 1
            ln = ''
            while i < len(str):
                c = str[i]
                if c not in _notNameChars:
                    ln = ln + c
                    i = i + 1
                else: break

            res.append((pfx, ln))
            return i

        else:  # delimiter was not ":"
            if ln and self.keywordsSet and ln not in self.keywords:
                res.append(('', ln))
                return i
            return -1
            
    def object(self, str, i, res):
        j = self.subject(str, i, res)
        if j>= 0:
            return j
        else:
            j = self.skipSpace(str, i)
            if j<0: return -1
            else: i=j

            if str[i]=='"':
                if str[i:i+3] == '"""': delim = '"""'
                else: delim = '"'
                i = i + len(delim)

                j, s = self.strconst(str, i, delim)

                res.append(self._store.newLiteral(s))
                progress("New string const ", s, j)
                return j
            else:
                return -1

    def nodeOrLiteral(self, str, i, res):
        j = self.node(str, i, res)
        startline = self.lines # Remember where for error messages
        if j>= 0:
            return j
        else:
            j = self.skipSpace(str, i)
            if j<0: return -1
            else: i=j

            ch = str[i]
            if ch in "-+0987654321":
                m = number_syntax.match(str, i)
                if m == None:
                    raise BadSyntax(self._thisDoc, self.lines, str, i,
                                "Bad number syntax")
                j = m.end()
                if m.group('exponent') != None: # includes decimal exponent
                    res.append(float(str[i:j]))
#                   res.append(self._store.newLiteral(str[i:j],
#                       self._store.newSymbol(FLOAT_DATATYPE)))
                elif m.group('decimal') != None:
                    res.append(Decimal(str[i:j]))
                else:
                    res.append(long(str[i:j]))
#                   res.append(self._store.newLiteral(str[i:j],
#                       self._store.newSymbol(INTEGER_DATATYPE)))
                return j

            if str[i]=='"':
                if str[i:i+3] == '"""': delim = '"""'
                else: delim = '"'
                i = i + len(delim)

                dt = None
                j, s = self.strconst(str, i, delim)
                lang = None
                if str[j:j+1] == "@":  # Language?
                    m = langcode.match(str, j+1)
                    if m == None:
                        raise BadSyntax(self._thisDoc, startline, str, i,
                        "Bad language code syntax on string literal, after @")
                    i = m.end()
                    lang = str[j+1:i]
                    j = i
                if str[j:j+2] == "^^":
                    res2 = []
                    j = self.uri_ref2(str, j+2, res2) # Read datatype URI
                    dt = res2[0]
#                     if dt.uriref() == "http://www.w3.org/1999/02/22-rdf-syntax-ns#XMLLiteral":
                    if dt == "http://www.w3.org/1999/02/22-rdf-syntax-ns#XMLLiteral":
                        try:
                            dom = XMLtoDOM('<rdf:envelope xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns">'
                                           + s
                                           + '</rdf:envelope>').firstChild
                        except:
                            raise  ValueError('s="%s"' % s)
                        res.append(self._store.newXMLLiteral(dom))
                        return j
                res.append(self._store.newLiteral(s, dt, lang))
                return j
            else:
                return -1
    
    def uriOf(self, sym):
        if isinstance(sym, types.TupleType):
            return sym[1] # old system for --pipe
        # return sym.uriref() # cwm api
        return sym


    def strconst(self, str, i, delim):
        """parse an N3 string constant delimited by delim.
        return index, val
        """


        j = i
        ustr = u""   # Empty unicode string
        startline = self.lines # Remember where for error messages
        while j<len(str):
            i = j + len(delim)
            if str[j:i] == delim: # done.
                return i, ustr

            if str[j] == '"':
                ustr = ustr + '"'
                j = j + 1
                continue
            m = interesting.search(str, j)  # was str[j:].
            # Note for pos param to work, MUST be compiled  ... re bug?
            assert m , "Quote expected in string at ^ in %s^%s" %(
                str[j-20:j], str[j:j+20]) # we at least have to find a quote

            i = m.start()
            try:
                ustr = ustr + str[j:i]
            except UnicodeError:
                err = ""
                for c in str[j:i]:
                    err = err + (" %02x" % ord(c))
                streason = sys.exc_info()[1].__str__()
                raise BadSyntax(self._thisDoc, startline, str, j,
                "Unicode error appending characters %s to string, because\n\t%s"
                                % (err, streason))
                
#           print "@@@ i = ",i, " j=",j, "m.end=", m.end()

            ch = str[i]
            if ch == '"':
                j = i
                continue
            elif ch == "\r":   # Strip carriage returns
                j = i+1
                continue
            elif ch == "\n":
                if delim == '"':
                    raise BadSyntax(self._thisDoc, startline, str, i,
                                    "newline found in string literal")
                self.lines = self.lines + 1
                ustr = ustr + ch
                j = i + 1
                self.startOfLine = j

            elif ch == "\\":
                j = i + 1
                ch = str[j:j+1]  # Will be empty if string ends
                if not ch:
                    raise BadSyntax(self._thisDoc, startline, str, i,
                                    "unterminated string literal (2)")
                k = string.find('abfrtvn\\"', ch)
                if k >= 0:
                    uch = '\a\b\f\r\t\v\n\\"'[k]
                    ustr = ustr + uch
                    j = j + 1
                elif ch == "u":
                    j, ch = self.uEscape(str, j+1, startline)
                    ustr = ustr + ch
                elif ch == "U":
                    j, ch = self.UEscape(str, j+1, startline)
                    ustr = ustr + ch
                else:
                    raise BadSyntax(self._thisDoc, self.lines, str, i,
                                    "bad escape")

        raise BadSyntax(self._thisDoc, self.lines, str, i,
                        "unterminated string literal")


    def uEscape(self, str, i, startline):
        j = i
        count = 0
        value = 0
        while count < 4:  # Get 4 more characters
            ch = str[j:j+1].lower() 
                # sbp http://ilrt.org/discovery/chatlogs/rdfig/2002-07-05
            j = j + 1
            if ch == "":
                raise BadSyntax(self._thisDoc, startline, str, i,
                                "unterminated string literal(3)")
            k = string.find("0123456789abcdef", ch)
            if k < 0:
                raise BadSyntax(self._thisDoc, startline, str, i,
                                "bad string literal hex escape")
            value = value * 16 + k
            count = count + 1
        uch = unichr(value)
        return j, uch

    def UEscape(self, str, i, startline):
        stringType = type('')
        j = i
        count = 0
        value = '\\U'
        while count < 8:  # Get 8 more characters
            ch = str[j:j+1].lower() 
            # sbp http://ilrt.org/discovery/chatlogs/rdfig/2002-07-05
            j = j + 1
            if ch == "":
                raise BadSyntax(self._thisDoc, startline, str, i,
                                "unterminated string literal(3)")
            k = string.find("0123456789abcdef", ch)
            if k < 0:
                raise BadSyntax(self._thisDoc, startline, str, i,
                                "bad string literal hex escape")
            value = value + ch
            count = count + 1
            
        uch = stringType(value).decode('unicode-escape')
        return j, uch

wide_build = True
try:
    unichr(0x10000)
except ValueError:
    wide_build = False

# If we are going to do operators then they should generate
#  [  is  operator:plus  of (  \1  \2 ) ]


class BadSyntax(SyntaxError):
    def __init__(self, uri, lines, str, i, why):
        self._str = str.encode('utf-8') # Better go back to strings for errors
        self._i = i
        self._why = why
        self.lines = lines
        self._uri = uri 

    def __str__(self):
        str = self._str
        i = self._i
        st = 0
        if i>60:
            pre="..."
            st = i - 60
        else: pre=""
        if len(str)-i > 60: post="..."
        else: post=""

        return 'at line %i of <%s>:\nBad syntax (%s) at ^ in:\n"%s%s^%s%s"' \
               % (self.lines +1, self._uri, self._why, pre,
                                    str[st:i], str[i:i+60], post)



def stripCR(str):
    res = ""
    for ch in str:
        if ch != "\r":
            res = res + ch
    return res

def dummyWrite(x):
    pass

################################################################################


def toBool(s):
    if s == 'true' or s == 'True' or s == '1':
        return True
    if s == 'false' or s == 'False' or s == '0':
        return False
    raise ValueError(s)
    




class Formula(object): 
   number = 0

   def __init__(self, parent): 
      self.counter = 0
      Formula.number += 1
      self.number = Formula.number
      self.existentials = {}
      self.universals = {}

      self.quotedgraph=QuotedGraph(store=parent.store, identifier=self.id())

   def __str__(self): 
      return '_:Formula%s' % self.number

   def id(self): 
      return BNode('_:Formula%s' % self.number)

   def newBlankNode(self, uri=None, why=None): 
      if uri is None: 
         self.counter += 1
         b = BNode('f%sb%s' % (id(self), self.counter))
      else: b = BNode(uri.split('#').pop().replace('_', 'b'))
      return b

   def newUniversal(self, uri, why=None): 
      return Variable(uri.split('#').pop())

   def declareExistential(self, x): 
      self.existentials[x] = self.newBlankNode()

   def close(self): 
      
      return self.quotedgraph

r_hibyte = re.compile(r'([\x80-\xff])')
def iri(uri): 
   return uri.decode('utf-8')
   # return unicode(r_hibyte.sub(lambda m: '%%%02X' % ord(m.group(1)), uri))

class RDFSink(object): 
   def __init__(self, graph): 
      self.rootFormula = None
      self.counter = 0
      self.graph=graph
      

   def newFormula(self): 
      assert self.graph.store.formula_aware
      f = Formula(self.graph)
      return f

   def newSymbol(self, *args): 
      uri = args[0].encode('utf-8')
      return URIRef(iri(uri))

   def newBlankNode(self, arg=None, **kargs): 
      if isinstance(arg, Formula): 
         return arg.newBlankNode()
      elif arg is None: 
         self.counter += 1
         b = BNode('n' + str(self.counter))
      else: b = BNode(str(arg[0]).split('#').pop().replace('_', 'b'))
      return b

   def newLiteral(self, s, dt, lang): 
      if dt: return Literal(s, datatype=dt)
      else: return Literal(s, lang=lang)

   def newList(self, n, f): 
      if not n: 
         return self.newSymbol(
            'http://www.w3.org/1999/02/22-rdf-syntax-ns#nil'
         )

      a = self.newBlankNode(f)
      first = self.newSymbol(
         'http://www.w3.org/1999/02/22-rdf-syntax-ns#first'
      )
      rest = self.newSymbol('http://www.w3.org/1999/02/22-rdf-syntax-ns#rest')
      self.makeStatement((f, first, a, n[0]))
      self.makeStatement((f, rest, a, self.newList(n[1:], f)))
      return a

   def newSet(self, *args): 
      return set(args)

   def setDefaultNamespace(self, *args): 
      return ':'.join(repr(n) for n in args)

   def makeStatement(self, quadruple, why=None): 
      f, p, s, o = quadruple

      if hasattr(p, 'formula'): 
         raise Exception("Formula used as predicate")

      s = self.normalise(f, s)
      p = self.normalise(f, p)
      o = self.normalise(f, o)


      if f == self.rootFormula: 
         # print s, p, o, '.'
         self.graph.add((s, p, o))
      else: 
         f.quotedgraph.add((s,p,o))


      #return str(quadruple)

   def normalise(self, f, n): 
      if isinstance(n, tuple): 
         return URIRef(unicode(n[1]))

      # if isinstance(n, list): 
      #    rdflist, f = n
      #    name = self.newBlankNode()
      #    if f == self.rootFormula: 
      #       sublist = name
      #       for i in xrange(0, len(rdflist) - 1): 
      #          print sublist, 'first', rdflist[i]
      #          rest = self.newBlankNode()
      #          print sublist, 'rest', rest
      #          sublist = rest
      #       print sublist, 'first', rdflist[-1]
      #       print sublist, 'rest', 'nil'
      #    return name

      if isinstance(n, bool): 
         s = Literal(str(n).lower(), datatype=BOOLEAN_DATATYPE)
         return s

      if isinstance(n, int) or isinstance(n, long): 
         s = Literal(unicode(n), datatype=INTEGER_DATATYPE)
         return s

      if isinstance(n, Decimal): 
         value = str(n.normalize())
         if value == '-0': 
            value = '0'
         s = Literal(value, datatype=DECIMAL_DATATYPE )
         return s

      if isinstance(n, float): 
         s = Literal(str(n), datatype=DOUBLE_DATATYPE )
         return s

      if f.existentials.has_key(n): 
         return f.existentials[n]

      # if isinstance(n, Var): 
      #    if f.universals.has_key(n): 
      #       return f.universals[n]
      #    f.universals[n] = f.newBlankNode()
      #    return f.universals[n]

      return n

   def intern(self, something): 
      return something

   def bind(self, pfx, uri): 
      pass # print pfx, ':', uri

   def startDoc(self, formula): 
      self.rootFormula = formula

   def endDoc(self, formula): 
      pass

        
###################################################
#
#   Utilities
#

Escapes = {'a':  '\a',
           'b':  '\b',
           'f':  '\f',
           'r':  '\r',
           't':  '\t',
           'v':  '\v',
           'n':  '\n',
           '\\': '\\',
           '"':  '"'}

forbidden1 = re.compile(ur'[\\\"\a\b\f\r\v\u0080-\U0000ffff]')
forbidden2 = re.compile(ur'[\\\"\a\b\f\r\v\t\n\u0080-\U0000ffff]')
#"
def stringToN3(str, singleLine=0, flags=""):
    res = ''
    if (len(str) > 20 and
        str[-1] <> '"' and
        not singleLine and
        (string.find(str, "\n") >=0 
         or string.find(str, '"') >=0)):
        delim= '"""'
        forbidden = forbidden1   # (allow tabs too now)
    else:
        delim = '"'
        forbidden = forbidden2
        
    i = 0

    while i < len(str):
        m = forbidden.search(str, i)
        if not m:
            break

        j = m.start()
        res = res + str[i:j]
        ch = m.group(0)
        if ch == '"' and delim == '"""' and str[j:j+3] != '"""':  #"
            res = res + ch
        else:
            k = string.find('\a\b\f\r\t\v\n\\"', ch)
            if k >= 0: res = res + "\\" + 'abfrtvn\\"'[k]
            else:
                if 'e' in flags:
#                res = res + ('\\u%04x' % ord(ch))
                    res = res + ('\\u%04X' % ord(ch)) 
                    # http://www.w3.org/TR/rdf-testcases/#ntriples
                else:
                    res = res + ch
        i = j + 1

    # The following code fixes things for really high range Unicode
    newstr = ""
    for ch in res + str[i:]:
        if ord(ch)>65535:
            newstr = newstr + ('\\U%08X' % ord(ch)) 
                # http://www.w3.org/TR/rdf-testcases/#ntriples
        else:
            newstr = newstr + ch
    #

    return delim + newstr + delim

def backslashUify(ustr):
    """Use URL encoding to return an ASCII string corresponding
        to the given unicode"""
#    progress("String is "+`ustr`)
#    s1=ustr.encode('utf-8')
    str  = ""
    for ch in ustr:  # .encode('utf-8'):
        if ord(ch) > 65535:
            ch = "\\U%08X" % ord(ch)       
        elif ord(ch) > 126:
            ch = "\\u%04X" % ord(ch)
        else:
            ch = "%c" % ord(ch)
        str = str + ch
    return str

def hexify(ustr):
    """Use URL encoding to return an ASCII string
    corresponding to the given UTF8 string

    >>> hexify("http://example/a b")
    'http://example/a%20b'
    
    """   #"
#    progress("String is "+`ustr`)
#    s1=ustr.encode('utf-8')
    str  = ""
    for ch in ustr:  # .encode('utf-8'):
        if ord(ch) > 126 or ord(ch) < 33 :
            ch = "%%%02X" % ord(ch)
        else:
            ch = "%c" % ord(ch)
        str = str + ch
    return str
    
def dummy():
        res = ""
        if len(str) > 20 and (string.find(str, "\n") >=0 
                                or string.find(str, '"') >=0):
                delim= '"""'
                forbidden = "\\\"\a\b\f\r\v"    # (allow tabs too now)
        else:
                delim = '"'
                forbidden = "\\\"\a\b\f\r\v\t\n"
        for i in range(len(str)):
                ch = str[i]
                j = string.find(forbidden, ch)
                if ch == '"' and delim == '"""' \
                                and i+1 < len(str) and str[i+1] != '"':
                    j=-1   # Single quotes don't need escaping in long format
                if j>=0: ch = "\\" + '\\"abfrvtn'[j]
                elif ch not in "\n\t" and (ch < " " or ch > "}"):
                    ch = "[[" + `ch` + "]]" #[2:-1] # Use python
                res = res + ch
        return delim + res + delim


class N3Parser(Parser):

    def __init__(self):
        pass

    def parse(self, source, graph):
        # we're currently being handed a Graph, not a ConjunctiveGraph
        assert graph.store.context_aware # is this implied by formula_aware
        assert graph.store.formula_aware

        conj_graph = ConjunctiveGraph(store=graph.store)
        conj_graph.default_context = graph # TODO: CG __init__ should have a default_context arg
        # TODO: update N3Processor so that it can use conj_graph as the sink
        conj_graph.namespace_manager = graph.namespace_manager
        sink = RDFSink(conj_graph)

        baseURI = graph.absolutize(source.getPublicId() or source.getSystemId() or "")
        p = SinkParser(sink, baseURI=baseURI) 
        
        p.loadStream(source.getByteStream())

        for prefix, namespace in p._bindings.items():
             conj_graph.bind(prefix, namespace)




def _test():
    import doctest
    doctest.testmod()


# if __name__ == '__main__':
#     _test()

def main(): 
   g=ConjunctiveGraph()

   sink = RDFSink(g)
   base = 'file://' + os.path.join(os.getcwd(), sys.argv[1])

   p = SinkParser(sink, baseURI=base)
   p._bindings[''] = p._baseURI + '#'
   p.startDoc()

   f = open(sys.argv[1], 'rb')
   bytes = f.read()
   f.close()

   p.feed(bytes)
   p.endDoc()
   for t in g.quads((None,None,None)):

      print t

if __name__ == '__main__':
    main()

#ends

