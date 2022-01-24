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
