from __future__ import generators

from rdflib import Triple, URIRef, BNode, Literal, RDF, RDFS
from rdflib.util import first

from rdflib import plugin

from rdflib.backends import Backend
from rdflib.syntax.serializer import SerializationDispatcher
from rdflib.syntax.parser import ParserDispatcher


class Graph(object):
    """
    An RDF Graph.  The constructor accepts one argument, the 'backend'
    that will be used to store the graph data (see the 'backends'
    package for backends currently shipped with rdflib).

    Backends can be context-aware or unaware.  Unaware backends take
    up (some) less space in the backend but cannot support features
    that require context, such as true merging/demerging of sub-graphs
    and provenance.
    """
    
    def __init__(self, backend=None):
        super(Graph, self).__init__()
        if backend is None:
            backend = plugin.get('default', 'backend')()
        elif not isinstance(backend, Backend):
            # TODO: error handling
            backend = plugin.get(backend, 'backend')()
        self.__backend = backend
        self.__parser = None
        self.__serializer = None

        self.__ns_prefix_map = {}
        self.__prefix_ns_map = {}

        self.prefix_mapping("rdf", "http://www.w3.org/1999/02/22-rdf-syntax-ns#")
        self.prefix_mapping("rdfs", "http://www.w3.org/2000/01/rdf-schema#")

    def _get_parser(self):
        if self.__parser is None:
            self.__parser = ParserDispatcher(self)
        return self.__parser

    parser = property(_get_parser)

    def _get_serializer(self):
        if self.__serializer is None:
            self.__serializer = SerializationDispatcher(self)
        return self.__serializer

    serializer = property(_get_serializer)

    # these two properties and their accesors are to be b/w
    # compatible while still alowing graphs to calculate their state.
    # By default tries to defer all state to the backend, otherwise
    # degenerates into the old behavior.

    def getNSPrefixMap(self):
        if hasattr(self.__backend, 'getNSPrefixMap'):
            return self.__backend.getNSPrefixMap()
        return self.__ns_prefix_map

    ns_prefix_map = property(getNSPrefixMap)


    def getPrefixNSMap(self):
        if hasattr(self.__backend, 'getPrefixNSMap'):
            return self.__backend.getPrefixNSMap()
        return self.__prefix_ns_map

    prefix_ns_map = property(getPrefixNSMap)

    def open(self, path):
        """ Open the graph backend.  Might be necessary for backends
        that require opening a connection to a database or acquiring some resource."""
        if hasattr(self.__backend, "open"):
            self.__backend.open(path)

    def close(self):
        """ Close the graph backend.  Might be necessary for backends
        that require closing a connection to a database or releasing some resource."""
        if hasattr(self.__backend, "close"):
            self.__backend.close()

    def add(self, triple, context=None):
        """ Add a triple, optionally provide a context.  A 3-tuple or
        rdflib.Triple can be provided.  Context must be a URIRef.  If
        no context is provides, triple is added to the default
        context."""
        if not isinstance(triple, Triple):
            s, p, o = triple
            triple = Triple(s, p, o)
        triple.check_statement()
        if context:
            triple.context = context
        self.__backend.add(triple)

    def remove(self, triple):
        """ Remove a triple from the graph.  If the triple does not
        provide a context attribute, removes the triple from all
        contexts."""
        if not isinstance(triple, Triple):
            s, p, o = triple
            triple = Triple(s, p, o)
        triple.check_pattern()
        self.__backend.remove(triple)

    def triples(self, triple):
        """ Generator over the triple store.  Returns triples that
        match the given triple pattern.  If triple pattern does not
        provide a context, all contexts will be searched."""
        if not isinstance(triple, Triple):
            s, p, o = triple
            triple = Triple(s, p, o)
        triple.check_pattern()            
        for t in self.__backend.triples(triple):
            yield t
        
    def contexts(self): # TODO: triple=None??
        """ Generator over all contexts in the graph. """
        for context in self.__backend.contexts():
            yield context

    def prefix_mapping(self, prefix, namespace):
        map = self.ns_prefix_map    
        map[namespace] = prefix

    def label(self, subject, default=''):
        """ Queries for the RDFS.label of the subject, returns default if no label exists. """
        for s, p, o in self.triples(Triple(subject, RDFS.label, None)):
            return o
        return default

    def comment(self, subject, default=''):
        """ Queries for the RDFS.comment of the subject, returns default if no comment exists. """
        for s, p, o in self.triples(Triple(subject, RDFS.comment, None)):
            return o
        return default

    def items(self, list):
        """ """
        while list:
            item = first(self.objects(list, RDF.first))
            if item:
                yield item
            list = first(self.objects(list, RDF.rest))

    def __iter__(self):
        """ Iterates over all triples in the store. """
        return self.triples((None, None, None))

    def __contains__(self, triple):
        """ Support for 'triple in graph' syntax.  Not very efficient. """
        for triple in self.triples(triple):
            return 1
        return 0

    def __len__(self):
        """ Returns the number of triples in the graph. """
        return self.__backend.__len__()
    
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
            self.__backend.add(triple) # TODO: context
        return self

    def __isub__(self, other):
        for triple in other:
            self.__backend.remove(triple) 
        return self

    def subjects(self, predicate=None, object=None):
        """ A generator of subjects with the given predicate and object. """
        for s, p, o in self.triples(Triple(None, predicate, object)):
            yield s

    def predicates(self, subject=None, object=None):
        """ A generator of predicates with the given subject and object. """        
        for s, p, o in self.triples(Triple(subject, None, object)):
            yield p

    def objects(self, subject=None, predicate=None):
        """ A generator of objects with the given subject and predicate. """                
        for s, p, o in self.triples(Triple(subject, predicate, None)):
            yield o

    def subject_predicates(self, object=None):
        """ A generator of (subject, predicate) tuples for the given object """
        for s, p, o in self.triples(Triple(None, None, object)):
            yield s, p
            
    def subject_objects(self, predicate=None):
        """ A generator of (subject, object) tuples for the given predicate """        
        for s, p, o in self.triples(Triple(None, predicate, None)):
            yield s, o
        
    def predicate_objects(self, subject=None):
        """ A generator of (predicate, object) tuples for the given subject """                
        for s, p, o in self.triples(Triple(subject, None, None)):
            yield p, o

    def get_context(self, identifier):
        """ Returns a Context graph for the given identifier, which
        must be a URIRef or BNode."""
        assert isinstance(identifier, URIRef) or \
               isinstance(identifier, BNode)
        return Context(self.__backend, identifier)

    def remove_context(self, identifier):
        """ Removes the given context from the graph. """
        self.__backend.remove_context(identifier)
        
    def transitive_objects(self, subject, property, remember=None):
        """ """
        if remember==None:
            remember = {}
        if not subject in remember:
            remember[subject] = 1
            yield subject
            for object in self.objects(subject, property):
                for o in self.transitive_objects(object, property, remember):
                    yield o

    def transitive_subjects(self, predicate, object, remember=None):
        """ """
        if remember==None:
            remember = {}
        if not object in remember:
            remember[object] = 1
            yield object
            for subject in self.subjects(predicate, object):
                for s in self.transitive_subjects(predicate, subject, remember):
                    yield s

    def load(self, location, publicID=None, format="xml"):
        """ for b/w compat. """
        return self.parser.load(location, publicID, format)

    def save(self, location, format="xml"):
        return self.serializer.serialize(destination=location, format=format) 

    def parse(self, source, publicID=None, format="xml"):
        return self.parser.parse(source=source, publicID=publicID, format=format) 

    def serialize(self, destination=None, format="xml"):
        return self.serializer.serialize(destination=destination, format=format) 



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
        super(Context, self).__init__(ContextBackend(information_store, identifier))
        self.identifier = identifier

