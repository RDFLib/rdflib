from test.utils.namespace import EGDO

from rdflib.graph import ConjunctiveGraph, Graph


def populate_graph(graph: Graph) -> None:
    assert isinstance(graph, ConjunctiveGraph)

    egdo_graph = graph.get_context(EGDO.graph)
    egdo_graph.add((EGDO.subject, EGDO.predicate, EGDO.object))


__all__ = ["populate_graph"]
