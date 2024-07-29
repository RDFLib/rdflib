"""
Issue 715 - path query chaining issue
Some incorrect matches were found when using oneOrMore ('+') and
zeroOrMore ('*') property paths and specifying neither the
subject or the object.
"""

from rdflib import Graph
from test.utils.namespace import EGDO


def test_issue_733():
    g = Graph()
    g.add((EGDO.S, EGDO.P, EGDO.O1))
    g.add((EGDO.S, EGDO.P, EGDO.O2))
    q = """
    prefix ex:<http://example.org/>
    select ?lexical_or_value ?ot ?gt where {
        {SELECT (count(*) as ?lexical_or_value) where {
        ?s ?p ?o .
            FILTER (?s=ex:S)
        }}
        {SELECT (count(*) as ?ot) where {
        ?s ?p ?o .
            FILTER (?o=ex:O1)
        }}
        {SELECT (count(*) as ?gt) where {
        ?s ?p ?o .
            FILTER (?o!=ex:O1 && ?s!=ex:O2)
        }}
    }
    """
    res = g.query(q)
    assert len(res) == 1
    results = [[lit.toPython() for lit in line] for line in res]
    assert results[0][0] == 2
    assert results[0][1] == 1
    assert results[0][2] == 1


def test_issue_733_independant():
    g = Graph()
    g.add((EGDO.S, EGDO.P, EGDO.O1))
    g.add((EGDO.S, EGDO.P, EGDO.O2))
    q = """
            prefix ex:<http://example.org/>
            select ?lexical_or_value where {
                {SELECT (count(*) as ?lexical_or_value) where {
                ?s ?p ?o .
                    FILTER (?s=ex:S)
                }}
            }
            """
    res = g.query(q)
    assert len(res) == 1
    results = [[lit.toPython() for lit in line] for line in res]
    assert results[0][0] == 2
    q = """
            prefix ex:<http://example.org/>
            select ?lexical_or_value where {
                {SELECT (count(*) as ?lexical_or_value) where {
                ?s ?p ?o .
                    FILTER (?o=ex:O1)
                }}
            }
            """
    res = g.query(q)
    results = [[lit.toPython() for lit in line] for line in res]
    assert results[0][0] == 1
