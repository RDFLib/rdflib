from __future__ import annotations

from decimal import Decimal

from rdflib import RDF, Graph, Literal, Namespace
from rdflib.plugins.sparql.algebra import translateQuery, traverse
from rdflib.plugins.sparql.parser import parseQuery
from rdflib.plugins.sparql.parserutils import CompValue
from rdflib.query import ResultRow


def test_no_extra_aggregate_sample_for_prior_agg_alias() -> None:
    query = """
    SELECT
        (COUNT(?t1) AS ?c1)
        (COUNT(?t2) AS ?c2)
        (?c1 / ?c2 * 100 AS ?p)
    WHERE {
        ?t1 a :Sample .
        ?t2 a :Sample
    }
    """
    ns = {"": "http://example.org/"}
    algebra = translateQuery(parseQuery(query), initNs=ns).algebra

    aggs: list[CompValue] = []

    def _collect_agg_joins(node: CompValue) -> None:
        if isinstance(node, CompValue) and node.name == "AggregateJoin":
            aggs.extend(node.A)

    traverse(algebra, visitPre=_collect_agg_joins)

    assert [a.name for a in aggs] == ["Aggregate_Count", "Aggregate_Count"]


def test_eval_expression_referencing_prior_aggregate_aliases() -> None:
    ex = Namespace("http://example.org/")
    g = Graph()
    g.add((ex.s1, RDF.type, ex.Sample))
    g.add((ex.s2, RDF.type, ex.Sample))

    query = """
    PREFIX : <http://example.org/>
    SELECT
        (COUNT(?t1) AS ?c1)
        (COUNT(?t2) AS ?c2)
        (?c1 / ?c2 * 100 AS ?p)
    WHERE {
        ?t1 a :Sample .
        ?t2 a :Sample
    }
    """
    rows = list(g.query(query))
    assert len(rows) == 1
    row = rows[0]
    assert isinstance(row, ResultRow)
    assert isinstance(row.c1, Literal) and row.c1.toPython() == 4
    assert isinstance(row.c2, Literal) and row.c2.toPython() == 4
    assert isinstance(row.p, Literal) and row.p.toPython() == Decimal(100)


def test_eval_chained_composite_aggregate_aliases() -> None:
    ex = Namespace("http://example.org/")
    g = Graph()
    g.add((ex.s1, RDF.type, ex.Sample))
    g.add((ex.s2, RDF.type, ex.Sample))

    query = """
    PREFIX : <http://example.org/>
    SELECT
        (COUNT(?t1) + 1 AS ?c1)
        (?c1 * 2 AS ?c2)
    WHERE {
        ?t1 a :Sample .
    }
    """
    rows = list(g.query(query))
    assert len(rows) == 1
    row = rows[0]
    assert isinstance(row, ResultRow)
    assert isinstance(row.c1, Literal) and row.c1.toPython() == 3
    assert isinstance(row.c2, Literal) and row.c2.toPython() == 6
