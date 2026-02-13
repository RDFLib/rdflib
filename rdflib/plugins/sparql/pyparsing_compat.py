"""
Compatibility helpers for supporting pyparsing v2 and v3 APIs.
"""

from __future__ import annotations

from typing import Any, Dict

import pyparsing

ParseResults = pyparsing.ParseResults
ParserElement = pyparsing.ParserElement


_RAW_VERSION = getattr(pyparsing, "__version__", "0")
try:
    PYPARSING_MAJOR_VERSION = int(_RAW_VERSION.split(".", 1)[0])
except (TypeError, ValueError):
    PYPARSING_MAJOR_VERSION = 0

PYPARSING_V3 = PYPARSING_MAJOR_VERSION >= 3

if PYPARSING_V3:
    DelimitedList = pyparsing.DelimitedList
    original_text_for = pyparsing.original_text_for
    rest_of_line = pyparsing.rest_of_line
else:
    DelimitedList = pyparsing.delimitedList  # type: ignore[misc]
    original_text_for = pyparsing.originalTextFor
    rest_of_line = pyparsing.restOfLine


if not hasattr(ParserElement, "set_parse_action"):
    ParserElement.set_parse_action = ParserElement.setParseAction  # type: ignore[method-assign]

if not hasattr(ParserElement, "add_parse_action"):
    ParserElement.add_parse_action = ParserElement.addParseAction  # type: ignore[method-assign]

if not hasattr(ParserElement, "leave_whitespace"):
    ParserElement.leave_whitespace = ParserElement.leaveWhitespace  # type: ignore[method-assign]

if not hasattr(ParserElement, "set_name"):
    ParserElement.set_name = ParserElement.setName  # type: ignore[method-assign]

if not hasattr(ParserElement, "set_results_name"):
    ParserElement.set_results_name = ParserElement.setResultsName  # type: ignore[method-assign]

if not hasattr(ParserElement, "parse_with_tabs"):
    ParserElement.parse_with_tabs = ParserElement.parseWithTabs  # type: ignore[method-assign]

if not hasattr(ParserElement, "search_string"):
    ParserElement.search_string = ParserElement.searchString  # type: ignore[method-assign]

if not hasattr(ParserElement, "set_default_whitespace_chars"):
    ParserElement.set_default_whitespace_chars = ParserElement.setDefaultWhitespaceChars  # type: ignore[method-assign]

if not hasattr(ParserElement, "parse_string"):

    def _parse_string(
        self: ParserElement,
        instring: Any,
        parse_all: bool = False,
        *,
        parseAll: bool = False,
    ) -> ParseResults:
        if parseAll:
            parse_all = parseAll
        return self.parseString(instring, parseAll=parse_all)

    ParserElement.parse_string = _parse_string  # type: ignore[method-assign]


if not hasattr(ParseResults, "as_list"):
    ParseResults.as_list = ParseResults.asList  # type: ignore[method-assign]


def combine_join_kwargs(value: str) -> Dict[str, str]:
    if PYPARSING_V3:
        return {"join_string": value}
    return {"joinString": value}
