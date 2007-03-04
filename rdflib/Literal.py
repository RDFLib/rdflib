from sys import version_info, getdefaultencoding
if version_info[0:2] > (2, 2):
    from unicodedata import normalize
else:
    normalize = None

from rdflib.Identifier import Identifier
from rdflib.URIRef import URIRef
from rdflib.Namespace import Namespace
from rdflib.exceptions import Error
from datetime import date,time,datetime
from time import strptime
import base64

XSD_NS = Namespace(u'http://www.w3.org/2001/XMLSchema#')

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
    return obj, None # TODO: is this right for the fall through case?

#Mappings from Python types to XSD datatypes and back (burrowed from sparta)
PythonToXSD = {
    basestring : (None,None),
    float      : (None,XSD_NS[u'float']),
    int        : (None,XSD_NS[u'int']),
    int        : (None,XSD_NS[u'integer']),
    long       : (None,XSD_NS[u'long']),
    bool       : (None,XSD_NS[u'boolean']),
    date       : (lambda i:i.isoformat(),XSD_NS[u'date']),
    time       : (lambda i:i.isoformat(),XSD_NS[u'time']),
    datetime   : (lambda i:i.isoformat(),XSD_NS[u'dateTime']),
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
    XSD_NS[u'time']               : (None,_strToTime),
    XSD_NS[u'date']               : (None,_strToDate),
    XSD_NS[u'dateTime']           : (None,_strToDateTime),
    XSD_NS[u'string']             : (None,None),
    XSD_NS[u'normalizedString']   : (None,None),
    XSD_NS[u'token']              : (None,None),
    XSD_NS[u'language']           : (None,None),
    XSD_NS[u'boolean']            : (None, lambda i:i.lower() in ['1','true']),
    XSD_NS[u'decimal']            : (float,None),
    XSD_NS[u'integer']            : (long ,None),
    XSD_NS[u'int']            : (long ,None),
    XSD_NS[u'nonPositiveInteger'] : (int,None),
    XSD_NS[u'long']               : (long,None),
    XSD_NS[u'nonNegativeInteger'] : (int, None),
    XSD_NS[u'negativeInteger']    : (int, None),
    XSD_NS[u'int']                : (int, None),
    XSD_NS[u'unsignedLong']       : (long, None),
    XSD_NS[u'positiveInteger']    : (int, None),
    XSD_NS[u'short']              : (int, None),
    XSD_NS[u'unsignedInt']        : (long, None),
    XSD_NS[u'byte']               : (int, None),
    XSD_NS[u'unsignedShort']      : (int, None),
    XSD_NS[u'unsignedByte']       : (int, None),
    XSD_NS[u'float']              : (float, None),
    XSD_NS[u'double']             : (float, None),
    XSD_NS[u'base64Binary']       : (base64.decodestring, None),
    XSD_NS[u'anyURI']             : (None,None),
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
        if datatype:
            datatype = URIRef(datatype)
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
    
    def __cmp__(self, other):
        """
        >>> lit2006 = Literal('2006-01-01',datatype=XSD_NS.date)
        >>> lit2006.toPython()
        datetime.date(2006, 1, 1)
        >>> lit2006 < Literal('2007-01-01',datatype=XSD_NS.date)
        True
        >>> oneInt     = Literal(1)
        >>> twoInt     = Literal(2)
        >>> twoInt < oneInt
        False
        >>> try: 
        ...   Literal('1') < Literal(1)
        ... except TypeError: 
        ...   print 'type error'
        type error
        >>> Literal('1') < Literal('1')
        False
        >>> try : Literal(1) < Literal('1')
        ... except TypeError: print 'type error'
        type error
        >>> Literal(1) < Literal(2.0)
        True
        >>> try:  Literal(1) < URIRef('foo')  
        ... except TypeError: print 'type error'
        type error
        >>> Literal(1) < 2.0
        True
        >>> try:  Literal(1) < object  
        ... except TypeError: print 'type error'
        type error
        """
        if other==None:
            raise TypeError("can't compare %s to None"%type(self))            
        elif isinstance(other, Literal):
            #If they are both literals, then their datatypes is the first
            #criteria for comparison
            if self.datatype == None or self.datatype == '' :
                if not(other.datatype == None or other.datatype == '') :
                    #Only one of the two has a datatype - not enough info to compare
                    raise TypeError("can't compare Literals with incompatible datatypes")
                else:
                    #Both don't have datatypes compare their lexical representations
                    return unicode(self).__cmp__(unicode(other))
            else:
                if other.datatype == None or other.datatype == '' :
                    #Only one of the two has a datatype - not enough info to compare
                    raise TypeError("can't compare Literals with incompatible datatypes")
                return cmp(self.toPython(),other.toPython())
        elif isinstance(other, Identifier):
            raise TypeError("can't compare Literals with other Identifiers")
        elif castPythonToLiteral(other)[-1]:
            #I know how to represent 'other' lexically and in Python uniformly
            #Compare natively in python
            return cmp(self.toPython(),other)
        else:
            raise TypeError("Unable to compare %s against %s"%(self,other))
        
    def __ne__(self, other):
        """
        Overriden to ensure property result for comparisons with None via !=.
        Routes all other such != and <> comparisons to __eq__
        
        >>> Literal('') != None
        True
        >>> Literal('2') <> Literal('2')
        False
         
        """
        if other==None:
            return True
        else:
            return not self.__eq__(other)

    def __eq__(self, other):
        """        
        >>> oneInt     = Literal(1)
        >>> oneNoDtype = Literal('1')
        >>> oneInt == oneNoDtype
        False
        >>> Literal("1",XSD_NS[u'string']) == Literal("1",XSD_NS[u'string']) 
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
        if other==None:
            return False
        elif isinstance(other, Literal):
            #If they are both literals, then their datatypes is the first
            #criteria for comparison
            if self.datatype == None or self.datatype == '' :
                if not(other.datatype == None or other.datatype == '') :
                    #Only one of the two has a datatype - not enough info to compare
                    return False
                else:
                    #Both don't have datatypes, check their language tags..
                    if self.language!=other.language:
                        #Different language tags..
                        return False                    
                    else:
                        #Neither has a datatype and their languages don't differ (or neither has a language tag))
                        #compare lexically
                        return unicode(self) == unicode(other)
            else:
                if other.datatype == None or other.datatype == '' :
                    #Only one of the two has a datatype - not enough info to compare
                    return False
                #Is the following case needed? It was causing an
                #inf. loop (in the case where self.toPython()
                #returns self, I think)
                #elif other.datatype in XSDToPython and self.datatype in XSDToPython:
                #    #I know how to cast both Literals into a python scalar - so compare with python 
                #    return self.toPython() == other.toPython()
                elif self.datatype == other.datatype :
                    #The datatypes are the same so we can do a simple lexical comparison
                    return unicode(self) == unicode(other)
                elif self.datatype != other.datatype :
                    #I have no way reliably compare both Literals 
                    return self.toPython() == other.toPython()
        elif isinstance(other, Identifier):
            return False
        elif castPythonToLiteral(other)[-1]:
            #I know how to represent 'other' lexically and in Python uniformly
            castFunc,dType = castPythonToLiteral(other)
            if dType == self.datatype:
                return other == self.toPython()
            else:
                return unicode(self)==unicode(other)
        else:
            return unicode(self)==other

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
        klass, convFunc = XSDToPython.get(self.datatype, (None, None))
        if klass:
            return "%s(%s)"%(klass.__name__, str(self))
        else:
            return """rdflib.Literal('%s', language=%s, datatype=%s)""" % (str(self),repr(self.language), repr(self.datatype))

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

def test():
    import doctest
    doctest.testmod()

if __name__ == '__main__':
    test()
