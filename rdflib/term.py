"""
This module defines the different types of terms...

"""

__all__ = [
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
from string import ascii_letters, rsplit
from random import choice
from itertools import islice
from datetime import date, time, datetime
from time import strptime

try:
    from hashlib import md5
except ImportError:
    from md5 import md5

# from sys import version_info
# if version_info[0:2] > (2, 2):
#     from unicodedata import normalize
# else:
#     normalize = None
#
#from rdflib.syntax.xml_names import is_ncname
#from rdflib.exceptions import Error


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

    def n3(self):
        return "<%s>" % self

    def concrete(self):
        if "#" in self:
            return URIRef("/".join(rsplit(self, "#", 1)))
        else:
            return self

    def abstract(self):
        if "#" not in self:
            scheme, netloc, path, params, query, fragment = urlparse(self)
            if path:
                return URIRef("#".join(rsplit(self, "/", 1)))
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

    def __str__(self):
        return self.encode("unicode-escape")

    def __repr__(self):
        if self.__class__ is URIRef:
            clsName = "rdflib.term.URIRef"
        else:
            clsName = self.__class__.__name__

        # quoting risk? drewp is not sure why this doesn't use %r
        return """%s('%s')""" % (clsName, str(self))
        

    def md5_term_hash(self):
        """a string of hex that will be the same for two URIRefs that
        are the same. It is not a suitable unique id.

        Supported for backwards compatibility; new code should
        probably just use __hash__
        """
        d = md5(str(self))
        d.update("U")
        return d.hexdigest()



def _letter():
    while True:
        yield choice(ascii_letters)

def _unique_id():
    """Create a (hopefully) unique prefix"""
    uid = "".join(islice(_letter(), 0, 8))
    return uid

def _serial_number_generator():
    i = 0
    while 1:
        yield i
        i = i + 1

bNodeLock = threading.RLock()

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
            bNodeLock.acquire()
            node_id = _sn_gen.next()
            bNodeLock.release()
            value = "%s%s" % (_prefix, node_id)
        else:
            # TODO: check that value falls within acceptable bnode value range
            # for RDF/XML needs to be something that can be serialzed
            # as a nodeID for N3 ??  Unless we require these
            # constraints be enforced elsewhere?
            pass #assert is_ncname(unicode(value)), "BNode identifiers
                 #must be valid NCNames"

        return Identifier.__new__(cls, value)

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

    def __str__(self):
        return self.encode("unicode-escape")

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
        d = md5(str(self))
        d.update("B")
        return d.hexdigest()


class Literal(Identifier):
    """
    RDF Literal: http://www.w3.org/TR/rdf-concepts/#section-Graph-Literal

    >>> Literal(1).toPython()
    1L
    >>> cmp(Literal("adsf"), 1)
    1
    >>> from rdflib.namespace import XSD
    >>> lit2006 = Literal('2006-01-01',datatype=XSD.date)
    >>> lit2006.toPython()
    datetime.date(2006, 1, 1)
    >>> lit2006 < Literal('2007-01-01',datatype=XSD.date)
    True
    >>> Literal(datetime.utcnow()).datatype
    rdflib.term.URIRef('http://www.w3.org/2001/XMLSchema#dateTime')
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
    """

    __slots__ = ("language", "datatype", "_cmp_value")

    def __new__(cls, value, lang=None, datatype=None):
        if lang is not None and datatype is not None:
            raise TypeError("A Literal can only have one of lang or datatype, "
               "per http://www.w3.org/TR/rdf-concepts/#section-Graph-Literal")

        if datatype:
            lang = None
        else:
            value, datatype = _castPythonToLiteral(value)
            if datatype:
                lang = None
        if datatype:
            datatype = URIRef(datatype)
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

    def __add__(self, val):
        """
        >>> Literal(1) + 1
        2L
        >>> Literal("1") + "1"
        rdflib.term.Literal(u'11')
        """

        py = self.toPython()
        if isinstance(py, Literal):
            s = super(Literal, self).__add__(val)
            return Literal(s, self.language, self.datatype)
        else:
            return py + val

    def __lt__(self, other):
        """
        >>> from rdflib.namespace import XSD
        >>> Literal("YXNkZg==", datatype=XSD[u'base64Binary']) < "foo"
        True
        >>> u"\xfe" < Literal(u"foo")
        False
        >>> Literal(base64.encodestring(u"\xfe".encode("utf-8")), datatype=URIRef("http://www.w3.org/2001/XMLSchema#base64Binary")) < u"foo"
        False
        """

        if other is None:
            return False # Nothing is less than None
        try:
            return self._cmp_value < other
        except TypeError, te:
            return unicode(self._cmp_value) < other
        except UnicodeDecodeError, ue:
            if isinstance(self._cmp_value, str):
                return self._cmp_value < other.encode("utf-8")
            else:
                raise ue

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
        except TypeError, te:
            return unicode(self._cmp_value) > other
        except UnicodeDecodeError, ue:
            if isinstance(self._cmp_value, str):
                return self._cmp_value > other.encode("utf-8")
            else:
                raise ue

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
        >>> Literal('2') <> Literal('2')
        False

        """
        return not self.__eq__(other)

    def __hash__(self):
        """
        >>> from rdflib.namespace import XSD
        >>> a = {Literal('1', datatype=XSD.integer):'one'}
        >>> Literal('1', datatype=XSD.double) in a
        False

        [[
        Called for the key object for dictionary operations, 
        and by the built-in function hash(). Should return 
        a 32-bit integer usable as a hash value for 
        dictionary operations. The only required property 
        is that objects which compare equal have the same 
        hash value; it is advised to somehow mix together 
        (e.g., using exclusive or) the hash values for the 
        components of the object that also play a part in 
        comparison of objects. 
        ]] -- 3.4.1 Basic customization (Python)

        [[
        Two literals are equal if and only if all of the following hold:
        * The strings of the two lexical forms compare equal, character by character.
        * Either both or neither have language tags.
        * The language tags, if any, compare equal.
        * Either both or neither have datatype URIs.
        * The two datatype URIs, if any, compare equal, character by character.
        ]] -- 6.5.1 Literal Equality (RDF: Concepts and Abstract Syntax)

        """
        return hash(str(self)) ^ hash(self.language) ^ hash(self.datatype)

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
        >>> Literal("1", XSD[u'string']) == Literal("1", XSD[u'string'])
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

    def n3(self):
        r'''
        Returns a representation in the N3 format.

        Examples::

            >>> Literal("foo").n3()
            u'"foo"'

        Strings with newlines or triple-quotes::

            >>> Literal("foo\nbar").n3()
            u'"""foo\nbar"""'

            >>> Literal("''\'").n3()
            u'"\'\'\'"'

            >>> Literal('"""').n3()
            u'"\\"\\"\\""'

        Language::

            >>> Literal("hello", lang="en").n3()
            u'"hello"@en'

        Datatypes::

            >>> Literal(1).n3()
            u'"1"^^<http://www.w3.org/2001/XMLSchema#integer>'

            >>> Literal(1, lang="en").n3()
            u'"1"^^<http://www.w3.org/2001/XMLSchema#integer>'

            >>> Literal(1.0).n3()
            u'"1.0"^^<http://www.w3.org/2001/XMLSchema#float>'

        Datatype and language isn't allowed (datatype takes precedence)::

            >>> Literal(True).n3()
            u'"true"^^<http://www.w3.org/2001/XMLSchema#boolean>'

        Custom datatype::

            >>> footype = URIRef("http://example.org/ns#foo")
            >>> Literal("1", datatype=footype).n3()
            u'"1"^^<http://example.org/ns#foo>'

        '''
        return self._literal_n3()

    def _literal_n3(self, use_plain=False, qname_callback=None):
        '''
        Using plain literal (shorthand) output::

            >>> Literal(1)._literal_n3(use_plain=True)
            u'1'

            >>> Literal(1.0)._literal_n3(use_plain=True)
            u'1.0'

            >>> from rdflib.namespace import XSD
            >>> Literal("foo", datatype=XSD.string)._literal_n3(
            ...         use_plain=True)
            u'"foo"^^<http://www.w3.org/2001/XMLSchema#string>'

            >>> Literal(True)._literal_n3(use_plain=True)
            u'true'

            >>> Literal(False)._literal_n3(use_plain=True)
            u'false'

        Using callback for datatype QNames::

            >>> Literal(1)._literal_n3(
            ...         qname_callback=lambda uri: u"xsd:integer")
            u'"1"^^xsd:integer'

        '''
        if use_plain and self.datatype in _PLAIN_LITERAL_TYPES:
            try:
                self.toPython() # check validity
                return '%s' % self
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

        # which is nicer?
        # if self.find("\"")!=-1 or self.find("'")!=-1 or self.find("\n")!=-1:
        if "\n" in self:
            # Triple quote this string.
            encoded = self.replace('\\', '\\\\')
            if '"""' in self:
                # is this ok?
                encoded = encoded.replace('"""','\\"""')
            if encoded.endswith('"'):
                encoded = encoded[:-1] + "\\\""
            return '"""%s"""' % encoded
        else:
            return '"%s"' % self.replace('\n','\\n').replace('\\', '\\\\'
                            ).replace('"', '\\"')

    def __str__(self):
        return self.encode("unicode-escape")

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
        d = md5(str(self))
        d.update("L")
        return d.hexdigest()



_XSD_PFX = 'http://www.w3.org/2001/XMLSchema#'

_PLAIN_LITERAL_TYPES = (
    URIRef(_XSD_PFX+'integer'),
    URIRef(_XSD_PFX+'float'),
    #XSD.decimal, XSD.double, # TODO: "subsumed" by float...
    URIRef(_XSD_PFX+'boolean'),
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

# Mappings from Python types to XSD datatypes and back (burrowed from sparta)
# datetime instances are also instances of date... so we need to order these.
_PythonToXSD = [
    (basestring, (None, None)),
    (float     , (None, URIRef(_XSD_PFX+'float'))),
    (bool      , (lambda i:str(i).lower(), URIRef(_XSD_PFX+'boolean'))),
    (int       , (None, URIRef(_XSD_PFX+'integer'))),
    (long      , (None, URIRef(_XSD_PFX+'long'))),
    (datetime  , (lambda i:i.isoformat(), URIRef(_XSD_PFX+'dateTime'))),
    (date      , (lambda i:i.isoformat(), URIRef(_XSD_PFX+'date'))),
    (time      , (lambda i:i.isoformat(), URIRef(_XSD_PFX+'time'))),
]

def _strToTime(v) :
    return strptime(v, "%H:%M:%S")

def _strToDate(v) :
    tstr = strptime(v, "%Y-%m-%d")
    return date(tstr.tm_year, tstr.tm_mon, tstr.tm_mday)

def _strToDateTime(v) :
    """
    Attempt to cast to datetime, or just return the string (otherwise)
    """
    try:
        tstr = strptime(v, "%Y-%m-%dT%H:%M:%S")
    except:
        try:
            tstr = strptime(v, "%Y-%m-%dT%H:%M:%SZ")
        except:
            try:
                tstr = strptime(v, "%Y-%m-%dT%H:%M:%S%Z")
            except:
                try:
                    # %f only works in python 2.6
                    return datetime.strptime(v, "%Y-%m-%dT%H:%M:%S.%f")
                except:
                    return v

    return datetime(tstr.tm_year, tstr.tm_mon, tstr.tm_mday,
                    tstr.tm_hour, tstr.tm_min, tstr.tm_sec)

XSDToPython = {
    URIRef(_XSD_PFX+'time')               : _strToTime,
    URIRef(_XSD_PFX+'date')               : _strToDate,
    URIRef(_XSD_PFX+'dateTime')           : _strToDateTime,
    URIRef(_XSD_PFX+'string')             : None,
    URIRef(_XSD_PFX+'normalizedString')   : None,
    URIRef(_XSD_PFX+'token')              : None,
    URIRef(_XSD_PFX+'language')           : None,
    URIRef(_XSD_PFX+'boolean')            : lambda i:i.lower() in ['1','true'],
    URIRef(_XSD_PFX+'decimal')            : float,
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
    URIRef(_XSD_PFX+'base64Binary')       : base64.decodestring,
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
        if value[0]=='?':
            value=value[1:]
        return unicode.__new__(cls, value)

    def __repr__(self):
        return self.n3()

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
        d = md5(str(self))
        d.update("V")
        return d.hexdigest()


class Statement(Node, tuple):

    def __new__(cls, (subject, predicate, object), context):
        return tuple.__new__(cls, ((subject, predicate, object), context))

    def __reduce__(self):
        return (Statement, (self[0], self[1]))


if __name__ == '__main__':
    import doctest
    doctest.testmod()


