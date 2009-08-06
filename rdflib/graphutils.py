# -*- coding: UTF-8 -*-
from rdflib.graph import Graph


class IsomorphicGraph(Graph):
    """
    Ported from <http://www.w3.org/2001/sw/DataAccess/proto-tests/tools/rdfdiff.py>
     (Sean B Palmer's RDF Graph Isomorphism Tester).
    """
    def __init__(self, **kargs):
        super(IsomorphicGraph,self).__init__(**kargs)
        self.hash = None

    def internal_hash(self):
        """
        This is defined instead of __hash__ to avoid a circular recursion
        scenario with the Memory store for rdflib which requires a hash lookup
        in order to return a generator of triples.
        """
        return hash(tuple(sorted(self.hashtriples())))

    def hashtriples(self):
        for triple in self:
            g = ((isinstance(t,BNode) and self.vhash(t)) or t for t in triple)
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

    def __eq__(self, G):
        """Graph isomorphism testing."""
        if not isinstance(G, IsomorphicGraph): return False
        elif len(self) != len(G): return False
        elif list.__eq__(list(self),list(G)): return True # @@
        return self.internal_hash() == G.internal_hash()

    def __ne__(self, G):
       """Negative graph isomorphism testing."""
       return not self.__eq__(G)

