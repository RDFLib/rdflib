"""
Serializer plugin interface.

This module is useful for those wanting to write a serializer that can
plugin to rdflib. If you are wanting to invoke a serializer you likely
want to do so through the Graph class serialize method.

TODO: info for how to write a serializer that can plugin to rdflib.
See also rdflib.plugin

"""

from typing import IO, TYPE_CHECKING, Optional

from rdflib.term import URIRef

if TYPE_CHECKING:
    from rdflib.graph import Graph

__all__ = ["Serializer"]


class Serializer:
    def __init__(self, store: "Graph"):
        self.store: "Graph" = store
        self.encoding: str = "utf-8"
        self.base: Optional[str] = None

    def serialize(
        self,
        stream: IO[bytes],
        base: Optional[str] = None,
        encoding: Optional[str] = None,
        **args,
    ) -> None:
        """Abstract method"""

    def relativize(self, uri: str):
        base = self.base
        if base is not None and uri.startswith(base):
            uri = URIRef(uri.replace(base, "", 1))
        return uri
