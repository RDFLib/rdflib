from typing import Optional, Union, Type, cast, overload, Generator, Tuple
import logging
from warnings import warn
import random
from rdflib.namespace import Namespace, RDF
from rdflib import plugin, exceptions, query, namespace
import rdflib.term
from rdflib.term import BNode, Node, URIRef, Literal, Genid
from rdflib.paths import Path
from rdflib.store import Store
from rdflib.serializer import Serializer
from rdflib.parser import Parser, create_input_source
from rdflib.namespace import NamespaceManager
from rdflib.resource import Resource
from rdflib.collection import Collection
import rdflib.util  # avoid circular dependency
from rdflib.exceptions import ParserError

import os
import shutil
import tempfile
import pathlib

from io import BytesIO, BufferedIOBase
from urllib.parse import urlparse

assert Literal  # avoid warning
assert Namespace  # avoid warning

logger = logging.getLogger(__name__)

# Type aliases to make unpacking what's going on a little more human friendly
ContextNode = Union[BNode, URIRef]
DatasetQuad = Tuple[Node, URIRef, Node, Optional[ContextNode]]

__doc__ = """\

RDFLib defines the following kinds of Graphs:

* :class:`~rdflib.graph.Graph`
* :class:`~rdflib.graph.QuotedGraph`
* :class:`~rdflib.graph.ConjunctiveGraph`
* :class:`~rdflib.graph.Dataset`

Graph
-----

An RDF graph is a set of RDF triples. Graphs support the python ``in``
operator, as well as iteration and some operations like union,
difference and intersection.

see :class:`~rdflib.graph.Graph`

Conjunctive Graph
-----------------

A Conjunctive Graph is the most relevant collection of graphs that are
considered to be the boundary for closed world assumptions.  This
boundary is equivalent to that of the store instance (which is itself
uniquely identified and distinct from other instances of
:class:`Store` that signify other Conjunctive Graphs).  It is
equivalent to all the named graphs within it and associated with a
``_default_`` graph which is automatically assigned a :class:`BNode`
for an identifier - if one isn't given.

see :class:`~rdflib.graph.ConjunctiveGraph`

Quoted graph
------------

The notion of an RDF graph [14] is extended to include the concept of
a formula node. A formula node may occur wherever any other kind of
node can appear. Associated with a formula node is an RDF graph that
is completely disjoint from all other graphs; i.e. has no nodes in
common with any other graph. (It may contain the same labels as other
RDF graphs; because this is, by definition, a separate graph,
considerations of tidiness do not apply between the graph at a formula
node and any other graph.)

This is intended to map the idea of "{ N3-expression }" that is used
by N3 into an RDF graph upon which RDF semantics is defined.

see :class:`~rdflib.graph.QuotedGraph`

Dataset
-------

The RDF 1.1 Dataset, a small extension to the Conjunctive Graph. The
primary term is "graphs in the datasets" and not "contexts with quads"
so there is a separate method to set/retrieve a graph in a dataset and
to operate with dataset graphs. As a consequence of this approach,
dataset graphs cannot be identified with blank nodes, a name is always
required (RDFLib will automatically add a name if one is not provided
at creation time). This implementation includes a convenience method
to directly add a single quad to a dataset graph.

see :class:`~rdflib.graph.Dataset`

Working with graphs
===================

Instantiating Graphs with default store (Memory) and default identifier
(a BNode):

    >>> g = Graph()
    >>> g.store.__class__
    <class 'rdflib.plugins.stores.memory.Memory'>
    >>> g.identifier.__class__
    <class 'rdflib.term.BNode'>

Instantiating Graphs with a Memory store and an identifier -
<http://rdflib.net>:

    >>> g = Graph('Memory', URIRef("http://rdflib.net"))
    >>> g.identifier
    rdflib.term.URIRef('http://rdflib.net')
    >>> str(g)  # doctest: +NORMALIZE_WHITESPACE
    "<http://rdflib.net> a rdfg:Graph;rdflib:storage
     [a rdflib:Store;rdfs:label 'Memory']."

Creating a ConjunctiveGraph - The top level container for all named Graphs
in a "database":

    >>> g = ConjunctiveGraph()
    >>> str(g.default_context)
    "[a rdfg:Graph;rdflib:storage [a rdflib:Store;rdfs:label 'Memory']]."

Adding / removing reified triples to Graph and iterating over it directly or
via triple pattern:

    >>> g = Graph()
    >>> statementId = BNode()
    >>> print(len(g))
    0
    >>> g.add((statementId, RDF.type, RDF.Statement)) # doctest: +ELLIPSIS
    <Graph identifier=... (<class 'rdflib.graph.Graph'>)>
    >>> g.add((statementId, RDF.subject,
    ...     URIRef("http://rdflib.net/store/ConjunctiveGraph"))) # doctest: +ELLIPSIS
    <Graph identifier=... (<class 'rdflib.graph.Graph'>)>
    >>> g.add((statementId, RDF.predicate, namespace.RDFS.label)) # doctest: +ELLIPSIS
    <Graph identifier=... (<class 'rdflib.graph.Graph'>)>
    >>> g.add((statementId, RDF.object, Literal("Conjunctive Graph"))) # doctest: +ELLIPSIS
    <Graph identifier=... (<class 'rdflib.graph.Graph'>)>
    >>> print(len(g))
    4
    >>> for s, p, o in g:
    ...     print(type(s))
    ...
    <class 'rdflib.term.BNode'>
    <class 'rdflib.term.BNode'>
    <class 'rdflib.term.BNode'>
    <class 'rdflib.term.BNode'>

    >>> for s, p, o in g.triples((None, RDF.object, None)):
    ...     print(o)
    ...
    Conjunctive Graph
    >>> g.remove((statementId, RDF.type, RDF.Statement)) # doctest: +ELLIPSIS
    <Graph identifier=... (<class 'rdflib.graph.Graph'>)>
    >>> print(len(g))
    3

``None`` terms in calls to :meth:`~rdflib.graph.Graph.triples` can be
thought of as "open variables".

Graph support set-theoretic operators, you can add/subtract graphs, as
well as intersection (with multiplication operator g1*g2) and xor (g1
^ g2).

Note that BNode IDs are kept when doing set-theoretic operations, this
may or may not be what you want. Two named graphs within the same
application probably want share BNode IDs, two graphs with data from
different sources probably not.  If your BNode IDs are all generated
by RDFLib they are UUIDs and unique.

    >>> g1 = Graph()
    >>> g2 = Graph()
    >>> u = URIRef("http://example.com/foo")
    >>> g1.add([u, namespace.RDFS.label, Literal("foo")]) # doctest: +ELLIPSIS
    <Graph identifier=... (<class 'rdflib.graph.Graph'>)>
    >>> g1.add([u, namespace.RDFS.label, Literal("bar")]) # doctest: +ELLIPSIS
    <Graph identifier=... (<class 'rdflib.graph.Graph'>)>
    >>> g2.add([u, namespace.RDFS.label, Literal("foo")]) # doctest: +ELLIPSIS
    <Graph identifier=... (<class 'rdflib.graph.Graph'>)>
    >>> g2.add([u, namespace.RDFS.label, Literal("bing")]) # doctest: +ELLIPSIS
    <Graph identifier=... (<class 'rdflib.graph.Graph'>)>
    >>> len(g1 + g2)  # adds bing as label
    3
    >>> len(g1 - g2)  # removes foo
    1
    >>> len(g1 * g2)  # only foo
    1
    >>> g1 += g2  # now g1 contains everything


Graph Aggregation - ConjunctiveGraphs and ReadOnlyGraphAggregate within
the same store:

    >>> store = plugin.get("Memory", Store)()
    >>> g1 = Graph(store)
    >>> g2 = Graph(store)
    >>> g3 = Graph(store)
    >>> stmt1 = BNode()
    >>> stmt2 = BNode()
    >>> stmt3 = BNode()
    >>> g1.add((stmt1, RDF.type, RDF.Statement)) # doctest: +ELLIPSIS
    <Graph identifier=... (<class 'rdflib.graph.Graph'>)>
    >>> g1.add((stmt1, RDF.subject,
    ...     URIRef('http://rdflib.net/store/ConjunctiveGraph'))) # doctest: +ELLIPSIS
    <Graph identifier=... (<class 'rdflib.graph.Graph'>)>
    >>> g1.add((stmt1, RDF.predicate, namespace.RDFS.label)) # doctest: +ELLIPSIS
    <Graph identifier=... (<class 'rdflib.graph.Graph'>)>
    >>> g1.add((stmt1, RDF.object, Literal('Conjunctive Graph'))) # doctest: +ELLIPSIS
    <Graph identifier=... (<class 'rdflib.graph.Graph'>)>
    >>> g2.add((stmt2, RDF.type, RDF.Statement)) # doctest: +ELLIPSIS
    <Graph identifier=... (<class 'rdflib.graph.Graph'>)>
    >>> g2.add((stmt2, RDF.subject,
    ...     URIRef('http://rdflib.net/store/ConjunctiveGraph'))) # doctest: +ELLIPSIS
    <Graph identifier=... (<class 'rdflib.graph.Graph'>)>
    >>> g2.add((stmt2, RDF.predicate, RDF.type)) # doctest: +ELLIPSIS
    <Graph identifier=... (<class 'rdflib.graph.Graph'>)>
    >>> g2.add((stmt2, RDF.object, namespace.RDFS.Class)) # doctest: +ELLIPSIS
    <Graph identifier=... (<class 'rdflib.graph.Graph'>)>
    >>> g3.add((stmt3, RDF.type, RDF.Statement)) # doctest: +ELLIPSIS
    <Graph identifier=... (<class 'rdflib.graph.Graph'>)>
    >>> g3.add((stmt3, RDF.subject,
    ...     URIRef('http://rdflib.net/store/ConjunctiveGraph'))) # doctest: +ELLIPSIS
    <Graph identifier=... (<class 'rdflib.graph.Graph'>)>
    >>> g3.add((stmt3, RDF.predicate, namespace.RDFS.comment)) # doctest: +ELLIPSIS
    <Graph identifier=... (<class 'rdflib.graph.Graph'>)>
    >>> g3.add((stmt3, RDF.object, Literal(
    ...     'The top-level aggregate graph - The sum ' +
    ...     'of all named graphs within a Store'))) # doctest: +ELLIPSIS
    <Graph identifier=... (<class 'rdflib.graph.Graph'>)>
    >>> len(list(ConjunctiveGraph(store).subjects(RDF.type, RDF.Statement)))
    3
    >>> len(list(ReadOnlyGraphAggregate([g1,g2]).subjects(
    ...     RDF.type, RDF.Statement)))
    2

ConjunctiveGraphs have a :meth:`~rdflib.graph.ConjunctiveGraph.quads` method
which returns quads instead of triples, where the fourth item is the Graph
(or subclass thereof) instance in which the triple was asserted:

    >>> uniqueGraphNames = set(
    ...     [graph.identifier for s, p, o, graph in ConjunctiveGraph(store
    ...     ).quads((None, RDF.predicate, None))])
    >>> len(uniqueGraphNames)
    3
    >>> unionGraph = ReadOnlyGraphAggregate([g1, g2])
    >>> uniqueGraphNames = set(
    ...     [graph.identifier for s, p, o, graph in unionGraph.quads(
    ...     (None, RDF.predicate, None))])
    >>> len(uniqueGraphNames)
    2

Parsing N3 from a string

    >>> g2 = Graph()
    >>> src = '''
    ... @prefix rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
    ... @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
    ... [ a rdf:Statement ;
    ...   rdf:subject <http://rdflib.net/store#ConjunctiveGraph>;
    ...   rdf:predicate rdfs:label;
    ...   rdf:object "Conjunctive Graph" ] .
    ... '''
    >>> g2 = g2.parse(data=src, format="n3")
    >>> print(len(g2))
    4

Using Namespace class:

    >>> RDFLib = Namespace("http://rdflib.net/")
    >>> RDFLib.ConjunctiveGraph
    rdflib.term.URIRef('http://rdflib.net/ConjunctiveGraph')
    >>> RDFLib["Graph"]
    rdflib.term.URIRef('http://rdflib.net/Graph')

"""


__all__ = [
    "Graph",
    "ConjunctiveGraph",
    "QuotedGraph",
    "Seq",
    "ModificationException",
    "Dataset",
    "UnSupportedAggregateOperation",
    "ReadOnlyGraphAggregate",
    "BatchAddGraph",
]


class Graph(Node):
    """An RDF Graph

    The constructor accepts one argument, the "store"
    that will be used to store the graph data (see the "store"
    package for stores currently shipped with rdflib).

    Stores can be context-aware or unaware.  Unaware stores take up
    (some) less space but cannot support features that require
    context, such as true merging/demerging of sub-graphs and
    provenance.

    The Graph constructor can take an identifier which identifies the Graph
    by name.  If none is given, the graph is assigned a BNode for its
    identifier.

    For more on named graphs, see: http://www.w3.org/2004/03/trix/
    """

    def __init__(
        self, store="default", identifier=None, namespace_manager=None, base=None
    ):
        super(Graph, self).__init__()
        self.base = base
        self.__identifier = identifier or BNode()

        if not isinstance(self.__identifier, Node):
            self.__identifier = URIRef(self.__identifier)

        if not isinstance(store, Store):
            # TODO: error handling
            self.__store = store = plugin.get(store, Store)()
        else:
            self.__store = store
        self.__namespace_manager = namespace_manager
        self.context_aware = False
        self.formula_aware = False
        self.default_union = False

    def __get_store(self):
        return self.__store

    store = property(__get_store)  # read-only attr

    def __get_identifier(self):
        return self.__identifier

    identifier = property(__get_identifier)  # read-only attr

    def _get_namespace_manager(self):
        if self.__namespace_manager is None:
            self.__namespace_manager = NamespaceManager(self)
        return self.__namespace_manager

    def _set_namespace_manager(self, nm):
        self.__namespace_manager = nm

    namespace_manager = property(
        _get_namespace_manager,
        _set_namespace_manager,
        doc="this graph's namespace-manager",
    )

    def __repr__(self):
        return "<Graph identifier=%s (%s)>" % (self.identifier, type(self))

    def __str__(self):
        if isinstance(self.identifier, URIRef):
            return (
                "%s a rdfg:Graph;rdflib:storage " + "[a rdflib:Store;rdfs:label '%s']."
            ) % (self.identifier.n3(), self.store.__class__.__name__)
        else:
            return (
                "[a rdfg:Graph;rdflib:storage " + "[a rdflib:Store;rdfs:label '%s']]."
            ) % self.store.__class__.__name__

    def toPython(self):
        return self

    def destroy(self, configuration):
        """Destroy the store identified by `configuration` if supported"""
        self.__store.destroy(configuration)
        return self

    # Transactional interfaces (optional)
    def commit(self):
        """Commits active transactions"""
        self.__store.commit()
        return self

    def rollback(self):
        """Rollback active transactions"""
        self.__store.rollback()
        return self

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
        return self.__store.close(commit_pending_transaction=commit_pending_transaction)

    def add(self, triple):
        """Add a triple with self as context"""
        s, p, o = triple
        assert isinstance(s, Node), "Subject %s must be an rdflib term" % (s,)
        assert isinstance(p, Node), "Predicate %s must be an rdflib term" % (p,)
        assert isinstance(o, Node), "Object %s must be an rdflib term" % (o,)
        self.__store.add((s, p, o), self, quoted=False)
        return self

    def addN(self, quads):
        """Add a sequence of triple with context"""

        self.__store.addN(
            (s, p, o, c)
            for s, p, o, c in quads
            if isinstance(c, Graph)
            and c.identifier is self.identifier
            and _assertnode(s, p, o)
        )
        return self

    def remove(self, triple):
        """Remove a triple from the graph

        If the triple does not provide a context attribute, removes the triple
        from all contexts.
        """
        self.__store.remove(triple, context=self)
        return self

    def triples(self, triple):
        """Generator over the triple store

        Returns triples that match the given triple pattern. If triple pattern
        does not provide a context, all contexts will be searched.
        """
        s, p, o = triple
        if isinstance(p, Path):
            for _s, _o in p.eval(self, s, o):
                yield _s, p, _o
        else:
            for (s, p, o), cg in self.__store.triples((s, p, o), context=self):
                yield s, p, o

    def __getitem__(self, item):
        """
        A graph can be "sliced" as a shortcut for the triples method
        The python slice syntax is (ab)used for specifying triples.
        A generator over matches is returned,
        the returned tuples include only the parts not given

        >>> import rdflib
        >>> g = rdflib.Graph()
        >>> g.add((rdflib.URIRef("urn:bob"), namespace.RDFS.label, rdflib.Literal("Bob"))) # doctest: +ELLIPSIS
        <Graph identifier=... (<class 'rdflib.graph.Graph'>)>

        >>> list(g[rdflib.URIRef("urn:bob")]) # all triples about bob
        [(rdflib.term.URIRef('http://www.w3.org/2000/01/rdf-schema#label'), rdflib.term.Literal('Bob'))]

        >>> list(g[:namespace.RDFS.label]) # all label triples
        [(rdflib.term.URIRef('urn:bob'), rdflib.term.Literal('Bob'))]

        >>> list(g[::rdflib.Literal("Bob")]) # all triples with bob as object
        [(rdflib.term.URIRef('urn:bob'), rdflib.term.URIRef('http://www.w3.org/2000/01/rdf-schema#label'))]

        Combined with SPARQL paths, more complex queries can be
        written concisely:

        Name of all Bobs friends:

        g[bob : FOAF.knows/FOAF.name ]

        Some label for Bob:

        g[bob : DC.title|FOAF.name|RDFS.label]

        All friends and friends of friends of Bob

        g[bob : FOAF.knows * "+"]

        etc.

        .. versionadded:: 4.0

        """

        if isinstance(item, slice):

            s, p, o = item.start, item.stop, item.step
            if s is None and p is None and o is None:
                return self.triples((s, p, o))
            elif s is None and p is None:
                return self.subject_predicates(o)
            elif s is None and o is None:
                return self.subject_objects(p)
            elif p is None and o is None:
                return self.predicate_objects(s)
            elif s is None:
                return self.subjects(p, o)
            elif p is None:
                return self.predicates(s, o)
            elif o is None:
                return self.objects(s, p)
            else:
                # all given
                return (s, p, o) in self

        elif isinstance(item, (Path, Node)):

            return self.predicate_objects(item)

        else:
            raise TypeError(
                "You can only index a graph by a single rdflib term or path, or a slice of rdflib terms."
            )

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

    def __cmp__(self, other):
        if other is None:
            return -1
        elif isinstance(other, Graph):
            return (self.identifier > other.identifier) - (
                self.identifier < other.identifier
            )
        else:
            # Note if None is considered equivalent to owl:Nothing
            # Then perhaps a graph with length 0 should be considered
            # equivalent to None (if compared to it)?
            return 1

    def __eq__(self, other):
        return isinstance(other, Graph) and self.identifier == other.identifier

    def __lt__(self, other):
        return (other is None) or (
            isinstance(other, Graph) and self.identifier < other.identifier
        )

    def __le__(self, other):
        return self < other or self == other

    def __gt__(self, other):
        return (isinstance(other, Graph) and self.identifier > other.identifier) or (
            other is not None
        )

    def __ge__(self, other):
        return self > other or self == other

    def __iadd__(self, other):
        """Add all triples in Graph other to Graph.
        BNode IDs are not changed."""
        self.addN((s, p, o, self) for s, p, o in other)
        return self

    def __isub__(self, other):
        """Subtract all triples in Graph other from Graph.
        BNode IDs are not changed."""
        for triple in other:
            self.remove(triple)
        return self

    def __add__(self, other):
        """Set-theoretic union
        BNode IDs are not changed."""
        try:
            retval = type(self)()
        except TypeError:
            retval = Graph()
        for (prefix, uri) in set(list(self.namespaces()) + list(other.namespaces())):
            retval.bind(prefix, uri)
        for x in self:
            retval.add(x)
        for y in other:
            retval.add(y)
        return retval

    def __mul__(self, other):
        """Set-theoretic intersection.
        BNode IDs are not changed."""
        try:
            retval = type(self)()
        except TypeError:
            retval = Graph()
        for x in other:
            if x in self:
                retval.add(x)
        return retval

    def __sub__(self, other):
        """Set-theoretic difference.
        BNode IDs are not changed."""
        try:
            retval = type(self)()
        except TypeError:
            retval = Graph()
        for x in self:
            if x not in other:
                retval.add(x)
        return retval

    def __xor__(self, other):
        """Set-theoretic XOR.
        BNode IDs are not changed."""
        return (self - other) + (other - self)

    __or__ = __add__
    __and__ = __mul__

    # Conv. methods

    def set(self, triple):
        """Convenience method to update the value of object

        Remove any existing triples for subject and predicate before adding
        (subject, predicate, object).
        """
        (subject, predicate, object_) = triple
        assert (
            subject is not None
        ), "s can't be None in .set([s,p,o]), as it would remove (*, p, *)"
        assert (
            predicate is not None
        ), "p can't be None in .set([s,p,o]), as it would remove (s, *, *)"
        self.remove((subject, predicate, None))
        self.add((subject, predicate, object_))
        return self

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

    def triples_choices(self, triple, context=None):
        subject, predicate, object_ = triple
        for (s, p, o), cg in self.store.triples_choices(
            (subject, predicate, object_), context=self
        ):
            yield s, p, o

    def value(
        self, subject=None, predicate=RDF.value, object=None, default=None, any=True
    ):
        """Get a value for a pair of two criteria

        Exactly one of subject, predicate, object must be None. Useful if one
        knows that there may only be one value.

        It is one of those situations that occur a lot, hence this
        'macro' like utility

        Parameters:
        subject, predicate, object  -- exactly one must be None
        default -- value to be returned if no values found
        any -- if True, return any value in the case there is more than one,
        else, raise UniquenessError
        """
        retval = default

        if (
            (subject is None and predicate is None)
            or (subject is None and object is None)
            or (predicate is None and object is None)
        ):
            return None

        if object is None:
            values = self.objects(subject, predicate)
        if subject is None:
            values = self.subjects(predicate, object)
        if predicate is None:
            values = self.predicates(subject, object)

        try:
            retval = next(values)
        except StopIteration:
            retval = default
        else:
            if any is False:
                try:
                    next(values)
                    msg = (
                        "While trying to find a value for (%s, %s, %s) the"
                        " following multiple values where found:\n"
                        % (subject, predicate, object)
                    )
                    triples = self.store.triples((subject, predicate, object), None)
                    for (s, p, o), contexts in triples:
                        msg += "(%s, %s, %s)\n (contexts: %s)\n" % (
                            s,
                            p,
                            o,
                            list(contexts),
                        )
                    raise exceptions.UniquenessError(msg)
                except StopIteration:
                    pass
        return retval

    def label(self, subject, default=""):
        """Query for the RDFS.label of the subject

        Return default if no label exists or any label if multiple exist.
        """
        warn(
            DeprecationWarning(
                "graph.label() is deprecated and will be removed in rdflib 6.0.0."
            )
        )
        if subject is None:
            return default
        return self.value(subject, namespace.RDFS.label, default=default, any=True)

    def preferredLabel(
        self,
        subject,
        lang=None,
        default=None,
        labelProperties=(namespace.SKOS.prefLabel, namespace.RDFS.label),
    ):
        """
        Find the preferred label for subject.

        By default prefers skos:prefLabels over rdfs:labels. In case at least
        one prefLabel is found returns those, else returns labels. In case a
        language string (e.g., "en", "de" or even "" for no lang-tagged
        literals) is given, only such labels will be considered.

        Return a list of (labelProp, label) pairs, where labelProp is either
        skos:prefLabel or rdfs:label.

        >>> from rdflib import ConjunctiveGraph, URIRef, Literal, namespace
        >>> from pprint import pprint
        >>> g = ConjunctiveGraph()
        >>> u = URIRef("http://example.com/foo")
        >>> g.add([u, namespace.RDFS.label, Literal("foo")]) # doctest: +ELLIPSIS
        <Graph identifier=... (<class 'rdflib.graph.ConjunctiveGraph'>)>
        >>> g.add([u, namespace.RDFS.label, Literal("bar")]) # doctest: +ELLIPSIS
        <Graph identifier=... (<class 'rdflib.graph.ConjunctiveGraph'>)>
        >>> pprint(sorted(g.preferredLabel(u)))
        [(rdflib.term.URIRef('http://www.w3.org/2000/01/rdf-schema#label'),
          rdflib.term.Literal('bar')),
         (rdflib.term.URIRef('http://www.w3.org/2000/01/rdf-schema#label'),
          rdflib.term.Literal('foo'))]
        >>> g.add([u, namespace.SKOS.prefLabel, Literal("bla")]) # doctest: +ELLIPSIS
        <Graph identifier=... (<class 'rdflib.graph.ConjunctiveGraph'>)>
        >>> pprint(g.preferredLabel(u))
        [(rdflib.term.URIRef('http://www.w3.org/2004/02/skos/core#prefLabel'),
          rdflib.term.Literal('bla'))]
        >>> g.add([u, namespace.SKOS.prefLabel, Literal("blubb", lang="en")]) # doctest: +ELLIPSIS
        <Graph identifier=... (<class 'rdflib.graph.ConjunctiveGraph'>)>
        >>> sorted(g.preferredLabel(u)) #doctest: +NORMALIZE_WHITESPACE
        [(rdflib.term.URIRef('http://www.w3.org/2004/02/skos/core#prefLabel'),
          rdflib.term.Literal('bla')),
          (rdflib.term.URIRef('http://www.w3.org/2004/02/skos/core#prefLabel'),
          rdflib.term.Literal('blubb', lang='en'))]
        >>> g.preferredLabel(u, lang="") #doctest: +NORMALIZE_WHITESPACE
        [(rdflib.term.URIRef('http://www.w3.org/2004/02/skos/core#prefLabel'),
          rdflib.term.Literal('bla'))]
        >>> pprint(g.preferredLabel(u, lang="en"))
        [(rdflib.term.URIRef('http://www.w3.org/2004/02/skos/core#prefLabel'),
          rdflib.term.Literal('blubb', lang='en'))]
        """
        warn(
            DeprecationWarning(
                "graph.preferredLabel() is deprecated and will be removed in rdflib 6.0.0."
            )
        )
        if default is None:
            default = []

        # setup the language filtering
        if lang is not None:
            if lang == "":  # we only want not language-tagged literals

                def langfilter(l_):
                    return l_.language is None

            else:

                def langfilter(l_):
                    return l_.language == lang

        else:  # we don't care about language tags

            def langfilter(l_):
                return True

        for labelProp in labelProperties:
            labels = list(filter(langfilter, self.objects(subject, labelProp)))
            if len(labels) == 0:
                continue
            else:
                return [(labelProp, l_) for l_ in labels]
        return default

    def comment(self, subject, default=""):
        """Query for the RDFS.comment of the subject

        Return default if no comment exists
        """
        warn(
            DeprecationWarning(
                "graph.comment() is deprecated and will be removed in rdflib 6.0.0."
            )
        )
        if subject is None:
            return default
        return self.value(subject, namespace.RDFS.comment, default=default, any=True)

    def items(self, list):
        """Generator over all items in the resource specified by list

        list is an RDF collection.
        """
        chain = set([list])
        while list:
            item = self.value(list, RDF.first)
            if item is not None:
                yield item
            list = self.value(list, RDF.rest)
            if list in chain:
                raise ValueError("List contains a recursive rdf:rest reference")
            chain.add(list)

    def transitiveClosure(self, func, arg, seen=None):
        """
        Generates transitive closure of a user-defined
        function against the graph

        >>> from rdflib.collection import Collection
        >>> g=Graph()
        >>> a=BNode("foo")
        >>> b=BNode("bar")
        >>> c=BNode("baz")
        >>> g.add((a,RDF.first,RDF.type)) # doctest: +ELLIPSIS
        <Graph identifier=... (<class 'rdflib.graph.Graph'>)>
        >>> g.add((a,RDF.rest,b)) # doctest: +ELLIPSIS
        <Graph identifier=... (<class 'rdflib.graph.Graph'>)>
        >>> g.add((b,RDF.first,namespace.RDFS.label)) # doctest: +ELLIPSIS
        <Graph identifier=... (<class 'rdflib.graph.Graph'>)>
        >>> g.add((b,RDF.rest,c)) # doctest: +ELLIPSIS
        <Graph identifier=... (<class 'rdflib.graph.Graph'>)>
        >>> g.add((c,RDF.first,namespace.RDFS.comment)) # doctest: +ELLIPSIS
        <Graph identifier=... (<class 'rdflib.graph.Graph'>)>
        >>> g.add((c,RDF.rest,RDF.nil)) # doctest: +ELLIPSIS
        <Graph identifier=... (<class 'rdflib.graph.Graph'>)>
        >>> def topList(node,g):
        ...    for s in g.subjects(RDF.rest, node):
        ...       yield s
        >>> def reverseList(node,g):
        ...    for f in g.objects(node, RDF.first):
        ...       print(f)
        ...    for s in g.subjects(RDF.rest, node):
        ...       yield s

        >>> [rt for rt in g.transitiveClosure(
        ...     topList,RDF.nil)] # doctest: +NORMALIZE_WHITESPACE
        [rdflib.term.BNode('baz'),
         rdflib.term.BNode('bar'),
         rdflib.term.BNode('foo')]

        >>> [rt for rt in g.transitiveClosure(
        ...     reverseList,RDF.nil)] # doctest: +NORMALIZE_WHITESPACE
        http://www.w3.org/2000/01/rdf-schema#comment
        http://www.w3.org/2000/01/rdf-schema#label
        http://www.w3.org/1999/02/22-rdf-syntax-ns#type
        [rdflib.term.BNode('baz'),
         rdflib.term.BNode('bar'),
         rdflib.term.BNode('foo')]

        """
        if seen is None:
            seen = {}
        elif arg in seen:
            return
        seen[arg] = 1
        for rt in func(arg, self):
            yield rt
            for rt_2 in self.transitiveClosure(func, rt, seen):
                yield rt_2

    def transitive_objects(self, subject, predicate, remember=None):
        """Transitively generate objects for the ``predicate`` relationship

        Generated objects belong to the depth first transitive closure of the
        ``predicate`` relationship starting at ``subject``.
        """
        if remember is None:
            remember = {}
        if subject in remember:
            return
        remember[subject] = 1
        yield subject
        for object in self.objects(subject, predicate):
            for o in self.transitive_objects(object, predicate, remember):
                yield o

    def transitive_subjects(self, predicate, object, remember=None):
        """Transitively generate subjects for the ``predicate`` relationship

        Generated subjects belong to the depth first transitive closure of the
        ``predicate`` relationship starting at ``object``.
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
        warn(
            DeprecationWarning(
                "graph.seq() is deprecated and will be removed in rdflib 6.0.0."
            )
        )
        if (subject, RDF.type, RDF.Seq) in self:
            return Seq(self, subject)
        else:
            return None

    def qname(self, uri):
        return self.namespace_manager.qname(uri)

    def compute_qname(self, uri, generate=True):
        return self.namespace_manager.compute_qname(uri, generate)

    def bind(self, prefix, namespace, override=True, replace=False):
        """Bind prefix to namespace

        If override is True will bind namespace to given prefix even
        if namespace was already bound to a different prefix.

        if replace, replace any existing prefix with the new namespace

        for example:  graph.bind("foaf", "http://xmlns.com/foaf/0.1/")

        """
        return self.namespace_manager.bind(
            prefix, namespace, override=override, replace=replace
        )

    def namespaces(self):
        """Generator over all the prefix, namespace tuples"""
        for prefix, namespace in self.namespace_manager.namespaces():
            yield prefix, namespace

    def absolutize(self, uri, defrag=1):
        """Turn uri into an absolute URI if it's not one already"""
        return self.namespace_manager.absolutize(uri, defrag)

    # no destination and non-None positional encoding
    @overload
    def serialize(
        self, destination: None, format: str, base: Optional[str], encoding: str, **args
    ) -> bytes:
        ...

    # no destination and non-None keyword encoding
    @overload
    def serialize(
        self,
        *,
        destination: None = ...,
        format: str = ...,
        base: Optional[str] = ...,
        encoding: str,
        **args,
    ) -> bytes:
        ...

    # no destination and None positional encoding
    @overload
    def serialize(
        self,
        destination: None,
        format: str,
        base: Optional[str],
        encoding: None,
        **args,
    ) -> str:
        ...

    # no destination and None keyword encoding
    @overload
    def serialize(
        self,
        *,
        destination: None = ...,
        format: str = ...,
        base: Optional[str] = ...,
        encoding: None = None,
        **args,
    ) -> str:
        ...

    # non-none destination
    @overload
    def serialize(
        self,
        destination: Union[str, BufferedIOBase, pathlib.PurePath],
        format: str = ...,
        base: Optional[str] = ...,
        encoding: Optional[str] = ...,
        **args,
    ) -> "Graph":
        ...

    # fallback
    @overload
    def serialize(
        self,
        destination: Union[str, BufferedIOBase, pathlib.PurePath, None] = None,
        format: str = "turtle",
        base: Optional[str] = None,
        encoding: Optional[str] = None,
        **args,
    ) -> Union[bytes, str, "Graph"]:
        ...

    def serialize(
        self,
        destination: Union[str, BufferedIOBase, pathlib.PurePath, None] = None,
        format: str = "turtle",
        base: Optional[str] = None,
        encoding: Optional[str] = None,
        **args,
    ) -> Union[bytes, str, "Graph"]:
        """Serialize the Graph to destination

        If destination is None serialize method returns the serialization as
        bytes or string.

        If encoding is None and destination is None, returns a string
        If encoding is set, and Destination is None, returns bytes

        Format defaults to turtle.

        Format support can be extended with plugins,
        but "xml", "n3", "turtle", "nt", "pretty-xml", "trix", "trig" and "nquads" are built in.
        """

        # if base is not given as attribute use the base set for the graph
        if base is None:
            base = self.base

        serializer = plugin.get(format, Serializer)(self)
        stream: BufferedIOBase
        if destination is None:
            stream = BytesIO()
            if encoding is None:
                serializer.serialize(stream, base=base, encoding="utf-8", **args)
                return stream.getvalue().decode("utf-8")
            else:
                serializer.serialize(stream, base=base, encoding=encoding, **args)
                return stream.getvalue()
        if hasattr(destination, "write"):
            stream = cast(BufferedIOBase, destination)
            serializer.serialize(stream, base=base, encoding=encoding, **args)
        else:
            if isinstance(destination, pathlib.PurePath):
                location = str(destination)
            else:
                location = cast(str, destination)
            scheme, netloc, path, params, _query, fragment = urlparse(location)
            if netloc != "":
                raise ValueError(
                    f"destination {destination} is not a local file reference"
                )
            fd, name = tempfile.mkstemp()
            stream = os.fdopen(fd, "wb")
            serializer.serialize(stream, base=base, encoding=encoding, **args)
            stream.close()
            dest = path if scheme == "file" else location
            if hasattr(shutil, "move"):
                shutil.move(name, dest)
            else:
                shutil.copy(name, dest)
                os.remove(name)
        return self

    def print(self, format="turtle", encoding="utf-8", out=None):
        print(
            self.serialize(None, format=format, encoding=encoding).decode(encoding),
            file=out,
            flush=True,
        )

    def parse(
        self,
        source=None,
        publicID=None,
        format=None,
        location=None,
        file=None,
        data=None,
        **args,
    ):
        """
        Parse an RDF source adding the resulting triples to the Graph.

        The source is specified using one of source, location, file or
        data.

        :Parameters:

          - `source`: An InputSource, file-like object, or string. In the case
            of a string the string is the location of the source.
          - `location`: A string indicating the relative or absolute URL of the
            source. Graph's absolutize method is used if a relative location
            is specified.
          - `file`: A file-like object.
          - `data`: A string containing the data to be parsed.
          - `format`: Used if format can not be determined from source, e.g. file
            extension or Media Type. Defaults to text/turtle. Format support can
            be extended with plugins, but "xml", "n3" (use for turtle), "nt" &
            "trix" are built in.
          - `publicID`: the logical URI to use as the document base. If None
            specified the document location is used (at least in the case where
            there is a document location).

        :Returns:

          - self, the graph instance.

        Examples:

        >>> my_data = '''
        ... <rdf:RDF
        ...   xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
        ...   xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"
        ... >
        ...   <rdf:Description>
        ...     <rdfs:label>Example</rdfs:label>
        ...     <rdfs:comment>This is really just an example.</rdfs:comment>
        ...   </rdf:Description>
        ... </rdf:RDF>
        ... '''
        >>> import tempfile
        >>> fd, file_name = tempfile.mkstemp()
        >>> f = os.fdopen(fd, "w")
        >>> dummy = f.write(my_data)  # Returns num bytes written
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
        >>> with open(file_name, "r") as f:
        ...     result = g.parse(f, format="application/rdf+xml")
        >>> len(g)
        2

        >>> os.remove(file_name)

        >>> # default turtle parsing
        >>> result = g.parse(data="<http://example.com/a> <http://example.com/a> <http://example.com/a> .")
        >>> len(g)
        3

        """

        source = create_input_source(
            source=source,
            publicID=publicID,
            location=location,
            file=file,
            data=data,
            format=format,
        )
        if format is None:
            format = source.content_type
        could_not_guess_format = False
        if format is None:
            if (
                hasattr(source, "file")
                and getattr(source.file, "name", None)
                and isinstance(source.file.name, str)
            ):
                format = rdflib.util.guess_format(source.file.name)
            if format is None:
                format = "turtle"
                could_not_guess_format = True
        parser = plugin.get(format, Parser)()
        try:
            parser.parse(source, self, **args)
        except SyntaxError as se:
            if could_not_guess_format:
                raise ParserError(
                    "Could not guess RDF format for %r from file extension so tried Turtle but failed."
                    "You can explicitly specify format using the format argument."
                    % source
                )
            else:
                raise se
        finally:
            if source.auto_close:
                source.close()
        return self

    def load(self, source, publicID=None, format="xml"):
        warn(
            DeprecationWarning(
                "graph.load() is deprecated, it will be removed in rdflib 6.0.0. "
                "Please use graph.parse() instead."
            )
        )
        return self.parse(source, publicID, format)

    def query(
        self,
        query_object,
        processor: Union[str, query.Processor] = "sparql",
        result: Union[str, Type[query.Result]] = "sparql",
        initNs=None,
        initBindings=None,
        use_store_provided: bool = True,
        **kwargs,
    ) -> query.Result:
        """
        Query this graph.

        A type of 'prepared queries' can be realised by providing
        initial variable bindings with initBindings

        Initial namespaces are used to resolve prefixes used in the query,
        if none are given, the namespaces from the graph's namespace manager
        are used.

        :returntype: rdflib.query.Result

        """

        initBindings = initBindings or {}
        initNs = initNs or dict(self.namespaces())

        if hasattr(self.store, "query") and use_store_provided:
            try:
                return self.store.query(
                    query_object,
                    initNs,
                    initBindings,
                    self.default_union and "__UNION__" or self.identifier,
                    **kwargs,
                )
            except NotImplementedError:
                pass  # store has no own implementation

        if not isinstance(result, query.Result):
            result = plugin.get(cast(str, result), query.Result)
        if not isinstance(processor, query.Processor):
            processor = plugin.get(processor, query.Processor)(self)

        return result(processor.query(query_object, initBindings, initNs, **kwargs))

    def update(
        self,
        update_object,
        processor="sparql",
        initNs=None,
        initBindings=None,
        use_store_provided=True,
        **kwargs,
    ):
        """Update this graph with the given update query."""
        initBindings = initBindings or {}
        initNs = initNs or dict(self.namespaces())

        if hasattr(self.store, "update") and use_store_provided:
            try:
                return self.store.update(
                    update_object,
                    initNs,
                    initBindings,
                    self.default_union and "__UNION__" or self.identifier,
                    **kwargs,
                )
            except NotImplementedError:
                pass  # store has no own implementation

        if not isinstance(processor, query.UpdateProcessor):
            processor = plugin.get(processor, query.UpdateProcessor)(self)

        return processor.update(update_object, initBindings, initNs, **kwargs)

    def n3(self):
        """Return an n3 identifier for the Graph"""
        return "[%s]" % self.identifier.n3()

    def __reduce__(self):
        return (
            Graph,
            (
                self.store,
                self.identifier,
            ),
        )

    def isomorphic(self, other):
        """
        does a very basic check if these graphs are the same
        If no BNodes are involved, this is accurate.

        See rdflib.compare for a correct implementation of isomorphism checks
        """
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
        if not all_nodes:
            return False

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
        res = set(self.objects())
        res.update(self.subjects())
        return res

    def collection(self, identifier):
        """Create a new ``Collection`` instance.

        Parameters:

        - ``identifier``: a URIRef or BNode instance.

        Example::

            >>> graph = Graph()
            >>> uri = URIRef("http://example.org/resource")
            >>> collection = graph.collection(uri)
            >>> assert isinstance(collection, Collection)
            >>> assert collection.uri is uri
            >>> assert collection.graph is graph
            >>> collection += [ Literal(1), Literal(2) ]
        """

        return Collection(self, identifier)

    def resource(self, identifier):
        """Create a new ``Resource`` instance.

        Parameters:

        - ``identifier``: a URIRef or BNode instance.

        Example::

            >>> graph = Graph()
            >>> uri = URIRef("http://example.org/resource")
            >>> resource = graph.resource(uri)
            >>> assert isinstance(resource, Resource)
            >>> assert resource.identifier is uri
            >>> assert resource.graph is graph

        """
        if not isinstance(identifier, Node):
            identifier = URIRef(identifier)
        return Resource(self, identifier)

    def _process_skolem_tuples(self, target, func):
        for t in self.triples((None, None, None)):
            target.add(func(t))

    def skolemize(self, new_graph=None, bnode=None, authority=None, basepath=None):
        def do_skolemize(bnode, t):
            (s, p, o) = t
            if s == bnode:
                s = s.skolemize(authority=authority, basepath=basepath)
            if o == bnode:
                o = o.skolemize(authority=authority, basepath=basepath)
            return s, p, o

        def do_skolemize2(t):
            (s, p, o) = t
            if isinstance(s, BNode):
                s = s.skolemize(authority=authority, basepath=basepath)
            if isinstance(o, BNode):
                o = o.skolemize(authority=authority, basepath=basepath)
            return s, p, o

        retval = Graph() if new_graph is None else new_graph

        if bnode is None:
            self._process_skolem_tuples(retval, do_skolemize2)
        elif isinstance(bnode, BNode):
            self._process_skolem_tuples(retval, lambda t: do_skolemize(bnode, t))

        return retval

    def de_skolemize(self, new_graph=None, uriref=None):
        def do_de_skolemize(uriref, t):
            (s, p, o) = t
            if s == uriref:
                s = s.de_skolemize()
            if o == uriref:
                o = o.de_skolemize()
            return s, p, o

        def do_de_skolemize2(t):
            (s, p, o) = t
            if isinstance(s, Genid):
                s = s.de_skolemize()
            if isinstance(o, Genid):
                o = o.de_skolemize()
            return s, p, o

        retval = Graph() if new_graph is None else new_graph

        if uriref is None:
            self._process_skolem_tuples(retval, do_de_skolemize2)
        elif isinstance(uriref, Genid):
            self._process_skolem_tuples(retval, lambda t: do_de_skolemize(uriref, t))

        return retval


class ConjunctiveGraph(Graph):
    """A ConjunctiveGraph is an (unnamed) aggregation of all the named
    graphs in a store.

    It has a ``default`` graph, whose name is associated with the
    graph throughout its life. :meth:`__init__` can take an identifier
    to use as the name of this default graph or it will assign a
    BNode.

    All methods that add triples work against this default graph.

    All queries are carried out against the union of all graphs.
    """

    def __init__(self, store="default", identifier=None, default_graph_base=None):
        super(ConjunctiveGraph, self).__init__(store, identifier=identifier)
        assert self.store.context_aware, (
            "ConjunctiveGraph must be backed by" " a context aware store."
        )
        self.context_aware = True
        self.default_union = True  # Conjunctive!
        self.default_context = Graph(
            store=self.store, identifier=identifier or BNode(), base=default_graph_base
        )

    def __str__(self):
        pattern = (
            "[a rdflib:ConjunctiveGraph;rdflib:storage "
            "[a rdflib:Store;rdfs:label '%s']]"
        )
        return pattern % self.store.__class__.__name__

    def _spoc(self, triple_or_quad, default=False):
        """
        helper method for having methods that support
        either triples or quads
        """
        if triple_or_quad is None:
            return (None, None, None, self.default_context if default else None)
        if len(triple_or_quad) == 3:
            c = self.default_context if default else None
            (s, p, o) = triple_or_quad
        elif len(triple_or_quad) == 4:
            (s, p, o, c) = triple_or_quad
            c = self._graph(c)
        return s, p, o, c

    def __contains__(self, triple_or_quad):
        """Support for 'triple/quad in graph' syntax"""
        s, p, o, c = self._spoc(triple_or_quad)
        for t in self.triples((s, p, o), context=c):
            return True
        return False

    def add(self, triple_or_quad):
        """
        Add a triple or quad to the store.

        if a triple is given it is added to the default context
        """

        s, p, o, c = self._spoc(triple_or_quad, default=True)

        _assertnode(s, p, o)

        self.store.add((s, p, o), context=c, quoted=False)
        return self

    def _graph(self, c):
        if c is None:
            return None
        if not isinstance(c, Graph):
            return self.get_context(c)
        else:
            return c

    def addN(self, quads):
        """Add a sequence of triples with context"""

        self.store.addN(
            (s, p, o, self._graph(c)) for s, p, o, c in quads if _assertnode(s, p, o)
        )
        return self

    def remove(self, triple_or_quad):
        """
        Removes a triple or quads

        if a triple is given it is removed from all contexts

        a quad is removed from the given context only

        """
        s, p, o, c = self._spoc(triple_or_quad)

        self.store.remove((s, p, o), context=c)
        return self

    def triples(self, triple_or_quad, context=None):
        """
        Iterate over all the triples in the entire conjunctive graph

        For legacy reasons, this can take the context to query either
        as a fourth element of the quad, or as the explicit context
        keyword parameter. The kw param takes precedence.
        """

        s, p, o, c = self._spoc(triple_or_quad)
        context = self._graph(context or c)

        if self.default_union:
            if context == self.default_context:
                context = None
        else:
            if context is None:
                context = self.default_context

        if isinstance(p, Path):
            if context is None:
                context = self

            for s, o in p.eval(context, s, o):
                yield s, p, o
        else:
            for (s, p, o), cg in self.store.triples((s, p, o), context=context):
                yield s, p, o

    def quads(self, triple_or_quad=None):
        """Iterate over all the quads in the entire conjunctive graph"""

        s, p, o, c = self._spoc(triple_or_quad)

        for (s, p, o), cg in self.store.triples((s, p, o), context=c):
            for ctx in cg:
                yield s, p, o, ctx

    def triples_choices(self, triple, context=None):
        """Iterate over all the triples in the entire conjunctive graph"""
        s, p, o = triple
        if context is None:
            if not self.default_union:
                context = self.default_context
        else:
            context = self._graph(context)

        for (s1, p1, o1), cg in self.store.triples_choices((s, p, o), context=context):
            yield s1, p1, o1

    def __len__(self):
        """Number of triples in the entire conjunctive graph"""
        return self.store.__len__()

    def contexts(self, triple=None):
        """Iterate over all contexts in the graph

        If triple is specified, iterate over all contexts the triple is in.
        """
        for context in self.store.contexts(triple):
            if isinstance(context, Graph):
                # TODO: One of these should never happen and probably
                # should raise an exception rather than smoothing over
                # the weirdness - see #225
                yield context
            else:
                yield self.get_context(context)

    def get_context(self, identifier, quoted=False, base=None):
        """Return a context graph for the given identifier

        identifier must be a URIRef or BNode.
        """
        return Graph(
            store=self.store, identifier=identifier, namespace_manager=self, base=base
        )

    def remove_context(self, context):
        """Removes the given context from the graph"""
        self.store.remove((None, None, None), context)

    def context_id(self, uri, context_id=None):
        """URI#context"""
        uri = uri.split("#", 1)[0]
        if context_id is None:
            context_id = "#context"
        return URIRef(context_id, base=uri)

    def parse(
        self,
        source=None,
        publicID=None,
        format=None,
        location=None,
        file=None,
        data=None,
        **args,
    ):
        """
        Parse source adding the resulting triples to its own context
        (sub graph of this graph).

        See :meth:`rdflib.graph.Graph.parse` for documentation on arguments.

        :Returns:

        The graph into which the source was parsed. In the case of n3
        it returns the root context.
        """

        source = create_input_source(
            source=source,
            publicID=publicID,
            location=location,
            file=file,
            data=data,
            format=format,
        )

        g_id = publicID and publicID or source.getPublicId()
        if not isinstance(g_id, Node):
            g_id = URIRef(g_id)

        context = Graph(store=self.store, identifier=g_id)
        context.remove((None, None, None))  # hmm ?
        context.parse(source, publicID=publicID, format=format, **args)
        return context

    def __reduce__(self):
        return ConjunctiveGraph, (self.store, self.identifier)


DATASET_DEFAULT_GRAPH_ID = URIRef("urn:x-rdflib:default")


class Dataset(ConjunctiveGraph):
    __doc__ = """
    RDF 1.1 Dataset. Small extension to the Conjunctive Graph:
    - the primary term is graphs in the datasets and not contexts with quads,
    so there is a separate method to set/retrieve a graph in a dataset and
    operate with graphs
    - graphs cannot be identified with blank nodes
    - added a method to directly add a single quad

    Examples of usage:

    >>> # Create a new Dataset
    >>> ds = Dataset()
    >>> # simple triples goes to default graph
    >>> ds.add((URIRef("http://example.org/a"),
    ...    URIRef("http://www.example.org/b"),
    ...    Literal("foo")))  # doctest: +ELLIPSIS
    <Graph identifier=... (<class 'rdflib.graph.Dataset'>)>
    >>>
    >>> # Create a graph in the dataset, if the graph name has already been
    >>> # used, the corresponding graph will be returned
    >>> # (ie, the Dataset keeps track of the constituent graphs)
    >>> g = ds.graph(URIRef("http://www.example.com/gr"))
    >>>
    >>> # add triples to the new graph as usual
    >>> g.add(
    ...     (URIRef("http://example.org/x"),
    ...     URIRef("http://example.org/y"),
    ...     Literal("bar")) ) # doctest: +ELLIPSIS
    <Graph identifier=... (<class 'rdflib.graph.Graph'>)>
    >>> # alternatively: add a quad to the dataset -> goes to the graph
    >>> ds.add(
    ...     (URIRef("http://example.org/x"),
    ...     URIRef("http://example.org/z"),
    ...     Literal("foo-bar"),g) ) # doctest: +ELLIPSIS
    <Graph identifier=... (<class 'rdflib.graph.Dataset'>)>
    >>>
    >>> # querying triples return them all regardless of the graph
    >>> for t in ds.triples((None,None,None)):  # doctest: +SKIP
    ...     print(t)  # doctest: +NORMALIZE_WHITESPACE
    (rdflib.term.URIRef("http://example.org/a"),
     rdflib.term.URIRef("http://www.example.org/b"),
     rdflib.term.Literal("foo"))
    (rdflib.term.URIRef("http://example.org/x"),
     rdflib.term.URIRef("http://example.org/z"),
     rdflib.term.Literal("foo-bar"))
    (rdflib.term.URIRef("http://example.org/x"),
     rdflib.term.URIRef("http://example.org/y"),
     rdflib.term.Literal("bar"))
    >>>
    >>> # querying quads() return quads; the fourth argument can be unrestricted
    >>> # (None) or restricted to a graph
    >>> for q in ds.quads((None, None, None, None)):  # doctest: +SKIP
    ...     print(q)  # doctest: +NORMALIZE_WHITESPACE
    (rdflib.term.URIRef("http://example.org/a"),
     rdflib.term.URIRef("http://www.example.org/b"),
     rdflib.term.Literal("foo"),
     None)
    (rdflib.term.URIRef("http://example.org/x"),
     rdflib.term.URIRef("http://example.org/y"),
     rdflib.term.Literal("bar"),
     rdflib.term.URIRef("http://www.example.com/gr"))
    (rdflib.term.URIRef("http://example.org/x"),
     rdflib.term.URIRef("http://example.org/z"),
     rdflib.term.Literal("foo-bar"),
     rdflib.term.URIRef("http://www.example.com/gr"))
    >>>
    >>> # unrestricted looping is equivalent to iterating over the entire Dataset
    >>> for q in ds:  # doctest: +SKIP
    ...     print(q)  # doctest: +NORMALIZE_WHITESPACE
    (rdflib.term.URIRef("http://example.org/a"),
     rdflib.term.URIRef("http://www.example.org/b"),
     rdflib.term.Literal("foo"),
     None)
    (rdflib.term.URIRef("http://example.org/x"),
     rdflib.term.URIRef("http://example.org/y"),
     rdflib.term.Literal("bar"),
     rdflib.term.URIRef("http://www.example.com/gr"))
    (rdflib.term.URIRef("http://example.org/x"),
     rdflib.term.URIRef("http://example.org/z"),
     rdflib.term.Literal("foo-bar"),
     rdflib.term.URIRef("http://www.example.com/gr"))
    >>>
    >>> # resticting iteration to a graph:
    >>> for q in ds.quads((None, None, None, g)):  # doctest: +SKIP
    ...     print(q)  # doctest: +NORMALIZE_WHITESPACE
    (rdflib.term.URIRef("http://example.org/x"),
     rdflib.term.URIRef("http://example.org/y"),
     rdflib.term.Literal("bar"),
     rdflib.term.URIRef("http://www.example.com/gr"))
    (rdflib.term.URIRef("http://example.org/x"),
     rdflib.term.URIRef("http://example.org/z"),
     rdflib.term.Literal("foo-bar"),
     rdflib.term.URIRef("http://www.example.com/gr"))
    >>> # Note that in the call above -
    >>> # ds.quads((None,None,None,"http://www.example.com/gr"))
    >>> # would have been accepted, too
    >>>
    >>> # graph names in the dataset can be queried:
    >>> for c in ds.graphs():  # doctest: +SKIP
    ...     print(c)  # doctest:
    DEFAULT
    http://www.example.com/gr
    >>> # A graph can be created without specifying a name; a skolemized genid
    >>> # is created on the fly
    >>> h = ds.graph()
    >>> for c in ds.graphs():  # doctest: +SKIP
    ...     print(c)  # doctest: +NORMALIZE_WHITESPACE +ELLIPSIS
    DEFAULT
    http://rdlib.net/.well-known/genid/rdflib/N...
    http://www.example.com/gr
    >>> # Note that the Dataset.graphs() call returns names of empty graphs,
    >>> # too. This can be restricted:
    >>> for c in ds.graphs(empty=False):  # doctest: +SKIP
    ...     print(c)  # doctest: +NORMALIZE_WHITESPACE
    DEFAULT
    http://www.example.com/gr
    >>>
    >>> # a graph can also be removed from a dataset via ds.remove_graph(g)

    .. versionadded:: 4.0
    """

    def __init__(self, store="default", default_union=False, default_graph_base=None):
        super(Dataset, self).__init__(store=store, identifier=None)

        if not self.store.graph_aware:
            raise Exception("DataSet must be backed by a graph-aware store!")
        self.default_context = Graph(
            store=self.store,
            identifier=DATASET_DEFAULT_GRAPH_ID,
            base=default_graph_base,
        )

        self.default_union = default_union

    def __str__(self):
        pattern = (
            "[a rdflib:Dataset;rdflib:storage " "[a rdflib:Store;rdfs:label '%s']]"
        )
        return pattern % self.store.__class__.__name__

    def graph(self, identifier=None, base=None):
        if identifier is None:
            from rdflib.term import rdflib_skolem_genid

            self.bind(
                "genid", "http://rdflib.net" + rdflib_skolem_genid, override=False
            )
            identifier = BNode().skolemize()

        g = self._graph(identifier)
        g.base = base

        self.store.add_graph(g)
        return g

    def parse(
        self,
        source=None,
        publicID=None,
        format=None,
        location=None,
        file=None,
        data=None,
        **args,
    ):
        c = ConjunctiveGraph.parse(
            self, source, publicID, format, location, file, data, **args
        )
        self.graph(c)
        return c

    def add_graph(self, g):
        """alias of graph for consistency"""
        return self.graph(g)

    def remove_graph(self, g):
        if not isinstance(g, Graph):
            g = self.get_context(g)

        self.store.remove_graph(g)
        if g is None or g == self.default_context:
            # default graph cannot be removed
            # only triples deleted, so add it back in
            self.store.add_graph(self.default_context)
        return self

    def contexts(self, triple=None):
        default = False
        for c in super(Dataset, self).contexts(triple):
            default |= c.identifier == DATASET_DEFAULT_GRAPH_ID
            yield c
        if not default:
            yield self.graph(DATASET_DEFAULT_GRAPH_ID)

    graphs = contexts

    def quads(self, quad):
        for s, p, o, c in super(Dataset, self).quads(quad):
            if c.identifier == self.default_context:
                yield s, p, o, None
            else:
                yield s, p, o, c.identifier

    def __iter__(self) -> Generator[DatasetQuad, None, None]:
        """Iterates over all quads in the store"""
        return self.quads((None, None, None, None))


class QuotedGraph(Graph):
    """
    Quoted Graphs are intended to implement Notation 3 formulae. They are
    associated with a required identifier that the N3 parser *must* provide
    in order to maintain consistent formulae identification for scenarios
    such as implication and other such processing.
    """

    def __init__(self, store, identifier):
        super(QuotedGraph, self).__init__(store, identifier)

    def add(self, triple):
        """Add a triple with self as context"""
        s, p, o = triple
        assert isinstance(s, Node), "Subject %s must be an rdflib term" % (s,)
        assert isinstance(p, Node), "Predicate %s must be an rdflib term" % (p,)
        assert isinstance(o, Node), "Object %s must be an rdflib term" % (o,)

        self.store.add((s, p, o), self, quoted=True)
        return self

    def addN(self, quads):
        """Add a sequence of triple with context"""

        self.store.addN(
            (s, p, o, c)
            for s, p, o, c in quads
            if isinstance(c, QuotedGraph)
            and c.identifier is self.identifier
            and _assertnode(s, p, o)
        )
        return self

    def n3(self):
        """Return an n3 identifier for the Graph"""
        return "{%s}" % self.identifier.n3()

    def __str__(self):
        identifier = self.identifier.n3()
        label = self.store.__class__.__name__
        pattern = (
            "{this rdflib.identifier %s;rdflib:storage "
            "[a rdflib:Store;rdfs:label '%s']}"
        )
        return pattern % (identifier, label)

    def __reduce__(self):
        return QuotedGraph, (self.store, self.identifier)


# Make sure QuotedGraph is ordered correctly
# wrt to other Terms.
# this must be done here, as the QuotedGraph cannot be
# circularily imported in term.py
rdflib.term._ORDERING[QuotedGraph] = 11


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
            if p.startswith(LI_INDEX):  # != RDF.Seq: #
                i = int(p.replace(LI_INDEX, ""))
                _list.append((i, o))

        # here is the trick: the predicates are _1, _2, _3, etc. Ie,
        # by sorting the keys (by integer) we have what we want!
        _list.sort()

    def toPython(self):
        return self

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


class ModificationException(Exception):
    def __init__(self):
        pass

    def __str__(self):
        return (
            "Modifications and transactional operations not allowed on "
            "ReadOnlyGraphAggregate instances"
        )


class UnSupportedAggregateOperation(Exception):
    def __init__(self):
        pass

    def __str__(self):
        return "This operation is not supported by ReadOnlyGraphAggregate " "instances"


class ReadOnlyGraphAggregate(ConjunctiveGraph):
    """Utility class for treating a set of graphs as a single graph

    Only read operations are supported (hence the name). Essentially a
    ConjunctiveGraph over an explicit subset of the entire store.
    """

    def __init__(self, graphs, store="default"):
        if store is not None:
            super(ReadOnlyGraphAggregate, self).__init__(store)
            Graph.__init__(self, store)
            self.__namespace_manager = None

        assert (
            isinstance(graphs, list)
            and graphs
            and [g for g in graphs if isinstance(g, Graph)]
        ), "graphs argument must be a list of Graphs!!"
        self.graphs = graphs

    def __repr__(self):
        return "<ReadOnlyGraphAggregate: %s graphs>" % len(self.graphs)

    def destroy(self, configuration):
        raise ModificationException()

    # Transactional interfaces (optional)
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

    def add(self, triple):
        raise ModificationException()

    def addN(self, quads):
        raise ModificationException()

    def remove(self, triple):
        raise ModificationException()

    def triples(self, triple):
        s, p, o = triple
        for graph in self.graphs:
            if isinstance(p, Path):
                for s, o in p.eval(self, s, o):
                    yield s, p, o
            else:
                for s1, p1, o1 in graph.triples((s, p, o)):
                    yield s1, p1, o1

    def __contains__(self, triple_or_quad):
        context = None
        if len(triple_or_quad) == 4:
            context = triple_or_quad[3]
        for graph in self.graphs:
            if context is None or graph.identifier == context.identifier:
                if triple_or_quad[:3] in graph:
                    return True
        return False

    def quads(self, triple):
        """Iterate over all the quads in the entire aggregate graph"""
        s, p, o = triple
        for graph in self.graphs:
            for s1, p1, o1 in graph.triples((s, p, o)):
                yield s1, p1, o1, graph

    def __len__(self):
        return sum(len(g) for g in self.graphs)

    def __hash__(self):
        raise UnSupportedAggregateOperation()

    def __cmp__(self, other):
        if other is None:
            return -1
        elif isinstance(other, Graph):
            return -1
        elif isinstance(other, ReadOnlyGraphAggregate):
            return (self.graphs > other.graphs) - (self.graphs < other.graphs)
        else:
            return -1

    def __iadd__(self, other):
        raise ModificationException()

    def __isub__(self, other):
        raise ModificationException()

    # Conv. methods

    def triples_choices(self, triple, context=None):
        subject, predicate, object_ = triple
        for graph in self.graphs:
            choices = graph.triples_choices((subject, predicate, object_))
            for (s, p, o) in choices:
                yield s, p, o

    def qname(self, uri):
        if hasattr(self, "namespace_manager") and self.namespace_manager:
            return self.namespace_manager.qname(uri)
        raise UnSupportedAggregateOperation()

    def compute_qname(self, uri, generate=True):
        if hasattr(self, "namespace_manager") and self.namespace_manager:
            return self.namespace_manager.compute_qname(uri, generate)
        raise UnSupportedAggregateOperation()

    def bind(self, prefix, namespace, override=True):
        raise UnSupportedAggregateOperation()

    def namespaces(self):
        if hasattr(self, "namespace_manager"):
            for prefix, namespace in self.namespace_manager.namespaces():
                yield prefix, namespace
        else:
            for graph in self.graphs:
                for prefix, namespace in graph.namespaces():
                    yield prefix, namespace

    def absolutize(self, uri, defrag=1):
        raise UnSupportedAggregateOperation()

    def parse(self, source, publicID=None, format=None, **args):
        raise ModificationException()

    def n3(self):
        raise UnSupportedAggregateOperation()

    def __reduce__(self):
        raise UnSupportedAggregateOperation()


def _assertnode(*terms):
    for t in terms:
        assert isinstance(t, Node), "Term %s must be an rdflib term" % (t,)
    return True


class BatchAddGraph(object):
    """
    Wrapper around graph that turns batches of calls to Graph's add
    (and optionally, addN) into calls to batched calls to addN`.

    :Parameters:

      - graph: The graph to wrap
      - batch_size: The maximum number of triples to buffer before passing to
        Graph's addN
      - batch_addn: If True, then even calls to `addN` will be batched according to
        batch_size

    graph: The wrapped graph
    count: The number of triples buffered since initialization or the last call to reset
    batch: The current buffer of triples

    """

    def __init__(self, graph, batch_size=1000, batch_addn=False):
        if not batch_size or batch_size < 2:
            raise ValueError("batch_size must be a positive number")
        self.graph = graph
        self.__graph_tuple = (graph,)
        self.__batch_size = batch_size
        self.__batch_addn = batch_addn
        self.reset()

    def reset(self):
        """
        Manually clear the buffered triples and reset the count to zero
        """
        self.batch = []
        self.count = 0
        return self

    def add(self, triple_or_quad):
        """
        Add a triple to the buffer

        :param triple: The triple to add
        """
        if len(self.batch) >= self.__batch_size:
            self.graph.addN(self.batch)
            self.batch = []
        self.count += 1
        if len(triple_or_quad) == 3:
            self.batch.append(triple_or_quad + self.__graph_tuple)
        else:
            self.batch.append(triple_or_quad)
        return self

    def addN(self, quads):
        if self.__batch_addn:
            for q in quads:
                self.add(q)
        else:
            self.graph.addN(quads)
        return self

    def __enter__(self):
        self.reset()
        return self

    def __exit__(self, *exc):
        if exc[0] is None:
            self.graph.addN(self.batch)


def test():
    import doctest

    doctest.testmod()


if __name__ == "__main__":
    test()
