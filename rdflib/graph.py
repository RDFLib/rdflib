"""Instantiating Graphs with default store (IOMemory) and default identifier 
(a BNode):

    >>> g = Graph()
    >>> g.store.__class__
    <class 'rdflib.plugins.memory.IOMemory'>
    >>> g.identifier.__class__
    <class 'rdflib.term.BNode'>

Instantiating Graphs with a specific kind of store (IOMemory) and a default 
identifier (a BNode):

Other store kinds: Sleepycat, MySQL, SQLite

    >>> store = plugin.get('IOMemory', Store)()
    >>> store.__class__.__name__
    'IOMemory'
    >>> graph = Graph(store)
    >>> graph.store.__class__
    <class 'rdflib.plugins.memory.IOMemory'>

Instantiating Graphs with Sleepycat store and an identifier - 
<http://rdflib.net>:

    >>> g = Graph('IOMemory', URIRef("http://rdflib.net"))
    >>> g.identifier
    rdflib.term.URIRef('http://rdflib.net')
    >>> str(g)
    "<http://rdflib.net> a rdfg:Graph;rdflib:storage [a rdflib:Store;rdfs:label 'IOMemory']."

Creating a ConjunctiveGraph - The top level container for all named Graphs 
in a 'database':

    >>> g = ConjunctiveGraph()
    >>> str(g.default_context)
    "[a rdfg:Graph;rdflib:storage [a rdflib:Store;rdfs:label 'IOMemory']]."

Adding / removing reified triples to Graph and iterating over it directly or 
via triple pattern:
    
    >>> g = Graph('IOMemory')
    >>> statementId = BNode()
    >>> print len(g)
    0
    >>> g.add((statementId, RDF.type, RDF.Statement))
    >>> g.add((statementId, RDF.subject, URIRef('http://rdflib.net/store/ConjunctiveGraph')))
    >>> g.add((statementId, RDF.predicate, RDFS.label))
    >>> g.add((statementId, RDF.object, Literal("Conjunctive Graph")))
    >>> print len(g)
    4
    >>> for s, p, o in g:
    ...     print type(s)
    ...
    <class 'rdflib.term.BNode'>
    <class 'rdflib.term.BNode'>
    <class 'rdflib.term.BNode'>
    <class 'rdflib.term.BNode'>
    
    >>> for s, p, o in g.triples((None, RDF.object, None)):
    ...     print o
    ...
    Conjunctive Graph
    >>> g.remove((statementId, RDF.type, RDF.Statement))
    >>> print len(g)
    3

None terms in calls to triple can be thought of as "open variables".

Graph Aggregation - ConjunctiveGraphs and ReadOnlyGraphAggregate within 
the same store:
    
    >>> store = plugin.get('IOMemory', Store)()
    >>> g1 = Graph(store)
    >>> g2 = Graph(store)
    >>> g3 = Graph(store)
    >>> stmt1 = BNode()
    >>> stmt2 = BNode()
    >>> stmt3 = BNode()
    >>> g1.add((stmt1, RDF.type, RDF.Statement))
    >>> g1.add((stmt1, RDF.subject, URIRef('http://rdflib.net/store/ConjunctiveGraph')))
    >>> g1.add((stmt1, RDF.predicate, RDFS.label))
    >>> g1.add((stmt1, RDF.object, Literal("Conjunctive Graph")))
    >>> g2.add((stmt2, RDF.type, RDF.Statement))
    >>> g2.add((stmt2, RDF.subject, URIRef('http://rdflib.net/store/ConjunctiveGraph')))
    >>> g2.add((stmt2, RDF.predicate, RDF.type))
    >>> g2.add((stmt2, RDF.object, RDFS.Class))
    >>> g3.add((stmt3, RDF.type, RDF.Statement))
    >>> g3.add((stmt3, RDF.subject, URIRef('http://rdflib.net/store/ConjunctiveGraph')))
    >>> g3.add((stmt3, RDF.predicate, RDFS.comment))
    >>> g3.add((stmt3, RDF.object, Literal("The top-level aggregate graph - The sum of all named graphs within a Store")))
    >>> len(list(ConjunctiveGraph(store).subjects(RDF.type, RDF.Statement)))
    3
    >>> len(list(ReadOnlyGraphAggregate([g1,g2]).subjects(RDF.type, RDF.Statement)))
    2

ConjunctiveGraphs have a 'quads' method which returns quads instead of 
triples, where the fourth item is the Graph (or subclass thereof) instance 
in which the triple was asserted:
    
    >>> uniqueGraphNames = set([graph.identifier for s, p, o, graph in ConjunctiveGraph(store).quads((None, RDF.predicate, None))])
    >>> len(uniqueGraphNames)
    3
    >>> unionGraph = ReadOnlyGraphAggregate([g1, g2])
    >>> uniqueGraphNames = set([graph.identifier for s, p, o, graph in unionGraph.quads((None, RDF.predicate, None))])
    >>> len(uniqueGraphNames)
    2
     
Parsing N3 from StringIO

    >>> g2 = Graph()
    >>> src = '''
    ... @prefix rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
    ... @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
    ... [ a rdf:Statement ;
    ...   rdf:subject <http://rdflib.net/store#ConjunctiveGraph>;
    ...   rdf:predicate rdfs:label;
    ...   rdf:object "Conjunctive Graph" ] .
    ... '''
    >>> g2 = g2.parse(StringIO(src), format='n3')
    >>> print len(g2)
    4

Using Namespace class:

    >>> RDFLib = Namespace('http://rdflib.net')
    >>> RDFLib.ConjunctiveGraph
    rdflib.term.URIRef('http://rdflib.netConjunctiveGraph')
    >>> RDFLib['Graph']
    rdflib.term.URIRef('http://rdflib.netGraph')

"""

from __future__ import generators

import logging
_logger = logging.getLogger(__name__)

#import md5
import random
import warnings

try:
    from hashlib import md5
except ImportError:
    from md5 import md5    

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO
def describe(terms,bindings,graph):
    """ 
    Default DESCRIBE returns all incomming and outgoing statements about the given terms 
    """
    from rdflib.sparql.sparqlOperators import getValue
    g=Graph()
    terms=[getValue(i)(bindings) for i in terms]
    for s,p,o in graph.triples_choices((terms,None,None)):
        g.add((s,p,o))
    for s,p,o in graph.triples_choices((None,None,terms)):
        g.add((s,p,o))
    return g

from rdflib.namespace import RDF, RDFS

from rdflib import plugin, exceptions, query
#, sparql

from rdflib.term import Node
from rdflib.term import URIRef
from rdflib.term import BNode
from rdflib.term import Literal
from rdflib.namespace import Namespace
from rdflib.store import Store
from rdflib.serializer import Serializer
from rdflib.parser import Parser
from rdflib.parser import create_input_source
from rdflib.namespace import NamespaceManager

import tempfile, shutil, os
from urlparse import urlparse


class Graph(Node):
    """An RDF Graph

    The constructor accepts one argument, the 'store'
    that will be used to store the graph data (see the 'store'
    package for stores currently shipped with rdflib).

    Stores can be context-aware or unaware.  Unaware stores take up
    (some) less space but cannot support features that require
    context, such as true merging/demerging of sub-graphs and
    provenance.

    The Graph constructor can take an identifier which identifies the Graph
    by name.  If none is given, the graph is assigned a BNode for its identifier.
    For more on named graphs, see: http://www.w3.org/2004/03/trix/

    Ontology for __str__ provenance terms::

        @prefix rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
        @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
        @prefix : <http://rdflib.net/store#> .
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
            rdfs:label "The top-level graph within the store - the union of all the Graphs within."
            rdfs:seeAlso <http://rdflib.net/rdf_store/#ConjunctiveGraph>.

        :DefaultGraph a owl:Class;
            rdfs:subClassOf rdfg:Graph;
            rdfs:label "The 'default' subgraph of a conjunctive graph".


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
            rdfs:range :DefaultGraph.


        {?cg a :ConjunctiveGraph;:storage ?store}
          => {?cg owl:sameAs ?store}.

        {?subGraph rdfg:subGraphOf ?cg;a :DefaultGraph}
          => {?cg a :ConjunctiveGraph;:default_context ?subGraphOf} .
        
    """

    def __init__(self, store='default', identifier=None,
                 namespace_manager=None):
        super(Graph, self).__init__()
        self.__identifier = identifier or BNode()
        if not isinstance(store, Store):
            # TODO: error handling
            self.__store = store = plugin.get(store, Store)()
        else:
            self.__store = store
        self.__namespace_manager = namespace_manager
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
            return "%s a rdfg:Graph;rdflib:storage [a rdflib:Store;rdfs:label '%s']."%(self.identifier.n3(),self.store.__class__.__name__)
        else:
            return "[a rdfg:Graph;rdflib:storage [a rdflib:Store;rdfs:label '%s']]."%(self.store.__class__.__name__)

    def destroy(self, configuration):
        """Destroy the store identified by `configuration` if supported"""
        self.__store.destroy(configuration)

    #Transactional interfaces (optional)
    def commit(self):
        """Commits active transactions"""
        self.__store.commit()

    def rollback(self):
        """Rollback active transactions"""
        self.__store.rollback()

    def open(self, configuration, create=False):
        """Open the graph store

        Might be necessary for stores that require opening a connection to a
        database or acquiring some resource.
        """
        return self.__store.open(configuration, create)

    def close(self, commit_pending_transaction=False):
        """Close the graph store

        Might be necessary for stores that require closing a connection to a
        database or releasing some resource.
        """
        self.__store.close(commit_pending_transaction=commit_pending_transaction)

    def add(self, (s, p, o)):
        """Add a triple with self as context"""
        self.__store.add((s, p, o), self, quoted=False)

    def addN(self, quads):
        """Add a sequence of triple with context"""
        self.__store.addN([(s, p, o, c) for s, p, o, c in quads
                                        if isinstance(c, Graph)
                                        and c.identifier is self.identifier])

    def remove(self, (s, p, o)):
        """Remove a triple from the graph

        If the triple does not provide a context attribute, removes the triple
        from all contexts.
        """
        self.__store.remove((s, p, o), context=self)

    def triples(self, (s, p, o)):
        """Generator over the triple store

        Returns triples that match the given triple pattern. If triple pattern
        does not provide a context, all contexts will be searched.
        """
        for (s, p, o), cg in self.__store.triples((s, p, o), context=self):
            yield (s, p, o)

    def __len__(self):
        """Returns the number of triples in the graph

        If context is specified then the number of triples in the context is
        returned instead.
        """
        return self.__store.__len__(context=self)

    def __iter__(self):
        """Iterates over all triples in the store"""
        return self.triples((None, None, None))

    def __contains__(self, triple):
        """Support for 'triple in graph' syntax"""
        for triple in self.triples(triple):
            return True
        return False

    def __hash__(self):
        return hash(self.identifier)

    def md5_term_hash(self):
        d = md5(str(self.identifier))
        d.update("G")
        return d.hexdigest()

    def __cmp__(self, other):
        if other is None:
            return -1
        elif isinstance(other, Graph):
            return cmp(self.identifier, other.identifier)
        else:
            #Note if None is considered equivalent to owl:Nothing
            #Then perhaps a graph with length 0 should be considered
            #equivalent to None (if compared to it)?
            return 1

    def __iadd__(self, other):
        """Add all triples in Graph other to Graph"""
        for triple in other:
            self.add(triple)
        return self

    def __isub__(self, other):
        """Subtract all triples in Graph other from Graph"""
        for triple in other:
            self.remove(triple)
        return self

    def __add__(self,other) :
        """Set theoretical union"""
        retval = Graph()
        for x in self:
            retval.add(x)
        for y in other:
            retval.add(y)
        return retval

    def __mul__(self,other) :
        """Set theoretical intersection"""
        retval = Graph()
        for x in other:
            if x in self: 
                retval.add(x)
        return retval

    def __sub__(self,other) :
        """Set theoretical difference"""
        retval = Graph()
        for x in self:
            if not x in other : 
                retval.add(x)
        return retval

    # Conv. methods

    def set(self, (subject, predicate, object)):
        """Convenience method to update the value of object

        Remove any existing triples for subject and predicate before adding
        (subject, predicate, object).
        """
        self.remove((subject, predicate, None))
        self.add((subject, predicate, object))

    def subjects(self, predicate=None, object=None):
        """A generator of subjects with the given predicate and object"""
        for s, p, o in self.triples((None, predicate, object)):
            yield s

    def predicates(self, subject=None, object=None):
        """A generator of predicates with the given subject and object"""
        for s, p, o in self.triples((subject, None, object)):
            yield p

    def objects(self, subject=None, predicate=None):
        """A generator of objects with the given subject and predicate"""
        for s, p, o in self.triples((subject, predicate, None)):
            yield o

    def subject_predicates(self, object=None):
        """A generator of (subject, predicate) tuples for the given object"""
        for s, p, o in self.triples((None, None, object)):
            yield s, p

    def subject_objects(self, predicate=None):
        """A generator of (subject, object) tuples for the given predicate"""
        for s, p, o in self.triples((None, predicate, None)):
            yield s, o

    def predicate_objects(self, subject=None):
        """A generator of (predicate, object) tuples for the given subject"""
        for s, p, o in self.triples((subject, None, None)):
            yield p, o

    def triples_choices(self, (subject, predicate, object_),context=None):
        for (s, p, o), cg in self.store.triples_choices(
            (subject, predicate, object_), context=self):
            yield (s, p, o)

    def value(self, subject=None, predicate=RDF.value, object=None,
              default=None, any=True):
        """Get a value for a pair of two criteria

        Exactly one of subject, predicate, object must be None. Useful if one
        knows that there may only be one value.

        It is one of those situations that occur a lot, hence this
        'macro' like utility

        :Parameters:

        subject, predicate, object  -- exactly one must be None
        default -- value to be returned if no values found
        any -- if True: return any value in the case there is more than one
               else: raise UniquenessError
        """
        retval = default

        if (subject is None and predicate is None) or \
                (subject is None and object is None) or \
                (predicate is None and object is None):
            return None
        
        if object is None:
            values = self.objects(subject, predicate)
        if subject is None:
            values = self.subjects(predicate, object)
        if predicate is None:
            values = self.predicates(subject, object)

        try:
            retval = values.next()
        except StopIteration, e:
            retval = default
        else:
            if any is False:
                try:
                    next = values.next()
                    msg = ("While trying to find a value for (%s, %s, %s) the "
                           "following multiple values where found:\n" %
                           (subject, predicate, object))
                    triples = self.store.triples((subject, predicate, object), None)
                    for (s, p, o), contexts in triples:
                        msg += "(%s, %s, %s)\n (contexts: %s)\n" % (
                            s, p, o, list(contexts))
                    raise exceptions.UniquenessError(msg)
                except StopIteration, e:
                    pass
        return retval

    def label(self, subject, default=''):
        """Query for the RDFS.label of the subject

        Return default if no label exists
        """
        if subject is None:
            return default
        return self.value(subject, RDFS.label, default=default, any=True)

    def comment(self, subject, default=''):
        """Query for the RDFS.comment of the subject

        Return default if no comment exists
        """
        if subject is None:
            return default
        return self.value(subject, RDFS.comment, default=default, any=True)

    def items(self, list):
        """Generator over all items in the resource specified by list

        list is an RDF collection.
        """
        while list:
            item = self.value(list, RDF.first)
            if item:
                yield item
            list = self.value(list, RDF.rest)

    def transitiveClosure(self,func,arg):
        """
        Generates transitive closure of a user-defined 
        function against the graph
        
        >>> from rdflib.collection import Collection
        >>> g=Graph()
        >>> a=BNode('foo')
        >>> b=BNode('bar')
        >>> c=BNode('baz')
        >>> g.add((a,RDF.first,RDF.type))
        >>> g.add((a,RDF.rest,b))
        >>> g.add((b,RDF.first,RDFS.label))
        >>> g.add((b,RDF.rest,c))
        >>> g.add((c,RDF.first,RDFS.comment))
        >>> g.add((c,RDF.rest,RDF.nil))
        >>> def topList(node,g):
        ...    for s in g.subjects(RDF.rest,node):
        ...       yield s
        >>> def reverseList(node,g):
        ...    for f in g.objects(node,RDF.first):
        ...       print f
        ...    for s in g.subjects(RDF.rest,node):
        ...       yield s
        
        >>> [rt for rt in g.transitiveClosure(topList,RDF.nil)]
        [rdflib.term.BNode('baz'), rdflib.term.BNode('bar'), rdflib.term.BNode('foo')]
        
        >>> [rt for rt in g.transitiveClosure(reverseList,RDF.nil)]
        http://www.w3.org/2000/01/rdf-schema#comment
        http://www.w3.org/2000/01/rdf-schema#label
        http://www.w3.org/1999/02/22-rdf-syntax-ns#type
        [rdflib.term.BNode('baz'), rdflib.term.BNode('bar'), rdflib.term.BNode('foo')]
        
        """
        for rt in func(arg,self):
            yield rt
            for rt_2 in self.transitiveClosure(func,rt):
                yield rt_2

    def transitive_objects(self, subject, property, remember=None):
        """Transitively generate objects for the `property` relationship

        Generated objects belong to the depth first transitive closure of the
        `property` relationship starting at `subject`.
        """
        if remember is None:
            remember = {}
        if subject in remember:
            return
        remember[subject] = 1
        yield subject
        for object in self.objects(subject, property):
            for o in self.transitive_objects(object, property, remember):
                yield o

    def transitive_subjects(self, predicate, object, remember=None):
        """Transitively generate objects for the `property` relationship

        Generated objects belong to the depth first transitive closure of the
        `property` relationship starting at `subject`.
        """
        if remember is None:
            remember = {}
        if object in remember:
            return
        remember[object] = 1
        yield object
        for subject in self.subjects(predicate, object):
            for s in self.transitive_subjects(predicate, subject, remember):
                yield s

    def seq(self, subject):
        """Check if subject is an rdf:Seq

        If yes, it returns a Seq class instance, None otherwise.
        """
        if (subject, RDF.type, RDF.Seq) in self:
            return Seq(self, subject)
        else:
            return None

    def qname(self, uri):
        return self.namespace_manager.qname(uri)

    def compute_qname(self, uri):
        return self.namespace_manager.compute_qname(uri)

    def bind(self, prefix, namespace, override=True):
        """Bind prefix to namespace

        If override is True will bind namespace to given prefix if namespace
        was already bound to a different prefix.
        """
        return self.namespace_manager.bind(prefix, namespace, override=override)

    def namespaces(self):
        """Generator over all the prefix, namespace tuples"""
        for prefix, namespace in self.namespace_manager.namespaces():
            yield prefix, namespace

    def absolutize(self, uri, defrag=1):
        """Turn uri into an absolute URI if it's not one already"""
        return self.namespace_manager.absolutize(uri, defrag)

    def serialize(self, destination=None, format="xml", base=None, encoding=None, **args):
        """Serialize the Graph to destination

        If destination is None serialize method returns the serialization as a
        string. Format defaults to xml (AKA rdf/xml).
        """
        serializer = plugin.get(format, Serializer)(self)
        if destination is None:
            stream = StringIO()
            serializer.serialize(stream, base=base, encoding=encoding, **args)
            return stream.getvalue()
        if hasattr(destination, "write"):
            stream = destination
            serializer.serialize(stream, base=base, encoding=encoding, **args)
        else:
            location = destination
            scheme, netloc, path, params, query, fragment = urlparse(location)
            if netloc!="":
                print "WARNING: not saving as location is not a local file reference"
                return
            name = tempfile.mktemp()
            stream = open(name, 'wb')
            serializer.serialize(stream, base=base, encoding=encoding, **args)
            stream.close()
            if hasattr(shutil,"move"):
                shutil.move(name, path)
            else:
                shutil.copy(name, path)
                os.remove(name)

    def parse(self, source=None, publicID=None, format=None,
              location=None, file=None, data=None, **args):
        """
        Parse source adding the resulting triples to the Graph.

        The source is specified using one of source, location, file or
        data.

        :Parameters: - `source`: An InputSource, file-like object, or string. In the case of a string the string is the location of the source.
                     - `location`: A string indicating the relative or absolute URL of the source. Graph's absolutize method is used if a relative location is specified.
                     - `file`: A file-like object.
                     - `data`: A string containing the data to be parsed.
                     - `format`: Used if format can not be determined from source. Defaults to rdf/xml.
                     - `publicID`: the logical URI to use as the document base. If None specified the document location is used (at least in the case where there is a document location).

        :Returns:

        self, the graph instance.

        Examples:

        >>> my_data = '''
        ... <rdf:RDF
        ...   xmlns:rdf='http://www.w3.org/1999/02/22-rdf-syntax-ns#'
        ...   xmlns:rdfs='http://www.w3.org/2000/01/rdf-schema#'
        ... >
        ...   <rdf:Description>
        ...     <rdfs:label>Example</rdfs:label>
        ...     <rdfs:comment>This is really just an example.</rdfs:comment>
        ...   </rdf:Description>
        ... </rdf:RDF>
        ... '''
        >>> import tempfile
        >>> file_name = tempfile.mktemp()
        >>> f = file(file_name, "w")
        >>> f.write(my_data)
        >>> f.close()

        >>> g = Graph()
        >>> result = g.parse(data=my_data, format="application/rdf+xml")
        >>> len(g)
        2

        >>> g = Graph()
        >>> result = g.parse(location=file_name, format="application/rdf+xml")
        >>> len(g)
        2

        >>> g = Graph()
        >>> result = g.parse(file=file(file_name, "r"), format="application/rdf+xml")
        >>> len(g)
        2

        """

        if format=="xml":
            # warn... backward compat.
            format = "application/rdf+xml"
        source = create_input_source(source=source, publicID=publicID, location=location, file=file, data=data, format=format)
        if format is None:
            format = source.content_type
        if format is None:
            #raise Exception("Could not determin format for %r. You can expicitly specify one with the format argument." % source)
            format = "application/rdf+xml"
        parser = plugin.get(format, Parser)()
        parser.parse(source, self, **args)
        return self

    def load(self, source, publicID=None, format="xml"):
        self.parse(source, publicID, format)

    def query(self, query_object, processor='sparql', result='sparql'):
        """
        """
        if not isinstance(processor, query.Processor):
            processor = plugin.get(processor, query.Processor)(self)
        if not isinstance(result, query.Result):
            result = plugin.get(result, query.Result)
        return result(processor.query(query_object))


    def n3(self):
        """return an n3 identifier for the Graph"""
        return "[%s]" % self.identifier.n3()

    def __reduce__(self):
        return (Graph, (self.store, self.identifier,))

    def isomorphic(self, other):
        # TODO: this is only an approximation.
        if len(self) != len(other):
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

    def connected(self):
        """Check if the Graph is connected

        The Graph is considered undirectional.

        Performs a search on the Graph, starting from a random node. Then
        iteratively goes depth-first through the triplets where the node is
        subject and object. Return True if all nodes have been visited and
        False if it cannot continue and there are still unvisited nodes left.
        """
        all_nodes = list(self.all_nodes())
        discovered = []

        # take a random one, could also always take the first one, doesn't
        # really matter.
        visiting = [all_nodes[random.randrange(len(all_nodes))]]
        while visiting:
            x = visiting.pop()
            if x not in discovered:
                discovered.append(x)
            for new_x in self.objects(subject=x):
                if new_x not in discovered and new_x not in visiting:
                    visiting.append(new_x)
            for new_x in self.subjects(object=x):
                if new_x not in discovered and new_x not in visiting:
                    visiting.append(new_x)

        # optimisation by only considering length, since no new objects can
        # be introduced anywhere.
        if len(all_nodes) == len(discovered):
            return True
        else:
            return False

    def all_nodes(self):
        obj = set(self.objects())
        allNodes = obj.union(set(self.subjects()))
        return allNodes

class ConjunctiveGraph(Graph):

    def __init__(self, store='default', identifier=None):
        super(ConjunctiveGraph, self).__init__(store)
        assert self.store.context_aware, ("ConjunctiveGraph must be backed by"
                                          " a context aware store.")
        self.context_aware = True
        self.default_context = Graph(store=self.store,
                                     identifier=identifier or BNode())

    def __str__(self):
        pattern = ("[a rdflib:ConjunctiveGraph;rdflib:storage "
                   "[a rdflib:Store;rdfs:label '%s']]")
        return pattern % self.store.__class__.__name__

    def __contains__(self, triple_or_quad):
        """Support for 'triple/quad in graph' syntax"""
        context = None
        if len(triple_or_quad) == 4:
            context = triple_or_quad[3]
        for t in self.triples(triple_or_quad[:3], context=context):
            return True
        return False

    def add(self, (s, p, o)):
        """Add the triple to the default context"""
        self.store.add((s, p, o), context=self.default_context, quoted=False)

    def addN(self, quads):
        """Add a sequence of triples with context"""
        self.store.addN([quad for quad in quads if quad not in self])

    def remove(self, (s, p, o)):
        """Removes from all its contexts"""
        self.store.remove((s, p, o), context=None)

    def triples(self, (s, p, o), context=None):
        """Iterate over all the triples in the entire conjunctive graph"""
        for (s, p, o), cg in self.store.triples((s, p, o), context=context):
            yield s, p, o

    def quads(self,(s,p,o)):
        """Iterate over all the quads in the entire conjunctive graph"""
        for (s, p, o), cg in self.store.triples((s, p, o), context=None):
            for ctx in cg:
                yield s, p, o, ctx
            
    def triples_choices(self, (s, p, o)):
        """Iterate over all the triples in the entire conjunctive graph"""
        for (s1, p1, o1), cg in self.store.triples_choices((s, p, o),
                                                           context=None):
            yield (s1, p1, o1)

    def __len__(self):
        """Number of triples in the entire conjunctive graph"""
        return self.store.__len__()

    def contexts(self, triple=None):
        """Iterate over all contexts in the graph

        If triple is specified, iterate over all contexts the triple is in.
        """
        for context in self.store.contexts(triple):
            yield context

    def get_context(self, identifier, quoted=False):
        """Return a context graph for the given identifier

        identifier must be a URIRef or BNode.
        """
        return Graph(store=self.store, identifier=identifier, namespace_manager=self)

    def remove_context(self, context):
        """Removes the given context from the graph"""
        self.store.remove((None, None, None), context)

    def context_id(self, uri, context_id=None):
        """URI#context"""
        uri = uri.split("#", 1)[0]
        if context_id is None:
            context_id = "#context"
        return URIRef(context_id, base=uri)

    def parse(self, source=None, publicID=None, format="xml",
              location=None, file=None, data=None, **args):
        """
        Parse source adding the resulting triples to it's own context
        (sub graph of this graph).

        See `rdflib.graph.Graph.parse` for documentation on arguments.

        :Returns:

        The graph into which the source was parsed. In the case of n3
        it returns the root context.
        """

        source = create_input_source(source=source, publicID=publicID, location=location, file=file, data=data, format=format)

        #id = self.context_id(self.absolutize(source.getPublicId()))
        context = Graph(store=self.store, identifier=
          publicID and URIRef(publicID) or source.getPublicId())
        context.remove((None, None, None))
        context.parse(source, publicID=publicID, format=format,
                      location=location, file=file, data=data, **args)
        return context

    def __reduce__(self):
        return (ConjunctiveGraph, (self.store, self.identifier))


class QuotedGraph(Graph):

    def __init__(self, store, identifier):
        super(QuotedGraph, self).__init__(store, identifier)

    def add(self, triple):
        """Add a triple with self as context"""
        self.store.add(triple, self, quoted=True)

    def addN(self,quads):
        """Add a sequence of triple with context"""
        self.store.addN([(s,p,o,c) for s,p,o,c in quads
                                   if isinstance(c, QuotedGraph)
                                   and c.identifier is self.identifier])

    def n3(self):
        """Return an n3 identifier for the Graph"""
        return "{%s}" % self.identifier.n3()

    def __str__(self):
        identifier = self.identifier.n3()
        label = self.store.__class__.__name__
        pattern = ("{this rdflib.identifier %s;rdflib:storage "
                   "[a rdflib:Store;rdfs:label '%s']}")
        return pattern % (identifier, label)

    def __reduce__(self):
        return (QuotedGraph, (self.store, self.identifier))


class GraphValue(QuotedGraph):
    def __init__(self, store, identifier=None, graph=None):
        if graph is not None:
            assert identifier is None
            np = store.node_pickler
            identifier = md5()
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

    def __reduce__(self):
        return (GraphValue, (self.store, self.identifier,))


class Seq(object):
    """Wrapper around an RDF Seq resource

    It implements a container type in Python with the order of the items
    returned corresponding to the Seq content. It is based on the natural
    ordering of the predicate names _1, _2, _3, etc, which is the
    'implementation' of a sequence in RDF terms.
    """

    def __init__(self, graph, subject):
        """Parameters:

        - graph:
            the graph containing the Seq

        - subject:
            the subject of a Seq. Note that the init does not
            check whether this is a Seq, this is done in whoever
            creates this instance!
        """

        _list = self._list = list()
        LI_INDEX = URIRef(str(RDF) + "_")
        for (p, o) in graph.predicate_objects(subject):
            if p.startswith(LI_INDEX): #!= RDF.Seq: #
                i = int(p.replace(LI_INDEX, ''))
                _list.append((i, o))

        # here is the trick: the predicates are _1, _2, _3, etc. Ie,
        # by sorting the keys (by integer) we have what we want!
        _list.sort()

    def __iter__(self):
        """Generator over the items in the Seq"""
        for _, item in self._list:
            yield item

    def __len__(self):
        """Length of the Seq"""
        return len(self._list)

    def __getitem__(self, index):
        """Item given by index from the Seq"""
        index, item = self._list.__getitem__(index)
        return item


class BackwardCompatGraph(ConjunctiveGraph):

    def __init__(self, backend='default'):
        warnings.warn("Use ConjunctiveGraph instead. "
                      "( from rdflib.graph import ConjunctiveGraph )",
                      DeprecationWarning, stacklevel=2)
        super(BackwardCompatGraph, self).__init__(store=backend)

    def __get_backend(self):
        return self.store
    backend = property(__get_backend)

    def open(self, configuration, create=True):
        return ConjunctiveGraph.open(self, configuration, create)

    def add(self, (s, p, o), context=None):
        """Add to to the given context or to the default context"""
        if context is not None:
            c = self.get_context(context)
            assert c.identifier == context, "%s != %s" % (c.identifier, context)
        else:
            c = self.default_context
        self.store.add((s, p, o), context=c, quoted=False)

    def remove(self, (s, p, o), context=None):
        """Remove from the given context or from the default context"""
        if context is not None:
            context = self.get_context(context)
        self.store.remove((s, p, o), context)

    def triples(self, (s, p, o), context=None):
        """Iterate over all the triples in the entire graph"""
        if context is not None:
            c = self.get_context(context)
            assert c.identifier == context
        else:
            c = None
        for (s, p, o), cg in self.store.triples((s, p, o), c):
            yield (s, p, o)

    def __len__(self, context=None):
        """Number of triples in the entire graph"""
        if context is not None:
            context = self.get_context(context)
        return self.store.__len__(context)

    def get_context(self, identifier, quoted=False):
        """Return a context graph for the given identifier

        identifier must be a URIRef or BNode.
        """
        assert isinstance(identifier, URIRef) or \
               isinstance(identifier, BNode), type(identifier)
        if quoted:
            assert False
            return QuotedGraph(self.store, identifier)
            #return QuotedGraph(self.store, Graph(store=self.store,
            #                                     identifier=identifier))
        else:
            return Graph(store=self.store, identifier=identifier,
                         namespace_manager=self)
            #return Graph(self.store, Graph(store=self.store,
            #                               identifier=identifier))

    def remove_context(self, context):
        """Remove the given context from the graph"""
        self.store.remove((None, None, None), self.get_context(context))

    def contexts(self, triple=None):
        """Iterate over all contexts in the graph

        If triple is specified, iterate over all contexts the triple is in.
        """
        for context in self.store.contexts(triple):
            yield context.identifier

    def subjects(self, predicate=None, object=None, context=None):
        """Generate subjects with the given predicate and object"""
        for s, p, o in self.triples((None, predicate, object), context):
            yield s

    def predicates(self, subject=None, object=None, context=None):
        """Generate predicates with the given subject and object"""
        for s, p, o in self.triples((subject, None, object), context):
            yield p

    def objects(self, subject=None, predicate=None, context=None):
        """Generate objects with the given subject and predicate"""
        for s, p, o in self.triples((subject, predicate, None), context):
            yield o

    def subject_predicates(self, object=None, context=None):
        """Generate (subject, predicate) tuples for the given object"""
        for s, p, o in self.triples((None, None, object), context):
            yield s, p

    def subject_objects(self, predicate=None, context=None):
        """Generate (subject, object) tuples for the given predicate"""
        for s, p, o in self.triples((None, predicate, None), context):
            yield s, o

    def predicate_objects(self, subject=None, context=None):
        """Generate (predicate, object) tuples for the given subject"""
        for s, p, o in self.triples((subject, None, None), context):
            yield p, o

    def __reduce__(self):
        return (BackwardCompatGraph, (self.store, self.identifier))

    def save(self, destination, format="xml", base=None, encoding=None):
        warnings.warn("Use serialize method instead. ",
                      DeprecationWarning, stacklevel=2)
        self.serialize(destination=destination, format=format, base=base,
                       encoding=encoding)

class ModificationException(Exception):

    def __init__(self):
        pass

    def __str__(self):
        return ("Modifications and transactional operations not allowed on "
                "ReadOnlyGraphAggregate instances")

class UnSupportedAggregateOperation(Exception):

    def __init__(self):
        pass

    def __str__(self):
        return ("This operation is not supported by ReadOnlyGraphAggregate "
                "instances")

class ReadOnlyGraphAggregate(ConjunctiveGraph):
    """Utility class for treating a set of graphs as a single graph

    Only read operations are supported (hence the name). Essentially a
    ConjunctiveGraph over an explicit subset of the entire store.
    """

    def __init__(self, graphs,store='default'):
        if store is not None:
            super(ReadOnlyGraphAggregate, self).__init__(store)
            Graph.__init__(self, store)
            self.__namespace_manager = None

        assert isinstance(graphs, list) and graphs\
               and [g for g in graphs if isinstance(g, Graph)],\
               "graphs argument must be a list of Graphs!!"
        self.graphs = graphs

    def __repr__(self):
        return "<ReadOnlyGraphAggregate: %s graphs>" % len(self.graphs)

    def destroy(self, configuration):
        raise ModificationException()

    #Transactional interfaces (optional)
    def commit(self):
        raise ModificationException()

    def rollback(self):
        raise ModificationException()

    def open(self, configuration, create=False):
        # TODO: is there a use case for this method?
        for graph in self.graphs:
            graph.open(self, configuration, create)

    def close(self):
        for graph in self.graphs:
            graph.close()

    def add(self, (s, p, o)):
        raise ModificationException()

    def addN(self, quads):
        raise ModificationException()

    def remove(self, (s, p, o)):
        raise ModificationException()

    def triples(self, (s, p, o)):
        for graph in self.graphs:
            for s1, p1, o1 in graph.triples((s, p, o)):
                yield (s1, p1, o1)
                
    def __contains__(self, triple_or_quad):
        context = None
        if len(triple_or_quad) == 4:
            context = triple_or_quad[3]
        for graph in self.graphs:
            if context is None or graph.identifier == context.identifier:
                if triple_or_quad[:3] in graph:
                    return True
        return False

    def quads(self,(s,p,o)):
        """Iterate over all the quads in the entire aggregate graph"""
        for graph in self.graphs:
            for s1, p1, o1 in graph.triples((s, p, o)):
                yield (s1, p1, o1, graph)

    def __len__(self):
        return reduce(lambda x, y: x + y, [len(g) for g in self.graphs])

    def __hash__(self):
        raise UnSupportedAggregateOperation()

    def __cmp__(self, other):
        if other is None:
            return -1
        elif isinstance(other, Graph):
            return -1
        elif isinstance(other, ReadOnlyGraphAggregate):
            return cmp(self.graphs, other.graphs)
        else:
            return -1

    def __iadd__(self, other):
        raise ModificationException()

    def __isub__(self, other):
        raise ModificationException()

    # Conv. methods

    def triples_choices(self, (subject, predicate, object_), context=None):
        for graph in self.graphs:
            choices = graph.triples_choices((subject, predicate, object_))
            for (s, p, o) in choices:
                yield (s, p, o)

    def qname(self, uri):
        if hasattr(self,'namespace_manager') and self.namespace_manager:
            return self.namespace_manager.qname(uri)
        raise UnSupportedAggregateOperation()

    def compute_qname(self, uri):
        if hasattr(self,'namespace_manager') and self.namespace_manager:
            return self.namespace_manager.compute_qname(uri)
        raise UnSupportedAggregateOperation()

    def bind(self, prefix, namespace, override=True):
        raise UnSupportedAggregateOperation()

    def namespaces(self):
        if hasattr(self,'namespace_manager'):
            for prefix, namespace in self.namespace_manager.namespaces():
                yield prefix, namespace
        else:
            for graph in self.graphs:
                for prefix, namespace in graph.namespaces():
                    yield prefix, namespace

    def absolutize(self, uri, defrag=1):
        raise UnSupportedAggregateOperation()

    def parse(self, source, publicID=None, format="xml", **args):
        raise ModificationException()

    def n3(self):
        raise UnSupportedAggregateOperation()

    def __reduce__(self):
        raise UnSupportedAggregateOperation()


def test():
    import doctest
    doctest.testmod()

if __name__ == '__main__':
    test()
