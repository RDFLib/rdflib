import logging
from test.utils import GraphHelper

import rdflib
import rdflib.term
from rdflib import Graph
from rdflib.graph import QuotedGraph
from rdflib.namespace import Namespace
from rdflib.plugins.parsers.notation3 import LOG_implies_URI
from rdflib.term import BNode, URIRef

logger = logging.getLogger(__name__)


def test_implies():
    test_n3 = """@prefix rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
    @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
    @prefix : <http://test/> .
    {:a :b :c;a :foo} => {:a :d :c,?y} .
    _:foo a rdfs:Class .
    :a :d :c ."""
    graph1 = rdflib.Graph()
    graph1.parse(data=test_n3, format="n3")

    if logger.isEnabledFor(logging.DEBUG):
        logging.debug("sorted(list(graph1)) = \n%s", sorted(list(graph1)))

    """
    >>> sorted(list(graph1))
    [
        (
            rdflib.term.BNode('fde0470d85a044b6780f0c6804b119063b1'),
            rdflib.term.URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type'),
            rdflib.term.URIRef('http://www.w3.org/2000/01/rdf-schema#Class')
        ),
        (
            rdflib.term.URIRef('http://test/a'),
            rdflib.term.URIRef('http://test/d'),
            rdflib.term.URIRef('http://test/c')
        ),
        (
            <Graph identifier=_:Formula2 (<class 'rdflib.graph.QuotedGraph'>)>,
            rdflib.term.URIRef('http://www.w3.org/2000/10/swap/log#implies'),
            <Graph identifier=_:Formula3 (<class 'rdflib.graph.QuotedGraph'>)>
        )
    ]
    """

    graph2 = rdflib.Graph()
    graph2.parse(data=graph1.serialize(format="n3"), format="n3")
    assert (
        rdflib.term.URIRef("http://test/a"),
        rdflib.term.URIRef("http://test/d"),
        rdflib.term.URIRef("http://test/c"),
    ) in graph2


EG = Namespace("http://example.com/")

LOG_implies = URIRef(LOG_implies_URI)


def test_merging() -> None:
    data_a = """
    @prefix : <http://example.com/>.
    :a :b :c.
    """
    data_b = """
    @prefix : <http://example.com/>.
    {:a :b :c} => {:d :e :f}.
    """
    graph = Graph()
    assert (EG.a, EG.b, EG.c) not in graph

    graph.parse(data=data_a, format="n3")
    assert (EG.a, EG.b, EG.c) in graph

    graph.parse(data=data_b, format="n3")
    assert (EG.a, EG.b, EG.c) in graph
    assert len(set(graph.triples((None, LOG_implies, None)))) == 1

    data_s = graph.serialize(format="n3")
    logging.debug("data_s = %s", data_s)

    graph = Graph()
    graph.parse(data=data_s, format="n3")
    quad_set = GraphHelper.triple_set(graph)

    assert (EG.a, EG.b, EG.c) in graph
    assert len(set(graph.triples((None, LOG_implies, None)))) == 1

    logging.debug("quad_set = %s", quad_set)


def test_single_simple_triple() -> None:
    data_a = """
    @prefix : <http://example.com/>.
    :a :b :c.
    """
    graph = Graph()
    assert (EG.a, EG.b, EG.c) not in graph

    graph.parse(data=data_a, format="n3")
    assert (EG.a, EG.b, EG.c) in graph

    data_s = graph.serialize(format="n3")
    logging.debug("data_s = %s", data_s)

    graph = Graph()
    graph.parse(data=data_s, format="n3")
    quad_set = GraphHelper.triple_set(graph)

    assert (EG.a, EG.b, EG.c) in graph

    logging.debug("quad_set = %s", quad_set)


def test_implies_nothing() -> None:
    triple_a = (EG.a, EG.b, EG.c)
    graph = Graph()
    qgraph_a = QuotedGraph(graph.store, BNode())
    qgraph_a.add(triple_a)
    qgraph_b = QuotedGraph(graph.store, BNode())
    graph.add((qgraph_a, LOG_implies, qgraph_b))
    graph.add(triple_a)

    data_s = graph.serialize(format="n3")
    logging.debug("data_s = %s", data_s)

    rgraph = Graph()
    rgraph.parse(data=data_s, format="n3")
    graph_qs, qgraph_a_qs, qgraph_b_qs = GraphHelper.triple_sets(
        (rgraph, qgraph_a, qgraph_b)
    )
    logging.debug("graph_qs = %s", graph_qs)
    logging.debug("qgraph_a_qs = %s", qgraph_a_qs)
    logging.debug("qgraph_b_qs = %s", qgraph_b_qs)

    assert len(graph_qs) == 2
    assert len(qgraph_a_qs) == 1
    assert len(qgraph_b_qs) == 0

    triple_b = (qgraph_a_qs, LOG_implies, qgraph_b_qs)

    logging.debug("triple_a = %s", triple_a)
    logging.debug("triple_b = %s", triple_b)

    assert triple_a in graph_qs
    assert triple_a in rgraph
    assert triple_b in graph_qs
