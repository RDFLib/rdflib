from __future__ import generators

import tempfile, shutil, os
from threading import Lock

from urlparse import urlparse, urljoin, urldefrag
from urllib import pathname2url, url2pathname

from rdflib import Triple
from rdflib import URIRef, BNode, Literal
from rdflib import RDF, RDFS

from rdflib.URLInputSource import URLInputSource
from rdflib.util import first

from rdflib.syntax.serializer import SerializationDispatcher
from rdflib.syntax.parser import ParserDispatcher

from rdflib.exceptions import SubjectTypeError
from rdflib.exceptions import PredicateTypeError
from rdflib.exceptions import ObjectTypeError
from rdflib.exceptions import ContextTypeError


Any = None

class Graph(object):
    """
    Abstract Class
    """
    
    def __init__(self, backend=None):
        super(Graph, self).__init__()
        if backend is None:
            if 0:
                from rdflib.backends.InMemoryBackend import InMemoryBackend
                backend = InMemoryBackend()
                self.default_context = None
            elif 0:
                from rdflib.backends.IOInMemoryContextBackend import IOInMemoryContextBackend
                backend = IOInMemoryContextBackend()
                self.default_context = BNode()                
            else:
                from rdflib.backends.SleepyCatBackend import SleepyCatBackend
                backend = SleepyCatBackend()
                backend.open("tmp")
                self.default_context = BNode()
        self.backend = backend
        self.ns_prefix_map = {}
        self.prefix_ns_map = {}
        self.prefix_mapping("rdf", "http://www.w3.org/1999/02/22-rdf-syntax-ns#")
        self.prefix_mapping("rdfs", "http://www.w3.org/2000/01/rdf-schema#")
        self.serialize = SerializationDispatcher(self)
        self.parse = ParserDispatcher(self)                
        self.__save_lock = Lock()
        
    def open(self, path):
        if hasattr(self.backend, "open"):
            self.backend.open(path)

    def close(self):
        if hasattr(self.backend, "close"):
            self.backend.close()

    def absolutize(self, uri, defrag=1):
        # TODO: make base settable
        base = urljoin("file:", pathname2url(os.getcwd()))
        uri = urljoin("%s/" % base, uri)
        if defrag:
            uri, frag = urldefrag(uri)            
        return URIRef(uri)
    
    def tmp_load(self, location, format="xml", publicID=None):
        # TODO: remove dup, not sure which version is close to the one we want yet though
        location = self.absolutize(location)
        for id in self.subjects(SOURCE, location):
            context = self.get_context(id)
            self.remove_context(id)
        id = BNode()
        context = self.get_context(id)
        context.add((id, TYPE, CONTEXT))
        context.add((id, SOURCE, location))
        context.load(location, format, publicID)
        return context

    def load(self, location, format="xml", publicID=None):
        source = URLInputSource(self.absolutize(location))
        if publicID:
            source.setPublicId(publicID)
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

            if hasattr(shutil,"move"):
                shutil.move(name, path)
            else:
                shutil.copy(name, path)
                os.remove(name)

        finally:
            self.__save_lock.release()

    def prefix_mapping(self, prefix, namespace):
        map = self.ns_prefix_map    
        map[namespace] = prefix

    def label(self, subject, default=''):
        for s, p, o in self.triples(Triple(subject, RDFS.label, None)):
            return o
        return default

    def comment(self, subject, default=''):
        for s, p, o in self.triples(Triple(subject, RDFS.comment, None)):
            return o
        return default

    def items(self, list):
        while list:
            item = first(self.objects(list, RDF.first))
            if item:
                yield item
            list = first(self.objects(list, RDF.rest))

    def __iter__(self):
        return self.triples((None, None, None))

    def __contains__(self, triple):
        for triple in self.triples(triple):
            return 1
        return 0

    def __len__(self):
        return self.backend.__len__()
    
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

    def __iadd__(self, other):
        for triple in other:
            self.backend.add(triple) # TODO: context
        return self

    def __isub__(self, other):
        for triple in other:
            self.backend.remove(triple) 
        return self

    def subjects(self, predicate=None, object=None):
        for s, p, o in self.triples(Triple(None, predicate, object)):
            yield s

    def predicates(self, subject=None, object=None):
        for s, p, o in self.triples(Triple(subject, None, object)):
            yield p

    def objects(self, subject=None, predicate=None):
        for s, p, o in self.triples(Triple(subject, predicate, None)):
            yield o

    def subject_predicates(self, object=None):
        for s, p, o in self.triples(Triple(None, None, object)):
            yield s, p
            
    def subject_objects(self, predicate=None):
        for s, p, o in self.triples(Triple(None, predicate, None)):
            yield s, o
        
    def predicate_objects(self, subject=None):
        for s, p, o in self.triples(Triple(subject, None, None)):
            yield p, o

    def get_context(self, identifier):
        assert isinstance(identifier, URIRef) or \
               isinstance(identifier, BNode)
        return Context(self.backend, identifier)

    def remove_context(self, identifier):
        self.backend.remove_context(identifier)
        
    def add(self, triple, context=None):
        if not isinstance(triple, Triple):
            s, p, o = triple
            triple = Triple(s, p, o)
        triple.check_statement()
        triple.context = context or self.default_context
        self.backend.add(triple)

    def remove(self, triple):
        if not isinstance(triple, Triple):
            s, p, o = triple
            triple = Triple(s, p, o)
        triple.check_pattern()
        self.backend.remove(triple)

    def triples(self, triple):
        if not isinstance(triple, Triple):
            s, p, o = triple
            triple = Triple(s, p, o)
        triple.check_pattern()            
        for t in self.backend.triples(triple):
            yield t
        
    def contexts(self): # TODO: triple=None??
        for context in self.backend.contexts():
            yield context


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


class ContextBackend(object):

    def __init__(self, information_store, identifier):
        super(ContextBackend, self).__init__()
        self.information_store = information_store
        self.identifier = identifier

    def add(self, triple):
        triple.context = self.identifier
        self.information_store.add(triple)
        
    def remove(self, triple):
        triple.context = self.identifier        
        self.information_store.remove(triple)
        
    def triples(self, triple):
        triple.context = self.identifier        
        return self.information_store.triples(triple)

    def __len__(self):
        # TODO: backends should support len
        i = 0
        for triple in self.triples((None, None, None)):
            i += 1
        return i
    

class Context(Graph):
    def __init__(self, information_store, identifier):
        super(Context, self).__init__(None, ContextBackend(information_store, identifier))
        self.identifier = identifier

