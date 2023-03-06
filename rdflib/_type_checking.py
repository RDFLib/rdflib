"""
This module contains type aliases that should only be used when type checking
as it would otherwise introduce a runtime dependency on `typing_extensions` for
older python versions which is not desirable.

This was made mainly to accommodate ``sphinx-autodoc-typehints`` which cannot
recognize type aliases from imported files if the type aliases are defined
inside ``if TYPE_CHECKING:``. So instead of placing the type aliases in normal
modules inside ``TYPE_CHECKING`` guards they are in this file which should only
be imported inside ``TYPE_CHECKING`` guards.

.. important::
    Things inside this module are not for use outside of RDFLib
    and this module is not part the the RDFLib public API.
"""
from __future__ import annotations

import sys
from typing import Any, BinaryIO, Callable
from urllib.request import Request
from urllib.response import addinfourl

__all__ = ["_NamespaceSetString", "_URLOpenerType", "_FileURIOpener"]


if sys.version_info >= (3, 8):
    from typing import Literal as PyLiteral, Protocol
else:
    from typing_extensions import Literal as PyLiteral, Protocol

_NamespaceSetString = PyLiteral["core", "rdflib", "none"]
_URLOpenerType = Callable[[Request], addinfourl]
_FileURIOpener = Callable[[str], BinaryIO]


# class _URLOpenerType(Protocol):
#     def __call__(self, url: Request) -> addinfourl:
#         ...


# class _FileURIOpener(Protocol):
#     def __call__(self, url: str) -> BinaryIO:
#         ...
