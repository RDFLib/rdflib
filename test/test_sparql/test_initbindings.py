from rdflib import Dataset, Literal, URIRef, Variable
from rdflib.plugins.sparql import prepareQuery
from test.utils.namespace import EGDC

g = Dataset()


def test_str():
    a = set(
        g.query(
            "SELECT (STR(?target) AS ?r) WHERE { }",
            initBindings={"target": URIRef("example:a")},
        )
    )
    b = set(
        g.query(
            "SELECT (STR(?target) AS ?r) WHERE { } VALUES (?target) {(<example:a>)}"
        )
    )
    assert a == b, "STR: %r != %r" % (a, b)


def test_is_iri():
    a = set(
        g.query(
            "SELECT (isIRI(?target) AS ?r) WHERE { }",
            initBindings={"target": URIRef("example:a")},
        )
    )
    b = set(
        g.query(
            "SELECT (isIRI(?target) AS ?r) WHERE { } VALUES (?target) {(<example:a>)}"
        )
    )
    assert a == b, "isIRI: %r != %r" % (a, b)


def test_is_blank():
    a = set(
        g.query(
            "SELECT (isBlank(?target) AS ?r) WHERE { }",
            initBindings={"target": URIRef("example:a")},
        )
    )
    b = set(
        g.query(
            "SELECT (isBlank(?target) AS ?r) WHERE { } VALUES (?target) {(<example:a>)}"
        )
    )
    assert a == b, "isBlank: %r != %r" % (a, b)


def test_is_literal():
    a = set(
        g.query(
            "SELECT (isLiteral(?target) AS ?r) WHERE { }",
            initBindings={"target": Literal("example")},
        )
    )
    b = set(
        g.query(
            "SELECT (isLiteral(?target) AS ?r) WHERE { } VALUES (?target) {('example')}"
        )
    )
    assert a == b, "isLiteral: %r != %r" % (a, b)


def test_ucase():
    a = set(
        g.query(
            "SELECT (UCASE(?target) AS ?r) WHERE { }",
            initBindings={"target": Literal("example")},
        )
    )
    b = set(
        g.query(
            "SELECT (UCASE(?target) AS ?r) WHERE { } VALUES (?target) {('example')}"
        )
    )
    assert a == b, "UCASE: %r != %r" % (a, b)


def test_no_func():
    a = set(
        g.query("SELECT ?target WHERE { }", initBindings={"target": Literal("example")})
    )
    b = set(g.query("SELECT ?target WHERE { } VALUES (?target) {('example')}"))
    assert a == b, "no func: %r != %r" % (a, b)


def test_order_by():
    a = set(
        g.query(
            "SELECT ?target WHERE { } ORDER BY ?target",
            initBindings={"target": Literal("example")},
        )
    )
    b = set(
        g.query(
            "SELECT ?target WHERE { } ORDER BY ?target VALUES (?target) {('example')}"
        )
    )
    assert a == b, "orderby: %r != %r" % (a, b)


def test_order_by_func():
    a = set(
        g.query(
            "SELECT (UCASE(?target) as ?r) WHERE { } ORDER BY ?target",
            initBindings={"target": Literal("example")},
        )
    )
    b = set(
        g.query(
            "SELECT (UCASE(?target) as ?r) WHERE { } ORDER BY ?target VALUES (?target) {('example')} "
        )
    )
    assert a == b, "orderbyFunc: %r != %r" % (a, b)


def test_no_func_limit():
    a = set(
        g.query(
            "SELECT ?target WHERE { } LIMIT 1",
            initBindings={"target": Literal("example")},
        )
    )
    b = set(g.query("SELECT ?target WHERE { } LIMIT 1 VALUES (?target) {('example')}"))
    assert a == b, "limit: %r != %r" % (a, b)


def test_order_by_limit():
    a = set(
        g.query(
            "SELECT ?target WHERE { } ORDER BY ?target LIMIT 1",
            initBindings={"target": Literal("example")},
        )
    )
    b = set(
        g.query(
            "SELECT ?target WHERE { } ORDER BY ?target LIMIT 1 VALUES (?target) {('example')}"
        )
    )
    assert a == b, "orderbyLimit: %r != %r" % (a, b)


def test_order_by_func_limit():
    a = set(
        g.query(
            "SELECT (UCASE(?target) as ?r) WHERE { } ORDER BY ?target LIMIT 1",
            initBindings={"target": Literal("example")},
        )
    )
    b = set(
        g.query(
            "SELECT (UCASE(?target) as ?r) WHERE { } ORDER BY ?target LIMIT 1 VALUES (?target) {('example')}"
        )
    )
    assert a == b, "orderbyFuncLimit: %r != %r" % (a, b)


def test_no_func_offset():
    a = set(
        g.query(
            "SELECT ?target WHERE { } OFFSET 1",
            initBindings={"target": Literal("example")},
        )
    )
    b = set(g.query("SELECT ?target WHERE { } OFFSET 1 VALUES (?target) {('example')}"))
    assert a == b, "offset: %r != %r" % (a, b)


def test_no_func_limit_offset():
    a = set(
        g.query(
            "SELECT ?target WHERE { } LIMIT 1 OFFSET 1",
            initBindings={"target": Literal("example")},
        )
    )
    b = set(
        g.query(
            "SELECT ?target WHERE { } LIMIT 1 OFFSET 1 VALUES (?target) {('example')}"
        )
    )
    assert a == b, "limitOffset: %r != %r" % (a, b)


def test_order_by_limit_offset():
    a = set(
        g.query(
            "SELECT ?target WHERE { } ORDER BY ?target LIMIT 1 OFFSET 1",
            initBindings={"target": Literal("example")},
        )
    )
    b = set(
        g.query(
            "SELECT ?target WHERE { } ORDER BY ?target LIMIT 1 OFFSET 1 VALUES (?target) {('example')}"
        )
    )
    assert a == b, "orderbyLimitOffset: %r != %r" % (a, b)


def test_order_by_func_limit_offset():
    a = set(
        g.query(
            "SELECT (UCASE(?target) as ?r) WHERE { } ORDER BY ?target LIMIT 1 OFFSET 1",
            initBindings={"target": Literal("example")},
        )
    )
    b = set(
        g.query(
            "SELECT (UCASE(?target) as ?r) WHERE { } ORDER BY ?target LIMIT 1 OFFSET 1 VALUES (?target) {('example')}"
        )
    )
    assert a == b, "orderbyFuncLimitOffset: %r != %r" % (a, b)


def test_distinct():
    a = set(
        g.query(
            "SELECT DISTINCT ?target WHERE { }",
            initBindings={"target": Literal("example")},
        )
    )
    b = set(g.query("SELECT DISTINCT ?target WHERE { } VALUES (?target) {('example')}"))
    assert a == b, "distinct: %r != %r" % (a, b)


def test_distinct_order_by():
    a = set(
        g.query(
            "SELECT DISTINCT ?target WHERE { } ORDER BY ?target",
            initBindings={"target": Literal("example")},
        )
    )
    b = set(
        g.query(
            "SELECT DISTINCT ?target WHERE { } ORDER BY ?target VALUES (?target) {('example')}"
        )
    )
    assert a == b, "distinctOrderby: %r != %r" % (a, b)


def test_distinct_order_by_limit():
    a = set(
        g.query(
            "SELECT DISTINCT ?target WHERE { } ORDER BY ?target LIMIT 1",
            initBindings={"target": Literal("example")},
        )
    )
    b = set(
        g.query(
            "SELECT DISTINCT ?target WHERE { } ORDER BY ?target LIMIT 1 VALUES (?target) {('example')}"
        )
    )
    assert a == b, "distinctOrderbyLimit: %r != %r" % (a, b)


def test_prepare():
    q = prepareQuery("SELECT ?target WHERE { }")
    r = list(g.query(q))
    e = []
    assert r == e, "prepare: %r != %r" % (r, e)

    r = list(g.query(q, initBindings={"target": Literal("example")}))
    e = [(Literal("example"),)]
    assert r == e, "prepare: %r != %r" % (r, e)

    r = list(g.query(q))
    e = []
    assert r == e, "prepare: %r != %r" % (r, e)


def test_data():
    data = Dataset()
    data += [
        (URIRef("urn:a"), URIRef("urn:p"), Literal("a")),
        (URIRef("urn:b"), URIRef("urn:p"), Literal("b")),
    ]

    a = set(
        g.query(
            "SELECT ?target WHERE { ?target <urn:p> ?val }",
            initBindings={"val": Literal("a")},
        )
    )
    b = set(
        g.query("SELECT ?target WHERE { ?target <urn:p> ?val } VALUES (?val) {('a')}")
    )

    assert a == b, "data: %r != %r" % (a, b)


def test_ask():
    a = set(g.query("ASK { }", initBindings={"target": Literal("example")}))
    b = set(g.query("ASK { } VALUES (?target) {('example')}"))
    assert a == b, "ask: %r != %r" % (a, b)


g2 = Dataset()
g2.bind("", EGDC)
g2.add((EGDC["s1"], EGDC["p"], EGDC["o1"]))
g2.add((EGDC["s2"], EGDC["p"], EGDC["o2"]))


def test_string_key():
    results = list(
        g2.query("SELECT ?o WHERE { ?s :p ?o }", initBindings={"s": EGDC["s1"]})
    )
    assert len(results) == 1, results


def test_string_key_with_question_mark():
    results = list(
        g2.query("SELECT ?o WHERE { ?s :p ?o }", initBindings={"?s": EGDC["s1"]})
    )
    assert len(results) == 1, results


def test_variable_key():
    results = list(
        g2.query(
            "SELECT ?o WHERE { ?s :p ?o }", initBindings={Variable("s"): EGDC["s1"]}
        )
    )
    assert len(results) == 1, results


def test_variable_key_with_question_mark():
    results = list(
        g2.query(
            "SELECT ?o WHERE { ?s :p ?o }", initBindings={Variable("?s"): EGDC["s1"]}
        )
    )
    assert len(results) == 1, results


def test_filter():
    results = list(
        g2.query(
            "SELECT ?o WHERE { ?s :p ?o FILTER (?s = ?x)}",
            initBindings={Variable("?x"): EGDC["s1"]},
        )
    )
    assert len(results) == 1, results
