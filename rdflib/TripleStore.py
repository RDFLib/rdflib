from __future__ import generators

from rdflib.Resource import Resource

from rdflib.constants import FIRST, REST, NIL
from rdflib.util import first

from rdflib.store.backends.InMemoryBackend import InMemoryBackend
from rdflib.store.Concurrent import Concurrent

from rdflib.syntax.LoadSave import LoadSave

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


class TripleStore(LoadSave):
    """
    TODO: Both the TypeCheck mixin and AbstractTripleStore are needed
    to describe the TripleStore interface. ... where to document
    the TripleStore "interface"?
    """
    
    def __init__(self, backend=None):
        super(TripleStore, self).__init__()
        self.backend = backend or Concurrent(InMemoryBackend())

        
    def add(self, (subject, predicate, object)):
        check_subject(subject)
        check_predicate(predicate)
        check_object(object)
        self.backend.add((subject, predicate, object))

    def remove(self, (subject, predicate, object)):
        check_subject(subject)
        check_predicate(predicate)
        check_object(object)

        self.backend.remove((subject, predicate, object))

    def triples(self, (subject, predicate, object)):
        if subject:
            check_subject(subject)
        if predicate:
            check_predicate(predicate)
        if object:
            check_object(object)
        for triple in self.backend.triples((subject, predicate, object)):
            yield triple
        
    def destroy(self):
        for triple in self.triples((None, None, None)):
            s, p, o = triple
            self.remove((s, p, o))
        return
    #eventually: raise NotImplementedError("Subclass must implement")

    def resources(self, (subject, predicate, object)):
        d = {}
        for s, p, o in self.triples((subject, predicate, object)):
            if not s in d:
                d[s] = r = Resource(s, self)
                for subject in r.subjects:
                    d[subject] = r                        
        for item in d.itervalues():
            yield item

    def items(self, list):
        while list:
            item = first(self.objects(list, FIRST))
            if item:
                yield item
            list = first(self.objects(list, REST))

    def __getitem__(self, subject):
        return Resource(subject, self)

    def __iter__(self):
        return self.triples((None, None, None))

    def __contains__(self, (subject, predicate, object)):
        for triple in self.triples((subject, predicate, object)):
            return 1
        return 0

    def __len__(self):
        return len(list(self))
    
    def __eq__(self, other):
        # Note: this is not a test of isomorphism, but rather exact
        # equality.
        if not other or len(self)!=len(other):
            return 0
        for s, p, o in self:
            if not (s, p, o) in other:
                return 0
        for s, p, o in other:
            if not (s, p, o) in self:
                return 0
        return 1

    def subjects(self, predicate=None, object=None):
        for s, p, o in self.triples((None, predicate, object)):
            yield s

    def predicates(self, subject=None, object=None):
        for s, p, o in self.triples((subject, None, object)):
            yield p

    def objects(self, subject=None, predicate=None):
        for s, p, o in self.triples((subject, predicate, None)):
            yield o

    def subject_predicates(self, object=None):
        for s, p, o in self.triples((None, None, object)):
            yield s, p
            
    def subject_objects(self, predicate=None):
        for s, p, o in self.triples((None, predicate, None)):
            yield s, o
        
    def predicate_objects(self, subject=None):
        for s, p, o in self.triples((subject, None, None)):
            yield p, o

    def transitive_objects(self, subject, property, remember=None):
        if remember==None:
            remember = {}
        if not subject in remember:
            remember[subject] = 1
            yield subject
            for object in self.objects(subject, property):
                for o in self.transitive_objects(object, property, remember):
                    yield o

    def transitive_subjects(self, predicate, object, remember=None):
        if remember==None:
            remember = {}
        if not object in remember:
            remember[object] = 1
            yield object
            for subject in self.subjects(predicate, object):
                for s in self.transitive_subjects(predicate, subject, remember):
                    yield s

    def remove_triples(self, (subject, predicate, object)):
        for s, p, o in self.triples((subject, predicate, object)):
            self.remove((s, p, o))

    def capabilities(self): pass
    """
    We want some kind of introspection mechanism for triple
    stores. That is, each triple store hasA special (perhaps
    optimized) triple store in which is stored assertions about the
    capacities of the main triple store. By keeping these capabilities
    assertions in a separate store, we can implement store.destroy()
    easily. It also -- contexts notwithstanding -- makes it less
    likely that we'll have assertional clashes with real users.
    """
