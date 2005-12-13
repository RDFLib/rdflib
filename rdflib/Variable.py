from rdflib.Identifier import Identifier
from cPickle import dumps

class Variable(Identifier):
    """ 
    """ 
    __slots__ = ()
    def __new__(cls, value):
        return Identifier.__new__(cls, value)
        
    def n3(self):
        return "?%s" % self

    def to_bits(self):
        return dumps((6, (unicode(self),)))
