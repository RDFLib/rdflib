from __future__ import generators

import logging

_logger = logging.getLogger(__name__)

import os

from urlparse import urljoin, urldefrag
from urllib import pathname2url

from rdflib.term import URIRef, Variable, _XSD_PFX


class Namespace(URIRef):

    @property
    def title(self):
        return URIRef(self + 'title')

    def term(self, name):
        return URIRef(self + name)

    def __getitem__(self, key, default=None):
        return self.term(key)

    def __getattr__(self, name):
        if name.startswith("__"): # ignore any special Python names!
            raise AttributeError
        else:
            return self.term(name)


class NamespaceDict(dict):

    def __new__(cls, uri=None, context=None):
        inst = dict.__new__(cls)
        inst.uri = uri # TODO: do we need to set these both here and in __init__ ??
        inst.__context = context
        return inst

    def __init__(self, uri, context=None):
        self.uri = uri
        self.__context = context

    def term(self, name):
        uri = self.get(name)
        if uri is None:
            uri = URIRef(self.uri + name)
            if self.__context and (uri, None, None) not in self.__context:
                _logger.warning("%s not defined" % uri)
            self[name] = uri
        return uri

    def __getattr__(self, name):
        return self.term(name)

    def __getitem__(self, key, default=None):
        return self.term(key) or default

    def __str__(self):
        return self.uri

    def __repr__(self):
        return """rdflib.namespace.NamespaceDict('%s')""" % str(self.uri)


class ClosedNamespace(object):
    """

    """

    def __init__(self, uri, terms):
        self.uri = uri
        self.__uris = {}
        for t in terms:
            self.__uris[t] = URIRef(self.uri + t)

    def term(self, name):
        uri = self.__uris.get(name)
        if uri is None:
            raise Exception("term '%s' not in namespace '%s'" % (name, self.uri))
        else:
            return uri

    def __getitem__(self, key, default=None):
        return self.term(key)

    def __getattr__(self, name):
        if name.startswith("__"): # ignore any special Python names!
            raise AttributeError
        else:
            return self.term(name)

    def __str__(self):
        return self.uri

    def __repr__(self):
        return """rdf.namespace.ClosedNamespace('%s')""" % str(self.uri)


class _RDFNamespace(ClosedNamespace):
    def __init__(self):
        super(_RDFNamespace, self).__init__(
            URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#"),
            terms=[
        # Syntax Names
        "RDF", "Description", "ID", "about", "parseType", "resource", "li", "nodeID", "datatype",

        # RDF Classes
        "Seq", "Bag", "Alt", "Statement", "Property", "XMLLiteral", "List", "PlainLiteral",

        # RDF Properties
        "subject", "predicate", "object", "type", "value", "first", "rest",
        # and _n where n is a non-negative integer

        # RDF Resources
        "nil"]
            )

    def term(self, name):
        try:
            i = int(name)
            return URIRef("%s_%s" % (self.uri, i))
        except ValueError, e:
            return super(_RDFNamespace, self).term(name)

RDF = _RDFNamespace()

RDFS = ClosedNamespace(
    uri = URIRef("http://www.w3.org/2000/01/rdf-schema#"),
    terms = [
        "Resource", "Class", "subClassOf", "subPropertyOf", "comment", "label",
        "domain", "range", "seeAlso", "isDefinedBy", "Literal", "Container",
        "ContainerMembershipProperty", "member", "Datatype"]
    )

OWL = Namespace('http://www.w3.org/2002/07/owl#')

XSD = Namespace(_XSD_PFX)


class NamespaceManager(object):
    def __init__(self, graph):
        self.graph = graph
        self.__cache = {}
        self.__log = None
        self.bind("xml", u"http://www.w3.org/XML/1998/namespace")
        self.bind("rdf", "http://www.w3.org/1999/02/22-rdf-syntax-ns#")
        self.bind("rdfs", "http://www.w3.org/2000/01/rdf-schema#")

    def reset(self):
        self.__cache = {}

    def __get_store(self):
        return self.graph.store
    store = property(__get_store)

    def qname(self, uri):
        prefix, namespace, name = self.compute_qname(uri)
        if prefix=="":
            return name
        else:
            return ":".join((prefix, name))

    def normalizeUri(self,rdfTerm):
        """
        Takes an RDF Term and 'normalizes' it into a QName (using the registered prefix)
        or (unlike compute_qname) the Notation 3 form for URIs: <...URI...>
        """
        try:
            namespace, name = split_uri(rdfTerm)
            namespace = URIRef(namespace)
        except:
            if isinstance(rdfTerm,Variable):
                return "?%s"%rdfTerm
            else:
                return "<%s>"%rdfTerm
        prefix = self.store.prefix(namespace)
        if prefix is None and isinstance(rdfTerm,Variable):
            return "?%s"%rdfTerm
        elif prefix is None:
            return "<%s>"%rdfTerm
        else:
            qNameParts = self.compute_qname(rdfTerm)
            return ':'.join([qNameParts[0],qNameParts[-1]])

    def compute_qname(self, uri):
        if not uri in self.__cache:
            namespace, name = split_uri(uri)
            namespace = URIRef(namespace)
            prefix = self.store.prefix(namespace)
            if prefix is None:
                prefix = "_%s" % len(list(self.store.namespaces()))
                self.bind(prefix, namespace)
            self.__cache[uri] = (prefix, namespace, name)
        return self.__cache[uri]

    def bind(self, prefix, namespace, override=True):
        namespace = URIRef(namespace)
        # When documenting explain that override only applies in what cases
        if prefix is None:
            prefix = ''
        bound_namespace = self.store.namespace(prefix)
        if bound_namespace and bound_namespace!=namespace:
            # prefix already in use for different namespace
            #
            # append number to end of prefix until we find one
            # that's not in use.
            if not prefix:
                prefix = "default"
            num = 1
            while 1:
                new_prefix = "%s%s" % (prefix, num)
                if not self.store.namespace(new_prefix):
                    break
                num +=1
            self.store.bind(new_prefix, namespace)
        else:
            bound_prefix = self.store.prefix(namespace)
            if bound_prefix is None:
                self.store.bind(prefix, namespace)
            elif bound_prefix == prefix:
                pass # already bound
            else:
                if override or bound_prefix.startswith("_"): # or a generated prefix
                    self.store.bind(prefix, namespace)

    def namespaces(self):
        for prefix, namespace in self.store.namespaces():
            namespace = URIRef(namespace)
            yield prefix, namespace

    def absolutize(self, uri, defrag=1):
        base = urljoin("file:", pathname2url(os.getcwd()))
        result = urljoin("%s/" % base, uri, allow_fragments=not defrag)
        if defrag:
            result = urldefrag(result)[0]
        if not defrag:
            if uri and uri[-1]=="#" and result[-1]!="#":
                result = "%s#" % result
        return URIRef(result)

# From: http://www.w3.org/TR/REC-xml#NT-CombiningChar
#
# * Name start characters must have one of the categories Ll, Lu, Lo,
#   Lt, Nl.
#
# * Name characters other than Name-start characters must have one of
#   the categories Mc, Me, Mn, Lm, or Nd.
#
# * Characters in the compatibility area (i.e. with character code
#   greater than #xF900 and less than #xFFFE) are not allowed in XML
#   names.
#
# * Characters which have a font or compatibility decomposition
#   (i.e. those with a "compatibility formatting tag" in field 5 of the
#   database -- marked by field 5 beginning with a "<") are not allowed.
#
# * The following characters are treated as name-start characters rather
#   than name characters, because the property file classifies them as
#   Alphabetic: [#x02BB-#x02C1], #x0559, #x06E5, #x06E6.
#
# * Characters #x20DD-#x20E0 are excluded (in accordance with Unicode
#   2.0, section 5.14).
#
# * Character #x00B7 is classified as an extender, because the property
#   list so identifies it.
#
# * Character #x0387 is added as a name character, because #x00B7 is its
#   canonical equivalent.
#
# * Characters ':' and '_' are allowed as name-start characters.
#
# * Characters '-' and '.' are allowed as name characters.

from unicodedata import category, decomposition

NAME_START_CATEGORIES = ["Ll", "Lu", "Lo", "Lt", "Nl"]
NAME_CATEGORIES = NAME_START_CATEGORIES + ["Mc", "Me", "Mn", "Lm", "Nd"]
ALLOWED_NAME_CHARS = [u"\u00B7", u"\u0387", u"-", u".", u"_"]

# http://www.w3.org/TR/REC-xml-names/#NT-NCName
#  [4] NCName ::= (Letter | '_') (NCNameChar)* /* An XML Name, minus
#      the ":" */
#  [5] NCNameChar ::= Letter | Digit | '.' | '-' | '_' | CombiningChar
#      | Extender

def is_ncname(name):
    first = name[0]
    if first=="_" or category(first) in NAME_START_CATEGORIES:
        for i in xrange(1, len(name)):
            c = name[i]
            if not category(c) in NAME_CATEGORIES:
                if c in ALLOWED_NAME_CHARS:
                    continue
                return 0
            #if in compatibility area
            #if decomposition(c)!='':
            #    return 0

        return 1
    else:
        return 0

XMLNS = "http://www.w3.org/XML/1998/namespace"

def split_uri(uri):
    if uri.startswith(XMLNS):
        return (XMLNS, uri.split(XMLNS)[1])
    length = len(uri)
    for i in xrange(0, length):
        c = uri[-i-1]
        if not category(c) in NAME_CATEGORIES:
            if c in ALLOWED_NAME_CHARS:
                continue
            for j in xrange(-1-i, length):
                if category(uri[j]) in NAME_START_CATEGORIES or uri[j]=="_":
                    ns = uri[:j]
                    if not ns:
                        break
                    ln = uri[j:]
                    return (ns, ln)
            break
    raise Exception("Can't split '%s'" % uri)
