# -*- coding: utf-8 -*-
"""
A collection of utilities for canonicalizing and inspecting graphs.

Among other things, they solve of the problem of deterministic bnode
comparisons.

Warning: the time to canonicalize bnodes may increase exponentially on larger
graphs. Use with care!

Example of comparing two graphs::

    >>> g1 = Graph().parse(format='n3', data='''
    ...     @prefix : <http://example.org/ns#> .
    ...     <http://example.org> :rel
    ...         <http://example.org/same>,
    ...         [ :label "Same" ],
    ...         <http://example.org/a>,
    ...         [ :label "A" ] .
    ... ''')
    >>> g2 = Graph().parse(format='n3', data='''
    ...     @prefix : <http://example.org/ns#> .
    ...     <http://example.org> :rel
    ...         <http://example.org/same>,
    ...         [ :label "Same" ],
    ...         <http://example.org/b>,
    ...         [ :label "B" ] .
    ... ''')
    >>>
    >>> iso1 = to_isomorphic(g1)
    >>> iso2 = to_isomorphic(g2)

These are not isomorphic::

    >>> iso1 == iso2
    False

Diff the two graphs::

    >>> in_both, in_first, in_second = graph_diff(iso1, iso2)

Present in both::

    >>> def dump_nt_sorted(g):
    ...     for l in sorted(g.serialize(format='nt').splitlines()):
    ...         if l: print l

    >>> dump_nt_sorted(in_both)
    <http://example.org> <http://example.org/ns#rel> <http://example.org/same> .
    <http://example.org> <http://example.org/ns#rel> _:cb1373e1895e37293a13204e8048bdcdc7 .
    _:cb1373e1895e37293a13204e8048bdcdc7 <http://example.org/ns#label> "Same" .

Only in first::

    >>> dump_nt_sorted(in_first)
    <http://example.org> <http://example.org/ns#rel> <http://example.org/a> .
    <http://example.org> <http://example.org/ns#rel> _:cb12f880a18a57364752aaeb157f2e66bb .
    _:cb12f880a18a57364752aaeb157f2e66bb <http://example.org/ns#label> "A" .

Only in second::

    >>> dump_nt_sorted(in_second)
    <http://example.org> <http://example.org/ns#rel> <http://example.org/b> .
    <http://example.org> <http://example.org/ns#rel> _:cb0a343fb77929ad37cf00a0317f06b801 .
    _:cb0a343fb77929ad37cf00a0317f06b801 <http://example.org/ns#label> "B" .
"""

# TODO:
# - Doesn't handle quads.
# - Add warning and/or safety mechanism before working on large graphs?
# - use this in existing Graph.isomorphic?


from rdflib.graph import Graph, ConjunctiveGraph, ReadOnlyGraphAggregate
from rdflib.term import BNode
import hashlib


class IsomorphicGraph(ConjunctiveGraph):
    """
    Ported from <http://www.w3.org/2001/sw/DataAccess/proto-tests/tools/rdfdiff.py>
    (Sean B Palmer's RDF Graph Isomorphism Tester).
    """

    def __init__(self, **kwargs):
        super(IsomorphicGraph, self).__init__(**kwargs)

    def __eq__(self, other):
        """Graph isomorphism testing."""
        if not isinstance(other, IsomorphicGraph):
            return False
        elif len(self) != len(other):
            return False
        elif list(self) == list(other):
            return True # TODO: really generally cheaper?
        return self.internal_hash() == other.internal_hash()

    def __ne__(self, other):
       """Negative graph isomorphism testing."""
       return not self.__eq__(other)

    def internal_hash(self):
        """
        This is defined instead of __hash__ to avoid a circular recursion
        scenario with the Memory store for rdflib which requires a hash lookup
        in order to return a generator of triples.
        """
        return _TripleCanonicalizer(self).to_hash()


class _TripleCanonicalizer(object):

    def __init__(self, graph, hashfunc=hash):
        self.graph = graph
        self.hashfunc = hashfunc

    def to_hash(self):
        return self.hashfunc(tuple(sorted(
                map(self.hashfunc, self.canonical_triples()) )))

    def canonical_triples(self):
        for triple in self.graph:
            yield tuple(self._canonicalize_bnodes(triple))

    def _canonicalize_bnodes(self, triple):
        for term in triple:
            if isinstance(term, BNode):
                yield BNode(value="cb%s"%self._canonicalize(term))
            else:
                yield term

    def _canonicalize(self, term, done=False):
        return self.hashfunc(tuple(sorted(self._vhashtriples(term, done))))

    def _vhashtriples(self, term, done):
        for triple in self.graph:
            if term in triple:
                yield tuple(self._vhashtriple(triple, term, done))

    def _vhashtriple(self, triple, target_term, done):
        for i, term in enumerate(triple):
            if not isinstance(term, BNode):
                yield term
            elif done or (term == target_term):
                yield i
            else:
                yield self._canonicalize(term, done=True)


def to_isomorphic(graph):
    if isinstance(graph, IsomorphicGraph):
        return graph
    return IsomorphicGraph(store=graph.store)


def isomorphic(graph1, graph2):
    """
    Compare graph for equality. Uses an algorithm to compute unique hashes
    which takes bnodes into account.

    Examples::

        >>> g1 = Graph().parse(format='n3', data='''
        ...     @prefix : <http://example.org/ns#> .
        ...     <http://example.org> :rel <http://example.org/a> .
        ...     <http://example.org> :rel <http://example.org/b> .
        ...     <http://example.org> :rel [ :label "A bnode." ] .
        ... ''')
        >>> g2 = Graph().parse(format='n3', data='''
        ...     @prefix ns: <http://example.org/ns#> .
        ...     <http://example.org> ns:rel [ ns:label "A bnode." ] .
        ...     <http://example.org> ns:rel <http://example.org/b>,
        ...             <http://example.org/a> .
        ... ''')
        >>> isomorphic(g1, g2)
        True

        >>> g3 = Graph().parse(format='n3', data='''
        ...     @prefix : <http://example.org/ns#> .
        ...     <http://example.org> :rel <http://example.org/a> .
        ...     <http://example.org> :rel <http://example.org/b> .
        ...     <http://example.org> :rel <http://example.org/c> .
        ... ''')
        >>> isomorphic(g1, g3)
        False
    """
    return _TripleCanonicalizer(graph1).to_hash() == _TripleCanonicalizer(graph2).to_hash()


def to_canonical_graph(g1):
    """
    Creates a canonical, read-only graph where all bnode id:s are based on
    deterministical MD5 checksums, correlated with the graph contents.
    """
    graph = Graph()
    graph += _TripleCanonicalizer(g1, _md5_hash).canonical_triples()
    return ReadOnlyGraphAggregate([graph])


def graph_diff(g1, g2):
    """
    Returns three sets of triples: "in both", "in first" and "in second".
    """
    # bnodes have deterministic values in canonical graphs:
    cg1 = to_canonical_graph(g1)
    cg2 = to_canonical_graph(g2)
    in_both = cg1*cg2
    in_first = cg1-cg2
    in_second = cg2-cg1
    return (in_both, in_first, in_second)


def _md5_hash(t):
    h = hashlib.md5()
    for i in t:
        if isinstance(i, tuple):
            h.update(_md5_hash(i))
        else:
            h.update("%s" % i)
    return h.hexdigest()


_MOCK_BNODE = BNode()

def similar(g1, g2):
    """
    Checks if the two graphs are "similar", by comparing sorted triples where
    all bnodes have been replaced by a singular mock bnode (the
    ``_MOCK_BNODE``).

    This is a much cheaper, but less reliable, alternative to the comparison
    algorithm in ``isomorphic``.
    """
    return all(t1 == t2 for (t1, t2) in _squashed_graphs_triples(g1, g2))

def _squashed_graphs_triples(g1, g2):
    for (t1, t2) in zip(sorted(_squash_graph(g1)), sorted(_squash_graph(g2))):
        yield t1, t2

def _squash_graph(graph):
    return (_squash_bnodes(triple) for triple in graph)

def _squash_bnodes(triple):
    return tuple((isinstance(t, BNode) and _MOCK_BNODE) or t for t in triple)


