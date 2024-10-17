from rdflib import Graph
from rdflib.plugins.sparql._contrib.valuesToTheLeftOfTheJoins import (
    ValuesToTheLeftOfTheJoin,
)
from rdflib.plugins.sparql.parser import *

# from rdflib.plugins.sparql.processor import prepareQuery
from rdflib.plugins.sparql.processor import parseQuery, translateQuery

query_slow = """
PREFIX ex:<https://example.org/>

SELECT ?x {
  ?x ?y ?z .
  VALUES (?x) {
    (ex:1)
    (ex:2)
    (ex:3)
  }
}
"""

query_fast = """
PREFIX ex:<https://example.org/>

SELECT ?x {
  VALUES (?x) {
    (ex:1)
    (ex:2)
    (ex:3)
  }
    ?x ?y ?z .
}
"""

query_regex = """
PREFIX ex:<https://example.org/>

SELECT ?x {
  ?x ?y ?z .
  FILTER(regex("?z", "hi"))
}
"""

query_contains = """
PREFIX ex:<https://example.org/>

SELECT ?x {
  ?x ?y ?z .
  FILTER(contains("?z", "hi"))
}
"""


def test_values_to_left():
    qs = _prepare_query(query_slow)
    qf = _prepare_query(query_fast)
    assert qs != qf
    qso = ValuesToTheLeftOfTheJoin.translate(qs)

    assert qso.algebra == qf.algebra


def _prepare_query(str_or_query):
    parse_tree = parseQuery(str_or_query)
    query = translateQuery(parse_tree, None, {})
    return query


if __name__ == "__main__":
    test_values_to_left()
