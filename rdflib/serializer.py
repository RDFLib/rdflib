"""
Serializer plugin interface.

This module is useful for those wanting to write a serializer that can
plugin to rdflib. If you are wanting to invoke a serializer you likely
want to do so through the Graph class serialize method.

TODO: info for how to write a serializer that can plugin to rdflib.
See also rdflib.plugin

"""

from __future__ import annotations

from typing import IO, TYPE_CHECKING, Any, Optional, TypeVar, Union

from rdflib.term import URIRef

if TYPE_CHECKING:
    from rdflib.graph import Graph


__all__ = ["Serializer"]

_StrT = TypeVar("_StrT", bound=str)


class Serializer:
    def __init__(self, store: Graph):
        self.store: Graph = store
        self.encoding: str = "utf-8"
        self.base: Optional[str] = None

    def serialize(
        self,
        stream: IO[bytes],
        base: Optional[str] = None,
        encoding: Optional[str] = None,
        **args: Any,
    ) -> None:
        """Abstract method"""

    def relativize(self, uri: _StrT) -> Union[_StrT, URIRef]:
        base = self.base
        if base is not None and uri.startswith(base):
            # type error: Incompatible types in assignment (expression has type "str", variable has type "Node")
            uri = URIRef(uri.replace(base, "", 1))  # type: ignore[assignment]
        return uri
