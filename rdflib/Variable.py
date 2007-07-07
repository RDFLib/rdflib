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
        if value[0]=='?':
            value=value[1:]
        return unicode.__new__(cls, value)

    def __repr__(self):
        return self.n3()

    def n3(self):
        return "?%s" % self

    def __reduce__(self):
        return (Variable, (unicode(self),))

    def md5_term_hash(self):
        d = md5(str(self))
        d.update("V")
        return d.hexdigest()