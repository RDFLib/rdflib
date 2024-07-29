from __future__ import annotations

import builtins
import logging
from dataclasses import dataclass
from typing import Any, Optional, Union
from xml.dom.minidom import DocumentFragment

from rdflib.term import Literal, URIRef
from test.utils.outcome import NoExceptionChecker


@dataclass(frozen=True)
class LiteralChecker(NoExceptionChecker[Literal]):
    value: Union[builtins.ellipsis, Any] = ...
    language: Union[builtins.ellipsis, str, None] = ...
    datatype: Union[builtins.ellipsis, URIRef, None] = ...
    ill_typed: Union[builtins.ellipsis, bool, None] = ...
    lexical: Union[builtins.ellipsis, str] = ...

    def check(self, actual: Literal) -> None:
        logging.debug(
            "actual = %r, value = %r, ill_typed = %r",
            actual,
            actual.value,
            actual.ill_typed,
        )
        if self.value is not Ellipsis:
            if callable(self.value):
                logging.debug(f"Checking value {actual.value} with {self.value}")
                if isinstance(actual.value, DocumentFragment):
                    logging.debug(f"childNodes = {actual.value.childNodes}")
                assert self.value(actual.value)
            else:
                assert self.value == actual.value
            assert self.value == actual.value
        if self.lexical is not Ellipsis:
            assert self.lexical == f"{actual}", "Literal lexical form does not match"
        if self.ill_typed is not Ellipsis:
            assert (
                self.ill_typed == actual.ill_typed
            ), "Literal ill_typed flag does not match"
        if self.language is not Ellipsis:
            assert self.language == actual.language, "Literal language does not match"
        if self.datatype is not Ellipsis:
            assert self.datatype == actual.datatype, "Literal datatype does not match"


def literal_idfn(value: Any) -> Optional[str]:
    if callable(value):
        try:
            literal = value()
        except Exception:
            return None
        return f"{literal}"
    if isinstance(value, LiteralChecker):
        return f"{value}"
    return None
