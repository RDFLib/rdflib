from rdflib.TripleStore import TripleStore
from rdflib.Store import Store
from rdflib.Store import check_subject, check_predicate, check_object
from rdflib.backends.SleepyCatBackend import SleepyCatBackend


from rdflib.exceptions import ContextTypeError

from rdflib.URIRef import URIRef
from rdflib.BNode import BNode

def check_context(c):
    if not (isinstance(c, URIRef) or \
       isinstance(c, BNode)):
        raise ContextTypeError(c)

class Context(object):

    def __init__(self, backend, identifier):
        super(Context, self).__init__()
        self.backend = backend
        self.identifier = identifier

    def add(self, (s, p, o)):
        #context = context or self.identifier
        context = self.identifier
        self.backend.add((s, p, o), context)
        
    def remove(self, (s, p, o)):
        #context = context or self.identifier
        context = self.identifier
        self.backend.remove((s, p, o), context)
        
    def triples(self, triple):
        #context = context or self.identifier
        context = self.identifier
        for triple in self.backend.triples(triple, context):
            yield triple

class InformationStore(Store):
    def __init__(self, path=None, backend=None):
        backend = backend or SleepyCatBackend()
        super(InformationStore, self).__init__(backend)
        self.__context = None
        if path:
            self.open(path)
        
    def __get_context(self):
        if self.__context==None:            
            self.__context = BNode()
        return self.__context

    def __set_context(self, context):
        self.__context = context

    # Declare context as a property
    context = property(__get_context, __set_context)

    def get_context(self, identifier):
        check_context(identifier)        
        return TripleStore(Context(self.backend, identifier))

    def add(self, (subject, predicate, object), context=None):
        context = context or self.context        
        check_subject(subject)
        check_predicate(predicate)
        check_object(object)
        check_context(context)
        self.backend.add((subject, predicate, object), context)

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

        
    def contexts(self, triple=None):
        for context in self.backend.contexts(triple):
            yield context
            
