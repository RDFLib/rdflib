from rdflib.Node import Node

class Identifier(Node, unicode): # we allow Identifiers to be Nodes in our Graph
    """
    See http://www.w3.org/2002/07/rdf-identifer-terminology/
    regarding choice of terminology.
    """
    __slots__ = ()
