from rdflib import URIRef, BNode, Literal
from rdflib.exceptions import SubjectTypeError, PredicateTypeError, ObjectTypeError


class Triple(tuple):
    def __new__(cls, s, p, o):
        return tuple.__new__(cls, (s, p, o)) 

    def __init__(self, s, p, o, c=None, check=True):
        self.context = c
        if check:
            if s and not (isinstance(s, URIRef) or isinstance(s, BNode)):
                raise SubjectTypeError(s)

            if p and not isinstance(p, URIRef):
                raise PredicateTypeError(p)

            if o and not (isinstance(o, URIRef) or \
                          isinstance(o, Literal) or \
                          isinstance(o, BNode)):
                raise ObjectTypeError(o)

    def isStatement(self):
        s, p, o = self
        if s and p and o:
            return True
        else:
            return False
            
