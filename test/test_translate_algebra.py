import logging
import os
from dataclasses import dataclass, field
from io import StringIO
from pathlib import Path
from typing import Collection, Tuple, Union, cast

import pytest
from _pytest.mark.structures import Mark, MarkDecorator, ParameterSet

import rdflib.plugins.sparql.algebra as algebra
import rdflib.plugins.sparql.parser as parser
from rdflib.plugins.sparql.algebra import translateAlgebra


@pytest.fixture
def data_path() -> Path:
    return Path(__file__).parent / "translate_algebra"


@dataclass
class AlgebraTest:
    id: str
    description: str
    marks: Union[MarkDecorator, Collection[Union[MarkDecorator, Mark]]] = field(
        default_factory=lambda: cast(Tuple[MarkDecorator], tuple())
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
        'and in the SUBSTR function gets properly translated into the query text.',
    ),
    AlgebraTest(
        "test_graph_patterns__group_and_nested_concat",
        'Test if a query with a nested concat expression in the select clause which '
        'uses a group variable gets properly translated into the query text.',
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
        "test_other__service2",
        'Test if "service" along with its service string is properly translated'
        "into the query text.",
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


if os.name != "nt":
    # On Windows this test causes a stackoverflow or memory error, so don't run
    # it on Windows. The test fails anyway on linux and should be fixed. Once
    # the cause of this failure is fixed the condition to not run it on windows
    # should be removed and it should be added to the normal tests.
    algebra_tests.append(
        AlgebraTest(
            "test_other__service1",
            "Test if a nested service pattern is properly translated"
            "into the query text.",
            pytest.mark.xfail(
                raises=RecursionError,
                reason="Fails with RecursionError inside parser.parseQuery",
            ),
        )
    )
else:
    unused_files.add("test_other__service1.txt")


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
