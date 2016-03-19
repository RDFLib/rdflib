from rdflib import Graph

query_tpl = '''
SELECT ?x (MIN(?y_) as ?y) (%s(DISTINCT ?z_) as ?z) {
  VALUES (?x ?y_ ?z_) {
    ("x1" 10 1)
    ("x1" 11 1)
    ("x2" 20 2)
  }
} GROUP BY ?x ORDER BY ?x
'''

def test_group_concat_distinct():
    g = Graph()
    results = g.query(query_tpl % 'GROUP_CONCAT')
    results = [ [ lit.toPython() for lit in line ] for line in results ]

    # this is the tricky part
    assert results[0][2] == "1", results[0][2]

    # still check the whole result, to be on the safe side
    assert results == [
        ["x1", 10, "1"],
        ["x2", 20, "2"],
    ], results

def test_sum_distinct():
    g = Graph()
    results = g.query(query_tpl % 'SUM')
    results = [ [ lit.toPython() for lit in line ] for line in results ]

    # this is the tricky part
    assert results[0][2] == 1, results[0][2]

    # still check the whole result, to be on the safe side
    assert results == [
        ["x1", 10, 1],
        ["x2", 20, 2],
    ], results

def test_avg_distinct():
    g = Graph()
    results = g.query("""
        SELECT ?x (MIN(?y_) as ?y) (AVG(DISTINCT ?z_) as ?z) {
          VALUES (?x ?y_ ?z_) {
            ("x1" 10 1)
            ("x1" 11 1)
            ("x1" 12 3)
            ("x2" 20 2)
          }
       } GROUP BY ?x ORDER BY ?x
    """)
    results = [ [ lit.toPython() for lit in line ] for line in results ]

    # this is the tricky part
    assert results[0][2] == 2, results[0][2]

    # still check the whole result, to be on the safe side
    assert results == [
        ["x1", 10, 2],
        ["x2", 20, 2],
    ], results
