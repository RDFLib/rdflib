from sys import version_info
if version_info[0:2] > (2, 2):
    from unicodedata import normalize
else:
    normalize = None

from rdflib.Identifier import Identifier
from rdflib.exceptions import Error


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

    def __eq__(self, other):
        if other!=None:
            if super(Literal, self).__cmp__(other)==0:                            
                if isinstance(other, Literal):
                    if self.language==other.language:
                        return 1
                    else:
                        return 0
                else:
                    return 1
            else:
                return 0
        else:
            return 0


