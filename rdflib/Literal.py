from sys import version_info
if version_info[0:2] > (2, 2):
    from unicodedata import normalize
else:
    normalize = None

from rdflib.Identifier import Identifier
from rdflib.exceptions import Error
import types

class Literal(Identifier):
    """

    http://www.w3.org/TR/rdf-concepts/#section-Graph-Literal
    """
    
    def __new__(cls, value, lang='', datatype=''):
        value = unicode(value)        
        return Identifier.__new__(cls, value)        

    def __init__(self, value, lang='', datatype=''):
        if normalize and value:
            if not isinstance(value, unicode):
                value = unicode(value)
            if value != normalize("NFC", value):
                raise Error("value must be in NFC normalized form.")
        
        if datatype:
            lang = ''
        self.language = lang
        self.datatype = datatype
        
    def __add__(self, val):
        s = super(Literal, self).__add__(val)
        return Literal(s, self.language, self.datatype)
    
    def n3(self):
        language = self.language
        datatype = self.datatype
        if language:
            if datatype:
                return '"%s"@%s^^<%s>' % (self, language, datatype)
            else:
                return '"%s"@%s' % (self, language)
        else:
            if datatype:
                return '"%s"^^<%s>' % (self, datatype)
            else:
                return '"%s"' % self

    def yaml(self): #this is wrong, but will do for now till we refactor the datatype stuff... XXX
        return str(self)

    def __eq__(self, other):
        if other==None:
            return 0
        elif isinstance(other, Literal):
            result = self.__cmp__(other)==0
            if result==1:
                if self.language==other.language:
                    return 1
                else:
                    return 0
            else:
                return result
        elif isinstance(other, Identifier):
            return 0
        else:
            return unicode(self)==other

#Some Notes for Improving rdflib datatype support

#the datatype="" value *must* be a URI now... If it's not we raise an
#Exception or a DeprecationWarning; if it is, that's the value of rdf:datatype and the other
#serializations do what? YAML...?

#int, integer, long --? ... Python doesn't have an xsd:integer; not
#sure how xsd:long maps to py:long; xsd:int and py:int on 32 bit
#machine seem compataible
#string
#float
#decimal
#boolean
#time,  date, dateTime, gYearMonth, gYear, gMonthDay, gDay, gMonth, 
#anyURI ... ?
#QName ... ?

# class TypedLiteral(object): pass
# class _IntType(TypedLiteral, types.IntType): pass
# class _LongType(TypedLiteral, types.LongType): pass
# class _FloatType(TypedLiteral,  types.FloatType): pass
# class _UniStrType(TypedLiteral, types.UnicodeType): pass
# class _StrType(TypedLiteral, types.StringType): pass
# class _BoolType(TypedLiteral, types.BooleanType): pass
# class _anyUriType(TypedLiteral,  URIFef): pass
# class _QName(TypedLiteral, types.TupleType): pass #???

# #not sure what to do about this one...
# class _DatetimeType(TypedLiteral, datetime.datetime): pass

# native_type_mapping = {
#     types.StringType: _StrType,
#     types.UnicodeType: _UniStrType,
#     types.IntType: _IntType,
#     types.FloatType: _FloatType,
#     types.LongType: _LongType,
#     #??: _DateTimeType,
#     types.BooleanType: _BoolType}

# def _type_dispatch(type_):
#     return native_type_mapping[type_]

# def literal(a, datatype=None):
#     """
#     I create instances of TypedLiteral.

#     @datattype = instance of URIRef, overrides native type checking (type()).
#     """
#     return _type_dispatch(type(a))

#each kind of serialization/parser that has its own type system -- for now, RDF and YAML, I guess -- has to define a mapping
#from the _fooTypes to its own native representations... often just strings, I guess, but need some operations, too.
