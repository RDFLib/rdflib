from __future__ import annotations

import io
import typing as t

from rdflib.graph import DATASET_DEFAULT_GRAPH_ID, Dataset, Graph
from rdflib.term import IdentifiedNode, URIRef

if t.TYPE_CHECKING:
    from rdflib.contrib.rdf4j.client import ObjectType, PredicateType, SubjectType


def build_context_param(
    params: dict[str, str],
    graph_name: IdentifiedNode | t.Iterable[IdentifiedNode] | str | None = None,
) -> None:
    """Build the RDF4J http context query parameters dictionary.

    !!! Note
        This mutates the params dictionary key `context`.

    Args:
        params: The `httpx.Request` parameter dictionary.
        graph_name: The graph name or iterable of graph names.

            This is the `context` query parameter value.
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


def build_spo_param(
    params: dict[str, str],
    subj: SubjectType = None,
    pred: PredicateType = None,
    obj: ObjectType = None,
) -> None:
    """Build the RDF4J http subj, predicate, and object query parameters dictionary.

    !!! Note
        This mutates the params dictionary key `subj`, `pred`, and `obj`.

    Args:
        params: The `httpx.Request` parameter dictionary.
        subj: The `subj` query parameter value.
        pred: The `pred` query parameter value.
        obj: The `obj` query parameter value.
    """
    if subj is not None:
        params["subj"] = subj.n3()
    if pred is not None:
        params["pred"] = pred.n3()
    if obj is not None:
        params["obj"] = obj.n3()


def build_infer_param(
    params: dict[str, str],
    infer: bool = True,
) -> None:
    """Build the RDF4J http infer query parameters dictionary.

    !!! Note
        This mutates the params dictionary key `infer`.

    Args:
        params: The `httpx.Request` parameter dictionary.
        infer: The `infer` query parameter value.
    """
    if not infer:
        params["infer"] = "false"


def rdf_payload_to_stream(
    data: str | bytes | t.BinaryIO | Graph | Dataset,
) -> tuple[t.BinaryIO, bool]:
    """Convert an RDF payload into a file-like object.

    Args:
        data: The RDF payload.

            This can be a python `str`, `bytes`, `BinaryIO`, or a
            [`Graph`][rdflib.graph.Graph] or [`Dataset`][rdflib.graph.Dataset].

    Returns:
        A tuple containing the file-like object and a boolean indicating whether the
        immediate caller should close the stream.
    """
    if isinstance(data, str):
        # Check if it looks like a file path. Assumes file path length is less than 260.
        if "\n" not in data and len(data) < 260:
            try:
                stream = open(data, "rb")
                should_close = True
            except (FileNotFoundError, OSError):
                # Treat as raw string content
                stream = io.BytesIO(data.encode("utf-8"))
                should_close = False
        else:
            # Treat as raw string content
            stream = io.BytesIO(data.encode("utf-8"))
            should_close = False
    elif isinstance(data, bytes):
        stream = io.BytesIO(data)
        should_close = False
    elif isinstance(data, (Graph, Dataset)):
        if data.context_aware:
            stream = io.BytesIO(
                data.serialize(format="application/n-quads", encoding="utf-8")
            )
        else:
            stream = io.BytesIO(
                data.serialize(format="application/n-triples", encoding="utf-8")
            )
        should_close = True
    else:
        # Assume it's already a file-like object
        stream = data
        should_close = False

    return stream, should_close
