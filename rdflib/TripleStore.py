from __future__ import generators

import tempfile, shutil, os
from threading import Lock

from urlparse import urlparse, urljoin, urldefrag
from urllib import pathname2url, url2pathname

from rdflib.URLInputSource import URLInputSource

from rdflib.URIRef import URIRef
from rdflib.BNode import BNode
from rdflib.Literal import Literal

from rdflib.constants import FIRST, REST, NIL
from rdflib.util import first

from rdflib.backends.InMemoryBackend import InMemoryBackend
from rdflib.backends.Concurrent import Concurrent

from rdflib.syntax.serializer import SerializationDispatcher
from rdflib.syntax.parser import ParserDispatcher

from rdflib.syntax.LoadSave import LoadSave
from rdflib.model.schema import Schema

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



class Context(object):

    def __init__(self, backend, identifier):
        super(Context, self).__init__()
        self.backend = backend
        self.identifier = identifier

    def add(self, (s, p, o), context=None):
        context = context or self.identifier
        self.backend.add((s, p, o), context)
        
    def remove(self, (s, p, o)):
        context = context or self.identifier        
        self.backend.remove((s, p, o), context)
        
    def triples(self, triple):
        context = context or self.identifier        
        for triple in self.backend.triples(triple, context):
            yield triple


class TripleStore(LoadSave, Schema):
    """
    TODO: Both the TypeCheck mixin and AbstractTripleStore are needed
    to describe the TripleStore interface. ... where to document
    the TripleStore "interface"?
    """
    
    def __init__(self, backend=None):
        super(TripleStore, self).__init__()
        self.backend = backend or Concurrent(InMemoryBackend())
        self.ns_prefix_map = {}
        self.prefix_ns_map = {}
        self.prefix_mapping("rdf", "http://www.w3.org/1999/02/22-rdf-syntax-ns#")
        self.prefix_mapping("rdfs", "http://www.w3.org/2000/01/rdf-schema#")
        self.serialize = SerializationDispatcher(self)
        self.parse = ParserDispatcher(self)                
        self.__context = None
        self.__save_lock = Lock()
        
    def load(self, location, format="xml"):
        cwd = urljoin("file:", pathname2url(os.getcwd()))
        location = urljoin("%s/" % cwd, location)
        location, frag = urldefrag(location)            
        scheme, netloc, path, params, query, fragment = urlparse(location)
        if netloc=="":
            path = url2pathname(path)
            # If local and it does not exist then create one.
            if not os.access(path, os.F_OK): # TODO: is this equiv to os.path.exists?
                self.save(path)
        source = URLInputSource(location)                    
        self.parse(source, format=format)

    def save(self, location, format="xml"):
        try:
            self.__save_lock.acquire()

            scheme, netloc, path, params, query, fragment = urlparse(location)
            if netloc!="":
                print "WARNING: not saving as location is not a local file reference"
                return

            name = tempfile.mktemp()            
            stream = open(name, 'wb')
            self.serialize(format=format, stream=stream)            
            stream.close()

            shutil.move(name, path)

        finally:
            self.__save_lock.release()

    def prefix_mapping(self, prefix, namespace):
        map = self.ns_prefix_map    
        map[namespace] = prefix

    def __get_context(self):
        if self.__context==None:            
            self.__context = BNode()
        return self.__context

    def __set_context(self, context):
        self.__context = context

    # Declare context as a property of AbstractInformationStore
    context = property(__get_context, __set_context)

    def get_context(self, identifier):
        return TripleStore(Context(self.backend), identifier)

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

    def items(self, list):
        while list:
            item = first(self.objects(list, FIRST))
            if item:
                yield item
            list = first(self.objects(list, REST))

    def __iter__(self):
        return self.triples((None, None, None))

    def __contains__(self, (subject, predicate, object)):
        for triple in self.triples((subject, predicate, object)):
            return 1
        return 0

    def __len__(self):
        # TODO: backends should support len
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
