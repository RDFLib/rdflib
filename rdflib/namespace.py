from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import logging

import os
from unicodedata import category

from six import string_types
from six import text_type

from six.moves.urllib.request import pathname2url
from six.moves.urllib.parse import urldefrag
from six.moves.urllib.parse import urljoin

from rdflib.term import URIRef, Variable, _XSD_PFX, _is_valid_uri

__doc__ = """
===================
Namespace Utilities
===================

RDFLib provides mechanisms for managing Namespaces.

In particular, there is a :class:`~rdflib.namespace.Namespace` class
that takes as its argument the base URI of the namespace.

.. code-block:: pycon

    >>> from rdflib.namespace import Namespace
    >>> owl = Namespace('http://www.w3.org/2002/07/owl#')

Fully qualified URIs in the namespace can be constructed either by attribute
or by dictionary access on Namespace instances:

.. code-block:: pycon

    >>> owl.seeAlso
    rdflib.term.URIRef(u'http://www.w3.org/2002/07/owl#seeAlso')
    >>> owl['seeAlso']
    rdflib.term.URIRef(u'http://www.w3.org/2002/07/owl#seeAlso')


Automatic handling of unknown predicates
-----------------------------------------

As a programming convenience, a namespace binding is automatically
created when :class:`rdflib.term.URIRef` predicates are added to the graph.

Importable namespaces
-----------------------

The following namespaces are available by directly importing from rdflib:

* RDF
* RDFS
* OWL
* XSD
* FOAF
* SKOS
* DOAP
* DC
* DCTERMS
* VOID

.. code-block:: pycon

    >>> from rdflib import OWL
    >>> OWL.seeAlso
    rdflib.term.URIRef(u'http://www.w3.org/2002/07/owl#seeAlso')

"""

__all__ = [
    'is_ncname', 'split_uri', 'Namespace',
    'ClosedNamespace', 'NamespaceManager',
    'XMLNS', 'RDF', 'RDFS', 'XSD', 'OWL',
    'SKOS', 'DOAP', 'FOAF', 'DC', 'DCTERMS', 'VOID']

logger = logging.getLogger(__name__)


class Namespace(text_type):

    __doc__ = """
    Utility class for quickly generating URIRefs with a common prefix

    >>> from rdflib import Namespace
    >>> n = Namespace("http://example.org/")
    >>> n.Person # as attribute
    rdflib.term.URIRef(u'http://example.org/Person')
    >>> n['first-name'] # as item - for things that are not valid python identifiers
    rdflib.term.URIRef(u'http://example.org/first-name')

    """

    def __new__(cls, value):
        try:
            rt = text_type.__new__(cls, value)
        except UnicodeDecodeError:
            rt = text_type.__new__(cls, value, 'utf-8')
        return rt

    @property
    def title(self):
        return URIRef(self + 'title')

    def term(self, name):
        # need to handle slices explicitly because of __getitem__ override
        return URIRef(self + (name if isinstance(name, string_types) else ''))

    def __getitem__(self, key, default=None):
        return self.term(key)

    def __getattr__(self, name):
        if name.startswith("__"):  # ignore any special Python names!
            raise AttributeError
        else:
            return self.term(name)

    def __repr__(self):
        return "Namespace(%r)" % text_type(self)


class URIPattern(text_type):

    __doc__ = """
    Utility class for creating URIs according to some pattern
    This supports either new style formatting with .format
    or old-style with % operator

    >>> u=URIPattern("http://example.org/%s/%d/resource")
    >>> u%('books', 12345)
    rdflib.term.URIRef(u'http://example.org/books/12345/resource')

    """

    def __new__(cls, value):
        try:
            rt = text_type.__new__(cls, value)
        except UnicodeDecodeError:
            rt = text_type.__new__(cls, value, 'utf-8')
        return rt

    def __mod__(self, *args, **kwargs):
        return URIRef(text_type(self).__mod__(*args, **kwargs))

    def format(self, *args, **kwargs):
        return URIRef(text_type.format(self, *args, **kwargs))

    def __repr__(self):
        return "URIPattern(%r)" % text_type(self)


class ClosedNamespace(object):
    """
    A namespace with a closed list of members

    Trying to create terms not listen is an error
    """

    def __init__(self, uri, terms):
        self.uri = uri
        self.__uris = {}
        for t in terms:
            self.__uris[t] = URIRef(self.uri + t)

    def term(self, name):
        uri = self.__uris.get(name)
        if uri is None:
            raise KeyError(
                "term '{}' not in namespace '{}'".format(name, self.uri)
            )
        else:
            return uri

    def __getitem__(self, key, default=None):
        return self.term(key)

    def __getattr__(self, name):
        if name.startswith("__"):  # ignore any special Python names!
            raise AttributeError
        else:
            try:
                return self.term(name)
            except KeyError as e:
                raise AttributeError(e)

    def __str__(self):
        return text_type(self.uri)

    def __repr__(self):
        return "rdf.namespace.ClosedNamespace(%r)" % text_type(self.uri)


class _RDFNamespace(ClosedNamespace):
    """
    Closed namespace for RDF terms
    """

    def __init__(self):
        super(_RDFNamespace, self).__init__(
            URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#"),
            terms=[
                # Syntax Names
                "RDF", "Description", "ID", "about", "parseType",
                "resource", "li", "nodeID", "datatype",

                # RDF Classes
                "Seq", "Bag", "Alt", "Statement", "Property",
                "List", "PlainLiteral",

                # RDF Properties
                "subject", "predicate", "object", "type",
                "value", "first", "rest",
                # and _n where n is a non-negative integer

                # RDF Resources
                "nil",

                # Added in RDF 1.1
                "XMLLiteral", "HTML", "langString",
            
                # Added in JSON-LD 1.1
                "JSON", "CompoundLiteral", "language", "direction"]
        )

    def term(self, name):
        # Container membership properties
        if name.startswith('_'):
            try:
                i = int(name[1:])
            except ValueError:
                pass
            else:
                if i > 0:
                    return URIRef("%s_%s" % (self.uri, i))

        return super(_RDFNamespace, self).term(name)


RDF = _RDFNamespace()


RDFS = ClosedNamespace(
    uri=URIRef("http://www.w3.org/2000/01/rdf-schema#"),
    terms=[
        "Resource", "Class", "subClassOf", "subPropertyOf", "comment", "label",
        "domain", "range", "seeAlso", "isDefinedBy", "Literal", "Container",
        "ContainerMembershipProperty", "member", "Datatype"]
)

OWL = Namespace('http://www.w3.org/2002/07/owl#')

XSD = Namespace(_XSD_PFX)

CSVW = Namespace('http://www.w3.org/ns/csvw#')
DC = Namespace('http://purl.org/dc/elements/1.1/')
DCAT = Namespace('http://www.w3.org/ns/dcat#')
DCTERMS = Namespace('http://purl.org/dc/terms/')
DOAP = Namespace('http://usefulinc.com/ns/doap#')
FOAF = ClosedNamespace(
    uri=URIRef('http://xmlns.com/foaf/0.1/'),
    terms=[
        # all taken from http://xmlns.com/foaf/spec/
        'Agent', 'Person', 'name', 'title', 'img',
        'depiction', 'depicts', 'familyName',
        'givenName', 'knows', 'based_near', 'age', 'made',
        'maker', 'primaryTopic', 'primaryTopicOf', 'Project', 'Organization',
        'Group', 'member', 'Document', 'Image', 'nick',
        'mbox', 'homepage', 'weblog', 'openid', 'jabberID',
        'mbox_sha1sum', 'interest', 'topic_interest', 'topic', 'page',
        'workplaceHomepage', 'workInfoHomepage', 'schoolHomepage', 'publications', 'currentProject',
        'pastProject', 'account', 'OnlineAccount', 'accountName', 'accountServiceHomepage',
        'PersonalProfileDocument', 'tipjar', 'sha1', 'thumbnail', 'logo'
    ]
)
ODRL2 = Namespace('http://www.w3.org/ns/odrl/2/')
ORG = Namespace('http://www.w3.org/ns/org#')
PROV = ClosedNamespace(
    uri=URIRef('http://www.w3.org/ns/prov#'),
    terms=[
        'Entity', 'Activity', 'Agent', 'wasGeneratedBy', 'wasDerivedFrom',
        'wasAttributedTo', 'startedAtTime', 'used', 'wasInformedBy', 'endedAtTime',
        'wasAssociatedWith', 'actedOnBehalfOf', 'Collection', 'EmptyCollection', 'Bundle',
        'Person', 'SoftwareAgent', 'Organization', 'Location', 'alternateOf',
        'specializationOf', 'generatedAtTime', 'hadPrimarySource', 'value', 'wasQuotedFrom',
        'wasRevisionOf', 'invalidatedAtTime', 'wasInvalidatedBy', 'hadMember', 'wasStartedBy',
        'wasEndedBy', 'invalidated', 'influenced', 'atLocation', 'generated',
        'Influence', 'EntityInfluence', 'Usage', 'Start', 'End',
        'Derivation', 'PrimarySource', 'Quotation', 'Revision', 'ActivityInfluence',
        'Generation', 'Communication', 'Invalidation', 'AgentInfluence',
        'Attribution', 'Association', 'Plan', 'Delegation', 'InstantaneousEvent',
        'Role', 'wasInfluencedBy', 'qualifiedInfluence', 'qualifiedGeneration', 'qualifiedDerivation',
        'qualifiedPrimarySource', 'qualifiedQuotation', 'qualifiedRevision', 'qualifiedAttribution',
        'qualifiedInvalidation', 'qualifiedStart', 'qualifiedUsage', 'qualifiedCommunication', 'qualifiedAssociation',
        'qualifiedEnd', 'qualifiedDelegation', 'influencer', 'entity', 'hadUsage', 'hadGeneration',
        'activity', 'agent', 'hadPlan', 'hadActivity', 'atTime', 'hadRole'
    ]
)
PROF = Namespace('http://www.w3.org/ns/dx/prof/')
SDO = Namespace('https://schema.org/')
SH = Namespace('http://www.w3.org/ns/shacl#')
SKOS = ClosedNamespace(
    uri=URIRef('http://www.w3.org/2004/02/skos/core#'),
    terms=[
        # all taken from https://www.w3.org/TR/skos-reference/#L1302
        'Concept', 'ConceptScheme', 'inScheme', 'hasTopConcept', 'topConceptOf',
        'altLabel', 'hiddenLabel', 'prefLabel', 'notation', 'changeNote',
        'definition', 'editorialNote', 'example', 'historyNote', 'note',
        'scopeNote', 'broader', 'broaderTransitive', 'narrower', 'narrowerTransitive',
        'related', 'semanticRelation', 'Collection', 'OrderedCollection', 'member',
        'memberList', 'broadMatch', 'closeMatch', 'exactMatch', 'mappingRelation',
        'narrowMatch', 'relatedMatch'
    ]
)
SOSA = Namespace('http://www.w3.org/ns/ssn/')
SSN = Namespace('http://www.w3.org/ns/sosa/')
TIME = Namespace('http://www.w3.org/2006/time#')
VOID = Namespace('http://rdfs.org/ns/void#')


class NamespaceManager(object):
    """

    Class for managing prefix => namespace mappings

    Sample usage from FuXi ...

    .. code-block:: python

        ruleStore = N3RuleStore(additionalBuiltins=additionalBuiltins)
        nsMgr = NamespaceManager(Graph(ruleStore))
        ruleGraph = Graph(ruleStore,namespace_manager=nsMgr)


    and ...

    .. code-block:: pycon

        >>> import rdflib
        >>> from rdflib import Graph
        >>> from rdflib.namespace import Namespace, NamespaceManager
        >>> exNs = Namespace('http://example.com/')
        >>> namespace_manager = NamespaceManager(Graph())
        >>> namespace_manager.bind('ex', exNs, override=False)
        >>> g = Graph()
        >>> g.namespace_manager = namespace_manager
        >>> all_ns = [n for n in g.namespace_manager.namespaces()]
        >>> assert ('ex', rdflib.term.URIRef('http://example.com/')) in all_ns
        >>>

    """

    def __init__(self, graph):
        self.graph = graph
        self.__cache = {}
        self.__cache_strict = {}
        self.__log = None
        self.__strie = {}
        self.__trie = {}
        for p, n in self.namespaces():  # self.bind is not always called
            insert_trie(self.__trie, str(n))
        self.bind("xml", "http://www.w3.org/XML/1998/namespace")
        self.bind("rdf", RDF)
        self.bind("rdfs", RDFS)
        self.bind("xsd", XSD)

    def reset(self):
        self.__cache = {}
        self.__strie = {}
        self.__trie = {}
        for p, n in self.namespaces():  # repopulate the trie
            insert_trie(self.__trie, str(n))

    def __get_store(self):
        return self.graph.store
    store = property(__get_store)

    def qname(self, uri):
        prefix, namespace, name = self.compute_qname(uri)
        if prefix == "":
            return name
        else:
            return ":".join((prefix, name))

    def qname_strict(self, uri):
        prefix, namespace, name = self.compute_qname_strict(uri)
        if prefix == '':
            return name
        else:
            return ':'.join((prefix, name))

    def normalizeUri(self, rdfTerm):
        """
        Takes an RDF Term and 'normalizes' it into a QName (using the
        registered prefix) or (unlike compute_qname) the Notation 3
        form for URIs: <...URI...>
        """
        try:
            namespace, name = split_uri(rdfTerm)
            if namespace not in self.__strie:
                insert_strie(self.__strie, self.__trie, str(namespace))
            namespace = URIRef(text_type(namespace))
        except:
            if isinstance(rdfTerm, Variable):
                return "?%s" % rdfTerm
            else:
                return "<%s>" % rdfTerm
        prefix = self.store.prefix(namespace)
        if prefix is None and isinstance(rdfTerm, Variable):
            return "?%s" % rdfTerm
        elif prefix is None:
            return "<%s>" % rdfTerm
        else:
            qNameParts = self.compute_qname(rdfTerm)
            return ':'.join([qNameParts[0], qNameParts[-1]])

    def compute_qname(self, uri, generate=True):

        if not _is_valid_uri(uri):
            raise ValueError(
                '"{}" does not look like a valid URI, cannot serialize this. Did you want to urlencode it?'.format(uri)
            )

        if uri not in self.__cache:
            try:
                namespace, name = split_uri(uri)
            except ValueError as e:
                namespace = URIRef(uri)
                prefix = self.store.prefix(namespace)
                if not prefix:
                    raise e
            if namespace not in self.__strie:
                insert_strie(self.__strie, self.__trie, namespace)

            if self.__strie[namespace]:
                pl_namespace = get_longest_namespace(self.__strie[namespace], uri)
                if pl_namespace is not None:
                    namespace = pl_namespace
                    name = uri[len(namespace):]

            namespace = URIRef(namespace)
            prefix = self.store.prefix(namespace)  # warning multiple prefixes problem

            if prefix is None:
                if not generate:
                    raise KeyError(
                        "No known prefix for {} and generate=False".format(namespace)
                    )
                num = 1
                while 1:
                    prefix = "ns%s" % num
                    if not self.store.namespace(prefix):
                        break
                    num += 1
                self.bind(prefix, namespace)
            self.__cache[uri] = (prefix, namespace, name)
        return self.__cache[uri]

    def compute_qname_strict(self, uri, generate=True):
        # code repeated to avoid branching on strict every time
        # if output needs to be strict (e.g. for xml) then
        # only the strict output should bear the overhead
        prefix, namespace, name = self.compute_qname(uri)
        if is_ncname(text_type(name)):
            return prefix, namespace, name
        else:
            if uri not in self.__cache_strict:
                try:
                    namespace, name = split_uri(uri, NAME_START_CATEGORIES)
                except ValueError as e:
                    message = ('This graph cannot be serialized to a strict format '
                               'because there is no valid way to shorten {}'.format(uri))
                    raise ValueError(message)
                    # omitted for strict since NCNames cannot be empty
                    #namespace = URIRef(uri)
                    #prefix = self.store.prefix(namespace)
                    #if not prefix:
                        #raise e

                if namespace not in self.__strie:
                    insert_strie(self.__strie, self.__trie, namespace)

                # omitted for strict
                #if self.__strie[namespace]:
                    #pl_namespace = get_longest_namespace(self.__strie[namespace], uri)
                    #if pl_namespace is not None:
                        #namespace = pl_namespace
                        #name = uri[len(namespace):]

                namespace = URIRef(namespace)
                prefix = self.store.prefix(namespace)  # warning multiple prefixes problem

                if prefix is None:
                    if not generate:
                        raise KeyError(
                            "No known prefix for {} and generate=False".format(namespace)
                        )
                    num = 1
                    while 1:
                        prefix = "ns%s" % num
                        if not self.store.namespace(prefix):
                            break
                        num += 1
                    self.bind(prefix, namespace)
                self.__cache_strict[uri] = (prefix, namespace, name)

            return self.__cache_strict[uri]

    def bind(self, prefix, namespace, override=True, replace=False):
        """bind a given namespace to the prefix

        if override, rebind, even if the given namespace is already
        bound to another prefix.

        if replace, replace any existing prefix with the new namespace

        """

        namespace = URIRef(text_type(namespace))
        # When documenting explain that override only applies in what cases
        if prefix is None:
            prefix = ''
        bound_namespace = self.store.namespace(prefix)
        # Check if the bound_namespace contains a URI
        # and if so convert it into a URIRef for comparison
        # This is to prevent duplicate namespaces with the
        # same URI
        if bound_namespace:
            bound_namespace = URIRef(bound_namespace)
        if bound_namespace and bound_namespace != namespace:

            if replace:
                self.store.bind(prefix, namespace)
                insert_trie(self.__trie, str(namespace))
                return

            # prefix already in use for different namespace
            #
            # append number to end of prefix until we find one
            # that's not in use.
            if not prefix:
                prefix = "default"
            num = 1
            while 1:
                new_prefix = "%s%s" % (prefix, num)
                tnamespace = self.store.namespace(new_prefix)
                if tnamespace and namespace == URIRef(tnamespace):
                    # the prefix is already bound to the correct
                    # namespace
                    return
                if not self.store.namespace(new_prefix):
                    break
                num += 1
            self.store.bind(new_prefix, namespace)
        else:
            bound_prefix = self.store.prefix(namespace)
            if bound_prefix is None:
                self.store.bind(prefix, namespace)
            elif bound_prefix == prefix:
                pass  # already bound
            else:
                if override or bound_prefix.startswith("_"):  # or a generated prefix
                    self.store.bind(prefix, namespace)
        insert_trie(self.__trie, str(namespace))

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
            if uri and uri[-1] == "#" and result[-1] != "#":
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


NAME_START_CATEGORIES = ["Ll", "Lu", "Lo", "Lt", "Nl"]
SPLIT_START_CATEGORIES = NAME_START_CATEGORIES + ['Nd']
NAME_CATEGORIES = NAME_START_CATEGORIES + ["Mc", "Me", "Mn", "Lm", "Nd"]
ALLOWED_NAME_CHARS = [u"\u00B7", u"\u0387", u"-", u".", u"_", u":"]


# http://www.w3.org/TR/REC-xml-names/#NT-NCName
#  [4] NCName ::= (Letter | '_') (NCNameChar)* /* An XML Name, minus
#      the ":" */
#  [5] NCNameChar ::= Letter | Digit | '.' | '-' | '_' | CombiningChar
#      | Extender


def is_ncname(name):
    if name:
        first = name[0]
        if first == "_" or category(first) in NAME_START_CATEGORIES:
            for i in range(1, len(name)):
                c = name[i]
                if not category(c) in NAME_CATEGORIES:
                    if c != ':' and c in ALLOWED_NAME_CHARS:
                        continue
                    return 0
                # if in compatibility area
                # if decomposition(c)!='':
                #    return 0

            return 1

    return 0


XMLNS = "http://www.w3.org/XML/1998/namespace"


def split_uri(uri, split_start=SPLIT_START_CATEGORIES):
    if uri.startswith(XMLNS):
        return (XMLNS, uri.split(XMLNS)[1])
    length = len(uri)
    for i in range(0, length):
        c = uri[-i - 1]
        if not category(c) in NAME_CATEGORIES:
            if c in ALLOWED_NAME_CHARS:
                continue
            for j in range(-1 - i, length):
                if category(uri[j]) in split_start or uri[j] == "_":
                    # _ prevents early split, roundtrip not generate
                    ns = uri[:j]
                    if not ns:
                        break
                    ln = uri[j:]
                    return (ns, ln)
            break
    raise ValueError("Can't split '{}'".format(uri))

def insert_trie(trie, value):  # aka get_subtrie_or_insert
    """ Insert a value into the trie if it is not already contained in the trie.
        Return the subtree for the value regardless of whether it is a new value
        or not. """
    if value in trie:
        return trie[value]
    multi_check = False
    for key in tuple(trie.keys()):
        if len(value) > len(key) and value.startswith(key):
            return insert_trie(trie[key], value)
        elif key.startswith(value):  # we know the value is not in the trie
            if not multi_check:
                trie[value] = {}
                multi_check = True  # there can be multiple longer existing prefixes
            dict_ = trie.pop(key)  # does not break strie since key<->dict_ remains unchanged
            trie[value][key] = dict_
    if value not in trie:
        trie[value] = {}
    return trie[value]

def insert_strie(strie, trie, value):
    if value not in strie:
        strie[value] = insert_trie(trie, value)

def get_longest_namespace(trie, value):
    for key in trie:
        if value.startswith(key):
            out = get_longest_namespace(trie[key], value)
            if out is None:
                return key
            else:
                return out
    return None
