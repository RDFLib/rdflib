from test.utils.namespace import EGDO

from rdflib.graph import Graph


def populate_graph(graph: Graph) -> None:
    graph.add((EGDO.subject, EGDO.predicate, EGDO.object))


__all__ = ["populate_graph"]
