from rdflib import Graph

g = Graph()

data = """
<urn:a> <urn:p> 1 .
<urn:b> <urn:p> 3 .
<urn:c> <urn:q> 1 .
"""
g.parse(data=data, format="turtle")


def test_group_by():
    query = "SELECT ?p" "WHERE { ?s ?p ?o } " "GROUP BY ?p"
    qres = g.query(query)

    assert len(qres) == 2


def test_having_aggregate_eq_literal():
    query = (
        "SELECT ?p (avg(?o) as ?a) "
        "WHERE { ?s ?p ?o } "
        "GROUP BY ?p HAVING (avg(?o) = 2 )"
    )
    qres = g.query(query)

    assert len(qres) == 1


def test_having_primary_expression_var_neq_iri():
    query = "SELECT ?p " "WHERE { ?s ?p ?o } " "GROUP BY ?p HAVING (?p != <urn:foo> )"
    qres = g.query(query)

    assert len(qres) == 2
