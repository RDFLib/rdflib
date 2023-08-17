from __future__ import annotations

import builtins
from dataclasses import dataclass
from typing import Any, Union

from rdflib.term import Literal, URIRef


@dataclass
class LiteralChecker:
    value: Union[builtins.ellipsis, Any] = ...
    language: Union[builtins.ellipsis, str, None] = ...
    datatype: Union[builtins.ellipsis, URIRef, None] = ...
    ill_typed: Union[builtins.ellipsis, bool, None] = ...
    lexical: Union[builtins.ellipsis, str] = ...

    def check(self, actual: Literal) -> None:
        if self.value is not Ellipsis:
            assert self.value == actual.value
        if self.lexical is not Ellipsis:
            assert self.lexical == f"{actual}"
        if self.ill_typed is not Ellipsis:
            assert self.ill_typed == actual.ill_typed
        if self.language is not Ellipsis:
            assert self.language == actual.language
        if self.datatype is not Ellipsis:
            assert self.datatype == actual.datatype
