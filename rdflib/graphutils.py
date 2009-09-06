# -*- coding: UTF-8 -*-
from rdflib.graph import ConjunctiveGraph
from rdflib.term import BNode


class IsomorphicGraph(ConjunctiveGraph):
    """
    Ported from <http://www.w3.org/2001/sw/DataAccess/proto-tests/tools/rdfdiff.py>
     (Sean B Palmer's RDF Graph Isomorphism Tester).
    """
    def __init__(self, **kwargs):
        super(IsomorphicGraph, self).__init__(**kwargs)
        self.hash = None

    def __eq__(self, other):
        """Graph isomorphism testing."""
        if not isinstance(other, IsomorphicGraph): return False
        elif len(self) != len(other): return False
        elif list(self) == list(other): return True # @@
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
        return hash(tuple(sorted(self.hashtriples())))

    def hashtriples(self):
        for triple in self:
            g = ((isinstance(t, BNode) and self.vhash(t)) or t for t in triple)
            yield hash(tuple(g))

    def vhash(self, term, done=False):
        return tuple(sorted(self.vhashtriples(term, done)))

    def vhashtriples(self, term, done):
        for t in self:
            if term in t: yield tuple(self.vhashtriple(t, term, done))

    def vhashtriple(self, triple, term, done):
        for p in xrange(3):
            if not isinstance(triple[p], BNode): yield triple[p]
            elif done or (triple[p] == term): yield p
            else: yield self.vhash(triple[p], done=True)


def isomorphic(graph1, graph2):
    """
    Compare graph for equality. Uses IsomorphicGraph to compute unique hashes
    which takes bnodes into account. Examples::

        >>> from rdflib.graph import Graph
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
    return IsomorphicGraph(store=graph1.store) == IsomorphicGraph(store=graph2.store)


# TODO: Useful? A cheaper but bnode-squashing comparison:
#def similar_graphs(g1, g2):
#    return all(t1 == t2 for (t1, t2) in similar_graphs_triples(g1, g2))
#
#def similar_graphs_triples(g1, g2):
#    for (t1, t2) in zip(sorted(_squash_graph(g1)), sorted(_squash_graph(g2))):
#        yield t1, t2
#
#def _squash_graph(graph):
#    return (_squash_bnodes(triple) for triple in graph)
#
#_BAD_NODE = BNode()
#def _squash_bnodes(triple):
#    return tuple((isinstance(t, BNode) and _BAD_NODE) or t for t in triple)


