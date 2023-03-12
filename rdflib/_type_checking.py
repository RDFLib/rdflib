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

import sys

__all__ = [
    "_NamespaceSetString",
    "_MulPathMod",
]


if sys.version_info >= (3, 8):
    from typing import Literal as PyLiteral
else:
    from typing_extensions import Literal as PyLiteral

_NamespaceSetString = PyLiteral["core", "rdflib", "none"]
_MulPathMod = PyLiteral["*", "+", "?"]  # noqa: F722
