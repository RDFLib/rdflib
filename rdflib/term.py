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

And those that are primarily for matching against 'Nodes' in the underlying Graph:

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

_LOGGER = logging.getLogger(__name__)

import base64
import threading

from urlparse import urlparse, urljoin, urldefrag
from string import ascii_letters
from random import choice
from itertools import islice
from datetime import date, time, datetime
from isodate import parse_time, parse_date, parse_datetime
from re import sub

try:
    from hashlib import md5
except ImportError:
    from md5 import md5

import py3compat
b = py3compat.b

class Node(object):
    """
    A Node in the Graph.
    """

    __slots__ = ()


class Identifier(Node, unicode): # we allow Identifiers to be Nodes in our Graph
    """
    See http://www.w3.org/2002/07/rdf-identifer-terminology/
    regarding choice of terminology.
    """

    __slots__ = ()

    def __new__(cls, value):
        return unicode.__new__(cls, value)


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
        #if normalize and value and value != normalize("NFC", value):
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
        if "#" in self:
            return URIRef("/".join(self.rsplit("#", 1)))
        else:
            return self

    def abstract(self):
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


    def __ne__(self, other):
        return not self.__eq__(other)

    def __eq__(self, other):
        if isinstance(other, URIRef):
            return unicode(self)==unicode(other)
        else:
            return False
    
    def __hash__(self):
        return hash(URIRef) ^ hash(unicode(self))

    if not py3compat.PY3:
        def __str__(self):
            return self.encode()

    def __repr__(self):
        if self.__class__ is URIRef:
            clsName = "rdflib.term.URIRef"
        else:
            clsName = self.__class__.__name__

        return """%s(%s)""" % (clsName, super(URIRef,self).__repr__())
        

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
    return "N" # ensure that id starts with a letter


# Adapted from http://icodesnip.com/snippet/python/simple-universally-unique-id-uuid-or-guid
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
        if value==None:
            # so that BNode values do not
            # collide with ones created with a different instance of this module
            # at some other time.
            node_id = _sn_gen()
            value = "%s%s" % (_prefix, node_id)
        else:
            # TODO: check that value falls within acceptable bnode value range
            # for RDF/XML needs to be something that can be serialzed
            # as a nodeID for N3 ??  Unless we require these
            # constraints be enforced elsewhere?
            pass # assert is_ncname(unicode(value)), "BNode identifiers
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

    def __ne__(self, other):
        return not self.__eq__(other)

    def __eq__(self, other):
        """
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
        """
        if isinstance(other, BNode):
            return unicode(self)==unicode(other)
        else:
            return False
    
    def __hash__(self):
        return hash(BNode) ^ hash(unicode(self))

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

    >>> from rdflib import Literal, XSD
    >>> Literal(1).toPython()
    1%(L)s
    >>> Literal("adsf") > 1
    True
    >>> from rdflib.namespace import XSD
    >>> lit2006 = Literal('2006-01-01',datatype=XSD.date)
    >>> lit2006.toPython()
    datetime.date(2006, 1, 1)
    >>> lit2006 < Literal('2007-01-01',datatype=XSD.date)
    True
    >>> Literal(datetime.utcnow()).datatype
    rdflib.term.URIRef(%(u)s'http://www.w3.org/2001/XMLSchema#dateTime')
    >>> oneInt     = Literal(1)
    >>> twoInt     = Literal(2)
    >>> twoInt < oneInt
    False
    >>> Literal('1') < Literal(1)
    False
    >>> Literal('1') < Literal('1')
    False
    >>> Literal(1) < Literal('1')
    True
    >>> Literal(1) < Literal(2.0)
    True
    >>> Literal(1) < URIRef('foo')
    True
    >>> Literal(1) < 2.0
    True
    >>> Literal(1) < object
    True
    >>> lit2006 < "2007"
    True
    >>> "2005" < lit2006
    True
    >>> x = Literal("2", datatype=XSD.integer)
    >>> x
    rdflib.term.Literal(%(u)s'2', datatype=rdflib.term.URIRef(%(u)s'http://www.w3.org/2001/XMLSchema#integer'))
    >>> Literal(x) == x
    True
    >>> x = Literal("cake", lang="en")
    >>> x
    rdflib.term.Literal(%(u)s'cake', lang='en')
    >>> Literal(x) == x
    True
    """
    __doc__ = py3compat.format_doctest_out(doc)

    __slots__ = ("language", "datatype", "_cmp_value")

    def __new__(cls, value, lang=None, datatype=None):
        if lang is not None and datatype is not None:
            raise TypeError("A Literal can only have one of lang or datatype, "
               "per http://www.w3.org/TR/rdf-concepts/#section-Graph-Literal")

        if isinstance(value, Literal): # create from another Literal instance
            datatype=datatype or value.datatype
            lang=lang or value.language

        if datatype:
            lang = None
        else:
            value, datatype = _castPythonToLiteral(value)
            if datatype:
                lang = None
        if datatype:
            datatype = URIRef(datatype)
        if py3compat.PY3 and isinstance(value, bytes):
            value = value.decode('utf-8')
        try:
            inst = unicode.__new__(cls, value)
        except UnicodeDecodeError:
            inst = unicode.__new__(cls, value, 'utf-8')
        inst.language = lang
        inst.datatype = datatype
        inst._cmp_value = inst._toCompareValue()
        return inst

    def __reduce__(self):
        return (Literal, (unicode(self), self.language, self.datatype),)

    def __getstate__(self):
        return (None, dict(language=self.language, datatype=self.datatype))

    def __setstate__(self, arg):
        _, d = arg
        self.language = d["language"]
        self.datatype = d["datatype"]

    @py3compat.format_doctest_out
    def __add__(self, val):
        """
        >>> Literal(1) + 1
        2%(L)s
        >>> Literal("1") + "1"
        rdflib.term.Literal(%(u)s'11')
        """

        py = self.toPython()
        if isinstance(py, Literal):
            s = super(Literal, self).__add__(val)
            return Literal(s, self.language, self.datatype)
        else:
            return py + val

    @py3compat.format_doctest_out
    def __neg__(self):
        """
        >>> (- Literal(1))
        -1%(L)s
        >>> (- Literal(10.5))
        -10.5
        >>> from rdflib.namespace import XSD
        >>> (- Literal("1", datatype=XSD['integer']))
        -1%(L)s
        
        Not working:
        #>>> (- Literal("1"))
        #Traceback (most recent call last):
        #  File "<stdin>", line 1, in <module>
        #TypeError: Not a number; rdflib.term.Literal(u'1')
        >>> 
        """

        py = self.toPython()
        try:
            return py.__neg__()
        except Exception, e:
            raise TypeError("Not a number; %s" % repr(self))

    @py3compat.format_doctest_out
    def __pos__(self):
        """
        >>> (+ Literal(1))
        1%(L)s
        >>> (+ Literal(-1))
        -1%(L)s
        >>> from rdflib.namespace import XSD
        >>> (+ Literal("-1", datatype=XSD['integer']))
        -1%(L)s
        
        Not working in Python 3:
        #>>> (+ Literal("1"))
        #Traceback (most recent call last):
        #  File "<stdin>", line 1, in <module>
        #TypeError: Not a number; rdflib.term.Literal(u'1')
        """
        py = self.toPython()
        try:
            return py.__pos__()
        except Exception, e:
            raise TypeError("Not a number; %s" % repr(self))

    @py3compat.format_doctest_out
    def __abs__(self):
        """
        >>> abs(Literal(-1))
        1%(L)s
        >>> from rdflib.namespace import XSD
        >>> abs( Literal("-1", datatype=XSD['integer']))
        1%(L)s
        
        Not working in Python 3:
        #>>> abs(Literal("1"))
        #Traceback (most recent call last):
        #  File "<stdin>", line 1, in <module>
        #TypeError: Not a number; rdflib.term.Literal(u'1')
        """
        py = self.toPython()
        try:
            return py.__abs__()
        except Exception, e:
            raise TypeError("Not a number; %s" % repr(self))

    @py3compat.format_doctest_out
    def __invert__(self):
        """
        >>> ~(Literal(-1))
        0%(L)s
        >>> from rdflib.namespace import XSD
        >>> ~( Literal("-1", datatype=XSD['integer']))
        0%(L)s
        
        Not working:
        #>>> ~(Literal("1"))
        #Traceback (most recent call last):
        #  File "<stdin>", line 1, in <module>
        #TypeError: Not a number; rdflib.term.Literal(u'1')
        >>> 
        """
        py = self.toPython()
        try:
            return py.__invert__()
        except Exception:
            raise TypeError("Not a number; %s" % repr(self))

    @py3compat.format_doctest_out
    def __lt__(self, other):
        """
        >>> from rdflib.namespace import XSD
        >>> Literal("YXNkZg==", datatype=XSD['base64Binary']) < "foo"
        True
        >>> %(u)s"\xfe" < Literal(%(u)s"foo")
        False
        >>> Literal(base64.encodestring(%(u)s"\xfe".encode("utf-8")), datatype=URIRef("http://www.w3.org/2001/XMLSchema#base64Binary")) < %(u)s"foo"
        False
        """

        if other is None:
            return False # Nothing is less than None
        try:
            return self._cmp_value < other
        except UnicodeDecodeError, ue:
            if isinstance(self._cmp_value, py3compat.bytestype):
                return self._cmp_value < other.encode("utf-8")
            else:
                raise ue
        except TypeError:
            try:
                # On Python 3, comparing bytes/str is a TypeError, not a UnicodeError
                if isinstance(self._cmp_value, py3compat.bytestype):
                    return self._cmp_value < other.encode("utf-8")
                return unicode(self._cmp_value) < other
            except (TypeError, AttributeError):
                # Treat different types like Python 2 for now.
                return py3compat.type_cmp(self._cmp_value, other) == -1

    def __le__(self, other):
        """
        >>> from rdflib.namespace import XSD
        >>> Literal('2007-01-01T10:00:00', datatype=XSD.dateTime) <= Literal('2007-01-01T10:00:00', datatype=XSD.dateTime)
        True
        """
        if other is None:
            return False
        if self==other:
            return True
        else:
            return self < other

    def __gt__(self, other):
        if other is None:
            return True # Everything is greater than None
        try:
            return self._cmp_value > other
        except UnicodeDecodeError, ue:
            if isinstance(self._cmp_value, py3compat.bytestype):
                return self._cmp_value > other.encode("utf-8")
            else:
                raise ue
        except TypeError:
            try:
                # On Python 3, comparing bytes/str is a TypeError, not a UnicodeError
                if isinstance(self._cmp_value, py3compat.bytestype):
                    return self._cmp_value > other.encode("utf-8")
                return unicode(self._cmp_value) > other
            except (TypeError, AttributeError):
                # Treat different types like Python 2 for now.
                return py3compat.type_cmp(self._cmp_value, other) == 1

    def __ge__(self, other):
        if other is None:
            return False
        if self==other:
            return True
        else:
            return self > other

    def __ne__(self, other):
        """
        Overriden to ensure property result for comparisons with None via !=.
        Routes all other such != and <> comparisons to __eq__

        >>> Literal('') != None
        True
        >>> Literal('2') != Literal('2')
        False

        """
        return not self.__eq__(other)

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
        * The strings of the two lexical forms compare equal, character by character.
        * Either both or neither have language tags.
        * The language tags, if any, compare equal.
        * Either both or neither have datatype URIs.
        * The two datatype URIs, if any, compare equal, character by character."
        -- 6.5.1 Literal Equality (RDF: Concepts and Abstract Syntax)

        """
        
        return Identifier.__hash__(self) ^ hash(self.language) ^ hash(self.datatype)

    @py3compat.format_doctest_out
    def __eq__(self, other):
        """
        >>> f = URIRef("foo")
        >>> f is None or f == ''
        False
        >>> Literal("1", datatype=URIRef("foo")) == Literal("1", datatype=URIRef("foo"))
        True
        >>> Literal("1", datatype=URIRef("foo")) == Literal("2", datatype=URIRef("foo"))
        False
        >>> Literal("1", datatype=URIRef("foo")) == "asdf"
        False
        >>> from rdflib.namespace import XSD
        >>> Literal('2007-01-01', datatype=XSD.date) == Literal('2007-01-01', datatype=XSD.date)
        True
        >>> Literal('2007-01-01', datatype=XSD.date) == date(2007, 1, 1)
        True
        >>> oneInt     = Literal(1)
        >>> oneNoDtype = Literal('1')
        >>> oneInt == oneNoDtype
        False
        >>> Literal("1", XSD['string']) == Literal("1", XSD['string'])
        True
        >>> Literal("one", lang="en") == Literal("one", lang="en")
        True
        >>> Literal("hast", lang='en') == Literal("hast", lang='de')
        False
        >>> oneInt == Literal(1)
        True
        >>> oneFloat   = Literal(1.0)
        >>> oneInt == oneFloat
        True
        >>> oneInt == 1
        True
        """
        if other is None:
            return False
        if isinstance(other, Literal):
            return self._cmp_value == other._cmp_value
        elif isinstance(other, basestring):
            return unicode(self) == other
        else:
            return self._cmp_value == other

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

        Using callback for datatype QNames::

            >>> Literal(1)._literal_n3(
            ...         qname_callback=lambda uri: "xsd:integer")
            %(u)s'"1"^^xsd:integer'

        '''
        if use_plain and self.datatype in _PLAIN_LITERAL_TYPES:
            try:
                self.toPython() # check validity
                # this is a bit of a mess - 
                # in py >=2.6 the string.format function makes this easier
                # we try to produce "pretty" output
                if self.datatype == _XSD_DOUBLE: 
                    return sub(".?0*e","e", u'%e' % float(self))
                elif self.datatype == _XSD_DECIMAL:
                    return sub("0*$","0",u'%f' % float(self))
                else:
                    return u'%s' % self
            except ValueError:
                pass # if it's in, we let it out?

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
            if datatype:
                # TODO: this isn't valid RDF (it's datatype XOR language)
                return '%s@%s^^%s' % (encoded, language, quoted_dt)
            return '%s@%s' % (encoded, language)
        elif datatype:
            return '%s^^%s' % (encoded, quoted_dt)
        else:
            return '%s' % encoded

    def _quote_encode(self):
        # This simpler encoding doesn't work; a newline gets encoded as "\\n",
        # which is ok in sourcecode, but we want "\n".
        #encoded = self.encode('unicode-escape').replace(
        #        '\\', '\\\\').replace('"','\\"')
        #encoded = self.replace.replace('\\', '\\\\').replace('"','\\"')

        # NOTE: Could in theory chose quotes based on quotes appearing in the
        # string, i.e. '"' and "'", but N3/turtle doesn't allow "'"(?).

        if "\n" in self:
            # Triple quote this string.
            encoded = self.replace('\\', '\\\\')
            if '"""' in self:
                # is this ok?
                encoded = encoded.replace('"""','\\"\\"\\"')
            return '"""%s"""' % encoded.replace('\r','\\r')
        else:
            return '"%s"' % self.replace('\n','\\n').replace('\\', '\\\\'
                            ).replace('"', '\\"').replace('\r','\\r')

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
        convFunc = _toPythonMapping.get(self.datatype, None)

        if convFunc:
            rt = convFunc(self)
        else:
            rt = self
        return rt

    def _toCompareValue(self):
        try:
            rt = self.toPython()
        except Exception, e:
            _LOGGER.warning("could not convert %s to a Python datatype" % 
                            repr(self))
            rt = self

        if rt is self:
            if self.language is None and self.datatype is None:
                return unicode(rt)
            else:
                return (unicode(rt), rt.datatype, rt.language)
        return rt

    def md5_term_hash(self):
        """a string of hex that will be the same for two Literals that
        are the same. It is not a suitable unique id.

        Supported for backwards compatibility; new code should
        probably just use __hash__
        """
        d = md5(self.encode())
        d.update(b("L"))
        return d.hexdigest()



_XSD_PFX = 'http://www.w3.org/2001/XMLSchema#'

_XSD_FLOAT = URIRef(_XSD_PFX+'float')
_XSD_DOUBLE = URIRef(_XSD_PFX+'double')
_XSD_DECIMAL = URIRef(_XSD_PFX+'decimal')


_PLAIN_LITERAL_TYPES = (
    URIRef(_XSD_PFX+'integer'),
    URIRef(_XSD_PFX+'boolean'),
    _XSD_DOUBLE,
    _XSD_DECIMAL,
)


def _castPythonToLiteral(obj):
    """
    Casts a python datatype to a tuple of the lexical value and a
    datatype URI (or None)
    """
    for pType,(castFunc,dType) in _PythonToXSD:
        if isinstance(obj, pType):
            if castFunc:
                return castFunc(obj), dType
            elif dType:
                return obj, dType
            else:
                return obj, None
    return obj, None # TODO: is this right for the fall through case?

from decimal import Decimal

# Mappings from Python types to XSD datatypes and back (burrowed from sparta)
# datetime instances are also instances of date... so we need to order these.

# SPARQL/Turtle/N3 has shortcuts for int, double, decimal 
# python has only float - to be in tune with sparql/n3/turtle
# we default to XSD.double for float literals

_PythonToXSD = [
    (basestring, (None, None)),
    (float     , (None, URIRef(_XSD_PFX+'double'))),
    (bool      , (lambda i:str(i).lower(), URIRef(_XSD_PFX+'boolean'))),
    (int       , (None, URIRef(_XSD_PFX+'integer'))),
    (long      , (None, URIRef(_XSD_PFX+'integer'))),
    (Decimal   , (None, URIRef(_XSD_PFX+'decimal'))),
    (datetime  , (lambda i:i.isoformat(), URIRef(_XSD_PFX+'dateTime'))),
    (date      , (lambda i:i.isoformat(), URIRef(_XSD_PFX+'date'))),
    (time      , (lambda i:i.isoformat(), URIRef(_XSD_PFX+'time'))),
]

XSDToPython = {
    URIRef(_XSD_PFX+'time')               : parse_time,
    URIRef(_XSD_PFX+'date')               : parse_date,
    URIRef(_XSD_PFX+'dateTime')           : parse_datetime,
    URIRef(_XSD_PFX+'string')             : None,
    URIRef(_XSD_PFX+'normalizedString')   : None,
    URIRef(_XSD_PFX+'token')              : None,
    URIRef(_XSD_PFX+'language')           : None,
    URIRef(_XSD_PFX+'boolean')            : lambda i:i.lower() in ['1','true'],
    URIRef(_XSD_PFX+'decimal')            : Decimal,
    URIRef(_XSD_PFX+'integer')            : long,
    URIRef(_XSD_PFX+'nonPositiveInteger') : int,
    URIRef(_XSD_PFX+'long')               : long,
    URIRef(_XSD_PFX+'nonNegativeInteger') : int,
    URIRef(_XSD_PFX+'negativeInteger')    : int,
    URIRef(_XSD_PFX+'int')                : long,
    URIRef(_XSD_PFX+'unsignedLong')       : long,
    URIRef(_XSD_PFX+'positiveInteger')    : int,
    URIRef(_XSD_PFX+'short')              : int,
    URIRef(_XSD_PFX+'unsignedInt')        : long,
    URIRef(_XSD_PFX+'byte')               : int,
    URIRef(_XSD_PFX+'unsignedShort')      : int,
    URIRef(_XSD_PFX+'unsignedByte')       : int,
    URIRef(_XSD_PFX+'float')              : float,
    URIRef(_XSD_PFX+'double')             : float,
    URIRef(_XSD_PFX+'base64Binary')       : lambda s: base64.b64decode(py3compat.b(s)),
    URIRef(_XSD_PFX+'anyURI')             : None,
}

_toPythonMapping = {}
_toPythonMapping.update(XSDToPython)

def bind(datatype, conversion_function):
    """
    bind a datatype to a function for converting it into a Python
    instance.
    """
    if datatype in _toPythonMapping:
        _LOGGER.warning("datatype '%s' was already bound. Rebinding." % 
                        datatype)
    _toPythonMapping[datatype] = conversion_function



class Variable(Identifier):
    """
    """
    __slots__ = ()
    def __new__(cls, value):
        if len(value)==0: raise Exception("Attempted to create variable with empty string as name!")
        if value[0]=='?':
            value=value[1:]
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
        return tuple.__new__(cls, ((subject, predicate, object), context))

    def __reduce__(self):
        return (Statement, (self[0], self[1]))

    def toPython(self):
        return (self[0], self[1])


if __name__ == '__main__':
    import doctest
    doctest.testmod()

