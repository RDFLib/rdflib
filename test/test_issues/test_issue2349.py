"""Equality must not turn evaluation failures into successful inequality checks."""

from collections.abc import Iterator
from typing import Any

import pytest

from rdflib import Graph, Literal, Variable
from rdflib.query import Result


@pytest.mark.parametrize("failing_side", ["left", "right"])
def test_result_equality_propagates_lazy_binding_error(failing_side: str) -> None:
    error = RuntimeError("synthetic result evaluation failure")

    def bindings() -> Iterator[dict[Variable, Any]]:
        yield {Variable("value"): Literal(1)}
        raise error

    left, right = Result("SELECT"), Result("SELECT")
    left.vars = right.vars = [Variable("value")]
    left.bindings = right.bindings = [{Variable("value"): Literal(1)}]
    failing = left if failing_side == "left" else right
    failing.bindings = bindings()
    with pytest.raises(RuntimeError) as caught:
        left == right
    assert caught.value is error


@pytest.mark.parametrize("result_type", ["ASK", "SELECT", "CONSTRUCT", "DESCRIBE"])
def test_valid_result_equality_is_unchanged(result_type: str) -> None:
    left, right = Result(result_type), Result(result_type)
    if result_type == "ASK":
        left.askAnswer = right.askAnswer = True
    elif result_type == "SELECT":
        left.vars = right.vars = [Variable("value")]
        left.bindings = right.bindings = [{Variable("value"): Literal(1)}]
    else:
        left.graph = right.graph = Graph()
    assert left == right


def test_different_result_types_are_unequal() -> None:
    assert Result("ASK") != Result("SELECT")


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
    result = Graph().query(query)

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
