from rdflib.Identifier import Identifier
try:
    from hashlib import md5
except ImportError:
    from md5 import md5    

class Variable(Identifier):
    """
    """
    __slots__ = ()
    def __new__(cls, value):
        return Identifier.__new__(cls, value)

    def n3(self):
        return "?%s" % self

    def __reduce__(self):
        return (Variable, (unicode(self),))

    def md5_term_hash(self):
        d = md5(str(self))
        d.update("V")
        return d.hexdigest()