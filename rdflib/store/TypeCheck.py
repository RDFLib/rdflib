from __future__ import generators

from rdflib.URIRef import URIRef
from rdflib.BNode import BNode
from rdflib.Literal import Literal

from rdflib.exceptions import SubjectTypeError
from rdflib.exceptions import PredicateTypeError
from rdflib.exceptions import ObjectTypeError
from rdflib.exceptions import ContextTypeError

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

def check_context(c):
    if not (isinstance(c, URIRef) or \
       isinstance(c, BNode)):
        raise ContextTypeError(c)

class TypeCheck(object):
    
    def add(self, (subject, predicate, object)):
        check_subject(subject)
        check_predicate(predicate)
        check_object(object)
        super(TypeCheck, self).add((subject, predicate, object))

    def remove(self, (subject, predicate, object)):
        check_subject(subject)
        check_predicate(predicate)
        check_object(object)
        super(TypeCheck, self).remove((subject, predicate, object))

    def triples(self, (subject, predicate, object)):
        if subject:
            check_subject(subject)
        if predicate:
            check_predicate(predicate)
        if object:
            check_object(object)
            
        for triple in super(TypeCheck, self).triples((subject, predicate, object)):
            yield triple
