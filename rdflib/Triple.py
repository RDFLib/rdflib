
class Triple(tuple):
    def __new__(cls, s, p, o, c=None):
        t = tuple.__new__(cls, (s, p, o))        
        t.context = c
        return t

    # TODO:
    def check_subject(self, s):
        if not (isinstance(s, URIRef) or isinstance(s, BNode)):
            raise SubjectTypeError(s)

    def check_predicate(self, p):
        if not isinstance(p, URIRef):
            raise PredicateTypeError(p)

    def check_object(self, o):
        if not (isinstance(o, URIRef) or \
           isinstance(o, Literal) or \
           isinstance(o, BNode)):
            raise ObjectTypeError(o)

