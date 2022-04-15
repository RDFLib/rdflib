import inspect
import logging
from io import StringIO
from typing import Mapping, Sequence, Type, Union

import pytest
from pyparsing import ParseException

from rdflib.query import Result
from rdflib.term import Identifier, Literal, Variable

BindingsType = Sequence[Mapping[Variable, Identifier]]
ParseOutcomeType = Union[BindingsType, Type[Exception]]


@pytest.mark.parametrize(
    ("data", "format", "parse_outcome"),
    [
        pytest.param(
            "a\n1",
            "csv",
            [{Variable("a"): Literal("1")}],
            id="csv-okay-1c1r",
        ),
        pytest.param(
            '?a\n"1"',
            "tsv",
            [{Variable("a"): Literal("1")}],
            id="tsv-okay-1c1r",
        ),
        pytest.param(
            "1,2,3\nhttp://example.com",
            "tsv",
            ParseException,
            id="tsv-invalid",
        ),
    ],
)
def test_select_result_parse(
    data: str, format: str, parse_outcome: ParseOutcomeType
) -> None:
    """
    Round tripping of a select query through the serializer and parser of a
    specific format results in an equivalent result object.
    """
    logging.debug("data = %s", data)

    if inspect.isclass(parse_outcome) and issubclass(parse_outcome, Exception):
        with pytest.raises(parse_outcome):
            parsed_result = Result.parse(StringIO(data), format=format)
    else:
        parsed_result = Result.parse(StringIO(data), format=format)
        assert parse_outcome == parsed_result.bindings
