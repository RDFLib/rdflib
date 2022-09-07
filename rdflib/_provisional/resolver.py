import abc
from typing import Optional, Tuple

from rdflib.parser import InputSource


class URIResolutionForbiddenError(ValueError):
    def __init__(self, uri: str, reason: Optional[str], *args: object) -> None:
        super().__init__(
            (
                f"resolution of {uri!r} not allowed"
                f"{ f': {reason}'  if reason is not None else ''  }"
            ),
            uri,
            reason,
            *args,
        )


class URIResolver(abc.ABC):
    """
    Resolves a file resource
    """

    @abc.abstractmethod
    def resolve_uri(self, uri: str, format: Optional[str] = None) -> InputSource:
        ...


class FilteringURIResolver(URIResolver):
    def __init__(self, backing_resolver: URIResolver) -> None:
        self._backing_resolver = backing_resolver

    @property
    def backing_resolver(self) -> URIResolver:
        return self._backing_resolver

    @abc.abstractmethod
    def is_uri_resolution_allowed(
        self, uri: str, format: Optional[str] = None
    ) -> Tuple[bool, Optional[str]]:
        ...

    def resolve_uri(self, uri: str, format: Optional[str] = None) -> InputSource:
        allowed, dissalowed_reason = self.is_uri_resolution_allowed(uri, format)
        if not allowed:
            raise URIResolutionForbiddenError(uri=uri, reason=dissalowed_reason)
        return super().resolve_uri(uri, format)


# _URIStringFilterType = Callable[[str], bool]


# class FilteringURIResolver(URIResolver):

#     def __init__(self, backing_resolver: URIResolver, accept_filters: Optional[List]) -> None:
#         super().__init__()
#         self._backing_resolver = backing_resolver
#         self._accept_filters = accept_filters


#     def _filter()
