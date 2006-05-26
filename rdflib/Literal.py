from sys import version_info
if version_info[0:2] > (2, 2):
    from unicodedata import normalize
else:
    normalize = None

from rdflib.Identifier import Identifier
from rdflib.exceptions import Error
from datetime import date,time,datetime
import base64

XSD_NS = u'http://www.w3.org/2001/XMLSchema#'

#Casts a python datatype to a tuple of the lexical value and a datatype URI (or None)
def castPythonToLiteral(obj):
    for pType,(castFunc,dType) in PythonToXSD.items():
        if isinstance(obj,pType):
            if castFunc:
                return castFunc(obj),dType
            elif dType:
                return obj,dType
            else:
                return obj,None

#Mappings from Python types to XSD datatypes and back (burrowed from sparta)
PythonToXSD = {
    basestring : (None,None),
    float      : (None,XSD_NS+u'float'),
    int        : (None,XSD_NS+u'int'),
    long       : (None,XSD_NS+u'long'),    
    bool       : (None,XSD_NS+u'boolean'),
    date       : (lambda i:i.isoformat(),XSD_NS+u'date'),
    time       : (lambda i:i.isoformat(),XSD_NS+u'time'),
    datetime   : (lambda i:i.isoformat(),XSD_NS+u'dateTime'),
}

XSDToPython = {  
    XSD_NS+u'string'             : (None,None),
    XSD_NS+u'normalizedString'   : (None,None),
    XSD_NS+u'token'              : (None,None),
    XSD_NS+u'language'           : (None,None),
    XSD_NS+u'boolean'            : (None, lambda i:i.lower() in ['1','true']),
    XSD_NS+u'decimal'            : (float,None), 
    XSD_NS+u'integer'            : (long ,None),
    XSD_NS+u'nonPositiveInteger' : (int,None),
    XSD_NS+u'long'               : (long,None),
    XSD_NS+u'nonNegativeInteger' : (int, None),
    XSD_NS+u'negativeInteger'    : (int, None),
    XSD_NS+u'int'                : (int, None),
    XSD_NS+u'unsignedLong'       : (long, None),
    XSD_NS+u'positiveInteger'    : (int, None),
    XSD_NS+u'short'              : (int, None),
    XSD_NS+u'unsignedInt'        : (long, None),
    XSD_NS+u'byte'               : (int, None),
    XSD_NS+u'unsignedShort'      : (int, None),
    XSD_NS+u'unsignedByte'       : (int, None),
    XSD_NS+u'float'              : (float, None),
    XSD_NS+u'double'             : (float, None),
    XSD_NS+u'base64Binary'       : (base64.decodestring, None),
    XSD_NS+u'anyURI'             : (None,None),
}

class Literal(Identifier):
    """

    http://www.w3.org/TR/rdf-concepts/#section-Graph-Literal
    """

    __slots__ = ("language", "datatype")

    def __new__(cls, value, lang=None, datatype=None):
        #if normalize and value:
        #    if value != normalize("NFC", value):
        #        raise Error("value must be in NFC normalized form.")
        if datatype:
            lang = None
        else:
            value,datatype = castPythonToLiteral(value)
            if datatype:
                lang = None
        try:
            inst = unicode.__new__(cls,value)
        except UnicodeDecodeError:
            inst = unicode.__new__(cls,value,'utf-8')
                
        inst.language = lang
        inst.datatype = datatype
        return inst

    def __reduce__(self):
        return (Literal, (unicode(self), self.language, self.datatype),)

#    
#    def __getnewargs__(self):
#        return (unicode(self), self.language, self.datatype)

    def __getstate__(self):
        return (None, dict(language=self.language, datatype=self.datatype))

    def __setstate__(self, arg):
        _, d = arg
        self.language = d["language"]
        self.datatype = d["datatype"]
        
    def __add__(self, val):
        s = super(Literal, self).__add__(val)
        return Literal(s, self.language, self.datatype)
    
    def __eq__(self, other):
        if other==None:
            return False
        elif isinstance(other, Literal):
            result = self.__cmp__(other)==False
            if result==True:
                if self.datatype == None or self.datatype == '' :
                    if not(other.datatype == None or other.datatype == '') :
                        return False
                else:
                    if other.datatype == None or other.datatype == '' :
                        return False
                    elif self.datatype != other.datatype :
                        return False
                if self.language!=other.language:
                    return False
                return True
            else:
                return result
        elif isinstance(other, Identifier):
            return False
        else:
            return unicode(self)==other

    def n3(self):
        language = self.language
        datatype = self.datatype
        encoded = self.encode('unicode-escape').replace('\\', '\\\\').replace('"','\\"')
        if language:
            if datatype:
                return '"%s"@%s^^<%s>' % (encoded, language, datatype)
            else:
                return '"%s"@%s' % (encoded, language)
        else:
            if datatype:
                return '"%s"^^<%s>' % (encoded, datatype)
            else:
                return '"%s"' % encoded

    def __repr__(self):
        klass,convFunc = XSDToPython.get(self.datatype,(None,None))
        if klass:
            return "%s(%s)"%(klass.__name__,str(self))
        else:
            return """rdflib.Literal('%s',language=%s,datatype=%s)""" % (unicode(self),repr(self.language), repr(self.datatype))

    def toPython(self):
        """
        Returns an appropriate python datatype derived from this RDF Literal
        """
        klass,convFunc = XSDToPython.get(self.datatype,(None,None))
        rt = self
        if convFunc:
            rt = convFunc(rt)
        if klass:
            rt = klass(rt)
        return rt