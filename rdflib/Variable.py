from rdflib.Identifier import Identifier


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
