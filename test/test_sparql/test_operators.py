import datetime

import pytest

import rdflib
from rdflib.plugins.sparql import operators, sparql


def test_date_cast():
    now = datetime.datetime.now()
    today = now.date()

    literal = rdflib.Literal(now)
    result = operators.date(literal)
    assert isinstance(result, datetime.date)
    assert result == today

    literal = rdflib.Literal(today)
    result = operators.date(literal)
    assert isinstance(result, datetime.date)
    assert result == today


def test_datetime_cast():
    now = datetime.datetime.now()
    literal = rdflib.Literal(now)
    result = operators.datetime(literal)
    assert isinstance(result, datetime.datetime)
    assert result == now


def test_datetime_cast_type_error():
    literal = rdflib.Literal("2020-01-02")
    with pytest.raises(sparql.SPARQLError):
        operators.date(literal)


@pytest.mark.parametrize(
    ("expression", "expected"),
    [
        ("true || ?u", True),
        ("?u || true", True),
        ("false && ?u", False),
        ("?u && false", False),
        ("(1/0) && false", False),
        ("true || (1/0)", True),
        ("(1/0) || true", True),
        ("false && (1/0)", False),
    ],
)
def test_logical_connectives_error_tolerance(expression, expected):
    # SPARQL 1.1 section 17.2: || and && use three-valued logic, so an error on
    # one operand does not poison the result when the other operand decides it.
    query = "SELECT ?r WHERE { BIND(2 AS ?o) BIND(%s AS ?r) }" % expression
    (row,) = rdflib.Graph().query(query)
    assert row[0] is not None
    assert row[0].toPython() is expected


def test_decimal_and_double_compare_as_the_same_number():
    # 0.1 is an xsd:decimal and 0.1e0 is an xsd:double. After promotion
    # to double they are the same number, so < is false.
    graph = rdflib.Graph()

    def ask(query: str) -> bool:
        answer = graph.query(query).askAnswer
        assert isinstance(answer, bool)
        return answer

    assert ask("ASK { FILTER(0.1 = 0.1e0) }") is True
    assert ask("ASK { FILTER(0.1 < 0.1e0) }") is False
    assert ask("ASK { FILTER(0.1 > 0.1e0) }") is False
    assert ask("ASK { FILTER(0.1 != 0.1e0) }") is False
    assert ask("ASK { FILTER(1.1 = 1.1e0) }") is True
    assert ask("ASK { FILTER(0.5 = 0.5e0) }") is True
    assert ask("ASK { FILTER(0.1 < 0.2e0) }") is True
    assert ask("ASK { FILTER(2 = 2.0e0) }") is True


@pytest.mark.parametrize(
    "expression",
    [
        "?u || ?v",
        "?u && ?v",
        "(1/0) || false",
        "true && (1/0)",
    ],
)
def test_logical_connectives_propagate_error(expression):
    # An error that is not overridden by the other operand must stay an error,
    # leaving the bound variable unbound.
    query = "SELECT ?o ?r WHERE { BIND(2 AS ?o) BIND(%s AS ?r) }" % expression
    (row,) = rdflib.Graph().query(query)
    assert row[1] is None
