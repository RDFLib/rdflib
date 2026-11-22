from rdflib.graph import ConjunctiveGraph, Graph
from rdflib.namespace import XSD
from rdflib.term import Literal
from test.utils.namespace import EGDC, EGSCHEME, EGURN


def populate_graph(graph: Graph) -> None:
    assert isinstance(graph, ConjunctiveGraph)

    graph.add((EGSCHEME.subject, EGSCHEME.predicate, EGSCHEME.object))
    graph.add((EGDC.subject, EGDC.predicate, Literal("typeless")))
    graph.add((EGURN.subject, EGURN.predicate, EGURN.object))

    egscheme_graph = graph.get_context(EGSCHEME.graph)
    egscheme_graph.add(
        (EGDC.subject, EGDC.predicate, Literal("日本語の表記体系", lang="jpx"))
    )
    egscheme_graph.add((EGURN.subject, EGSCHEME.predicate, EGSCHEME.subject))
    egscheme_graph.add((EGSCHEME.subject, EGSCHEME.predicate, EGSCHEME.object))
    egscheme_graph.add((EGSCHEME.subject, EGSCHEME.predicate, Literal(12)))

    egurn_graph = graph.get_context(EGURN.graph)
    egurn_graph.add((EGSCHEME.subject, EGSCHEME.predicate, EGSCHEME.object))
    egurn_graph.add((EGSCHEME.subject, EGDC.predicate, EGDC.object))
    egurn_graph.add(
        (EGSCHEME.subject, EGDC.predicate, Literal("XSD string", datatype=XSD.string))
    )


__all__ = ["populate_graph"]
