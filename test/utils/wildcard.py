from typing import Any
from urllib.parse import ParseResult


class EqWildcard:
    """
    An object that matches anything.
    """

    def __eq__(self, other: Any) -> Any:
        return True

    def __req__(self, other: Any) -> Any:
        return True

    def __repr__(self) -> str:
        return "EqWildcard()"


EQ_WILDCARD: Any = EqWildcard()


URL_PARSE_RESULT_WILDCARD = ParseResult(
    EQ_WILDCARD, EQ_WILDCARD, EQ_WILDCARD, EQ_WILDCARD, EQ_WILDCARD, EQ_WILDCARD
)
"""
This should be equal to any `ParseResult` object.
"""
