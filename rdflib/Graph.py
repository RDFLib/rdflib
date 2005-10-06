from __future__ import generators

from rdflib import URIRef, BNode, Literal, Namespace, RDF, RDFS

from rdflib.util import check_statement, check_pattern, check_context
from rdflib.util import check_subject, check_predicate, check_object

from rdflib import plugin, exceptions

from rdflib.backends import Backend
from rdflib.syntax.serializer import Serializer
from rdflib.syntax.parsers import Parser

from rdflib.syntax.NamespaceManager import NamespaceManager

from rdflib.URLInputSource import URLInputSource
from xml.sax.xmlreader import InputSource
from xml.sax.saxutils import prepare_input_source

from rdflib.interfaces import implements, IGraph

import logging


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

    implements(IGraph)

    def __init__(self, backend='default'):
        super(Graph, self).__init__()
        if not isinstance(backend, Backend):
            # TODO: error handling
            backend = plugin.get(backend, Backend)()
        self.__backend = backend
        self.__namespace_manager = None

    def __get_backend(self):
        return self.__backend
    backend = property(__get_backend)

    def _get_namespace_manager(self):
        if self.__namespace_manager is None:
            self.__namespace_manager = NamespaceManager(self)
        return self.__namespace_manager
    def _set_namespace_manager(self, nm):
        self.__namespace_manager = nm
    namespace_manager = property(_get_namespace_manager, _set_namespace_manager)

    def _get_context_aware(self):
        return self.__backend.context_aware
    context_aware = property(_get_context_aware)

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

    def add(self, (s, p, o), context=None, quoted=False):
        """ Add a triple, optionally provide a context.  A 3-tuple or
        rdflib.Triple can be provided.  Context must be a URIRef.  If
        no context is provides, triple is added to the default
        context."""
        check_statement((s, p, o))
        if self.context_aware:
            if context:
                check_context(context)
            self.__backend.add((s, p, o), context, quoted)
        else:
            assert quoted==False
            self.__backend.add((s, p, o))

    def remove(self, (s, p, o), context=None):
        """ Remove a triple from the graph.  If the triple does not
        provide a context attribute, removes the triple from all
        contexts."""

        check_pattern((s, p, o))
        if self.context_aware:
            if context:
                check_context(context)
            self.__backend.remove((s, p, o), context)
        else:
            self.__backend.remove((s, p, o))

    def triples(self, (s, p, o), context=None):
        """ Generator over the triple store.  Returns triples that
        match the given triple pattern.  If triple pattern does not
        provide a context, all contexts will be searched."""
        check_pattern((s, p, o))
        if self.context_aware:
            if context:
                check_context(context)
            for t in self.__backend.triples((s, p, o), context):
                yield t
        else:
            for t in self.__backend.triples((s, p, o)):
                yield t


    def contexts(self, triple=None):
        """ Generator over all contexts in the graph. If triple is specified, a generator over all contexts the triple is in."""
        assert self.context_aware, "Graph must be context aware to use this method"
        for context in self.__backend.contexts(triple):
            yield context

    def value(self, subject, predicate=RDF.value, object=None, default=None, any=False):
        """ Get a value for a subject/predicate, predicate/object, or
        subject/object pair -- exactly one of subject, predicate,
        object must be None. Useful if one knows that there may only
        be one value.

        It is one of those situations that occur a lot, hence this
        'macro' like utility

        Parameters:
        -----------
        subject, predicate, object  -- exactly one must be None
        default -- value to be returned if no values found
        any -- if True:
                 return any value in the case there is more than one
               else:
                 raise UniquenessError
        """
        retval = default
        if object is None:
            assert subject is not None
            assert predicate is not None
            values = self.objects(subject, predicate)
        if subject is None:
            assert predicate is not None
            assert object is not None
            values = self.subjects(predicate, object)
        if predicate is None:
            assert subject is not None
            assert object is not None
            values = self.predicates(subject, object)

        try:
            retval = values.next()
        except StopIteration, e:
            retval = default
        else:
            if any is False:
                try:
                    next = values.next()
                    raise exceptions.UniquenessError([retval, next] + list(values))
                except StopIteration, e:
                    pass
        return retval

    def label(self, subject, default=''):
        """ Queries for the RDFS.label of the subject, returns default if no label exists. """
        if subject is None:
            return default
        return self.value(subject, RDFS.label, default=default, any=True)

    def comment(self, subject, default=''):
        """ Queries for the RDFS.comment of the subject, returns default if no comment exists. """
        if subject is None:
            return default
        return self.value(subject, RDFS.comment, default=default, any=True)

    def items(self, list):
        """Generator over all items in the resource specified by list (an RDF collection)"""
        while list:
            item = self.value(list, RDF.first)
            if item:
                yield item
            list = self.value(list, RDF.rest)

    def __iter__(self):
        """ Iterates over all triples in the store. """
        return self.triples((None, None, None))

    def __contains__(self, triple):
        """ Support for 'triple in graph' syntax. """
        for triple in self.triples(triple):
            return 1
        return 0

    def __len__(self, context=None):
        """ Returns the number of triples in the graph. If context is specified then the number of triples in the context is returned instead."""
        if self.context_aware:
            return self.__backend.__len__(context)
        else:
            return self.__backend.__len__()

    def __eq__(self, other):
        """ Test if Graph is exactly equal to Graph other."""
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
        """ Add all triples in Graph other to Graph."""
        for triple in other:
            self.__backend.add(triple) # TODO: context
        return self

    def __isub__(self, other):
        """ Subtract all triples in Graph other from Graph."""
        for triple in other:
            self.__backend.remove(triple)
        return self

    def subjects(self, predicate=None, object=None):
        """ A generator of subjects with the given predicate and object. """
        for s, p, o in self.triples((None, predicate, object)):
            yield s

    def predicates(self, subject=None, object=None):
        """ A generator of predicates with the given subject and object. """
        for s, p, o in self.triples((subject, None, object)):
            yield p

    def objects(self, subject=None, predicate=None):
        """ A generator of objects with the given subject and predicate. """
        for s, p, o in self.triples((subject, predicate, None)):
            yield o

    def subject_predicates(self, object=None):
        """ A generator of (subject, predicate) tuples for the given object """
        for s, p, o in self.triples((None, None, object)):
            yield s, p

    def subject_objects(self, predicate=None):
        """ A generator of (subject, object) tuples for the given predicate """
        for s, p, o in self.triples((None, predicate, None)):
            yield s, o

    def predicate_objects(self, subject=None):
        """ A generator of (predicate, object) tuples for the given subject """
        for s, p, o in self.triples((subject, None, None)):
            yield p, o

    def get_context(self, identifier):
        """ Returns a Context graph for the given identifier, which
        must be a URIRef or BNode."""
        assert isinstance(identifier, URIRef) or \
               isinstance(identifier, BNode)
        return Context(self, identifier)

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
        """ for b/w compat. See parse."""
        return self.parse(location, publicID, format)

    def save(self, location, format="xml", base=None, encoding=None):
        """ for b/x compat. See serialize."""
        return self.serialize(location, format, base, encoding)

    def context_id(self, uri):
        uri = uri.split("#", 1)[0]
        return URIRef("%s#context" % uri)

    def prepare_input_source(self, source, publicID=None):
        if isinstance(source, InputSource):
            input_source = source
        else:
            if hasattr(source, "read") and not isinstance(source, Namespace): # we need to make sure it's not an instance of Namespace since Namespace instances have a read attr
                input_source = prepare_input_source(source)
            else:
                location = self.absolutize(source)
                input_source = URLInputSource(location)
                publicID = publicID or location
        if publicID:
            input_source.setPublicId(publicID)
        id = input_source.getPublicId()
        if id is None:
            logging.info("no publicID set for source. Using '' for publicID.")
            input_source.setPublicId("")
        return input_source

    def parse(self, source, publicID=None, format="xml"):
        """ Parse source into Graph. If Graph is context-aware it'll get loaded into it's own context (sub graph). Format defaults to xml (AKA rdf/xml). The publicID argument is for specifying the logical URI for the case that it's different from the physical source URI. Returns the context into which the source was parsed."""
        source = self.prepare_input_source(source, publicID)
        if self.context_aware:
            id = self.context_id(URIRef(source.getPublicId()))
            self.remove_context(id)
            context = self.get_context(id)
        else:
            context = self
        parser = plugin.get(format, Parser)()
        parser.parse(source, context)
        return context

        return parser.parse(source, publicID, format)

    def serialize(self, destination=None, format="xml", base=None, encoding=None):
        """ Serialize the Graph to destination. If destination is None serialize method returns the serialization as a string. Format defaults to xml (AKA rdf/xml)."""
        serializer = plugin.get(format, Serializer)(self)
        return serializer.serialize(destination, base=base, encoding=encoding)

    def seq(self, subject) :
        """
        Check if subject is an rdf:Seq. If yes, it returns a Seq
        class instance, None otherwise.
        """
        if (subject, RDF.type, RDF.Seq) in self :
            return Seq(self, subject)
        else :
            return None

    def absolutize(self, uri, defrag=1):
        """ Will turn uri into an absolute URI if it's not one already. """
        return self.namespace_manager.absolutize(uri, defrag)

    def bind(self, prefix, namespace, override=True):
        """Bind prefix to namespace. If override is True will bind namespace to given prefix if namespace was already bound to a different prefix."""
        return self.namespace_manager.bind(prefix, namespace, override=override)

    def namespaces(self):
        """Generator over all the prefix, namespace tuples.
        """
        for prefix, namespace in self.namespace_manager.namespaces():
            yield prefix, namespace


class Context(Graph):
    def __init__(self, graph, identifier):
        super(Context, self).__init__(backend=graph.backend)
        self.graph = graph
        self.namespace_manager = graph.namespace_manager
        self.identifier = identifier

    def _get_context_aware(self):
        return False
    context_aware = property(_get_context_aware)


    def add(self, triple, context=None, quoted=False): # TODO: test if we need context=None arg
        #assert context is None or context is self.identifier
	#This is commented out so that the N3 parser can go through
	#the context it's being loaded into to add triples to the
	#other contexts
        self.graph.add(triple, self.identifier, quoted)

    def remove(self, triple, context=None):
        assert context is None
        self.backend.remove(triple, self.identifier)

    def triples(self, triple, context=None):
        assert context is None
        return self.backend.triples(triple, self.identifier)

    def bind(self, prefix, namespace, override=True):
        return self.graph.bind(prefix, namespace, override)

    def __len__(self, context=None):
        assert context is None
        return self.backend.__len__(self.identifier)


class Seq(object):
    """
    Wrapper around an RDF Seq resource. It implements a container
    type in Python with the order of the items returned
    corresponding to the Seq content. It is based on the natural
    ordering of the predicate names _1, _2, _3, etc, which is the
    'implementation' of a sequence in RDF terms.
    """
    _list  = {}
    def __init__(self, graph, subject):
        """
        The graph which contains the sequence. The subject is
        simply the subject which is supposed to be a Seq.

        Parameters:
        -----------
        graph: the graph containing the Seq
        subject: the subject of a Seq. Note that the init does not
        check whether this is a Seq, this is done in whoever
        creates this instance!
        """

        _list = self._list = list()
        LI_INDEX = RDF.RDFNS["_"]
        for (p, o) in graph.predicate_objects(subject):
            if p.startswith(LI_INDEX): #!= RDF.Seq: #
                _list.append(("%s" % p, o))
        # here is the trick: the predicates are _1, _2, _3, etc. Ie,
        # by sorting the keys we have what we want!
        _list.sort()

    def __iter__(self):
        """Generator over the index, item tuples in the Seq"""
        for index, item in self._list:
            yield item

    def __len__(self):
        """ Returns the length of the Seq."""
        return len(self._list)

    def __getitem__(self, index):
        """ Returns the item given by index from the Seq."""
        index, item = self._list.__getitem__(index)
        return item
