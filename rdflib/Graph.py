from __future__ import generators

from rdflib import URIRef, BNode, Literal, Namespace
from rdflib import RDF, RDFS

from rdflib.Node import Node

from rdflib import plugin, exceptions

from rdflib.store import Store

from rdflib.syntax.serializer import Serializer
from rdflib.syntax.parsers import Parser
from rdflib.syntax.NamespaceManager import NamespaceManager

from rdflib.URLInputSource import URLInputSource

from xml.sax.xmlreader import InputSource
from xml.sax.saxutils import prepare_input_source

import logging


class Graph(Node):
    """
    An RDF Graph.  The constructor accepts one argument, the 'store'
    that will be used to store the graph data (see the 'store'
    package for stores currently shipped with rdflib).

    Stores can be context-aware or unaware.  Unaware stores take up
    (some) less space but cannot support features that require
    context, such as true merging/demerging of sub-graphs and
    provenance.
    
    The Graph constructor can take an identifier which identifies the Graph
    by name.  If none is given, the graph is assigned a BNode for it's identifier.
    For more on named graphs, see: http://www.w3.org/2004/03/trix/
    
    Ontology for __str__ provenance terms:
    
    @prefix rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
    @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
    @prefix : <http://rdflib.net/store/> .
    @prefix rdfg: <http://www.w3.org/2004/03/trix/rdfg-1/>.
    @prefix owl: <http://www.w3.org/2002/07/owl#>.
    @prefix log: <http://www.w3.org/2000/10/swap/log#>.
    @prefix xsd: <http://www.w3.org/2001/XMLSchema#>.
    
    :Store a owl:Class;
        rdfs:subClassOf <http://xmlns.com/wordnet/1.6/Electronic_database>;
        rdfs:subClassOf
            [a owl:Restriction;
             owl:onProperty rdfs:label;
             owl:allValuesFrom [a owl:DataRange;
                                owl:oneOf ("IOMemory"
                                           "Sleepcat"
                                           "MySQL"
                                           "Redland"
                                           "REGEXMatching"
                                           "ZODB"
                                           "AuditableStorage"
                                           "Memory")]
            ].

    :ConjunctiveGraph a owl:Class;
        rdfs:subClassOf rdfg:Graph;
        rdfs:label "The top-level graph within the store - the concatenation of all the contexts within."
        rdfs:seeAlso <http://rdflib.net/rdf_store/#ConjunctiveGraph>.
            
    :DefaultContext a owl:Class;
        rdfs:subClassOf rdfg:Graph;
        rdfs:label "The default subgraph of a conjunctive graph".
    
    
    :identifier a owl:Datatypeproperty;
        rdfs:label "The store-associated identifier of the formula. ".
        rdfs:domain log:Formula
        rdfs:range xsd:anyURI;
        
    :storage a owl:ObjectProperty;
        rdfs:domain [
            a owl:Class;
            owl:unionOf (log:Formula rdfg:Graph :ConjunctiveGraph)
        ];
        rdfs:range :Store.
        
    :default_context a owl:FunctionalProperty;
        rdfs:label "The default context for a conjunctive graph";
        rdfs:domain :ConjunctiveGraph;
        rdfs:range :DefaultContext.
        
        
    {?cg a :ConjunctiveGraph;:storage ?store}
      => {?cg owl:sameAs ?store}.
      
    {?subGraph rdfg:subGraphOf ?cg;a :DefaultContext}
      => {?cg a :ConjunctiveGraph;:default_context ?subGraphOf} .
    """

    def __init__(self, store='default', identifier=None):
        super(Graph, self).__init__()
        self.__identifier = identifier or BNode() 
        if not isinstance(store, Store):
            # TODO: error handling
            store = plugin.get(store, Store)()
        self.__store = store
        self.__namespace_manager = None
        self.context_aware = False
        self.formula_aware = False

    def __get_store(self):
        return self.__store
    store = property(__get_store)

    def __get_identifier(self):
        return self.__identifier
    identifier = property(__get_identifier)

    def _get_namespace_manager(self):
        if self.__namespace_manager is None:
            self.__namespace_manager = NamespaceManager(self)
        return self.__namespace_manager
    def _set_namespace_manager(self, nm):
        self.__namespace_manager = nm
    namespace_manager = property(_get_namespace_manager, _set_namespace_manager)

    def __repr__(self):
        return "<Graph identifier=%s (%s)>" % (self.identifier, type(self))

    def __str__(self):
        if isinstance(self.identifier,URIRef):
            return "%s a rdfg:Graph;rdflib:storage [a rdflibStore [a rdflib:Store;rdfs:label '%s']]."%(self.identifier.n3(),self.store.__class__.__name__)
        else:
            return "[a rdfg:Graph;rdflib:storage [a rdflib:Store;rdfs:label '%s']]."%(self.store.__class__.__name__)

    def destroy(self, configuration):
        """
        For stores that support this functionality, it destroyes the store identified by the given configuration
        """
        if hasattr(self.__store, "destroy"):
            self.__store.destroy(configuration)

    #Transactional interfaces (optional)
    def commit(self):
        """
        Commits active transactions
        """
        if hasattr(self.__store, "commit"):
            self.__store.commit()
    
    def rollback(self):
        """
        Rollback active transactions
        """
        if hasattr(self.__store, "rollback"):
            self.__store.rollback()

    def open(self, configuration, create=True):
        """ Open the graph store.  Might be necessary for stores
        that require opening a connection to a database or acquiring some resource."""
        if hasattr(self.__store, "open"):
            self.__store.open(configuration, create)

    def close(self):
        """ Close the graph store.  Might be necessary for stores
        that require closing a connection to a database or releasing some resource."""
        if hasattr(self.__store, "close"):
            self.__store.close()

    def add(self, (s, p, o)):
        """ Add a triple, optionally provide a context.  A 3-tuple or
        rdflib.Triple can be provided.  Context must be a URIRef.  If
        no context is provides, triple is added to the default
        context."""
        self.__store.add((s, p, o), self, quoted=False)

    def remove(self, (s, p, o)):
        """ Remove a triple from the graph.  If the triple does not
        provide a context attribute, removes the triple from all
        contexts."""

        self.__store.remove((s, p, o), context=self)

    def triples(self, (s, p, o)):
        """ Generator over the triple store.  Returns triples that
        match the given triple pattern.  If triple pattern does not
        provide a context, all contexts will be searched."""
        for (s, p, o), cg in self.__store.triples((s, p, o), context=self):
            yield (s, p, o)

    def __len__(self):
        """ Returns the number of triples in the graph. If context is specified then the number of triples in the context is returned instead."""
        return self.__store.__len__(context=self)

    def __iter__(self):
        """ Iterates over all triples in the store. """
        return self.triples((None, None, None))

    def __contains__(self, triple):
        """ Support for 'triple in graph' syntax. """
        for triple in self.triples(triple):
            return 1
        return 0

    def __hash__(self):
        return hash(self.identifier)
    def __cmp__(self, other):
        if other is None:
            return -1
        elif isinstance(other, Graph):
            return self.identifier.__cmp__(other.identifier)
        else:
            #Note if None is considered equivalent to owl:Nothing
            #Then perhaps a graph with length 0 should be considered
            #equivalent to None (if compared to it)?
            return 1


    def __iadd__(self, other):
        """ Add all triples in Graph other to Graph."""
        for triple in other:
            self.add(triple) 
        return self

    def __isub__(self, other):
        """ Subtract all triples in Graph other from Graph."""
        for triple in other:
            self.remove(triple)
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

    def value(self, subject=None, predicate=RDF.value, object=None, default=None, any=False):
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
                    msg = "While trying to find a value for (%s, %s, %s) the following multiple values where found:\n" % (subject, predicate, object)
                    for (s, p, o), contexts in self.store.triples((subject, predicate, object), None):
                        msg += "(%s, %s, %s)\n (contexts: %s)\n" % (s, p, o, list(contexts))
                    raise exceptions.UniquenessError(msg)
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

    def serialize(self, destination=None, format="xml", base=None, encoding=None):
        """ Serialize the Graph to destination. If destination is None serialize method returns the serialization as a string. Format defaults to xml (AKA rdf/xml)."""
        serializer = plugin.get(format, Serializer)(self)
        return serializer.serialize(destination, base=base, encoding=encoding)

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
        parser = plugin.get(format, Parser)()
        parser.parse(source, self)
        return self

    def load(self, source, publicID=None, format="xml"):
        self.parse(source, publicID, format)

    def n3(self):
        """return an n3 identifier for the Graph"""
        return "[%s]" % self.identifier.n3()

    def __reduce__(self):
        return (Graph, (self.store, self.identifier,))

#     def __getstate__(self):
#         return False

    def isomorphic(self, other):
        # TODO: this is only an approximation.
        if len(self)!=len(other):
            return False
        for s, p, o in self:
            if not isinstance(s, BNode) and not isinstance(o, BNode):
                if not (s, p, o) in other:
                    return False
        for s, p, o in other:
            if not isinstance(s, BNode) and not isinstance(o, BNode):
                if not (s, p, o) in self:
                    return False
        # TODO: very well could be a false positive at this point yet.
        return True


class ConjunctiveGraph(Graph): # AKA ConjunctiveGraph

    def __init__(self, store='default'):
        super(ConjunctiveGraph, self).__init__(store)
        assert self.store.context_aware, "ConjunctiveGraph must be backed by a context aware store."
        self.context_aware = True
        self.default_context = Graph(store=self.store, identifier=BNode())

    def __str__(self):
        return "[a rdflib:DefaultContext] rdfg:subGraphOf [a rdfg:Graph;rdflib:storage [a rdflib:Store;rdfs:label '%s']]"%(self.store.__class__.__name__)

    def add(self, (s, p, o), context=None):
        """"A conjunctive graph adds to its default context."""
        self.store.add((s, p, o), context=context or self.default_context, quoted=False)
    
    def remove(self, (s, p, o), context=None):
        """A conjunctive graph removes from all its contexts."""
        self.store.remove((s, p, o), context)

    def triples(self, (s, p, o), context=None):
        """An iterator over all the triples in the entire conjunctive graph."""
        for (s, p, o), cg in self.store.triples((s, p, o), context):
            yield (s, p, o), cg

    def subjects(self, predicate=None, object=None):
        """ A generator of subjects with the given predicate and object. """
        for (s, p, o), cg in self.triples((None, predicate, object)):
            yield s

    def predicates(self, subject=None, object=None):
        """ A generator of predicates with the given subject and object. """
        for (s, p, o), cg in self.triples((subject, None, object)):
            yield p

    def objects(self, subject=None, predicate=None):
        """ A generator of objects with the given subject and predicate. """
        for (s, p, o), cg in self.triples((subject, predicate, None)):
            yield o

    def subject_predicates(self, object=None):
        """ A generator of (subject, predicate) tuples for the given object """
        for (s, p, o), cg in self.triples((None, None, object)):
            yield s, p

    def subject_objects(self, predicate=None):
        """ A generator of (subject, object) tuples for the given predicate """
        for (s, p, o), cg in self.triples((None, predicate, None)):
            yield s, o

    def predicate_objects(self, subject=None):
        """ A generator of (predicate, object) tuples for the given subject """
        for (s, p, o), cg in self.triples((subject, None, None)):
            yield p, o

    def __len__(self, context=None):
        """Returns the number of triples in the entire conjunctive graph."""
        return self.store.__len__(context)

    def contexts(self, triple=None):
        """ 
        Iterator over all contexts in the graph. If triple is
        specified, a generator over all contexts the triple is in.
        """
        for context in self.store.contexts(triple):
            yield context

    def remove_context(self, context):
        """ Removes the given context from the graph. """
        self.store.remove((None, None, None), context)

    def context_id(self, uri, context_id=None):
        """ URI#context """
        uri = uri.split("#", 1)[0]
        if context_id is None:
            context_id = "#context"
        return URIRef(context_id, base=uri)

    def parse(self, source, publicID=None, format="xml"):
        """ 
        Parse source into Graph into it's own context (sub
        graph). Format defaults to xml (AKA rdf/xml). The publicID
        argument is for specifying the logical URI for the case that
        it's different from the physical source URI. Returns the
        context into which the source was parsed. In the case of n3 it
        returns the root context.
        """
        source = self.prepare_input_source(source, publicID)
        id = self.context_id(self.absolutize(source.getPublicId()))
        context = Graph(store=self.store, identifier=id)
        context.remove((None, None, None))
        context.parse(source, publicID=publicID, format=format)
        return context

    def __reduce__(self):
        return (ConjunctiveGraph, (self.store, self.identifier,))


class QuotedGraph(Graph):

    def __init__(self, store, identifier):
        super(QuotedGraph, self).__init__(store, identifier)

    def add(self, triple): 
        self.store.add(triple, self, quoted=True)

    def n3(self):
        """return an n3 identifier for the Graph"""
        return "{%s}" % self.identifier.n3()
    
    def __str__(self):
        if isinstance(self.identifier,URIRef):
            return "{this rdflib.identifier %s;rdflib:storage [a rdflib:Store;rdfs:label '%s']}"%(self.identifier.n3(),self.store.__class__.__name__)
        else:
            return "{this rdflib:identifier %s;rdflib:storage [a rdflib:Store;rdfs:label '%s']}"%(self.identifier.n3(),self.store.__class__.__name__)

    def __reduce__(self):
        return (QuotedGraph, (self.store, self.identifier,))


class GraphValue(QuotedGraph):
    def __init__(self, store, identifier=None, graph=None):
        if graph is not None:
            assert identifier is None
            np = NodePickler(self.store)
            import md5
            identifier = md5.new()
            s = list(graph.triples((None, None, None)))
            s.sort()
            for t in s:
                identifier.update("^".join((np.dumps(i) for i in t)))
            identifier = URIRef("data:%s" % identifier.hexdigest())
            super(GraphValue, self).__init__(store, identifier)            
            for t in graph:
                store.add(t, context=self)
        else:
            super(GraphValue, self).__init__(store, identifier)            


    def add(self, triple):
        raise Exception("not mutable")

    def remove(self, triple):
        raise Exception("not mutable")

    def __hash__(self):
        return hash(self.identifier)

    def __cmp__(self, other):
        return self.identifier.__cmp__(other.identifier)

    def __reduce__(self):
        return (GraphValue, (self.store, self.identifier,))


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
        # Ah... TODO: this needs to sort by integer... not string value.
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

class BackwardCompatGraph(ConjunctiveGraph):
    def __init__(self, backend='default'):    
        super(BackwardCompatGraph, self).__init__(store=backend)        

    def __get_backend(self):
        return self.store
    backend = property(__get_backend)

    def add(self, (s, p, o), context=None):
        """"A conjunctive graph adds to its default context."""
        if context is not None:
            c = self.get_context(context)
            assert c.identifier == context, "%s != %s" % (c.identifier, context)
        else:
            c = self.default_context
        self.store.add((s, p, o), context=c, quoted=False)
    
    def remove(self, (s, p, o), context=None):
        """A conjunctive graph removes from all its contexts."""
        if context is not None:
            context = self.get_context(context)
        self.store.remove((s, p, o), context)

    def triples(self, (s, p, o), context=None):
        """An iterator over all the triples in the entire conjunctive graph."""
        if context is not None:
            c = self.get_context(context)
            assert c.identifier == context
        else:
            c = None
        for (s, p, o), cg in self.store.triples((s, p, o), c):
            yield (s, p, o)

    def __len__(self, context=None):
        """Returns the number of triples in the entire conjunctive graph."""
        if context is not None:
            context = self.get_context(context)
        return self.store.__len__(context)

    def get_context(self, identifier, quoted=False):
        """ Returns a Context graph for the given identifier, which
        must be a URIRef or BNode."""
        assert isinstance(identifier, URIRef) or \
               isinstance(identifier, BNode), type(identifier)
        if quoted:
            assert False
            return QuotedGraph(self.store, identifier)
            #return QuotedGraph(self.store, Graph(store=self.store, identifier=identifier))
        else:
            return Graph(self.store, identifier)
            #return Graph(self.store, Graph(store=self.store, identifier=identifier))

    def remove_context(self, context):
        """ Removes the given context from the graph. """
        self.store.remove((None, None, None), self.get_context(context))

    def contexts(self, triple=None):
        """ 
        Iterator over all contexts in the graph. If triple is
        specified, a generator over all contexts the triple is in.
        """
        for context in self.store.contexts(triple):
            yield context.identifier

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

    def __reduce__(self):
        return (BackwardCompatGraph, (self.store, self.identifier,))
