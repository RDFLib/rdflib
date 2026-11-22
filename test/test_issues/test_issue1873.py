from rdflib import Graph


def test_sparql_error_implicit_bind():
    [r for r in Graph().query('SELECT (concat("", sha1(?x)) AS ?y) WHERE {}')]


def test_sparql_error_explicit_bind():
    [r for r in Graph().query("SELECT ?v ?p ?m WHERE {?v ?p ?m BIND (sha1(?x) AS ?m)}")]
