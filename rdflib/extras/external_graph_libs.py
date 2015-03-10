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

_identity = lambda x: x

def _rdflib_to_networkx_graph(
        graph,
        nxgraph,
        calc_weights,
        edge_attrs,
        transform_s=_identity, transform_o=_identity):
    """Helper method for multidigraph, digraph and graph.

    Modifies nxgraph in-place!

    Arguments:
        graph: an rdflib.Graph.
        nxgraph: a networkx.Graph/DiGraph/MultiDigraph.
        calc_weights: If True adds a 'weight' attribute to each edge according
            to the count of s,p,o triples between s and o, which is meaningful
            for Graph/DiGraph.
        edge_attrs: Callable to construct edge data from s, p, o.
           'triples' attribute is handled specially to be merged.
           'weight' should not be generated if calc_weights==True.
           (see invokers below!)
        transform_s: Callable to transform node generated from s.
        transform_o: Callable to transform node generated from o.
    """
    assert callable(edge_attrs)
    assert callable(transform_s)
    assert callable(transform_o)
    import networkx as nx
    for s, p, o in graph:
        ts, to = transform_s(s), transform_o(o)  # apply possible transformations
        data = nxgraph.get_edge_data(ts, to)
        if data is None or isinstance(nxgraph, nx.MultiDiGraph):
            # no edge yet, set defaults
            data = edge_attrs(s, p, o)
            if calc_weights:
                data['weight'] = 1
            nxgraph.add_edge(ts, to, **data)
        else:
            # already have an edge, just update attributes
            if calc_weights:
                data['weight'] += 1
            if 'triples' in data:
                d = edge_attrs(s, p, o)
                data['triples'].extend(d['triples'])

def rdflib_to_networkx_multidigraph(
        graph,
        edge_attrs=lambda s, p, o: {'key': p},
        **kwds):
    """Converts the given graph into a networkx.MultiDiGraph.

    The subjects and objects are the later nodes of the MultiDiGraph.
    The predicates are used as edge keys (to identify multi-edges).

    Arguments:
        graph: a rdflib.Graph.
        edge_attrs: Callable to construct later edge_attributes. It receives
            3 variables (s, p, o) and should construct a dictionary that is
            passed to networkx's add_edge(s, o, **attrs) function.

            By default this will include setting the MultiDiGraph key=p here.
            If you don't want to be able to re-identify the edge later on, you
            can set this to `lambda s, p, o: {}`. In this case MultiDiGraph's
            default (increasing ints) will be used.

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

    >>> mdg = rdflib_to_networkx_multidigraph(g, edge_attrs=lambda s,p,o: {})
    >>> mdg.has_edge(a, b, key=0)
    True
    >>> mdg.has_edge(a, b, key=1)
    True
    """
    import networkx as nx
    mdg = nx.MultiDiGraph()
    _rdflib_to_networkx_graph(graph, mdg, False, edge_attrs, **kwds)
    return mdg

def rdflib_to_networkx_digraph(
        graph,
        calc_weights=True,
        edge_attrs=lambda s, p, o: {'triples': [(s, p, o)]},
        **kwds):
    """Converts the given graph into a networkx.DiGraph.

    As an rdflib.Graph() can contain multiple edges between nodes, by default
    adds the a 'triples' attribute to the single DiGraph edge with a list of
    all triples between s and o.
    Also by default calculates the edge weight as the length of triples.

    Args:
        graph: a rdflib.Graph.
        calc_weights: If true calculate multi-graph edge-count as edge 'weight'
        edge_attrs: Callable to construct later edge_attributes. It receives
            3 variables (s, p, o) and should construct a dictionary that is
            passed to networkx's add_edge(s, o, **attrs) function.

            By default this will include setting the 'triples' attribute here,
            which is treated specially by us to be merged. Other attributes of
            multi-edges will only contain the attributes of the first edge.
            If you don't want the 'triples' attribute for tracking, set this to
            `lambda s, p, o: {}`.

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

    >>> dg = rdflib_to_networkx_graph(g, False, edge_attrs=lambda s,p,o:{})
    >>> 'weight' in dg[a][b]
    False
    >>> 'triples' in dg[a][b]
    False
    """
    import networkx as nx
    dg = nx.DiGraph()
    _rdflib_to_networkx_graph(graph, dg, calc_weights, edge_attrs, **kwds)
    return dg


def rdflib_to_networkx_graph(
        graph,
        calc_weights=True,
        edge_attrs=lambda s, p, o: {'triples': [(s, p, o)]},
        **kwds):
    """Converts the given graph into a networkx.Graph.

    As an rdflib.Graph() can contain multiple directed edges between nodes, by
    default adds the a 'triples' attribute to the single DiGraph edge with a
    list of triples between s and o in graph.
    Also by default calculates the edge weight as the len(triples).

    Args:
        graph: a rdflib.Graph.
        calc_weights: If true calculate multi-graph edge-count as edge 'weight'
        edge_attrs: Callable to construct later edge_attributes. It receives
            3 variables (s, p, o) and should construct a dictionary that is
            passed to networkx's add_edge(s, o, **attrs) function.

            By default this will include setting the 'triples' attribute here,
            which is treated specially by us to be merged. Other attributes of
            multi-edges will only contain the attributes of the first edge.
            If you don't want the 'triples' attribute for tracking, set this to
            `lambda s, p, o: {}`.

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

    >>> ug = rdflib_to_networkx_graph(g, False, edge_attrs=lambda s,p,o:{})
    >>> 'weight' in ug[a][b]
    False
    >>> 'triples' in ug[a][b]
    False
    """
    import networkx as nx
    g = nx.Graph()
    _rdflib_to_networkx_graph(graph, g, calc_weights, edge_attrs, **kwds)
    return g


def main(): # pragma: no cover
    import sys
    import logging.config
    logging.basicConfig(level=logging.DEBUG)

    import nose
    nose.run(argv=[sys.argv[0], sys.argv[0], '-v', '--with-doctest'])

if __name__ == '__main__':
    main()
