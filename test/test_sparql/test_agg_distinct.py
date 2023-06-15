from rdflib import Graph, URIRef
from rdflib.term import Literal

query_tpl = """
SELECT ?x (MIN(?y_) as ?y) (%s(DISTINCT ?z_) as ?z) {
  VALUES (?x ?y_ ?z_) {
    ("x1" 10 1)
    ("x1" 11 1)
    ("x2" 20 2)
  }
} GROUP BY ?x ORDER BY ?x
"""


def test_group_concat_distinct():
    g = Graph()
    results = g.query(query_tpl % "GROUP_CONCAT")
    results = [[lit.toPython() for lit in line] for line in results]

    # this is the tricky part
    assert results[0][2] == "1", results[0][2]

    # still check the whole result, to be on the safe side
    assert results == [
        ["x1", 10, "1"],
        ["x2", 20, "2"],
    ], results


def test_sum_distinct():
    g = Graph()
    results = g.query(query_tpl % "SUM")
    results = [[lit.toPython() for lit in line] for line in results]

    # this is the tricky part
    assert results[0][2] == 1, results[0][2]

    # still check the whole result, to be on the safe side
    assert results == [
        ["x1", 10, 1],
        ["x2", 20, 2],
    ], results


def test_avg_distinct():
    g = Graph()
    results = g.query(
        """
        SELECT ?x (MIN(?y_) as ?y) (AVG(DISTINCT ?z_) as ?z) {
          VALUES (?x ?y_ ?z_) {
            ("x1" 10 1)
            ("x1" 11 1)
            ("x1" 12 3)
            ("x2" 20 2)
          }
       } GROUP BY ?x ORDER BY ?x
    """
    )
    results = [[lit.toPython() for lit in line] for line in results]

    # this is the tricky part
    assert results[0][2] == 2, results[0][2]

    # still check the whole result, to be on the safe side
    assert results == [
        ["x1", 10, 2],
        ["x2", 20, 2],
    ], results


def test_count_distinct():
    g = Graph()

    g.parse(
        format="turtle",
        publicID="http://example.org/",
        data="""
    @prefix : <> .

    <#a>
      :knows <#b>, <#c> ;
      :age 42 .

    <#b>
      :knows <#a>, <#c> ;
      :age 36 .

    <#c>
      :knows <#b>, <#c> ;
      :age 20 .

    """,
    )

    # Query 1: people knowing someone younger
    results = g.query(
        """
    PREFIX : <http://example.org/>

    SELECT DISTINCT ?x {
      ?x :age ?ax ; :knows [ :age ?ay ].
      FILTER( ?ax > ?ay )
    }
    """
    )
    assert len(results) == 2

    # nQuery 2: count people knowing someone younger
    results = g.query(
        """
    PREFIX : <http://example.org/>

    SELECT (COUNT(DISTINCT ?x) as ?cx) {
      ?x :age ?ax ; :knows [ :age ?ay ].
      FILTER( ?ax > ?ay )
    }
    """
    )
    assert list(results)[0][0].toPython() == 2


def test_count_optional_values():
    """Problematic query because ?inst may be not bound.
    So when counting over not bound variables it throws a NotBoundError.
    """
    g = Graph()
    g.bind("ex", "http://example.com/")
    g.parse(
        format="ttl",
        data="""@prefix ex: <http://example.com/>.
            ex:1 a ex:a;
                ex:d ex:b.
            ex:2 a ex:a;
                ex:d ex:c;
                ex:d ex:b.
            ex:3 a ex:a.
    """,
    )

    query = """
    SELECT DISTINCT ?x (COUNT(DISTINCT ?inst) as ?cnt)
    WHERE {
        ?x a ex:a
        OPTIONAL {
            VALUES ?inst {ex:b ex:c}.
            ?x ex:d ?inst.
        }
    }  GROUP BY ?x
    """
    results = dict(g.query(query))
    assert results == {
        URIRef("http://example.com/1"): Literal(1),
        URIRef("http://example.com/2"): Literal(2),
        URIRef("http://example.com/3"): Literal(0),
    }
