"""
Utilities for interacting with SHACL Shapes Graphs more easily.
"""

from __future__ import annotations

from typing import Optional, Union

from rdflib import Graph, Literal, URIRef, paths
from rdflib.namespace import RDF, SH
from rdflib.paths import Path
from rdflib.term import Node


class SHACLPathError(Exception):
    pass


# This implementation is roughly based on
# pyshacl.helper.sparql_query_helper::SPARQLQueryHelper._shacl_path_to_sparql_path
def parse_shacl_path(
    shapes_graph: Graph,
    path_identifier: Node,
) -> Union[URIRef, Path]:
    """
    Parse a valid SHACL path (e.g. the object of a triple with predicate sh:path)
    from a :class:`~rdflib.graph.Graph` as a :class:`~rdflib.term.URIRef` if the path
    is simply a predicate or a :class:`~rdflib.paths.Path` otherwise.

    :param shapes_graph: A :class:`~rdflib.graph.Graph` containing the path to be parsed
    :param path_identifier: A :class:`~rdflib.term.Node` of the path
    :return: A :class:`~rdflib.term.URIRef` or a :class:`~rdflib.paths.Path`
    """
    path: Optional[Union[URIRef, Path]] = None

    # Literals are not allowed.
    if isinstance(path_identifier, Literal):
        raise TypeError("Literals are not a valid SHACL path.")

    # If a path is a URI, that's the whole path.
    elif isinstance(path_identifier, URIRef):
        if path_identifier == RDF.nil:
            raise SHACLPathError(
                "A list of SHACL Paths must contain at least two path items."
            )
        path = path_identifier

    # Handle Sequence Paths
    elif shapes_graph.value(path_identifier, RDF.first) is not None:
        sequence = list(shapes_graph.items(path_identifier))
        if len(sequence) < 2:
            raise SHACLPathError(
                "A list of SHACL Sequence Paths must contain at least two path items."
            )
        path = paths.SequencePath(
            *(parse_shacl_path(shapes_graph, path) for path in sequence)
        )

    # Handle sh:inversePath
    elif inverse_path := shapes_graph.value(path_identifier, SH.inversePath):
        path = paths.InvPath(parse_shacl_path(shapes_graph, inverse_path))

    # Handle sh:alternativePath
    elif alternative_path := shapes_graph.value(path_identifier, SH.alternativePath):
        alternatives = list(shapes_graph.items(alternative_path))
        if len(alternatives) < 2:
            raise SHACLPathError(
                "List of SHACL alternate paths must have at least two path items."
            )
        path = paths.AlternativePath(
            *(
                parse_shacl_path(shapes_graph, alternative)
                for alternative in alternatives
            )
        )

    # Handle sh:zeroOrMorePath
    elif zero_or_more_path := shapes_graph.value(path_identifier, SH.zeroOrMorePath):
        path = paths.MulPath(parse_shacl_path(shapes_graph, zero_or_more_path), "*")

    # Handle sh:oneOrMorePath
    elif one_or_more_path := shapes_graph.value(path_identifier, SH.oneOrMorePath):
        path = paths.MulPath(parse_shacl_path(shapes_graph, one_or_more_path), "+")

    # Handle sh:zeroOrOnePath
    elif zero_or_one_path := shapes_graph.value(path_identifier, SH.zeroOrOnePath):
        path = paths.MulPath(parse_shacl_path(shapes_graph, zero_or_one_path), "?")

    # Raise error if none of the above options were found
    elif path is None:
        raise SHACLPathError(f"Cannot parse {repr(path_identifier)} as a SHACL Path.")

    return path
