from rdflib.graph import Graph
from test.utils.namespace import EGDO


def populate_graph(graph: Graph) -> None:
    graph.add((EGDO.subject, EGDO.predicate, EGDO.object))


__all__ = ["populate_graph"]
