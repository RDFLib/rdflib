#!/usr/bin/env python2.7
# encoding: utf-8
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

"""Convert (to and) from rdflib graphs to other well known graph libraries.

Currently the following libraries are supported:
- networkx: MultiDiGraph, DiGraph, Graph
"""

import logging
logger = logging.getLogger(__name__)

def rdflib_to_networkx_multidigraph(graph, triple_attr=True, **edge_attrs):
    """Converts the given graph into a networkx.MultiDiGraph.

    The subjects and objects are the later nodes of the MultiDiGraph.
    The predicates are used as edge keys (to identify multi-edges).

    Arguments:
        triple_attr: Adds a 'triple' attribute to each edge.
        **edge_attrs: Default edge attributes

    Returns:
        networkx.MultiDiGraph

    >>> from rdflib import Graph, URIRef, Literal
    >>> g = Graph()
    >>> a, b, l = URIRef('a'), URIRef('b'), Literal('l')
    >>> p, q = URIRef('p'), URIRef('q')
    >>> edges = [(a, p, b), (a, q, b), (b, p, a), (b, p, l)]
    >>> for t in edges:
    ...     g.add(t)
    ...
    >>> mdg = rdflib_to_networkx_multidigraph(g)
    >>> len(mdg.edges())
    4
    >>> mdg.has_edge(a, b)
    True
    >>> mdg.has_edge(a, b, key=p)
    True
    >>> mdg.has_edge(a, b, key=q)
    True
    >>> mdg[a][b][p]['triple'] == (a, p, b)
    True
    """
    import networkx as nx
    mdg = nx.MultiDiGraph()
    for s, p, o in graph:
        d = dict(**edge_attrs)
        if triple_attr:
            d['triple'] = (s, p, o)
        mdg.add_edge(s, o, key=p, **d)
    return mdg

def _rdflib_to_networkx_graph(graph,
                              nxgraph,
                              calc_weights=True,
                              triples_attr=True,
                              **edge_attrs):
    """Helper method for graph and digraph, modifies nxgraph in-place!"""
    for s, p, o in graph:
        data = nxgraph.get_edge_data(s, o)
        if data is None:
            # no edge yet, set defaults
            data = dict(**edge_attrs)
            if calc_weights:
                data['weight'] = 1
            if triples_attr:
                data['triples'] = [(s, p, o)]
            nxgraph.add_edge(s, o, data)
        else:
            # already have an edge, just update attributes
            if calc_weights:
                data['weight'] += 1
            if triples_attr:
                data['triples'].append((s, p, o))

def rdflib_to_networkx_digraph(graph,
                               calc_weights=True,
                               triples_attr=True,
                               **edge_attrs):
    """Converts the given graph into a networkx.DiGraph.

    As an rdflib.Graph() can contain multiple edges between nodes, by default
    adds the a 'triples' attribute to the single DiGraph edge with a list of
    all triples between s and o.
    Also by default calculates the edge weight as the length of triples.

    Args:
        calc_weights: If true calculate multi-graph edge-count as edge 'weight'
        triples_attr: If true each edge will have a 'triples' attr.
        **edge_attrs: Attributes added to each edge.

    Returns:
        networkx.DiGraph

    >>> from rdflib import Graph, URIRef, Literal
    >>> g = Graph()
    >>> a, b, l = URIRef('a'), URIRef('b'), Literal('l')
    >>> p, q = URIRef('p'), URIRef('q')
    >>> edges = [(a, p, b), (a, q, b), (b, p, a), (b, p, l)]
    >>> for t in edges:
    ...     g.add(t)
    ...
    >>> dg = rdflib_to_networkx_digraph(g)
    >>> dg[a][b]['weight']
    2
    >>> sorted(dg[a][b]['triples']) == [(a, p, b), (a, q, b)]
    True
    >>> len(dg.edges())
    3
    >>> dg.size()
    3
    >>> dg.size(weight='weight')
    4.0
    """
    import networkx as nx
    dg = nx.DiGraph()
    _rdflib_to_networkx_graph(graph, dg, calc_weights,
                              triples_attr, **edge_attrs)
    return dg


def rdflib_to_networkx_graph(graph,
                             calc_weights=True,
                             triples_attr=True,
                             **edge_attrs):
    """Converts the given graph into a networkx.Graph.

    As an rdflib.Graph() can contain multiple directed edges between nodes, by
    default adds the a 'triples' attribute to the single DiGraph edge with a
    list of triples between s and o in graph.
    Also by default calculates the edge weight as the len(triples).

    Args:
        calc_weights: If true calculate multi-graph edge-count as edge 'weight'.
        triples_attr: If true each edge will have a 'triples' attr.
        **edge_attrs: Attributes added to each edge.

    Returns:
        networkx.Graph

    >>> from rdflib import Graph, URIRef, Literal
    >>> g = Graph()
    >>> a, b, l = URIRef('a'), URIRef('b'), Literal('l')
    >>> p, q = URIRef('p'), URIRef('q')
    >>> edges = [(a, p, b), (a, q, b), (b, p, a), (b, p, l)]
    >>> for t in edges:
    ...     g.add(t)
    ...
    >>> ug = rdflib_to_networkx_graph(g)
    >>> ug[a][b]['weight']
    3
    >>> sorted(ug[a][b]['triples']) == [(a, p, b), (a, q, b), (b, p, a)]
    True
    >>> len(ug.edges())
    2
    >>> ug.size()
    2
    >>> ug.size(weight='weight')
    4.0
    """
    import networkx as nx
    g = nx.Graph()
    _rdflib_to_networkx_graph(graph, g, calc_weights,
                              triples_attr, **edge_attrs)
    return g


def main(): # pragma: no cover
    import sys
    import logging.config
    logging.basicConfig(level=logging.DEBUG)

    import nose
    nose.run(argv=[sys.argv[0], sys.argv[0], '-v', '--with-doctest'])

if __name__ == '__main__':
    main()
