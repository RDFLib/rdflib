from rdflib import URIRef, BNode, Literal
from rdflib.exceptions import SubjectTypeError, PredicateTypeError, ObjectTypeError


class Triple(object):
    __slots__ = ["subject", "predicate", "object", "context"]
    
    def __init__(self, s, p, o, c=None):
        self.subject = s
        self.predicate = p
        self.object = o
        self.context = c

    def __iter__(self):
        yield self.subject
        yield self.predicate
        yield self.object

    def __getitem__(self, index):
        # TODO: optimize
        # index may be slice object see:
        #   http://docs.python.org/ref/sequence-types.html
        return (self.subject, self.predicate, self.object)[index]
        
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
