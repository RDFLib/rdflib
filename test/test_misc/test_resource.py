from rdflib import Graph
from rdflib.namespace import RDFS
from rdflib.resource import Resource


def test_properties(rdfs_graph: Graph) -> None:
    """
    The properties of a `rdflib.resource.Resource` work as expected.
    """
    cres = Resource(rdfs_graph, RDFS.Container)
    assert cres.graph is rdfs_graph
    assert cres.identifier == RDFS.Container
