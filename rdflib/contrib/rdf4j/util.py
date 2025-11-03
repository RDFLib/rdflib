from __future__ import annotations

import typing as t

from rdflib.graph import DATASET_DEFAULT_GRAPH_ID
from rdflib.term import IdentifiedNode, URIRef


def build_context_param(
    params: dict[str, str],
    graph_name: IdentifiedNode | t.Iterable[IdentifiedNode] | str | None = None,
) -> None:
    """Build the RDF4J http context param.

    !!! Note
        This mutates the params dictionary key `context`.

    Args:
        params: The `httpx.Request` parameter dictionary.
        graph_name: The graph name or iterable of graph names.
    """
    if graph_name is not None and isinstance(graph_name, IdentifiedNode):
        if graph_name == DATASET_DEFAULT_GRAPH_ID:
            # Special RDF4J null value for context-less statements.
            params["context"] = "null"
        else:
            params["context"] = graph_name.n3()
    elif graph_name is not None and isinstance(graph_name, str):
        params["context"] = URIRef(graph_name).n3()
    elif graph_name is not None and isinstance(graph_name, t.Iterable):
        graph_names = ",".join([x.n3() for x in graph_name])
        params["context"] = graph_names
