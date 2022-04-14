import logging
import pytest
import rdflib
import rdflib.term

logger = logging.getLogger(__name__)


@pytest.mark.xfail(
    reason="""\
N3 serializer randomly omits triple. See https://github.com/RDFLib/rdflib/issues/1807
""",
    raises=AssertionError,
)
def test():
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
        rdflib.term.URIRef('http://test/a'),
        rdflib.term.URIRef('http://test/d'),
        rdflib.term.URIRef('http://test/c'),
    ) in graph2
