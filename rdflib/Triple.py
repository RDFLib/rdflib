from rdflib import URIRef, BNode, Literal
from rdflib.exceptions import SubjectTypeError, PredicateTypeError, ObjectTypeError


class Triple(tuple):
    def __new__(cls, s, p, o, c=None):
        return tuple.__new__(cls, (s, p, o)) 

    def __init__(self, s, p, o, c=None):
        self.context = c

    def check_statement(self):
        s, p, o = self
        if not (isinstance(s, URIRef) or isinstance(s, BNode)):
            raise SubjectTypeError(s)

        if not isinstance(p, URIRef):
            raise PredicateTypeError(p)

        if not (isinstance(o, URIRef) or \
                isinstance(o, Literal) or \
                isinstance(o, BNode)):
            raise ObjectTypeError(o)

    def check_pattern(self):
        s, p, o = self        
        if s and not (isinstance(s, URIRef) or isinstance(s, BNode)):
            raise SubjectTypeError(s)

        if p and not isinstance(p, URIRef):
            raise PredicateTypeError(p)

        if o and not (isinstance(o, URIRef) or \
                      isinstance(o, Literal) or \
                      isinstance(o, BNode)):
            raise ObjectTypeError(o)
