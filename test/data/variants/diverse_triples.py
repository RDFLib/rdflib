from rdflib.graph import Graph
from rdflib.term import Literal
from test.utils.namespace import EGDC, EGSCHEME, EGURN


def populate_graph(graph: Graph) -> None:
    assert isinstance(graph, Graph)

    graph.add((EGDC.subject, EGDC.predicate, Literal("日本語の表記体系", lang="jpx")))
    graph.add((EGURN.subject, EGSCHEME.predicate, EGSCHEME.subject))

    graph.add((EGSCHEME.object, EGDC.predicate, Literal("XSD string")))
    graph.add((EGSCHEME.subject, EGSCHEME.predicate, EGSCHEME.object))
    graph.add((EGSCHEME.subject, EGSCHEME.predicate, Literal(12)))


__all__ = ["populate_graph"]
