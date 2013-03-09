"""
This module defines the different types of terms. Terms are the kinds of
objects that can appear in a quoted/asserted triple. This includes those
that are core to RDF:

* Blank Nodes
* URI References
* Literals (which consist of a literal value,datatype and language tag)

Those that extend the RDF model into N3:

* Formulae
* Universal Quantifications (Variables)

And those that are primarily for matching against 'Nodes' in the
underlying Graph:

* REGEX Expressions
* Date Ranges
* Numerical Ranges

"""

__all__ = [
    'bind',

    'Node',
    'Identifier',

    'URIRef',
    'BNode',
    'Literal',

    'Variable',
    'Statement',
]

import logging
import warnings

_LOGGER = logging.getLogger(__name__)

import base64

from urlparse import urlparse, urljoin, urldefrag
from datetime import date, time, datetime
from isodate import parse_time, parse_date, parse_datetime
from re import sub


try:
    from hashlib import md5
    assert md5
except ImportError:
    from md5 import md5


import rdflib
from . import py3compat
from rdflib.compat import numeric_greater

b = py3compat.b


class Node(object):
    """
    A Node in the Graph.
    """

    __slots__ = ()


class Identifier(Node, unicode):  # allow Identifiers to be Nodes in the Graph
    """
    See http://www.w3.org/2002/07/rdf-identifer-terminology/
    regarding choice of terminology.
    """

    __slots__ = ()

    def __new__(cls, value):
        return unicode.__new__(cls, value)

    def eq(self, other):
        """A "semantic"/interpreted equality function,
        by default, same as __eq__"""
        return self.__eq__(other)

    def neq(self, other):
        """A "semantic"/interpreted not equal function,
        by default, same as __ne__"""
        return self.__ne__(other)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __eq__(self, other):
        """
        Equality for Nodes.

        >>> BNode("foo")==None
        False
        >>> BNode("foo")==URIRef("foo")
        False
        >>> URIRef("foo")==BNode("foo")
        False
        >>> BNode("foo")!=URIRef("foo")
        True
        >>> URIRef("foo")!=BNode("foo")
        True
        >>> Variable('a')!=URIRef('a')
        True
        >>> Variable('a')!=Variable('a')
        False
        """

        if type(self) == type(other):
            return unicode(self) == unicode(other)
        else:
            return False

    def __gt__(self, other):
        """
        This implements ordering for Nodes,

        This tries to implement this:
        http://www.w3.org/TR/sparql11-query/#modOrderBy

        Variables are no included in the SPARQL list, but
        they are greater than BNodes and smaller than everything else

        """
        if other is None:
            return True  # everything bigger than None
        elif type(self) == type(other):
            return unicode(self) > unicode(other)
        elif isinstance(other, Node):
            return _ORDERING[type(self)] > _ORDERING[type(other)]

        return NotImplemented

    def __lt__(self, other):
        if other is None:
            return False  # Nothing is less than None
        elif type(self) == type(other):
            return unicode(self) < unicode(other)
        elif isinstance(other, Node):
            return _ORDERING[type(self)] < _ORDERING[type(other)]

        return NotImplemented

    def __le__(self, other):
        r = self.__lt__(other)
        if r:
            return True
        return self == other

    def __ge__(self, other):
        r = self.__gt__(other)
        if r:
            return True
        return self == other

    def __hash__(self):
        return hash(type(self)) ^ hash(unicode(self))


class URIRef(Identifier):
    """
    RDF URI Reference: http://www.w3.org/TR/rdf-concepts/#section-Graph-URIref
    """

    __slots__ = ()

    def __new__(cls, value, base=None):
        if base is not None:
            ends_in_hash = value.endswith("#")
            value = urljoin(base, value, allow_fragments=1)
            if ends_in_hash:
                if not value.endswith("#"):
                    value += "#"
        # if normalize and value and value != normalize("NFC", value):
        #    raise Error("value must be in NFC normalized form.")
        try:
            rt = unicode.__new__(cls, value)
        except UnicodeDecodeError:
            rt = unicode.__new__(cls, value, 'utf-8')
        return rt

    def toPython(self):
        return unicode(self)

    def n3(self):
        return "<%s>" % self

    def concrete(self):
        warnings.warn("URIRef.concrete is deprecated.",
                      category=DeprecationWarning, stacklevel=2)
        if "#" in self:
            return URIRef("/".join(self.rsplit("#", 1)))
        else:
            return self

    def abstract(self):
        warnings.warn("URIRef.abstract is deprecated.",
                      category=DeprecationWarning, stacklevel=2)
        if "#" not in self:
            scheme, netloc, path, params, query, fragment = urlparse(self)
            if path:
                return URIRef("#".join(self.rsplit("/", 1)))
            else:
                if not self.endswith("#"):
                    return URIRef("%s#" % self)
                else:
                    return self
        else:
            return self

    def defrag(self):
        if "#" in self:
            url, frag = urldefrag(self)
            return URIRef(url)
        else:
            return self

    def __reduce__(self):
        return (URIRef, (unicode(self),))

    def __getnewargs__(self):
        return (unicode(self), )

    if not py3compat.PY3:
        def __str__(self):
            return self.encode()

    def __repr__(self):
        if self.__class__ is URIRef:
            clsName = "rdflib.term.URIRef"
        else:
            clsName = self.__class__.__name__

        return """%s(%s)""" % (clsName, super(URIRef, self).__repr__())

    def md5_term_hash(self):
        """a string of hex that will be the same for two URIRefs that
        are the same. It is not a suitable unique id.

        Supported for backwards compatibility; new code should
        probably just use __hash__
        """
        d = md5(self.encode())
        d.update(b("U"))
        return d.hexdigest()


def _unique_id():
    # Used to read: """Create a (hopefully) unique prefix"""
    # now retained merely to leave interal API unchanged.
    # From BNode.__new__() below ...
    #
    # acceptable bnode value range for RDF/XML needs to be
    # something that can be serialzed as a nodeID for N3
    #
    # BNode identifiers must be valid NCNames" _:[A-Za-z][A-Za-z0-9]*
    # http://www.w3.org/TR/2004/REC-rdf-testcases-20040210/#nodeID
    return "N"  # ensure that id starts with a letter


# Adapted from http://icodesnip.com/snippet/python/
# simple-universally-unique-id-uuid-or-guid
def bnode_uuid():
    """
    Generates a uuid on behalf of Python 2.4
    """
    import os
    import random
    import socket
    from time import time
    from binascii import hexlify

    pid = [None]

    try:
        ip = socket.gethostbyname(socket.gethostname())
        ip = long(ip.replace('.', '999').replace(':', '999'))
    except:
        # if we can't get a network address, just imagine one
        ip = long(random.random() * 100000000000000000L)

    def _generator():
        if os.getpid() != pid[0]:
            # Process might have been forked (issue 200), must reseed random:
            try:
                preseed = long(hexlify(os.urandom(16)), 16)
            except NotImplementedError:
                preseed = 0
            seed = long(str(preseed) + str(os.getpid())
                        + str(long(time() * 1000000)) + str(ip))
            random.seed(seed)
            pid[0] = os.getpid()

        t = long(time() * 1000.0)
        r = long(random.random() * 100000000000000000L)
        data = str(t) + ' ' + str(r) + ' ' + str(ip)
        return md5(data).hexdigest()

    return _generator


def uuid4_ncname():
    """
    Generates UUID4-based but ncname-compliant identifiers.
    """
    from uuid import uuid4

    def _generator():
        return uuid4().hex

    return _generator


def _serial_number_generator():
    import sys
    if sys.version_info[:2] < (2, 5):
        return bnode_uuid()
    else:
        return uuid4_ncname()


class BNode(Identifier):
    """
    Blank Node: http://www.w3.org/TR/rdf-concepts/#section-blank-nodes

    """
    __slots__ = ()

    def __new__(cls, value=None,
                _sn_gen=_serial_number_generator(), _prefix=_unique_id()):
        """
        # only store implementations should pass in a value
        """
        if value is None:
            # so that BNode values do not collide with ones created with
            # a different instance of this module at some other time.
            node_id = _sn_gen()
            value = "%s%s" % (_prefix, node_id)
        else:
            # TODO: check that value falls within acceptable bnode value range
            # for RDF/XML needs to be something that can be serialzed
            # as a nodeID for N3 ??  Unless we require these
            # constraints be enforced elsewhere?
            pass  # assert is_ncname(unicode(value)), "BNode identifiers
                 # must be valid NCNames" _:[A-Za-z][A-Za-z0-9]*
                 # http://www.w3.org/TR/2004/REC-rdf-testcases-20040210/#nodeID
        return Identifier.__new__(cls, value)

    def toPython(self):
        return unicode(self)

    def n3(self):
        return "_:%s" % self

    def __getnewargs__(self):
        return (unicode(self), )

    def __reduce__(self):
        return (BNode, (unicode(self),))

    if not py3compat.PY3:
        def __str__(self):
            return self.encode()

    def __repr__(self):
        if self.__class__ is BNode:
            clsName = "rdflib.term.BNode"
        else:
            clsName = self.__class__.__name__
        return """%s('%s')""" % (clsName, str(self))

    def md5_term_hash(self):
        """a string of hex that will be the same for two BNodes that
        are the same. It is not a suitable unique id.

        Supported for backwards compatibility; new code should
        probably just use __hash__
        """
        d = md5(self.encode())
        d.update(b("B"))
        return d.hexdigest()


class Literal(Identifier):
    doc = """
    RDF Literal: http://www.w3.org/TR/rdf-concepts/#section-Graph-Literal

    The lexical value of the literal is the unicode object
    The interpreted, datatyped value is available from .value

    For valid XSD datatypes, the lexical form is optionally normalized
    at construction time. Default behaviour is set by rdflib.NORMALIZE_LITERALS
    and can be overridden by the normalize parameter to __new__

    Equality and hashing of Literals are done based on the lexical form, i.e.:

    >>> from rdflib.namespace import XSD

    >>> Literal('01')!=Literal('1') # clear - strings differ
    True

    but with data-type they get normalized:
    >>> Literal('01', datatype=XSD.integer)!=Literal('1', datatype=XSD.integer)
    False

    unless disabled:
    >>> Literal('01', datatype=XSD.integer, normalize=False)!=Literal('1', datatype=XSD.integer)
    True


    Value based comparison is possible:
    >>> Literal('01', datatype=XSD.integer).eq(Literal('1', datatype=XSD.float))
    True

    The eq method also provides limited support for basic python types:
    >>> Literal(1).eq(1) # fine - int compatible with xsd:integer
    True
    >>> Literal('a').eq('b') # fine - str compatible with plain-lit
    False
    >>> Literal('a', datatype=XSD.string).eq('a') # fine - str compatible with xsd:string
    True
    >>> Literal('a').eq(1) # not fine, int incompatible with plain-lit
    NotImplemented


    Greater-than/less-than ordering comparisons are also done in value space, when compatible datatypes are used.
    Incompatible datatypes are ordered by DT, or by lang-tag.
    For other nodes the ordering is None < BNode < URIRef < Literal

    Any comparison with non-rdflib Node are "NotImplemented"
    In PY2.X some stable order will be made up by python
    In PY3 this is an error.

    >>> from rdflib import Literal, XSD
    >>> lit2006 = Literal('2006-01-01',datatype=XSD.date)
    >>> lit2006.toPython()
    datetime.date(2006, 1, 1)
    >>> lit2006 < Literal('2007-01-01',datatype=XSD.date)
    True
    >>> Literal(datetime.utcnow()).datatype
    rdflib.term.URIRef(%(u)s'http://www.w3.org/2001/XMLSchema#dateTime')
    >>> Literal(1) > Literal(2) # by value
    False
    >>> Literal(1) > Literal(2.0) # by value
    False
    >>> Literal('1') > Literal(1) # by DT
    True
    >>> Literal('1') < Literal('1') # by lexical form
    False
    >>> Literal('a', lang='en') > Literal('a', lang='fr') # by lang-tag
    False
    >>> Literal(1) > URIRef('foo') # by node-type
    True

    The > < operators will eat this NotImplemented and either make up an ordering (py2.x)
    or throw a TypeError (py3k)
    >>> Literal(1).__gt__(2.0)
    NotImplemented


    """
    __doc__ = py3compat.format_doctest_out(doc)

    if not py3compat.PY3:
        __slots__ = ("language", "datatype", "value", "_language",
                     "_datatype", "_value")
    else:
        __slots__ = ("_language", "_datatype", "_value")

    def __new__(cls, lexical_or_value, lang=None, datatype=None, normalize=None):

        if lang == '':
            lang = None  # no empty lang-tags in RDF

        normalize = normalize if normalize != None else rdflib.NORMALIZE_LITERALS

        if lang is not None and datatype is not None:
            raise TypeError(
                "A Literal can only have one of lang or datatype, "
                "per http://www.w3.org/TR/rdf-concepts/#section-Graph-Literal")

        if datatype:
            datatype = URIRef(datatype)

        value = None
        if isinstance(lexical_or_value, Literal):  # create from another Literal instance
            datatype = datatype or lexical_or_value.datatype
            lang = lang or lexical_or_value.language
            value = lexical_or_value.value

        if value == None and isinstance(lexical_or_value, basestring):

            if datatype:
                convFunc = _toPythonMapping.get(datatype, None)
                if convFunc:
                    try:
                        value = convFunc(lexical_or_value)
                    except:
                        pass  # not a valid lexical representation for this dt

                if value is not None and normalize:
                    _value, _datatype = _castPythonToLiteral(value)
                    if _value is not None:
                        lexical_or_value = _value

        else:
            value = lexical_or_value
            _value, _datatype = _castPythonToLiteral(lexical_or_value)
            datatype = datatype or _datatype
            if _value is not None:
                lexical_or_value = _value
            if datatype:
                lang = None

        if py3compat.PY3 and isinstance(lexical_or_value, bytes):
            lexical_or_value = lexical_or_value.decode('utf-8')

        try:
            inst = unicode.__new__(cls, lexical_or_value)
        except UnicodeDecodeError:
            inst = unicode.__new__(cls, lexical_or_value, 'utf-8')

        inst._language = lang
        inst._datatype = datatype
        inst._value = value
        return inst

    @py3compat.format_doctest_out
    def normalize(self):
        """
        Returns a new literal with a normalised lexical representation
        of this literal
        >>> from rdflib import XSD
        >>> Literal("01", datatype=XSD.integer, normalize=False).normalize()
        rdflib.term.Literal(%(u)s'1', datatype=rdflib.term.URIRef(%(u)s'http://www.w3.org/2001/XMLSchema#integer'))

        Illegal lexical forms for the datatype given are simply passed on
        >>> Literal("a", datatype=XSD.integer, normalize=False)
        rdflib.term.Literal(%(u)s'a', datatype=rdflib.term.URIRef(%(u)s'http://www.w3.org/2001/XMLSchema#integer'))

        """

        if self.value != None:
            return Literal(self.value, datatype=self.datatype, lang=self.language)
        else:
            return self

    @property
    def value(self):
        return self._value

    @property
    def language(self):
        return self._language

    @property
    def datatype(self):
        return self._datatype

    def __reduce__(self):
        return (Literal, (unicode(self), self.language, self.datatype),)

    def __getstate__(self):
        return (None, dict(language=self.language, datatype=self.datatype))

    def __setstate__(self, arg):
        _, d = arg
        self._language = d["language"]
        self._datatype = d["datatype"]

    @py3compat.format_doctest_out
    def __add__(self, val):
        """
        >>> Literal(1) + 1
        rdflib.term.Literal(%(u)s'2', datatype=rdflib.term.URIRef(%(u)s'http://www.w3.org/2001/XMLSchema#integer'))
        >>> Literal("1") + "1"
        rdflib.term.Literal(%(u)s'11')
        """

        py = self.toPython()
        if isinstance(py, Literal):
            s = super(Literal, self).__add__(val)
            return Literal(s, self.language, self.datatype)
        else:
            return Literal(py + val)

    def __nonzero__(self):
        """
        Is the Literal "True"
        This is used for if statements, bool(literal), etc.
        """
        if self.value != None:
            return bool(self.value)
        return len(self) != 0

    @py3compat.format_doctest_out
    def __neg__(self):
        """
        >>> (- Literal(1))
        rdflib.term.Literal(%(u)s'-1', datatype=rdflib.term.URIRef(%(u)s'http://www.w3.org/2001/XMLSchema#integer'))
        >>> (- Literal(10.5))
        rdflib.term.Literal(%(u)s'-10.5', datatype=rdflib.term.URIRef(%(u)s'http://www.w3.org/2001/XMLSchema#double'))
        >>> from rdflib.namespace import XSD
        >>> (- Literal("1", datatype=XSD.integer))
        rdflib.term.Literal(%(u)s'-1', datatype=rdflib.term.URIRef(%(u)s'http://www.w3.org/2001/XMLSchema#integer'))

        >>> (- Literal("1"))
        Traceback (most recent call last):
          File "<stdin>", line 1, in <module>
        TypeError: Not a number; rdflib.term.Literal(%(u)s'1')
        >>>
        """

        if isinstance(self.value, (int, long, float)):
            return Literal(self.value.__neg__())
        else:
            raise TypeError("Not a number; %s" % repr(self))

    @py3compat.format_doctest_out
    def __pos__(self):
        """
        >>> (+ Literal(1))
        rdflib.term.Literal(%(u)s'1', datatype=rdflib.term.URIRef(%(u)s'http://www.w3.org/2001/XMLSchema#integer'))
        >>> (+ Literal(-1))
        rdflib.term.Literal(%(u)s'-1', datatype=rdflib.term.URIRef(%(u)s'http://www.w3.org/2001/XMLSchema#integer'))
        >>> from rdflib.namespace import XSD
        >>> (+ Literal("-1", datatype=XSD.integer))
        rdflib.term.Literal(%(u)s'-1', datatype=rdflib.term.URIRef(%(u)s'http://www.w3.org/2001/XMLSchema#integer'))

        >>> (+ Literal("1"))
        Traceback (most recent call last):
          File "<stdin>", line 1, in <module>
        TypeError: Not a number; rdflib.term.Literal(%(u)s'1')
        """
        if isinstance(self.value, (int, long, float)):
            return Literal(self.value.__pos__())
        else:
            raise TypeError("Not a number; %s" % repr(self))

    @py3compat.format_doctest_out
    def __abs__(self):
        """
        >>> abs(Literal(-1))
        rdflib.term.Literal(%(u)s'1', datatype=rdflib.term.URIRef(%(u)s'http://www.w3.org/2001/XMLSchema#integer'))

        >>> from rdflib.namespace import XSD
        >>> abs( Literal("-1", datatype=XSD.integer))
        rdflib.term.Literal(%(u)s'1', datatype=rdflib.term.URIRef(%(u)s'http://www.w3.org/2001/XMLSchema#integer'))

        >>> abs(Literal("1"))
        Traceback (most recent call last):
          File "<stdin>", line 1, in <module>
        TypeError: Not a number; rdflib.term.Literal(%(u)s'1')
        """
        if isinstance(self.value, (int, long, float)):
            return Literal(self.value.__abs__())
        else:
            raise TypeError("Not a number; %s" % repr(self))

    @py3compat.format_doctest_out
    def __invert__(self):
        """
        >>> ~(Literal(-1))
        rdflib.term.Literal(%(u)s'0', datatype=rdflib.term.URIRef(%(u)s'http://www.w3.org/2001/XMLSchema#integer'))

        >>> from rdflib.namespace import XSD
        >>> ~( Literal("-1", datatype=XSD.integer))
        rdflib.term.Literal(%(u)s'0', datatype=rdflib.term.URIRef(%(u)s'http://www.w3.org/2001/XMLSchema#integer'))

        Not working:
        >>> ~(Literal("1"))
        Traceback (most recent call last):
          File "<stdin>", line 1, in <module>
        TypeError: Not a number; rdflib.term.Literal(%(u)s'1')
        """
        if isinstance(self.value, (int, long, float)):
            return Literal(self.value.__invert__())
        else:
            raise TypeError("Not a number; %s" % repr(self))

    def __gt__(self, other):
        """

        This implements ordering for Literals,
        the other comparison methods delegate here

        This tries to implement this:
        http://www.w3.org/TR/sparql11-query/#modOrderBy

        In short, Literals with compatible data-types are orderd in value space,
        i.e.
        >>> from rdflib import XSD

        >>> Literal(1)>Literal(2) # int/int
        False
        >>> Literal(2.0)>Literal(1) # double/int
        True
        >>> from decimal import Decimal
        >>> Literal(Decimal("3.3")) > Literal(2.0) # decimal/double
        True
        >>> Literal(Decimal("3.3")) < Literal(4.0) # decimal/double
        True
        >>> Literal('b')>Literal('a') # plain lit/plain lit
        True
        >>> Literal('b')>Literal('a', datatype=XSD.string) # plain lit/xsd:string
        True

        Incompatible datatype mismatches ordered by DT

        >>> Literal(1)>Literal("2") # int>string
        False

        Langtagged literals by lang tag
        >>> Literal("a", lang="en")>Literal("a", lang="fr")
        False
        """
        if other is None:
            return True  # Everything is greater than None
        if isinstance(other, Literal):

            if self.datatype in _NUMERIC_LITERAL_TYPES and \
                    other.datatype in _NUMERIC_LITERAL_TYPES:
                return numeric_greater(self.value, other.value)

            # plain-literals and xsd:string literals
            # are "the same"
            dtself = self.datatype or _XSD_STRING
            dtother = other.datatype or _XSD_STRING

            if dtself != dtother:
                if rdflib.DAWG_LITERAL_COLLATION:
                    return NotImplemented
                else:
                    return dtself > dtother

            if self.language != other.language:
                if not self.language:
                    return False
                elif not other.language:
                    return True
                else:
                    return self.language > other.language

            if self.value != None and other.value != None:
                return self.value > other.value

            if unicode(self) != unicode(other):
                return unicode(self) > unicode(other)

            # same language, same lexical form, check real dt
            # plain-literals come before xsd:string!
            if self.datatype != other.datatype:
                if not self.datatype:
                    return False
                elif not other.datatype:
                    return True
                else:
                    return self.datatype > other.datatype

            return False  # they are the same

        elif isinstance(other, Node):
            return True  # Literal are the greatest!
        else:
            return NotImplemented  # we can only compare to nodes

    def __lt__(self, other):
        if other is None:
            return False  # Nothing is less than None
        if isinstance(other, Literal):
            try:
                return not self.__gt__(other) and not self.eq(other)
            except TypeError:
                return NotImplemented
        if isinstance(other, Node):
            return False  # all nodes are less-than Literals

        return NotImplemented

    def __le__(self, other):
        """
        >>> from rdflib.namespace import XSD
        >>> Literal('2007-01-01T10:00:00', datatype=XSD.dateTime
        ...     ) <= Literal('2007-01-01T10:00:00', datatype=XSD.dateTime)
        True
        """
        r = self.__lt__(other)
        if r:
            return True
        try:
            return self.eq(other)
        except TypeError:
            return NotImplemented

    def __ge__(self, other):
        r = self.__gt__(other)
        if r:
            return True
        try:
            return self.eq(other)
        except TypeError:
            return NotImplemented

    def _comparable_to(self, other):
        """
        Helper method to decide which things are meaningful to
        rich-compare with this literal
        """
        if isinstance(other, Literal):
            if (self.datatype and other.datatype):
                # two datatyped literals
                if not self.datatype in XSDToPython or not other.datatype in XSDToPython:
                    # non XSD DTs must match
                    if self.datatype != other.datatype:
                        return False

            else:
                # xsd:string may be compared with plain literals
                if not (self.datatype == _XSD_STRING and not other.datatype) or \
                        (other.datatype == _XSD_STRING and not self.datatype):
                    return False

                # if given lang-tag has to be case insensitive equal
                if (self.language or "").lower() != (other.language or "").lower():
                    return False

        return True

    def __hash__(self):
        """
        >>> from rdflib.namespace import XSD
        >>> a = {Literal('1', datatype=XSD.integer):'one'}
        >>> Literal('1', datatype=XSD.double) in a
        False


        "Called for the key object for dictionary operations,
        and by the built-in function hash(). Should return
        a 32-bit integer usable as a hash value for
        dictionary operations. The only required property
        is that objects which compare equal have the same
        hash value; it is advised to somehow mix together
        (e.g., using exclusive or) the hash values for the
        components of the object that also play a part in
        comparison of objects." -- 3.4.1 Basic customization (Python)

        "Two literals are equal if and only if all of the following hold:
        * The strings of the two lexical forms compare equal, character by
        character.
        * Either both or neither have language tags.
        * The language tags, if any, compare equal.
        * Either both or neither have datatype URIs.
        * The two datatype URIs, if any, compare equal, character by
        character."
        -- 6.5.1 Literal Equality (RDF: Concepts and Abstract Syntax)

        """

        return unicode.__hash__(self) ^ hash(self.language.lower() if self.language else None) ^ hash(self.datatype)

    @py3compat.format_doctest_out
    def __eq__(self, other):
        """
        Literals are only equal to other literals.

        "Two literals are equal if and only if all of the following hold:
        * The strings of the two lexical forms compare equal, character by character.
        * Either both or neither have language tags.
        * The language tags, if any, compare equal.
        * Either both or neither have datatype URIs.
        * The two datatype URIs, if any, compare equal, character by character."
        -- 6.5.1 Literal Equality (RDF: Concepts and Abstract Syntax)

        >>> Literal("1", datatype=URIRef("foo")) == Literal("1", datatype=URIRef("foo"))
        True
        >>> Literal("1", datatype=URIRef("foo")) == Literal("1", datatype=URIRef("foo2"))
        False

        >>> Literal("1", datatype=URIRef("foo")) == Literal("2", datatype=URIRef("foo"))
        False
        >>> Literal("1", datatype=URIRef("foo")) == "asdf"
        False
        >>> from rdflib import XSD
        >>> Literal('2007-01-01', datatype=XSD.date) == Literal('2007-01-01', datatype=XSD.date)
        True
        >>> Literal('2007-01-01', datatype=XSD.date) == date(2007, 1, 1)
        False
        >>> Literal("one", lang="en") == Literal("one", lang="en")
        True
        >>> Literal("hast", lang='en') == Literal("hast", lang='de')
        False
        >>> Literal("1", datatype=XSD.integer) == Literal(1)
        True
        >>> Literal("1", datatype=XSD.integer) == Literal("01", datatype=XSD.integer)
        True

        """
        if self is other:
            return True
        if other is None:
            return False
        if isinstance(other, Literal):
            return self.datatype == other.datatype \
                and (self.language.lower() if self.language else None) == (other.language.lower() if other.language else None) \
                and unicode.__eq__(self, other)

        return False

    def eq(self, other):
        """
        Compare the value of this literal with something else

        Either, with the value of another literal
        comparisons are then done in literal "value space",
        and according to the rules of XSD subtype-substitution/type-promotion

        OR, with a python object:

        basestring objects can be compared with plain-literals,
        or those with datatype xsd:string

        bool objects with xsd:boolean

        a int, long or float with numeric xsd types

        isodate date,time,datetime objects with xsd:date,xsd:time or xsd:datetime

        Any other operations returns NotImplemented

        """
        if isinstance(other, Literal):

            if self.datatype in _NUMERIC_LITERAL_TYPES  \
                    and other.datatype in _NUMERIC_LITERAL_TYPES:
                if self.value != None and other.value != None:
                    return self.value == other.value
                else:
                    if unicode.__eq__(self, other):
                        return True
                    raise TypeError(
                        'I cannot know that these two lexical forms do not map to the same value: %s and %s' % (self, other))

            if (self.language or "").lower() != (other.language or "").lower():
                return False

            dtself = self.datatype or _XSD_STRING
            dtother = other.datatype or _XSD_STRING

            if (dtself == _XSD_STRING and dtother == _XSD_STRING):
                # string/plain literals, compare on lexical form
                return unicode.__eq__(self, other)

            if dtself != dtother:
                if rdflib.DAWG_LITERAL_COLLATION:
                    raise TypeError("I don't know how to compare literals with datatypes %s and %s" % (
                        self.datatype, other.datatype))
                else:
                    return False

            # matching non-string DTs

            if self.value != None and other.value != None:
                return self.value == other.value
            else:

                if unicode.__eq__(self, other):
                    return True

                if self.datatype == _XSD_STRING:
                    return False  # string value space=lexical space

                # matching DTs, but not matching, we cannot compare!
                raise TypeError(
                    'I cannot know that these two lexical forms do not map to the same value: %s and %s' % (self, other))

        elif isinstance(other, Node):
            return False  # no non-Literal nodes are equal to a literal

        elif isinstance(other, basestring):
            # only plain-literals can be directly compared to strings

            # TODO: Is "blah"@en eq "blah" ?
            if self.language is not None:
                return False

            if (self.datatype == _XSD_STRING or self.datatype is None):
                return unicode(self) == other

        elif isinstance(other, (int, long, float)):
            if self.datatype in _NUMERIC_LITERAL_TYPES:
                return self.value == other
        elif isinstance(other, (date, datetime, time)):
            if self.datatype in (_XSD_DATETIME, _XSD_DATE, _XSD_TIME):
                return self.value == other
        elif isinstance(other, bool):
            if self.datatype == _XSD_BOOLEAN:
                return self.value == other

        return NotImplemented

    def neq(self, other):
        return not self.eq(other)

    @py3compat.format_doctest_out
    def n3(self):
        r'''
        Returns a representation in the N3 format.

        Examples::

            >>> Literal("foo").n3()
            %(u)s'"foo"'

        Strings with newlines or triple-quotes::

            >>> Literal("foo\nbar").n3()
            %(u)s'"""foo\nbar"""'

            >>> Literal("''\'").n3()
            %(u)s'"\'\'\'"'

            >>> Literal('"""').n3()
            %(u)s'"\\"\\"\\""'

        Language::

            >>> Literal("hello", lang="en").n3()
            %(u)s'"hello"@en'

        Datatypes::

            >>> Literal(1).n3()
            %(u)s'"1"^^<http://www.w3.org/2001/XMLSchema#integer>'

            >>> Literal(1, lang="en").n3()
            %(u)s'"1"^^<http://www.w3.org/2001/XMLSchema#integer>'

            >>> Literal(1.0).n3()
            %(u)s'"1.0"^^<http://www.w3.org/2001/XMLSchema#double>'

        Datatype and language isn't allowed (datatype takes precedence)::

            >>> Literal(True).n3()
            %(u)s'"true"^^<http://www.w3.org/2001/XMLSchema#boolean>'

        Custom datatype::

            >>> footype = URIRef("http://example.org/ns#foo")
            >>> Literal("1", datatype=footype).n3()
            %(u)s'"1"^^<http://example.org/ns#foo>'

        '''
        return self._literal_n3()

    @py3compat.format_doctest_out
    def _literal_n3(self, use_plain=False, qname_callback=None):
        '''
        Using plain literal (shorthand) output::
            >>> from rdflib.namespace import XSD

            >>> Literal(1)._literal_n3(use_plain=True)
            %(u)s'1'

            >>> Literal(1.0)._literal_n3(use_plain=True)
            %(u)s'1e+00'

            >>> Literal(1.0, datatype=XSD.decimal)._literal_n3(use_plain=True)
            %(u)s'1.0'

            >>> Literal(1.0, datatype=XSD.float)._literal_n3(use_plain=True)
            %(u)s'"1.0"^^<http://www.w3.org/2001/XMLSchema#float>'

            >>> Literal("foo", datatype=XSD.string)._literal_n3(
            ...         use_plain=True)
            %(u)s'"foo"^^<http://www.w3.org/2001/XMLSchema#string>'

            >>> Literal(True)._literal_n3(use_plain=True)
            %(u)s'true'

            >>> Literal(False)._literal_n3(use_plain=True)
            %(u)s'false'

            >>> Literal(1.91)._literal_n3(use_plain=True)
            %(u)s'1.91e+00'

            Only limited precision available for floats:
            >>> Literal(0.123456789)._literal_n3(use_plain=True)
            %(u)s'1.234568e-01'

            >>> Literal('0.123456789',
            ...     datatype=XSD.decimal)._literal_n3(use_plain=True)
            %(u)s'0.123456789'

        Using callback for datatype QNames::

            >>> Literal(1)._literal_n3(
            ...         qname_callback=lambda uri: "xsd:integer")
            %(u)s'"1"^^xsd:integer'

        '''
        if use_plain and self.datatype in _PLAIN_LITERAL_TYPES:
            if self.value is not None:

                # this is a bit of a mess -
                # in py >=2.6 the string.format function makes this easier
                # we try to produce "pretty" output
                if self.datatype == _XSD_DOUBLE:
                    return sub("\\.?0*e", "e", u'%e' % float(self))
                elif self.datatype == _XSD_DECIMAL:
                    s = '%s' % self
                    if '.' not in s:
                        s += '.0'
                    return s

                elif self.datatype == _XSD_BOOLEAN:
                    return (u'%s' % self).lower()
                else:
                    return u'%s' % self

        encoded = self._quote_encode()

        datatype = self.datatype
        quoted_dt = None
        if datatype:
            if qname_callback:
                quoted_dt = qname_callback(datatype)
            if not quoted_dt:
                quoted_dt = "<%s>" % datatype

        language = self.language
        if language:
            return '%s@%s' % (encoded, language)
        elif datatype:
            return '%s^^%s' % (encoded, quoted_dt)
        else:
            return '%s' % encoded

    def _quote_encode(self):
        # This simpler encoding doesn't work; a newline gets encoded as "\\n",
        # which is ok in sourcecode, but we want "\n".
        # encoded = self.encode('unicode-escape').replace(
        #        '\\', '\\\\').replace('"','\\"')
        # encoded = self.replace.replace('\\', '\\\\').replace('"','\\"')

        # NOTE: Could in theory chose quotes based on quotes appearing in the
        # string, i.e. '"' and "'", but N3/turtle doesn't allow "'"(?).

        if "\n" in self:
            # Triple quote this string.
            encoded = self.replace('\\', '\\\\')
            if '"""' in self:
                # is this ok?
                encoded = encoded.replace('"""', '\\"\\"\\"')
            if encoded[-1] == '"' and encoded[-2] != '\\':
                encoded = encoded[:-1] + '\\' + '"'

            return '"""%s"""' % encoded.replace('\r', '\\r')
        else:
            return '"%s"' % self.replace(
                '\n', '\\n').replace(
                    '\\', '\\\\').replace(
                        '"', '\\"').replace(
                            '\r', '\\r')

    if not py3compat.PY3:
        def __str__(self):
            return self.encode()

    def __repr__(self):
        args = [super(Literal, self).__repr__()]
        if self.language is not None:
            args.append("lang=%s" % repr(self.language))
        if self.datatype is not None:
            args.append("datatype=%s" % repr(self.datatype))
        if self.__class__ == Literal:
            clsName = "rdflib.term.Literal"
        else:
            clsName = self.__class__.__name__
        return """%s(%s)""" % (clsName, ", ".join(args))

    def toPython(self):
        """
        Returns an appropriate python datatype derived from this RDF Literal
        """

        if self.value is not None:
            return self.value
        return self

    def md5_term_hash(self):
        """a string of hex that will be the same for two Literals that
        are the same. It is not a suitable unique id.

        Supported for backwards compatibility; new code should
        probably just use __hash__
        """
        d = md5(self.encode())
        d.update(b("L"))
        return d.hexdigest()


# Cannot import Namespace/XSD because of circular dependencies
_XSD_PFX = 'http://www.w3.org/2001/XMLSchema#'

_XSD_STRING = URIRef(_XSD_PFX + 'string')

_XSD_FLOAT = URIRef(_XSD_PFX + 'float')
_XSD_DOUBLE = URIRef(_XSD_PFX + 'double')
_XSD_DECIMAL = URIRef(_XSD_PFX + 'decimal')
_XSD_INTEGER = URIRef(_XSD_PFX + 'integer')
_XSD_BOOLEAN = URIRef(_XSD_PFX + 'boolean')

_XSD_DATETIME = URIRef(_XSD_PFX + 'dateTime')
_XSD_DATE = URIRef(_XSD_PFX + 'date')
_XSD_TIME = URIRef(_XSD_PFX + 'time')

# TODO: duration, gYearMonth, gYear, gMonthDay, gDay, gMonth

_NUMERIC_LITERAL_TYPES = (
    _XSD_INTEGER,
    _XSD_DECIMAL,
    _XSD_DOUBLE,
    URIRef(_XSD_PFX + 'float'),

    URIRef(_XSD_PFX + 'byte'),
    URIRef(_XSD_PFX + 'int'),
    URIRef(_XSD_PFX + 'long'),
    URIRef(_XSD_PFX + 'negativeInteger'),
    URIRef(_XSD_PFX + 'nonNegativeInteger'),
    URIRef(_XSD_PFX + 'nonPositiveInteger'),
    URIRef(_XSD_PFX + 'positiveInteger'),
    URIRef(_XSD_PFX + 'short'),
    URIRef(_XSD_PFX + 'unsignedByte'),
    URIRef(_XSD_PFX + 'unsignedInt'),
    URIRef(_XSD_PFX + 'unsignedLong'),
    URIRef(_XSD_PFX + 'unsignedShort'),

)

# these have "native" syntax in N3/SPARQL
_PLAIN_LITERAL_TYPES = (
    _XSD_INTEGER,
    _XSD_BOOLEAN,
    _XSD_DOUBLE,
    _XSD_DECIMAL,
)


def _castPythonToLiteral(obj):
    """
    Casts a python datatype to a tuple of the lexical value and a
    datatype URI (or None)
    """
    for pType, (castFunc, dType) in _PythonToXSD:
        if isinstance(obj, pType):
            if castFunc:
                return castFunc(obj), dType
            elif dType:
                return obj, dType
            else:
                return obj, None
    return obj, None  # TODO: is this right for the fall through case?

from decimal import Decimal

# Mappings from Python types to XSD datatypes and back (borrowed from sparta)
# datetime instances are also instances of date... so we need to order these.

# SPARQL/Turtle/N3 has shortcuts for integer, double, decimal
# python has only float - to be in tune with sparql/n3/turtle
# we default to XSD.double for float literals

# python ints are promoted to longs when overflowing
# python longs have no limit
# both map to the abstract integer type,
# rather than some concrete bit-limited datatype

_PythonToXSD = [
    (basestring, (None, None)),
    (float, (None, _XSD_DOUBLE)),
    (bool, (lambda i:str(i).lower(), _XSD_BOOLEAN)),
    (int, (None, _XSD_INTEGER)),
    (long, (None, _XSD_INTEGER)),
    (Decimal, (None, _XSD_DECIMAL)),
    (datetime, (lambda i:i.isoformat(), _XSD_DATETIME)),
    (date, (lambda i:i.isoformat(), _XSD_DATE)),
    (time, (lambda i:i.isoformat(), _XSD_TIME)),
]

XSDToPython = {
    URIRef(_XSD_PFX + 'time'): parse_time,
    URIRef(_XSD_PFX + 'date'): parse_date,
    URIRef(_XSD_PFX + 'dateTime'): parse_datetime,
    URIRef(_XSD_PFX + 'string'): None,
    URIRef(_XSD_PFX + 'normalizedString'): None,
    URIRef(_XSD_PFX + 'token'): None,
    URIRef(_XSD_PFX + 'language'): None,
    URIRef(_XSD_PFX + 'boolean'): lambda i: i.lower() in ['1', 'true'],
    URIRef(_XSD_PFX + 'decimal'): Decimal,
    URIRef(_XSD_PFX + 'integer'): long,
    URIRef(_XSD_PFX + 'nonPositiveInteger'): int,
    URIRef(_XSD_PFX + 'long'): long,
    URIRef(_XSD_PFX + 'nonNegativeInteger'): int,
    URIRef(_XSD_PFX + 'negativeInteger'): int,
    URIRef(_XSD_PFX + 'int'): long,
    URIRef(_XSD_PFX + 'unsignedLong'): long,
    URIRef(_XSD_PFX + 'positiveInteger'): int,
    URIRef(_XSD_PFX + 'short'): int,
    URIRef(_XSD_PFX + 'unsignedInt'): long,
    URIRef(_XSD_PFX + 'byte'): int,
    URIRef(_XSD_PFX + 'unsignedShort'): int,
    URIRef(_XSD_PFX + 'unsignedByte'): int,
    URIRef(_XSD_PFX + 'float'): float,
    URIRef(_XSD_PFX + 'double'): float,
    URIRef(
        _XSD_PFX + 'base64Binary'): lambda s: base64.b64decode(py3compat.b(s)),
    URIRef(_XSD_PFX + 'anyURI'): None,
}

_toPythonMapping = {}
_toPythonMapping.update(XSDToPython)


def bind(datatype, pythontype, constructor=None, lexicalizer=None):
    """
    register a new datatype<->pythontype binding

    Args:
       constructor : an optional function for converting lexical forms
                     into a Python instances, if not given the pythontype
                     is used directly
       lexicalizer : an optinoal function for converting python objects to
                     lexical form, if not given object.__str__ is used

    """
    if datatype in _toPythonMapping:
        _LOGGER.warning("datatype '%s' was already bound. Rebinding." %
                        datatype)

    if constructor == None:
        constructor = pythontype
    _toPythonMapping[datatype] = constructor
    _PythonToXSD.append((pythontype, (lexicalizer, datatype)))


class Variable(Identifier):
    """
    """
    __slots__ = ()

    def __new__(cls, value):
        if len(value) == 0:
            raise Exception(
                "Attempted to create variable with empty string as name!")
        if value[0] == '?':
            value = value[1:]
        return unicode.__new__(cls, value)

    def __repr__(self):
        return self.n3()

    def toPython(self):
        return "?%s" % self

    def n3(self):
        return "?%s" % self

    def __reduce__(self):
        return (Variable, (unicode(self),))

    def md5_term_hash(self):
        """a string of hex that will be the same for two Variables that
        are the same. It is not a suitable unique id.

        Supported for backwards compatibility; new code should
        probably just use __hash__
        """
        d = md5(self.encode())
        d.update(b("V"))
        return d.hexdigest()


class Statement(Node, tuple):

    def __new__(cls, (subject, predicate, object), context):
        warnings.warn(
            "Class Statement is deprecated, and will be removed in " +
            "the future. If you use this please let rdflib-dev know!",
            category=DeprecationWarning, stacklevel=2)
        return tuple.__new__(cls, ((subject, predicate, object), context))

    def __reduce__(self):
        return (Statement, (self[0], self[1]))

    def toPython(self):
        return (self[0], self[1])

# Nodes are ordered like this
# See http://www.w3.org/TR/sparql11-query/#modOrderBy
_ORDERING = dict(map(reversed, enumerate([BNode, Variable, URIRef, Literal])))

if __name__ == '__main__':
    import doctest
    doctest.testmod()
