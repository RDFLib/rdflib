from rdflib.term import URIRef
from rdflib.term import Identifier

class QName(Identifier):
    __slots__ = ("localname", "prefix")
    def __new__(cls,value):
        try:
            inst = unicode.__new__(cls,value)
        except UnicodeDecodeError:
            inst = unicode.__new__(cls,value,'utf-8')

        inst.prefix,inst.localname = value.split(':')
        return inst

class QNamePrefix(Identifier):
    def __init__(self,prefix):
        super(QNamePrefix,self).__init__(prefix)

