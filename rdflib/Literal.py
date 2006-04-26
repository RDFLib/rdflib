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

    def __new__(cls, value, lang=None, datatype=None):
        #if normalize and value:
        #    if value != normalize("NFC", value):
        #        raise Error("value must be in NFC normalized form.")
        try:
            inst = unicode.__new__(cls,value)
        except UnicodeDecodeError:
            inst = unicode.__new__(cls,value,'utf-8')

        if datatype:
            lang = None
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

    def __repr__(self):
        return """<Literal language=%s datatype=%s value=%s>""" % (repr(self.language), repr(self.datatype), unicode(self))
