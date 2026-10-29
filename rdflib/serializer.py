"""Serializer plugin interface.

The RDF serialization plugins used during
[RDFlib's common serialization of a graph][rdflib.graph.Graph.serialize]
is described in this module.

TODO: info for how to write a serializer that can plugin to rdflib.
See also [`rdflib.plugin`][rdflib.plugin]

All builtin RDF Serializer are listed
under [`rdflib.plugins.serializers`][rdflib.plugins.serializers].
"""

from __future__ import annotations

import re
from typing import IO, TYPE_CHECKING, Any, TypeVar, Union
from urllib.parse import urljoin

from rdflib.term import URIRef

if TYPE_CHECKING:
    from rdflib.graph import Graph


__all__ = ["Serializer"]

_StrT = TypeVar("_StrT", bound=str)


class Serializer:
    """Base class for RDF Serializer.

    New Serializer can be registered as plugin as described
    in [`rdflib.plugin`][rdflib.plugin].
    """

    def __init__(self, store: Graph):
        self.store: Graph = store
        self.encoding: str = "utf-8"
        self.base: str | None = None

    def _get_base(self, base: str | None, **args: Any) -> str | None:
        """Resolve the base passed from Graph.serialize."""
        return self.store.base if base is None else base

    def serialize(
        self,
        stream: IO[bytes],
        base: str | None = None,
        encoding: str | None = None,
        **args: Any,
    ) -> None:
        """Abstract method. Print [Graph][rdflib.graph.Graph].
        Used in [Graph.serialize][rdflib.graph.Graph.serialize]

        Serialize Graph

        Args:
            stream: The destination to serialize the graph to.
            base: The base IRI for formats that support it.
            encoding: Encoding of output.
            args: Additional arguments to pass to the Serializer that will be used.
        """

    def relativize(self, uri: _StrT) -> Union[_StrT, URIRef]:
        """Shorten an IRI only if the reference resolves back to that IRI."""
        base = self.base
        if base is not None and uri.startswith(base):
            relative = uri[len(base) :]
            # RFC 3986 forbids colons in the first relative path segment,
            # even when urljoin does not recognize it as a scheme.
            if re.match(r"[^/?#]*:", relative):
                return uri
            # A shared string prefix need not be a valid relative reference.
            # Fragments are not part of the base used for IRI resolution.
            try:
                resolved = urljoin(base.split("#", 1)[0], relative)
            except ValueError:
                return uri
            if resolved == str(uri):
                return URIRef(relative)
        return uri
