import pytest

import rdflib
from rdflib import Graph


def test_issue_166() -> None:
    g = Graph()
    query = "SELECT * { ?a ?b ?c } LIMIT 10"
    qres = g.query(query)
    assert qres.vars == [
        rdflib.term.Variable('a'),
        rdflib.term.Variable('b'),
        rdflib.term.Variable('c'),
    ]
