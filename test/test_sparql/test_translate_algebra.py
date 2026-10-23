from __future__ import annotations

import logging
from collections.abc import Collection
from dataclasses import dataclass, field
from io import StringIO
from pathlib import Path
from typing import Union, cast

import pytest
from _pytest.mark.structures import Mark, MarkDecorator, ParameterSet

import rdflib.plugins.sparql.algebra as algebra
import rdflib.plugins.sparql.parser as parser
from rdflib import Graph, Literal, URIRef, Variable
from rdflib.plugins.sparql.algebra import translateAlgebra
from test.data import TEST_DATA_DIR


@pytest.fixture
def data_path() -> Path:
    return TEST_DATA_DIR / "translate_algebra"


@dataclass
class AlgebraTest:
    id: str
    description: str
    marks: Union[MarkDecorator, Collection[Union[MarkDecorator, Mark]]] = field(
        default_factory=lambda: cast(tuple[MarkDecorator], tuple())
    )

    @property
    def filename(self) -> str:
        return f"{self.id}.txt"

    def pytest_param(self) -> ParameterSet:
        return pytest.param(self, id=self.id, marks=self.marks)


def _format_query(query: str) -> str:
    buffer = StringIO()
    p = "{"
    q = "}"
    i = 0
    f = 1

    for e in query:
        if e in p:
            if not f:
                buffer.write("\n")
            buffer.write(" " * i + e)
            buffer.write("\n")
            i += 4
            f = 1
        elif e in q:
            if not f:
                buffer.write("\n")
            i -= 4
            f = 1
            buffer.write(" " * i + e)
            buffer.write("\n")
        else:
            if f:
                buffer.write(" " * i)
            buffer.write(e)
    return buffer.getvalue()


algebra_tests = [
    AlgebraTest(
        "test_functions__functional_forms",
        "Test if functional forms are properly translated into the query text.",
    ),
    AlgebraTest(
        "test_functions__functional_forms_not_exists",
        "Test if the not exists form is properly translated into the query text.",
    ),
    AlgebraTest(
        "test_functions__functions_on_dates_and_time",
        "Test if functions on dates and time are properly translated into the query text.",
    ),
    AlgebraTest(
        "test_functions__functions_on_numerics",
        "Test if functions on numerics are properly translated into the query text.",
    ),
    AlgebraTest(
        "test_functions__functions_on_rdf_terms",
        "Test if functions on rdf terms are properly translated into the query text.",
    ),
    AlgebraTest(
        "test_functions__functions_on_strings",
        "Test if functions on strings are properly translated into the query text.",
    ),
    AlgebraTest(
        "test_functions__hash_functions",
        "Test if hash functions are properly translated into the query text.",
    ),
    AlgebraTest(
        "test_graph_patterns__aggregate_join",
        "Test if aggregate join including all aggregation functions"
        "are properly translated into the query text.",
    ),
    AlgebraTest(
        "test_graph_patterns__bgp",
        "Test if basic graph patterns are properly translated into the query text.",
    ),
    AlgebraTest(
        "test_graph_patterns__bnode_subject",
        "Test if a blank node subject gets properly translated into the query text.",
    ),
    AlgebraTest(
        "test_graph_patterns__extend",
        'Test if "extend" (=Bind explicitly or implicitly in projection)'
        "gets properly translated into the query text.",
    ),
    AlgebraTest(
        "test_graph_patterns__filter",
        "Test if filter gets properly translated into the query text.",
    ),
    AlgebraTest(
        "test_graph_patterns__graph",
        'Test if "graph" gets properly translated into the query text.',
    ),
    AlgebraTest(
        "test_graph_patterns__group",
        'Test if "group" gets properly translated into the query text.',
    ),
    AlgebraTest(
        "test_graph_patterns__group_and_substr",
        'Test if a query with a variable that is used in the "GROUP BY" clause '
        "and in the SUBSTR function gets properly translated into the query text.",
    ),
    AlgebraTest(
        "test_graph_patterns__group_and_nested_concat",
        "Test if a query with a nested concat expression in the select clause which "
        "uses a group variable gets properly translated into the query text.",
    ),
    AlgebraTest(
        "test_graph_patterns__group_in_second_subquery",
        'Test if a "GROUP BY" stays on its own subquery when an earlier sibling '
        "subquery has none.",
    ),
    AlgebraTest(
        "test_graph_patterns__having",
        'Test if "having" gets properly translated into the query text.',
    ),
    AlgebraTest(
        "test_graph_patterns__join",
        'Test if "join" gets properly translated into the query text.',
    ),
    AlgebraTest(
        "test_graph_patterns__left_join",
        'Test if "left join" gets properly translated into "OPTIONAL {...}" in the query text.',
    ),
    AlgebraTest(
        "test_graph_patterns__minus",
        'Test if "minus" gets properly translated into the query text.',
    ),
    AlgebraTest(
        "test_graph_patterns__union",
        'Test if "union" gets properly translated into the query text.',
    ),
    AlgebraTest(
        "test_integration__complex_query1",
        "Test a query with multiple graph patterns and solution modifiers"
        "gets properly translated into the query text.",
    ),
    AlgebraTest(
        "test_operators__arithmetics",
        "Test if arithmetics are properly translated into the query text.",
    ),
    AlgebraTest(
        "test_operators__conditional_and",
        'Test if "conditional ands (&&)" are properly translated into the query text.',
    ),
    AlgebraTest(
        "test_operators__conditional_or",
        'Test if "conditional ors (||)" are properly translated into the query text.',
    ),
    AlgebraTest(
        "test_operators__relational",
        "Test if relational expressions are properly translated into the query text.",
    ),
    AlgebraTest(
        "test_operators__unary",
        "Test if unary expressions are properly translated into the query text.",
    ),
    AlgebraTest(
        "test_other__service1",
        "Test if a nested service pattern is properly translated",
    ),
    AlgebraTest(
        "test_other__service2",
        'Test if "service" along with its service string is properly translated'
        "into the query text.",
    ),
    AlgebraTest(
        "test_other__service_minus",
        'Test if "minus" inside a "service" pattern is properly translated into '
        "the query text.",
    ),
    AlgebraTest(
        "test_other__values",
        'Test if "values" gets properly translated into the query text.',
    ),
    AlgebraTest(
        "test_property_path__alternative_path",
        "Test if an alternative path gets properly translated into the query text.",
    ),
    AlgebraTest(
        "test_property_path__inverse_path",
        "Test if an inverse path gets properly translated into the query text.",
    ),
    AlgebraTest(
        "test_property_path__negated_property_set",
        "Test if a negated property set gets properly translated into the query text.",
        pytest.mark.xfail(
            raises=TypeError, reason="fails with TypeError in translateAlgebra"
        ),
    ),
    AlgebraTest(
        "test_property_path__one_or_more_path",
        "Test if a oneOrMore path gets properly translated into the query text.",
    ),
    AlgebraTest(
        "test_property_path__sequence_path",
        "Test if a sequence path gets properly translated into the query text.",
    ),
    AlgebraTest(
        "test_property_path__zero_or_more_path",
        "Test if a zeroOrMore path gets properly translated into the query text.",
    ),
    AlgebraTest(
        "test_property_path__zero_or_one_path",
        "Test if a zeroOrOne path gets properly translated into the query text.",
    ),
    AlgebraTest(
        "test_solution_modifiers__distinct",
        'Test if "distinct" gets properly translated into the query text.',
    ),
    AlgebraTest(
        "test_solution_modifiers__order_by",
        'Test if "order by" gets properly translated into the query text.',
    ),
    AlgebraTest(
        "test_solution_modifiers__reduced",
        'Test if "reduced" gets properly translated into the query text.',
    ),
    AlgebraTest(
        "test_solution_modifiers__slice",
        "Test if slice get properly translated into the limit and offset.",
    ),
    AlgebraTest(
        "test_solution_modifiers__to_multiset",
        "Test if subqueries get properly translated into the query text.",
    ),
]

unused_files = {
    "test_property_path__predicate_path.txt",
    "test_solution_modifiers__project.txt",
}


def test_all_files_used(data_path: Path) -> None:
    all_files_names = {path.name for path in data_path.glob("*")}
    expected_files = {test.filename for test in algebra_tests}

    # These files are not being used, and they are empty, they were likely
    # added as placeholders.

    all_files_names.difference_update(unused_files)

    assert expected_files == all_files_names


@pytest.mark.parametrize("test_spec", [test.pytest_param() for test in algebra_tests])
def test_roundtrip(test_spec: AlgebraTest, data_path: Path) -> None:
    """
    Query remains the same over two successive parse and translate cycles.
    """
    query_text = (data_path / test_spec.filename).read_text()

    logging.info("checking expectation: %s", test_spec.description)
    query_tree = parser.parseQuery(query_text)
    query_algebra = algebra.translateQuery(query_tree)
    query_from_algebra = translateAlgebra(query_algebra)
    logging.debug(
        "query_from_query_from_algebra = \n%s",
        query_from_algebra,
    )

    query_tree_2 = parser.parseQuery(query_from_algebra)
    query_algebra_2 = algebra.translateQuery(query_tree_2)
    query_from_query_from_algebra = translateAlgebra(query_algebra_2)
    logging.debug(
        "query_from_query_from_algebra = \n%s",
        query_from_query_from_algebra,
    )
    assert (
        query_from_algebra == query_from_query_from_algebra
    ), f"failed expectation: {test_spec.description}"

    # TODO: Execute the raw query (query_text) and the reconstituted query
    # (query_from_query_from_algebra) against a well defined graph and ensure
    # they yield the same result.


def test_group_by_stays_on_its_subquery(data_path: Path) -> None:
    """A later subquery's GROUP BY must not move to an earlier sibling subquery."""
    query_text = (
        data_path / "test_graph_patterns__group_in_second_subquery.txt"
    ).read_text()
    graph = Graph().parse(
        format="turtle",
        data="""
        @prefix : <http://example.org/> .
        :a :p 1 , 2 .
        :b :p 3 .
        :a :q 10 , 11 .
        :b :q 20 .
        """,
    )

    query_from_algebra = translateAlgebra(
        algebra.translateQuery(parser.parseQuery(query_text))
    )

    assert sorted(graph.query(query_from_algebra)) == sorted(graph.query(query_text))


_RESULTS_DATA = """
@prefix : <http://example.org/> .
:a :p 1 , 2 , 3 ; :q 10 ; :name "x" , "" .
:b :p 4 ; :q 30 .
:c :p 5 , 6 .
"""


@pytest.mark.parametrize(
    "query",
    [
        pytest.param(
            """
            SELECT ?k ?n WHERE {
              { SELECT ?k WHERE { VALUES ?k { 1 1 2 } } }
              {
                SELECT (COUNT(?v) AS ?n)
                WHERE { VALUES (?x ?v) { (:a 1) (:a 2) (:b 3) } }
                GROUP BY ?x
              }
            }
            """,
            id="group_by_after_values_only_subquery",
        ),
        pytest.param(
            """
            SELECT ?k ?n WHERE {
              { SELECT ?k WHERE { VALUES ?k { 1 1 2 } } }
              {
                SELECT (COUNT(?v) AS ?n)
                WHERE { VALUES (?x ?v) { (:a 1) (:a 2) (:b 3) } }
                GROUP BY ?x HAVING (COUNT(?v) > 1)
              }
            }
            """,
            id="having_after_values_only_subquery",
        ),
        pytest.param(
            """
            SELECT ?x (COUNT(?y) AS ?n) WHERE { ?x :p ?y }
            GROUP BY ?x HAVING (COUNT(?y) > 1)
            """,
            id="having_with_group_variable_projected",
        ),
        pytest.param(
            """
            SELECT ?x (SUM(?y) AS ?n) WHERE { ?x :p ?y }
            GROUP BY ?x HAVING (SUM(?y) > 5)
            """,
            id="having_sum_with_group_variable_projected",
        ),
        pytest.param(
            """
            SELECT ?x (COUNT(?y) AS ?n) WHERE { ?x :p ?y }
            GROUP BY ?x HAVING (MAX(?y) > 4)
            """,
            id="having_on_aggregate_not_projected",
        ),
        pytest.param(
            """
            SELECT ?x (COUNT(?y) AS ?n) WHERE { ?x :p ?y }
            GROUP BY ?x HAVING (?x = :a)
            """,
            id="having_on_group_variable",
        ),
        pytest.param(
            """
            SELECT ?x WHERE { ?x :p ?y } GROUP BY ?x HAVING (COUNT(?y) > 1)
            """,
            id="having_with_only_group_variable_projected",
        ),
        pytest.param(
            """
            SELECT ?x ?x (COUNT(?y) AS ?n) WHERE { ?x :p ?y } GROUP BY ?x
            """,
            id="group_variable_projected_twice",
        ),
        pytest.param(
            """
            SELECT ?x ?x (COUNT(?y) AS ?n) WHERE { ?x :p ?y }
            GROUP BY ?x HAVING (COUNT(?y) > 1)
            """,
            id="group_variable_projected_twice_with_having",
        ),
        pytest.param(
            """
            SELECT ?x (COUNT(?y) AS ?n) WHERE { ?x :p ?y }
            GROUP BY ?x HAVING (COUNT(?y) > 1) VALUES ?x { :a :b }
            """,
            id="having_with_values_clause",
        ),
        pytest.param(
            """
            SELECT ?n ?m WHERE {
              { SELECT (COUNT(?y) AS ?n) WHERE { ?x :p ?y } }
              { SELECT (COUNT(?z) AS ?m) WHERE { ?w :q ?z } }
            }
            """,
            id="aggregate_in_sibling_subqueries",
        ),
        pytest.param(
            """
            SELECT (SUM(?n) AS ?t) WHERE {
              { SELECT ?k (COUNT(?v) AS ?n) WHERE { ?k :p ?v } GROUP BY ?k }
            }
            """,
            id="aggregate_in_nested_subquery",
        ),
        pytest.param(
            """
            SELECT ?k (SUM(?v) + 1 AS ?y) WHERE { ?k :p ?v } GROUP BY ?k
            """,
            id="aggregate_inside_select_expression",
        ),
        pytest.param(
            """
            SELECT ?s (STR(?o) AS ?b) WHERE { ?s :name ?o FILTER(STR(?s) != "") }
            """,
            id="select_expression_and_filter_with_same_function",
        ),
        pytest.param(
            """
            SELECT ?s ?b WHERE { ?s :name ?o BIND(STR(?o) AS ?b) FILTER(?b != "") }
            """,
            id="bind_used_by_filter",
        ),
        pytest.param(
            """
            SELECT ?s WHERE { ?s :name ?o BIND(STR(?o) AS ?b) FILTER(?b != "") }
            """,
            id="bind_not_projected",
        ),
        pytest.param(
            """
            SELECT ?s ?c WHERE {
              ?s :name ?o BIND(STR(?o) AS ?b) BIND(CONCAT(?b, "!") AS ?c)
            }
            """,
            id="chained_binds",
        ),
        pytest.param(
            """
            SELECT ?c ?b WHERE {
              ?s :name ?o BIND(STR(?o) AS ?b) BIND(CONCAT(?b, "!") AS ?c)
            }
            """,
            id="chained_binds_projected_in_other_order",
        ),
        pytest.param(
            """
            SELECT ?s ?o WHERE { BIND(:a AS ?s) ?s :p ?o }
            """,
            id="leading_bind",
        ),
        pytest.param(
            """
            SELECT ?x ?one WHERE { ?x :p ?v OPTIONAL { ?x :q ?w BIND(1 AS ?one) } }
            """,
            id="bind_in_optional",
        ),
        pytest.param(
            """
            SELECT ?s ?o WHERE { { ?s :name ?o FILTER(!BOUND(?b)) } BIND(STR(?o) AS ?b) }
            """,
            id="bind_after_group_with_filter",
        ),
        pytest.param(
            """
            SELECT ?s ?v ?z WHERE { BIND(4 AS ?z) { ?s :p ?v FILTER(?v = ?z) } }
            """,
            id="bind_before_group_with_filter",
        ),
        pytest.param(
            """
            SELECT ?k (COUNT(?v) AS ?n) WHERE { ?x :p ?v } GROUP BY (STR(?x) AS ?k)
            """,
            id="group_by_expression",
        ),
        pytest.param(
            """
            SELECT ?ss (STR(?o) AS ?s) WHERE { ?ss :name ?o }
            """,
            id="select_expression_named_as_prefix_of_variable",
        ),
    ],
)
def test_translation_returns_same_results(query: str) -> None:
    """The query translated from the algebra returns the same rows as the original."""
    query = "PREFIX : <http://example.org/>\n" + query
    graph = Graph().parse(format="turtle", data=_RESULTS_DATA)

    query_from_algebra = translateAlgebra(
        algebra.translateQuery(parser.parseQuery(query))
    )

    assert sorted(graph.query(query_from_algebra)) == sorted(graph.query(query))


def test_group_by_stays_on_its_subquery_after_service() -> None:
    """A GROUP BY must not move to an earlier sibling subquery that only has a SERVICE."""
    query = """
    PREFIX : <http://example.org/>
    SELECT ?k ?n WHERE {
      { SELECT ?k WHERE { SERVICE <http://example.org/sparql> { ?k :p ?v } } }
      { SELECT (COUNT(?v) AS ?n) WHERE { ?x :p ?v } GROUP BY ?x }
    }
    """

    query_from_algebra = translateAlgebra(
        algebra.translateQuery(parser.parseQuery(query))
    )

    assert query_from_algebra.index("GROUP BY") > query_from_algebra.index("COUNT(")


def test_sparql_group_concat():
    """Tests if GROUP_CONCAT correctly uses the separator keyword"""
    query = """
    PREFIX : <http://example.org/>

    SELECT ?subject (GROUP_CONCAT(?object; separator="")
                        AS ?concatenatedObjects)
    WHERE {
      VALUES (?subject ?object) {
        (:pred "a")
        (:pred "b")
        (:pred "c")
      }
    }
    GROUP BY ?subject
    """

    g = Graph()
    q = dict(g.query(query))
    assert q[URIRef("http://example.org/pred")] == Literal("abc")


def test_sparql_blank_node_comma():
    """Tests if blank nodes separated by commas are correctly parsed"""

    query = """
    PREFIX : <http://example.org/>

    SELECT ?s WHERE {
    ?s :hasIngredient [:name "chicken"], [:name "butter"] .
    } LIMIT 10
    """

    parse_results = parser.parseQuery(query)
    triples = parse_results[1]["where"].part[0].triples[0]
    s_count = sum(1 for i in range(0, len(triples), 3) if triples[i] == Variable("s"))
    assert s_count == 2, f"Found ?s as subject {s_count} times, expected 2"
