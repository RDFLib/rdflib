from __future__ import generators

from rdflib import Triple, URIRef, BNode, Literal, RDF, RDFS

from rdflib.syntax.serializer import SerializationDispatcher
from rdflib.syntax.parser import ParserDispatcher

from rdflib.URLInputSource import URLInputSource
from rdflib.util import first


from urlparse import urljoin, urldefrag
from urllib import pathname2url, url2pathname

Any = None


class Graph(object):
    """
    Abstract Class
    """
    
    def __init__(self, backend=None):
        super(Graph, self).__init__()
        if backend is None:
            from rdflib.backends.IOMemory import IOMemory
            backend = IOMemory()
        self.__backend = backend
        self.__parse_dispatcher = ParserDispatcher(self)                        
        self.__serialization_dispatcher = SerializationDispatcher(self)

        self.default_context = BNode() # TODO: have some static default context?        
        
        self.ns_prefix_map = {}
        self.prefix_ns_map = {}
        self.prefix_mapping("rdf", "http://www.w3.org/1999/02/22-rdf-syntax-ns#")
        self.prefix_mapping("rdfs", "http://www.w3.org/2000/01/rdf-schema#")


    def open(self, path):
        if hasattr(self.__backend, "open"):
            self.__backend.open(path)

    def close(self):
        if hasattr(self.__backend, "close"):
            self.__backend.close()

    def _absolutize(self, uri, defrag=1):
        base = urljoin("file:", pathname2url(os.getcwd()))
        uri = urljoin("%s/" % base, uri)
        if defrag:
            uri, frag = urldefrag(uri)            
        return URIRef(uri)

    def _context_id(self, uri):
        uri = uri.split("#", 1)[0]
        return URIRef("%s#context" % uri)
    
    def load(self, location, publicID=None, format="xml"):
        location = self._absolutize(location)
        id = self._context_id(publicID or location)
        self.remove_context(id)
        context = self.get_context(id)
        context.add((id, RDF.type, CONTEXT))
        context.add((id, SOURCE, location))
        context.parse(source=location, publicID=publicID, format=format)
        return context

    def parse(self, source, publicID=None, format="xml"):
        return self.__parser_dispatcher(source=source, publicID=publicID, format=format)

    def save(self, location, format="xml"):
        return self.serialize(destination=location, format=format)

    def serialize(self, destination=None, format="xml"):
        return self.__serialization_dispatcher(destination=destination, format=format)            

    def add(self, triple, context=None):
        if not isinstance(triple, Triple):
            s, p, o = triple
            triple = Triple(s, p, o)
        triple.check_statement()
        triple.context = context or self.default_context
        self.__backend.add(triple)

    def remove(self, triple):
        if not isinstance(triple, Triple):
            s, p, o = triple
            triple = Triple(s, p, o)
        triple.check_pattern()
        self.__backend.remove(triple)

    def triples(self, triple):
        if not isinstance(triple, Triple):
            s, p, o = triple
            triple = Triple(s, p, o)
        triple.check_pattern()            
        for t in self.__backend.triples(triple):
            yield t
        
    def contexts(self): # TODO: triple=None??
        for context in self.__backend.contexts():
            yield context

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
        return Context(self.__backend, identifier)

    def remove_context(self, identifier):
        self.__backend.remove_context(identifier)
        
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

