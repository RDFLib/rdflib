from rdflib.URIRef import URIRef


class Namespace(URIRef):

    def __getitem__(self, key, default=None):
        return URIRef(self + key)


# TODO: how on earth did these get here?
def check_subject(s):
    if not (isinstance(s, URIRef) or isinstance(s, BNode)):
        raise SubjectTypeError(s)

def check_predicate(p):
    if not isinstance(p, URIRef):
        raise PredicateTypeError(p)

def check_object(o):
    if not (isinstance(o, URIRef) or \
       isinstance(o, Literal) or \
       isinstance(o, BNode)):
        raise ObjectTypeError(o)


