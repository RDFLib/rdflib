from rdflib.Identifier import Identifier
from rdflib.URIRef import URIRef
from rdflib.Namespace import Namespace
from rdflib.exceptions import Error
from datetime import date,time,datetime
from time import strptime
import base64

try:
    from hashlib import md5
except ImportError:
    from md5 import md5    

import logging

_logger = logging.getLogger(__name__)

class Literal(Identifier):
    """
    RDF Literal: http://www.w3.org/TR/rdf-concepts/#section-Graph-Literal

    >>> Literal(1).toPython()
    1L
    >>> cmp(Literal("adsf"), 1)
    1
    >>> lit2006 = Literal('2006-01-01',datatype=_XSD_NS.date)
    >>> lit2006.toPython()
    datetime.date(2006, 1, 1)
    >>> lit2006 < Literal('2007-01-01',datatype=_XSD_NS.date)
    True
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
        if datatype:
            lang = None
        else:
            value,datatype = _castPythonToLiteral(value)
            if datatype:
                lang = None
        if datatype:
            datatype = URIRef(datatype)
        try:
            inst = unicode.__new__(cls,value)
        except UnicodeDecodeError:
            inst = unicode.__new__(cls,value,'utf-8')
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
        rdflib.Literal('11', language=None, datatype=None)
        """

        py = self.toPython()
        if isinstance(py, Literal):
            s = super(Literal, self).__add__(val)            
            return Literal(s, self.language, self.datatype)
        else:
            return py + val 


    
    def __lt__(self, other):
        """
        >>> Literal("YXNkZg==", datatype=_XSD_NS[u'base64Binary']) < "foo"
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
        if other is None:
            return True
        else:
            return not self.__eq__(other)

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
        >>> oneInt     = Literal(1)
        >>> oneNoDtype = Literal('1')
        >>> oneInt == oneNoDtype
        False
        >>> Literal("1",_XSD_NS[u'string']) == Literal("1",_XSD_NS[u'string']) 
        True
        >>> Literal("one",lang="en") == Literal("one",lang="en")
        True
        >>> Literal("hast",lang='en') == Literal("hast",lang='de')
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
        else:
            return self._cmp_value==other

    def n3(self):
        language = self.language
        datatype = self.datatype
        # unfortunately this doesn't work: a newline gets encoded as \\n, which is ok in sourcecode, but we want \n
        #encoded = self.encode('unicode-escape').replace('\\', '\\\\').replace('"','\\"')
        #encoded = self.replace.replace('\\', '\\\\').replace('"','\\"')

        # TODO: We could also chose quotes based on the quotes appearing in the string, i.e. '"' and "'" ...

        # which is nicer?
        #if self.find("\"")!=-1 or self.find("'")!=-1 or self.find("\n")!=-1:
        if self.find("\n")!=-1:
            # Triple quote this string.
            encoded=self.replace('\\', '\\\\')
            if self.find('"""')!=-1: 
                # is this ok?
                encoded=encoded.replace('"""','\\"""')
            if encoded.endswith('"'): encoded=encoded[:-1]+"\\\""
            encoded='"""%s"""'%encoded
        else: 
            encoded='"%s"'%self.replace('\n','\\n').replace('\\', '\\\\').replace('"','\\"')
        if language:
            if datatype:    
                return '%s@%s^^<%s>' % (encoded, language, datatype)
            else:
                return '%s@%s' % (encoded, language)
        else:
            if datatype:
                return '%s^^<%s>' % (encoded, datatype)
            else:
                return '%s' % encoded

    def __str__(self):
        return self.encode("unicode-escape")

    def __repr__(self):
        return """rdflib.Literal('%s', language=%s, datatype=%s)""" % (str(self), repr(self.language), repr(self.datatype))

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
            _logger.warning("could not convert %s to a Python datatype" % repr(self))
            rt = self
                
        if rt is self:
            if self.language is None and self.datatype is None:
                return unicode(rt)
            else:
                return (unicode(rt), rt.datatype, rt.language)
        return rt

    def md5_term_hash(self):
        d = md5(str(self))
        d.update("L")
        return d.hexdigest()


_XSD_NS = Namespace(u'http://www.w3.org/2001/XMLSchema#')

#Casts a python datatype to a tuple of the lexical value and a datatype URI (or None)
def _castPythonToLiteral(obj):
    for pType,(castFunc,dType) in _PythonToXSD.items():
        if isinstance(obj,pType):
            if castFunc:
                return castFunc(obj),dType
            elif dType:
                return obj,dType
            else:
                return obj,None
    return obj, None # TODO: is this right for the fall through case?

#Mappings from Python types to XSD datatypes and back (burrowed from sparta)
_PythonToXSD = {
    basestring : (None,None),
    float      : (None,_XSD_NS[u'float']),
    int        : (None,_XSD_NS[u'int']),
    long       : (None,_XSD_NS[u'long']),
    bool       : (None,_XSD_NS[u'boolean']),
    date       : (lambda i:i.isoformat(),_XSD_NS[u'date']),
    time       : (lambda i:i.isoformat(),_XSD_NS[u'time']),
    datetime   : (lambda i:i.isoformat(),_XSD_NS[u'dateTime']),
}

def _strToTime(v) :
    return strptime(v,"%H:%M:%S")

def _strToDate(v) :
    tstr = strptime(v,"%Y-%m-%d")
    return date(tstr.tm_year,tstr.tm_mon,tstr.tm_mday)

def _strToDateTime(v) :
    """
    Attempt to cast to datetime, or just return the string (otherwise)
    """
    try:
        tstr = strptime(v,"%Y-%m-%dT%H:%M:%S")
    except:
        try:
            tstr = strptime(v,"%Y-%m-%dT%H:%M:%SZ")
        except:
            try:
                tstr = strptime(v,"%Y-%m-%dT%H:%M:%S%Z")
            except:
                return v

    return datetime(tstr.tm_year,tstr.tm_mon,tstr.tm_mday,tstr.tm_hour,tstr.tm_min,tstr.tm_sec)

XSDToPython = {
    _XSD_NS[u'time']               : _strToTime,
    _XSD_NS[u'date']               : _strToDate,
    _XSD_NS[u'dateTime']           : _strToDateTime,
    _XSD_NS[u'string']             : None,
    _XSD_NS[u'normalizedString']   : None,
    _XSD_NS[u'token']              : None,
    _XSD_NS[u'language']           : None,
    _XSD_NS[u'boolean']            : lambda i:i.lower() in ['1','true'],
    _XSD_NS[u'decimal']            : float,
    _XSD_NS[u'integer']            : long,
    _XSD_NS[u'nonPositiveInteger'] : int,
    _XSD_NS[u'long']               : long,
    _XSD_NS[u'nonNegativeInteger'] : int,
    _XSD_NS[u'negativeInteger']    : int,
    _XSD_NS[u'int']                : long,
    _XSD_NS[u'unsignedLong']       : long,
    _XSD_NS[u'positiveInteger']    : int,
    _XSD_NS[u'short']              : int,
    _XSD_NS[u'unsignedInt']        : long,
    _XSD_NS[u'byte']               : int,
    _XSD_NS[u'unsignedShort']      : int,
    _XSD_NS[u'unsignedByte']       : int,
    _XSD_NS[u'float']              : float,
    _XSD_NS[u'double']             : float,
    _XSD_NS[u'base64Binary']       : base64.decodestring,
    _XSD_NS[u'anyURI']             : None,
}

_toPythonMapping = {}
_toPythonMapping.update(XSDToPython)

def bind(datatype, conversion_function):
    """bind a datatype to a function for converting it into a Python instance."""
    if datatype in _toPythonMapping:
        _logger.warning("datatype '%s' was already bound. Rebinding." % datatype)
    _toPythonMapping[datatype] = conversion_function



def test():
    import doctest
    doctest.testmod()

if __name__ == '__main__':
    test()
