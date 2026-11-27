# Test for https://github.com/RDFLib/rdflib/issues/2349

from collections.abc import Mapping, MutableSequence
from typing import Any

import pytest

import rdflib
from rdflib.query import Result
from rdflib.term import Literal, Variable

SELECT_QUERY = "SELECT ?s WHERE { ?s ?p ?o }"


def _select_result(
    bindings: MutableSequence[Mapping[Variable, Any]],
) -> Result:
    result = Result("SELECT")
    result.vars = [Variable("s")]
    result.bindings = bindings
    return result


def _ask_result(answer: bool) -> Result:
    result = Result("ASK")
    result.askAnswer = answer
    return result


def test_equal_select_results() -> None:
    graph = rdflib.Graph()
    graph.parse(data="<http://a> <http://b> <http://c> .", format="turtle")
    first = graph.query(SELECT_QUERY)
    second = graph.query(SELECT_QUERY)
    assert first == second
    assert not first != second


def test_unequal_select_results() -> None:
    assert _select_result([{Variable("s"): Literal("a")}]) != _select_result(
        [{Variable("s"): Literal("b")}]
    )


def test_equal_ask_results() -> None:
    assert _ask_result(True) == _ask_result(True)
    assert _ask_result(True) != _ask_result(False)


def test_unsupported_operand_returns_notimplemented() -> None:
    result = _ask_result(True)
    assert Result.__eq__(result, None) is NotImplemented
    # The reflected operation keeps ordinary container operations working.
    assert result in [None, result]
    assert (result == None) is False  # noqa: E711
    assert (result != None) is True  # noqa: E711


def test_comparison_errors_propagate() -> None:
    class Exploding:
        def __eq__(self, other: Any) -> bool:
            raise ValueError("comparison failed")

    first = _select_result([{Variable("s"): Exploding()}])
    second = _select_result([{Variable("s"): Exploding()}])
    with pytest.raises(ValueError, match="comparison failed"):
        first == second


@pytest.mark.parametrize(
    "query",
    [
        "ASK {}",
        "SELECT * WHERE {}",
        "CONSTRUCT {} WHERE {}",
        "DESCRIBE <urn:example>",
    ],
    ids=["ASK", "SELECT", "CONSTRUCT", "DESCRIBE"],
)
@pytest.mark.parametrize(
    "other", [None, 1, "result", object()], ids=["none", "int", "str", "object"]
)
def test_result_equality_with_unrelated_objects(query: str, other: object) -> None:
    result = rdflib.Graph().query(query)

    assert not (result == other)
    assert not (other == result)
    assert result != other
    assert other != result
    assert result in [other, result]
    assert other not in [result]


def test_result_equality_defers_to_other_operand() -> None:
    class Comparable:
        def __eq__(self, other: object) -> bool:
            return isinstance(other, Result)

    result = Result("ASK")
    other = Comparable()

    assert result == other
    assert other == result
    assert not (result != other)
    assert not (other != result)
