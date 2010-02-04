# -*- coding: utf-8 -*-
"""
A collection of utilities for canonicalizing and inspecting graphs.

Ported from <http://www.w3.org/2001/sw/DataAccess/proto-tests/tools/rdfdiff.py>
(Sean B Palmer's RDF Graph Isomorphism Tester).

IsomorphicGraph solves of the problem of deterministic bnode comparisons.
(Warning: the time to canonicalize bnodes may increase exponentially on larger
graphs - use with care!)

Example scenario - diffing two graphs::

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

Create canonical graphs (where bnodes have deterministic values)::

    >>> cg1 = iso1.canonical_graph()
    >>> cg2 = iso2.canonical_graph()

Present in both graphs::

    >>> def dump_nt_sorted(g):
    ...     for l in sorted(g.serialize(format='nt').splitlines()):
    ...         if l: print l

    >>> dump_nt_sorted(cg1*cg2)
    <http://example.org> <http://example.org/ns#rel> <http://example.org/same> .
    <http://example.org> <http://example.org/ns#rel> _:cb1373e1895e37293a13204e8048bdcdc7 .
    _:cb1373e1895e37293a13204e8048bdcdc7 <http://example.org/ns#label> "Same" .

Only in first::

    >>> dump_nt_sorted(cg1-cg2)
    <http://example.org> <http://example.org/ns#rel> <http://example.org/a> .
    <http://example.org> <http://example.org/ns#rel> _:cb12f880a18a57364752aaeb157f2e66bb .
    _:cb12f880a18a57364752aaeb157f2e66bb <http://example.org/ns#label> "A" .

Only in second::

    >>> dump_nt_sorted(cg2-cg1)
    <http://example.org> <http://example.org/ns#rel> <http://example.org/b> .
    <http://example.org> <http://example.org/ns#rel> _:cb0a343fb77929ad37cf00a0317f06b801 .
    _:cb0a343fb77929ad37cf00a0317f06b801 <http://example.org/ns#label> "B" .

"""

# TODO:
# - Doesn't handle quads yet.
# - Warning and/or safety mechanism before working on large graphs?
# - Redesign: create a read-only CanonicalGraph too/instead?
# - use this in existing Graph.isomorphic?

# Suggestions:
# - Create a proposed official canonicalization of bnode id:s (e.g. by
#   using md5 instead of (I assume) python's internal hash algorithm).

from rdflib.graph import Graph, ConjunctiveGraph
from rdflib.term import BNode

import hashlib
def _hash(t):
    h = hashlib.md5()
    for i in t:
        if isinstance(i, tuple):
            h.update(_hash(i))
        else:
            h.update("%s" % i)
    return h.hexdigest()



class IsomorphicGraph(ConjunctiveGraph):
    """
    """
    def __init__(self, **kwargs):
        super(IsomorphicGraph, self).__init__(**kwargs)
        #self.hash = None

    def __eq__(self, other):
        """Graph isomorphism testing."""
        if not isinstance(other, IsomorphicGraph): return False
        elif len(self) != len(other): return False
        elif list(self) == list(other): return True # @@
        return self.internal_hash() == other.internal_hash()

    def __ne__(self, other):
       """Negative graph isomorphism testing."""
       return not self.__eq__(other)

    def canonical_graph(self):
        # TODO: a read-only version (otherwise we have to recalculate canonical
        # bnodes for every change)
        graph = Graph()
        graph += self.canonical_triples()
        return graph

    def internal_hash(self):
        """
        This is defined instead of __hash__ to avoid a circular recursion
        scenario with the Memory store for rdflib which requires a hash lookup
        in order to return a generator of triples.
        """
        return _hash(tuple(sorted(
                map(_hash, self.canonical_triples()) )))

    def canonical_triples(self):
        for triple in self:
            yield tuple(self._canonicalize_bnodes(triple))

    def _canonicalize_bnodes(self, triple):
        for term in triple:
            if isinstance(term, BNode):
                yield BNode(value="cb%s"%self._canonicalize(term))
            else:
                yield term

    def _canonicalize(self, term, done=False):
        return _hash(tuple(sorted(self._vhashtriples(term, done))))

    def _vhashtriples(self, term, done):
        for triple in self:
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
    Compare graph for equality. Uses IsomorphicGraph to compute unique hashes
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
    return to_isomorphic(graph1) == to_isomorphic(graph2)


# TODO: Useful? A much cheaper but bnode-squashing comparison mechanism:
#def similar_graphs(g1, g2):
#    return all(t1 == t2 for (t1, t2) in _similar_graphs_triples(g1, g2))
#
#def _similar_graphs_triples(g1, g2):
#    for (t1, t2) in zip(sorted(_squash_graph(g1)), sorted(_squash_graph(g2))):
#        yield t1, t2
#
#def _squash_graph(graph):
#    return (_squash_bnodes(triple) for triple in graph)
#
#_MOCK_BNODE = BNode()
#def _squash_bnodes(triple):
#    return tuple((isinstance(t, BNode) and _MOCK_BNODE) or t for t in triple)

