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

    __slots__ = ("language", "datatype")

    def __getstate__(self):
        return (None, dict(language=self.language,
                           datatype=self.datatype))

    def __setstate__(self, arg):
        _, d = arg
        self.language = d['language']
        self.datatype = d['datatype']
    
    def __new__(cls, value, lang='', datatype=''):
        value = unicode(value)        
        return Identifier.__new__(cls, value)        

    def __getstate__(self):
	return (None, dict(language=self.language, datatype=self.datatype))

    def __setstate__(self, arg):
	_, d = arg
	self.language = d["language"]
	self.datatype = d["datatype"]

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
        encoded = self.encode('unicode-escape')
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

