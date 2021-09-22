import logging
import warnings
from typing import List
from unicodedata import category

from pathlib import Path
from urllib.parse import urldefrag
from urllib.parse import urljoin

from rdflib.term import URIRef, Variable, _is_valid_uri

__doc__ = """
===================
Namespace Utilities
===================

RDFLib provides mechanisms for managing Namespaces.

In particular, there is a :class:`~rdflib.namespace.Namespace` class
that takes as its argument the base URI of the namespace.

.. code-block:: pycon

    >>> from rdflib.namespace import Namespace
    >>> RDFS = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")

Fully qualified URIs in the namespace can be constructed either by attribute
or by dictionary access on Namespace instances:

.. code-block:: pycon

    >>> RDFS.seeAlso
    rdflib.term.URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#seeAlso')
    >>> RDFS['seeAlso']
    rdflib.term.URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#seeAlso')


Automatic handling of unknown predicates
-----------------------------------------

As a programming convenience, a namespace binding is automatically
created when :class:`rdflib.term.URIRef` predicates are added to the graph.

Importable namespaces
-----------------------

The following namespaces are available by directly importing from rdflib:

* BRICK
* CSVW
* DC
* DCMITYPE
* DCAT
* DCTERMS
* DCAM
* DOAP
* FOAF
* ODRL2
* ORG
* OWL
* PROF
* PROV
* QB
* RDF
* RDFS
* SDO
* SH
* SKOS
* SOSA
* SSN
* TIME
* VOID
* XSD
* VANN

.. code-block:: pycon
    >>> from rdflib.namespace import RDFS
    >>> RDFS.seeAlso
    rdflib.term.URIRef('http://www.w3.org/2000/01/rdf-schema#seeAlso')
"""

__all__ = ["is_ncname", "split_uri", "Namespace", "ClosedNamespace", "NamespaceManager"]


logger = logging.getLogger(__name__)


class Namespace(str):
    """
    Utility class for quickly generating URIRefs with a common prefix

    >>> from rdflib.namespace import Namespace
    >>> n = Namespace("http://example.org/")
    >>> n.Person # as attribute
    rdflib.term.URIRef('http://example.org/Person')
    >>> n['first-name'] # as item - for things that are not valid python identifiers
    rdflib.term.URIRef('http://example.org/first-name')
    >>> n.Person in n
    True
    >>> n2 = Namespace("http://example2.org/")
    >>> n.Person in n2
    False
    """

    def __new__(cls, value):
        try:
            rt = str.__new__(cls, value)
        except UnicodeDecodeError:
            rt = str.__new__(cls, value, "utf-8")
        return rt

    @property
    def title(self):
        # Override for DCTERMS.title to return a URIRef instead of str.title method
        return URIRef(self + "title")

    def term(self, name):
        # need to handle slices explicitly because of __getitem__ override
        return URIRef(self + (name if isinstance(name, str) else ""))

    def __getitem__(self, key):
        return self.term(key)

    def __getattr__(self, name):
        if name.startswith("__"):  # ignore any special Python names!
            raise AttributeError
        return self.term(name)

    def __repr__(self):
        return f"Namespace({super().__repr__()})"

    def __contains__(self, ref):
        """Allows to check if a URI is within (starts with) this Namespace.

        >>> from rdflib import URIRef
        >>> namespace = Namespace('http://example.org/')
        >>> uri = URIRef('http://example.org/foo')
        >>> uri in namespace
        True
        >>> person_class = namespace['Person']
        >>> person_class in namespace
        True
        >>> obj = URIRef('http://not.example.org/bar')
        >>> obj in namespace
        False
        """
        return ref.startswith(self)  # test namespace membership with "ref in ns" syntax


class URIPattern(str):
    """
    Utility class for creating URIs according to some pattern
    This supports either new style formatting with .format
    or old-style with % operator

    >>> u=URIPattern("http://example.org/%s/%d/resource")
    >>> u%('books', 12345)
    rdflib.term.URIRef('http://example.org/books/12345/resource')

    """

    def __new__(cls, value):
        try:
            rt = str.__new__(cls, value)
        except UnicodeDecodeError:
            rt = str.__new__(cls, value, "utf-8")
        return rt

    def __mod__(self, *args, **kwargs):
        return URIRef(super().__mod__(*args, **kwargs))

    def format(self, *args, **kwargs):
        return URIRef(super().format(*args, **kwargs))

    def __repr__(self):
        return f"URIPattern({super().__repr__()})"


class DefinedNamespaceMeta(type):
    """
    Utility metaclass for generating URIRefs with a common prefix

    """

    _NS: Namespace
    _warn: bool = True
    _fail: bool = False  # True means mimic ClosedNamespace
    _extras: List[str] = []  # List of non-pythonesque items
    _underscore_num: bool = False  # True means pass "_n" constructs

    def __getitem__(cls, name, default=None):
        name = str(name)
        if str(name).startswith("__"):
            return super().__getitem__(name, default)
        if (cls._warn or cls._fail) and not name in cls:
            if cls._fail:
                raise AttributeError(f"term '{name}' not in namespace '{cls._NS}'")
            else:
                warnings.warn(
                    f"Code: {name} is not defined in namespace {cls.__name__}",
                    stacklevel=3,
                )
        return cls._NS[name]

    def __getattr__(cls, name):
        return cls.__getitem__(name)

    def __repr__(cls):
        return f'Namespace("{cls._NS}")'

    def __str__(cls):
        return str(cls._NS)

    def __add__(cls, other):
        return cls.__getitem__(other)

    def __contains__(cls, item):
        """Determine whether a URI or an individual item belongs to this namespace"""
        item_str = str(item)
        if item_str.startswith("__"):
            return super().__contains__(item)
        if item_str.startswith(str(cls._NS)):
            item_str = item_str[len(str(cls._NS)) :]
        return any(
            item_str in c.__annotations__
            or item_str in c._extras
            or (cls._underscore_num and item_str[0] == "_" and item_str[1:].isdigit())
            for c in cls.mro()
            if issubclass(c, DefinedNamespace)
        )


class DefinedNamespace(metaclass=DefinedNamespaceMeta):
    """
    A Namespace with an enumerated list of members.
    Warnings are emitted if unknown members are referenced if _warn is True
    """

    def __init__(self):
        raise TypeError("namespace may not be instantiated")


class ClosedNamespace(Namespace):
    """
    A namespace with a closed list of members

    Trying to create terms not listed is an error
    """

    def __new__(cls, uri, terms):
        rt = super().__new__(cls, uri)
        rt.__uris = {t: URIRef(rt + t) for t in terms}
        return rt

    @property
    def uri(self):  # Back-compat
        return str(self)

    def term(self, name):
        uri = self.__uris.get(name)
        if uri is None:
            raise KeyError(f"term '{name}' not in namespace '{self}'")
        return uri

    def __getitem__(self, key):
        return self.term(key)

    def __getattr__(self, name):
        if name.startswith("__"):  # ignore any special Python names!
            raise AttributeError
        else:
            try:
                return self.term(name)
            except KeyError as e:
                raise AttributeError(e)

    def __repr__(self):
        return f"{self.__module__}.{self.__class__.__name__}({str(self)!r})"

    def __dir__(self):
        return list(self.__uris)

    def __contains__(self, ref):
        return (
            ref in self.__uris.values()
        )  # test namespace membership with "ref in ns" syntax

    def _ipython_key_completions_(self):
        return dir(self)


XMLNS = Namespace("http://www.w3.org/XML/1998/namespace")


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
        self.bind("xml", XMLNS)
        self.bind("rdf", RDF)
        self.bind("rdfs", RDFS)
        self.bind("xsd", XSD)

    def __contains__(self, ref):
        # checks if a reference is in any of the managed namespaces with syntax
        # "ref in manager". Note that we don't use "ref in ns", as
        # NamespaceManager.namespaces() returns Iterator[Tuple[str, URIRef]]
        # rather than Iterator[Tuple[str, Namespace]]
        return any(ref.startswith(ns) for prefix, ns in self.namespaces())

    def reset(self):
        self.__cache = {}
        self.__strie = {}
        self.__trie = {}
        for p, n in self.namespaces():  # repopulate the trie
            insert_trie(self.__trie, str(n))

    @property
    def store(self):
        return self.graph.store

    def qname(self, uri):
        prefix, namespace, name = self.compute_qname(uri)
        if prefix == "":
            return name
        else:
            return ":".join((prefix, name))

    def qname_strict(self, uri):
        prefix, namespace, name = self.compute_qname_strict(uri)
        if prefix == "":
            return name
        else:
            return ":".join((prefix, name))

    def normalizeUri(self, rdfTerm) -> str:
        """
        Takes an RDF Term and 'normalizes' it into a QName (using the
        registered prefix) or (unlike compute_qname) the Notation 3
        form for URIs: <...URI...>
        """
        try:
            namespace, name = split_uri(rdfTerm)
            if namespace not in self.__strie:
                insert_strie(self.__strie, self.__trie, str(namespace))
            namespace = URIRef(str(namespace))
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
            return ":".join([qNameParts[0], qNameParts[-1]])

    def compute_qname(self, uri, generate=True):

        if not _is_valid_uri(uri):
            raise ValueError(
                '"{}" does not look like a valid URI, cannot serialize this. Did you want to urlencode it?'.format(
                    uri
                )
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
                    name = uri[len(namespace) :]

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
        if is_ncname(str(name)):
            return prefix, namespace, name
        else:
            if uri not in self.__cache_strict:
                try:
                    namespace, name = split_uri(uri, NAME_START_CATEGORIES)
                except ValueError as e:
                    message = (
                        "This graph cannot be serialized to a strict format "
                        "because there is no valid way to shorten {}".format(uri)
                    )
                    raise ValueError(message)
                    # omitted for strict since NCNames cannot be empty
                    # namespace = URIRef(uri)
                    # prefix = self.store.prefix(namespace)
                    # if not prefix:
                    # raise e

                if namespace not in self.__strie:
                    insert_strie(self.__strie, self.__trie, namespace)

                # omitted for strict
                # if self.__strie[namespace]:
                # pl_namespace = get_longest_namespace(self.__strie[namespace], uri)
                # if pl_namespace is not None:
                # namespace = pl_namespace
                # name = uri[len(namespace):]

                namespace = URIRef(namespace)
                prefix = self.store.prefix(
                    namespace
                )  # warning multiple prefixes problem

                if prefix is None:
                    if not generate:
                        raise KeyError(
                            "No known prefix for {} and generate=False".format(
                                namespace
                            )
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

        namespace = URIRef(str(namespace))
        # When documenting explain that override only applies in what cases
        if prefix is None:
            prefix = ""
        elif " " in prefix:
            raise KeyError("Prefixes may not contain spaces.")

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
        base = Path.cwd().as_uri()
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
SPLIT_START_CATEGORIES = NAME_START_CATEGORIES + ["Nd"]
NAME_CATEGORIES = NAME_START_CATEGORIES + ["Mc", "Me", "Mn", "Lm", "Nd"]
ALLOWED_NAME_CHARS = ["\u00B7", "\u0387", "-", ".", "_", "%", "(", ")"]


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
                    if c in ALLOWED_NAME_CHARS:
                        continue
                    return 0
                # if in compatibility area
                # if decomposition(c)!='':
                #    return 0

            return 1

    return 0


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
    """Insert a value into the trie if it is not already contained in the trie.
    Return the subtree for the value regardless of whether it is a new value
    or not."""
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
            dict_ = trie.pop(
                key
            )  # does not break strie since key<->dict_ remains unchanged
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


from rdflib.namespace._BRICK import BRICK
from rdflib.namespace._CSVW import CSVW
from rdflib.namespace._DC import DC
from rdflib.namespace._DCAT import DCAT
from rdflib.namespace._DCTERMS import DCTERMS
from rdflib.namespace._DOAP import DOAP
from rdflib.namespace._FOAF import FOAF
from rdflib.namespace._ODRL2 import ODRL2
from rdflib.namespace._ORG import ORG
from rdflib.namespace._OWL import OWL
from rdflib.namespace._PROF import PROF
from rdflib.namespace._PROV import PROV
from rdflib.namespace._QB import QB
from rdflib.namespace._RDF import RDF
from rdflib.namespace._RDFS import RDFS
from rdflib.namespace._SDO import SDO
from rdflib.namespace._SH import SH
from rdflib.namespace._SKOS import SKOS
from rdflib.namespace._SOSA import SOSA
from rdflib.namespace._SSN import SSN
from rdflib.namespace._TIME import TIME
from rdflib.namespace._VOID import VOID
from rdflib.namespace._XSD import XSD
