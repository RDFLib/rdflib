from test_base import Test, TestExecution, format_text
from rdflib.plugins.sparql.algebra import translateAlgebra
import rdflib.plugins.sparql.parser as parser
import rdflib.plugins.sparql.algebra as algebra
import sys
import logging


def _pprint_query(query: str):
    p = "{"
    q = "}"
    i = 0
    f = 1

    for e in query:
        if e in p:
            f or print()
            print(" " * i + e)
            i += 4
            f = 1
        elif e in q:
            f or print()
            i -= 4
            f = 1
            print(" " * i + e)
        else:
            not f or print(" " * i, end="")
            f = print(e, end="")


class TestAlgebraToTest(TestExecution):
    def __init__(self, annotated_tests: bool = False):
        super().__init__(annotated_tests)
        self.rdf_engine = None
        self.query_text = None
        self.query_algebra = None
        self.query_from_algebra = None
        self.query_from_query_from_algebra = None

    def before_single_test(self, test_name: str):
        """

        :return:
        """

        print("Executing before_single_tests ...")

        if self.annotated_tests:
            test_name = test_name[2:]

        self.query_text = open("test_data/{0}.txt".format(test_name), "r").read()

    def test_functions__functional_forms(self):
        query_tree = parser.parseQuery(self.query_text)
        query_algebra = algebra.translateQuery(query_tree)
        self.query_from_algebra = translateAlgebra(query_algebra)

        query_tree_2 = parser.parseQuery(self.query_from_algebra)
        query_algebra_2 = algebra.translateQuery(query_tree_2)
        self.query_from_query_from_algebra = translateAlgebra(query_algebra_2)

        test = Test(
            test_number=1,
            tc_desc="Test if functional forms are properly translated into the query text. "
            "The query must also be executable and shall not violate any SPARQL query syntax.",
            expected_result=self.query_from_algebra,
            actual_result=self.query_from_query_from_algebra,
        )

        try:
            self.rdf_engine.get_data(
                self.query_from_query_from_algebra, yn_timestamp_query=False
            )
        except Exception as e:
            print(e)
            print("The query must be executable. Otherwise, the test has failed.")
            return Test(
                test_number=test.test_number,
                tc_desc=test.tc_desc,
                expected_result="0",
                actual_result="not_executable",
            )

        return test

    def test_functions__functional_forms_not_exists(self):
        query_tree = parser.parseQuery(self.query_text)
        query_algebra = algebra.translateQuery(query_tree)
        self.query_from_algebra = translateAlgebra(query_algebra)

        query_tree_2 = parser.parseQuery(self.query_from_algebra)
        query_algebra_2 = algebra.translateQuery(query_tree_2)
        self.query_from_query_from_algebra = translateAlgebra(query_algebra_2)
        _pprint_query(self.query_from_query_from_algebra)

        test = Test(
            test_number=2,
            tc_desc="Test if the not exists form is properly translated into the query text. "
            "The query must also be executable and shall not violate any SPARQL query syntax.",
            expected_result=self.query_from_algebra,
            actual_result=self.query_from_query_from_algebra,
        )

        return test

    def test_functions__functions_on_rdf_terms(self):
        query_tree = parser.parseQuery(self.query_text)
        query_algebra = algebra.translateQuery(query_tree)
        self.query_from_algebra = translateAlgebra(query_algebra)

        query_tree_2 = parser.parseQuery(self.query_from_algebra)
        query_algebra_2 = algebra.translateQuery(query_tree_2)
        self.query_from_query_from_algebra = translateAlgebra(query_algebra_2)
        _pprint_query(self.query_from_query_from_algebra)

        test = Test(
            test_number=3,
            tc_desc="Test if functions on rdf terms are properly translated into the query text. "
            "The query must also be executable and shall not violate any SPARQL query syntax.",
            expected_result=self.query_from_algebra,
            actual_result=self.query_from_query_from_algebra,
        )

        return test

    def test_functions__functions_on_strings(self):
        query_tree = parser.parseQuery(self.query_text)
        query_algebra = algebra.translateQuery(query_tree)
        self.query_from_algebra = translateAlgebra(query_algebra)

        query_tree_2 = parser.parseQuery(self.query_from_algebra)
        query_algebra_2 = algebra.translateQuery(query_tree_2)
        self.query_from_query_from_algebra = translateAlgebra(query_algebra_2)
        _pprint_query(self.query_from_query_from_algebra)

        test = Test(
            test_number=4,
            tc_desc="Test if functions on strings are properly translated into the query text. "
            "The query must also be executable and shall not violate any SPARQL query syntax.",
            expected_result=self.query_from_algebra,
            actual_result=self.query_from_query_from_algebra,
        )

        return test

    def test_functions__functions_on_numerics(self):
        query_tree = parser.parseQuery(self.query_text)
        query_algebra = algebra.translateQuery(query_tree)
        self.query_from_algebra = translateAlgebra(query_algebra)

        query_tree_2 = parser.parseQuery(self.query_from_algebra)
        query_algebra_2 = algebra.translateQuery(query_tree_2)
        self.query_from_query_from_algebra = translateAlgebra(query_algebra_2)
        _pprint_query(self.query_from_query_from_algebra)

        test = Test(
            test_number=5,
            tc_desc="Test if functions on numerics are properly translated into the query text. "
            "The query must also be executable and shall not violate any SPARQL query syntax.",
            expected_result=self.query_from_algebra,
            actual_result=self.query_from_query_from_algebra,
        )

        return test

    def test_functions__hash_functions(self):
        query_tree = parser.parseQuery(self.query_text)
        query_algebra = algebra.translateQuery(query_tree)
        self.query_from_algebra = translateAlgebra(query_algebra)

        query_tree_2 = parser.parseQuery(self.query_from_algebra)
        query_algebra_2 = algebra.translateQuery(query_tree_2)
        self.query_from_query_from_algebra = translateAlgebra(query_algebra_2)
        _pprint_query(self.query_from_query_from_algebra)

        test = Test(
            test_number=6,
            tc_desc="Test if hash functions are properly translated into the query text. "
            "The query must also be executable and shall not violate any SPARQL query syntax.",
            expected_result=self.query_from_algebra,
            actual_result=self.query_from_query_from_algebra,
        )

        return test

    def test_functions__functions_on_dates_and_time(self):
        query_tree = parser.parseQuery(self.query_text)
        query_algebra = algebra.translateQuery(query_tree)
        self.query_from_algebra = translateAlgebra(query_algebra)

        query_tree_2 = parser.parseQuery(self.query_from_algebra)
        query_algebra_2 = algebra.translateQuery(query_tree_2)
        self.query_from_query_from_algebra = translateAlgebra(query_algebra_2)
        _pprint_query(self.query_from_query_from_algebra)

        test = Test(
            test_number=7,
            tc_desc="Test if functions on dates and time are properly translated into the query text. "
            "The query must also be executable and shall not violate any SPARQL query syntax.",
            expected_result=self.query_from_algebra,
            actual_result=self.query_from_query_from_algebra,
        )

        return test

    def test_graph_patterns__aggregate_join(self):
        query_tree = parser.parseQuery(self.query_text)
        query_algebra = algebra.translateQuery(query_tree)
        self.query_from_algebra = translateAlgebra(query_algebra)

        query_tree_2 = parser.parseQuery(self.query_from_algebra)
        query_algebra_2 = algebra.translateQuery(query_tree_2)
        self.query_from_query_from_algebra = translateAlgebra(query_algebra_2)
        _pprint_query(self.query_from_query_from_algebra)

        test = Test(
            test_number=8,
            tc_desc="Test if aggregate join including all aggregation functions "
            "are properly translated into the query text. "
            "The query must also be executable and shall not violate any SPARQL query syntax.",
            expected_result=self.query_from_algebra,
            actual_result=self.query_from_query_from_algebra,
        )

        return test

    def test_graph_patterns__bgp(self):
        query_tree = parser.parseQuery(self.query_text)
        query_algebra = algebra.translateQuery(query_tree)
        self.query_from_algebra = translateAlgebra(query_algebra)

        query_tree_2 = parser.parseQuery(self.query_from_algebra)
        query_algebra_2 = algebra.translateQuery(query_tree_2)
        self.query_from_query_from_algebra = translateAlgebra(query_algebra_2)
        _pprint_query(self.query_from_query_from_algebra)

        test = Test(
            test_number=9,
            tc_desc="Test if basic graph patterns are properly translated into the query text. "
            "The query must also be executable and shall not violate any SPARQL query syntax.",
            expected_result=self.query_from_algebra,
            actual_result=self.query_from_query_from_algebra,
        )

        return test

    def test_graph_patterns__extend(self):
        query_tree = parser.parseQuery(self.query_text)
        query_algebra = algebra.translateQuery(query_tree)
        self.query_from_algebra = translateAlgebra(query_algebra)

        query_tree_2 = parser.parseQuery(self.query_from_algebra)
        query_algebra_2 = algebra.translateQuery(query_tree_2)
        self.query_from_query_from_algebra = translateAlgebra(query_algebra_2)
        _pprint_query(self.query_from_query_from_algebra)

        test = Test(
            test_number=10,
            tc_desc='Test if "extend" (=Bind explicitly or implicitly in projection) '
            "gets properly translated into the query text. "
            "The query must also be executable and shall not violate any SPARQL query syntax.",
            expected_result=self.query_from_algebra,
            actual_result=self.query_from_query_from_algebra,
        )

        return test

    def test_graph_patterns__filter(self):
        query_tree = parser.parseQuery(self.query_text)
        query_algebra = algebra.translateQuery(query_tree)
        self.query_from_algebra = translateAlgebra(query_algebra)

        query_tree_2 = parser.parseQuery(self.query_from_algebra)
        query_algebra_2 = algebra.translateQuery(query_tree_2)
        self.query_from_query_from_algebra = translateAlgebra(query_algebra_2)
        _pprint_query(self.query_from_query_from_algebra)

        test = Test(
            test_number=11,
            tc_desc="Test if filter gets properly translated into the query text. "
            "The query must also be executable and shall not violate any SPARQL query syntax.",
            expected_result=self.query_from_algebra,
            actual_result=self.query_from_query_from_algebra,
        )

        return test

    def test_graph_patterns__graph(self):
        query_tree = parser.parseQuery(self.query_text)
        query_algebra = algebra.translateQuery(query_tree)
        self.query_from_algebra = translateAlgebra(query_algebra)

        query_tree_2 = parser.parseQuery(self.query_from_algebra)
        query_algebra_2 = algebra.translateQuery(query_tree_2)
        self.query_from_query_from_algebra = translateAlgebra(query_algebra_2)
        _pprint_query(self.query_from_query_from_algebra)

        test = Test(
            test_number=12,
            tc_desc='Test if "graph" gets properly translated into the query text. '
            "The query must also be executable and shall not violate any SPARQL query syntax.",
            expected_result=self.query_from_algebra,
            actual_result=self.query_from_query_from_algebra,
        )

        return test

    def test_graph_patterns__group(self):
        query_tree = parser.parseQuery(self.query_text)
        query_algebra = algebra.translateQuery(query_tree)
        self.query_from_algebra = translateAlgebra(query_algebra)

        query_tree_2 = parser.parseQuery(self.query_from_algebra)
        query_algebra_2 = algebra.translateQuery(query_tree_2)
        self.query_from_query_from_algebra = translateAlgebra(query_algebra_2)
        _pprint_query(self.query_from_query_from_algebra)

        test = Test(
            test_number=13,
            tc_desc='Test if "group" gets properly translated into the query text. '
            "The query must also be executable and shall not violate any SPARQL query syntax.",
            expected_result=self.query_from_algebra,
            actual_result=self.query_from_query_from_algebra,
        )

        return test

    def test_graph_patterns__having(self):
        query_tree = parser.parseQuery(self.query_text)
        query_algebra = algebra.translateQuery(query_tree)
        self.query_from_algebra = translateAlgebra(query_algebra)

        query_tree_2 = parser.parseQuery(self.query_from_algebra)
        query_algebra_2 = algebra.translateQuery(query_tree_2)
        self.query_from_query_from_algebra = translateAlgebra(query_algebra_2)
        _pprint_query(self.query_from_query_from_algebra)

        test = Test(
            test_number=14,
            tc_desc='Test if "having" gets properly translated into the query text. '
            "The query must also be executable and shall not violate any SPARQL query syntax.",
            expected_result=self.query_from_algebra,
            actual_result=self.query_from_query_from_algebra,
        )

        return test

    def test_graph_patterns__join(self):
        query_tree = parser.parseQuery(self.query_text)
        query_algebra = algebra.translateQuery(query_tree)
        self.query_from_algebra = translateAlgebra(query_algebra)

        query_tree_2 = parser.parseQuery(self.query_from_algebra)
        query_algebra_2 = algebra.translateQuery(query_tree_2)
        self.query_from_query_from_algebra = translateAlgebra(query_algebra_2)
        _pprint_query(self.query_from_query_from_algebra)

        test = Test(
            test_number=15,
            tc_desc='Test if "join" gets properly translated into the query text. '
            "The query must also be executable and shall not violate any SPARQL query syntax.",
            expected_result=self.query_from_algebra,
            actual_result=self.query_from_query_from_algebra,
        )

        return test

    def test_graph_patterns__left_join(self):
        query_tree = parser.parseQuery(self.query_text)
        query_algebra = algebra.translateQuery(query_tree)
        self.query_from_algebra = translateAlgebra(query_algebra)

        query_tree_2 = parser.parseQuery(self.query_from_algebra)
        query_algebra_2 = algebra.translateQuery(query_tree_2)
        self.query_from_query_from_algebra = translateAlgebra(query_algebra_2)
        _pprint_query(self.query_from_query_from_algebra)

        test = Test(
            test_number=16,
            tc_desc='Test if "left join" gets properly translated into "OPTIONAL {...}" in the query text. '
            "The query must also be executable and shall not violate any SPARQL query syntax.",
            expected_result=self.query_from_algebra,
            actual_result=self.query_from_query_from_algebra,
        )

        return test

    def test_graph_patterns__minus(self):
        query_tree = parser.parseQuery(self.query_text)
        query_algebra = algebra.translateQuery(query_tree)
        self.query_from_algebra = translateAlgebra(query_algebra)

        query_tree_2 = parser.parseQuery(self.query_from_algebra)
        query_algebra_2 = algebra.translateQuery(query_tree_2)
        self.query_from_query_from_algebra = translateAlgebra(query_algebra_2)
        _pprint_query(self.query_from_query_from_algebra)

        test = Test(
            test_number=17,
            tc_desc='Test if "minus" gets properly translated into the query text. '
            "The query must also be executable and shall not violate any SPARQL query syntax.",
            expected_result=self.query_from_algebra,
            actual_result=self.query_from_query_from_algebra,
        )

        return test

    def test_graph_patterns__union(self):
        query_tree = parser.parseQuery(self.query_text)
        query_algebra = algebra.translateQuery(query_tree)
        self.query_from_algebra = translateAlgebra(query_algebra)

        query_tree_2 = parser.parseQuery(self.query_from_algebra)
        query_algebra_2 = algebra.translateQuery(query_tree_2)
        self.query_from_query_from_algebra = translateAlgebra(query_algebra_2)
        _pprint_query(self.query_from_query_from_algebra)

        test = Test(
            test_number=18,
            tc_desc='Test if "union" gets properly translated into the query text. '
            "The query must also be executable and shall not violate any SPARQL query syntax.",
            expected_result=self.query_from_algebra,
            actual_result=self.query_from_query_from_algebra,
        )

        return test

    def test_operators__arithmetics(self):
        query_tree = parser.parseQuery(self.query_text)
        query_algebra = algebra.translateQuery(query_tree)
        self.query_from_algebra = translateAlgebra(query_algebra)

        query_tree_2 = parser.parseQuery(self.query_from_algebra)
        query_algebra_2 = algebra.translateQuery(query_tree_2)
        self.query_from_query_from_algebra = translateAlgebra(query_algebra_2)
        _pprint_query(self.query_from_query_from_algebra)

        test = Test(
            test_number=19,
            tc_desc="Test if arithmetics are properly translated into the query text. "
            "The query must also be executable and shall not violate any SPARQL query syntax.",
            expected_result=self.query_from_algebra,
            actual_result=self.query_from_query_from_algebra,
        )

        return test

    def test_operators__conditional_and(self):
        query_tree = parser.parseQuery(self.query_text)
        query_algebra = algebra.translateQuery(query_tree)
        self.query_from_algebra = translateAlgebra(query_algebra)

        query_tree_2 = parser.parseQuery(self.query_from_algebra)
        query_algebra_2 = algebra.translateQuery(query_tree_2)
        self.query_from_query_from_algebra = translateAlgebra(query_algebra_2)
        _pprint_query(self.query_from_query_from_algebra)

        test = Test(
            test_number=20,
            tc_desc='Test if "conditional ands (&&)" are properly translated into the query text. '
            "The query must also be executable and shall not violate any SPARQL query syntax.",
            expected_result=self.query_from_algebra,
            actual_result=self.query_from_query_from_algebra,
        )

        return test

    def test_operators__conditional_or(self):
        query_tree = parser.parseQuery(self.query_text)
        query_algebra = algebra.translateQuery(query_tree)
        self.query_from_algebra = translateAlgebra(query_algebra)

        query_tree_2 = parser.parseQuery(self.query_from_algebra)
        query_algebra_2 = algebra.translateQuery(query_tree_2)
        self.query_from_query_from_algebra = translateAlgebra(query_algebra_2)
        _pprint_query(self.query_from_query_from_algebra)

        test = Test(
            test_number=21,
            tc_desc='Test if "conditional ors (||)" are properly translated into the query text. '
            "The query must also be executable and shall not violate any SPARQL query syntax.",
            expected_result=self.query_from_algebra,
            actual_result=self.query_from_query_from_algebra,
        )

        return test

    def test_operators__relational(self):
        query_tree = parser.parseQuery(self.query_text)
        query_algebra = algebra.translateQuery(query_tree)
        self.query_from_algebra = translateAlgebra(query_algebra)

        query_tree_2 = parser.parseQuery(self.query_from_algebra)
        query_algebra_2 = algebra.translateQuery(query_tree_2)
        self.query_from_query_from_algebra = translateAlgebra(query_algebra_2)
        _pprint_query(self.query_from_query_from_algebra)

        test = Test(
            test_number=22,
            tc_desc="Test if relational expressions are properly translated into the query text. "
            "The query must also be executable and shall not violate any SPARQL query syntax.",
            expected_result=self.query_from_algebra,
            actual_result=self.query_from_query_from_algebra,
        )

        return test

    def test_operators__unary(self):
        query_tree = parser.parseQuery(self.query_text)
        query_algebra = algebra.translateQuery(query_tree)
        self.query_from_algebra = translateAlgebra(query_algebra)

        query_tree_2 = parser.parseQuery(self.query_from_algebra)
        query_algebra_2 = algebra.translateQuery(query_tree_2)
        self.query_from_query_from_algebra = translateAlgebra(query_algebra_2)
        _pprint_query(self.query_from_query_from_algebra)

        test = Test(
            test_number=23,
            tc_desc="Test if unary expressions are properly translated into the query text. "
            "The query must also be executable and shall not violate any SPARQL query syntax.",
            expected_result=self.query_from_algebra,
            actual_result=self.query_from_query_from_algebra,
        )

        return test

    def test_other__service1(self):
        tc_desc = (
            "Test if a nested service pattern is properly translated "
            "into the query text. "
            "The query must also be executable and shall not violate any SPARQL query syntax."
        )
        try:
            query_tree = parser.parseQuery(self.query_text)
        except Exception as e:
            print(e)
            return Test(
                test_number=24,
                tc_desc=tc_desc,
                expected_result="0",
                actual_result="Not executable. Error returned from parseQuery",
            )
        query_algebra = algebra.translateQuery(query_tree)
        self.query_from_algebra = translateAlgebra(query_algebra)

        query_tree_2 = parser.parseQuery(self.query_from_algebra)
        query_algebra_2 = algebra.translateQuery(query_tree_2)
        self.query_from_query_from_algebra = translateAlgebra(query_algebra_2)
        _pprint_query(self.query_from_query_from_algebra)

        test = Test(
            test_number=24,
            tc_desc=tc_desc,
            expected_result=self.query_from_algebra,
            actual_result=self.query_from_query_from_algebra,
        )

        return test

    def test_other__service2(self):
        tc_desc = (
            'Test if "service" along with its service string is properly translated '
            "into the query text. "
            "The query must also be executable and shall not violate any SPARQL query syntax."
        )
        try:
            query_tree = parser.parseQuery(self.query_text)
        except Exception as e:
            print(e)
            return Test(
                test_number=25,
                tc_desc=tc_desc,
                expected_result="0",
                actual_result="Not executable. Error returned from parseQuery().",
            )
        query_algebra = algebra.translateQuery(query_tree)
        self.query_from_algebra = translateAlgebra(query_algebra)

        query_tree_2 = parser.parseQuery(self.query_from_algebra)
        query_algebra_2 = algebra.translateQuery(query_tree_2)
        self.query_from_query_from_algebra = translateAlgebra(query_algebra_2)
        _pprint_query(self.query_from_query_from_algebra)

        test = Test(
            test_number=25,
            tc_desc=tc_desc,
            expected_result=self.query_from_algebra,
            actual_result=self.query_from_query_from_algebra,
        )

        return test

    def test_other__values(self):
        query_tree = parser.parseQuery(self.query_text)
        query_algebra = algebra.translateQuery(query_tree)
        self.query_from_algebra = translateAlgebra(query_algebra)

        query_tree_2 = parser.parseQuery(self.query_from_algebra)
        query_algebra_2 = algebra.translateQuery(query_tree_2)
        self.query_from_query_from_algebra = translateAlgebra(query_algebra_2)
        _pprint_query(self.query_from_query_from_algebra)

        test = Test(
            test_number=26,
            tc_desc='Test if "values" gets properly translated into the query text. '
            "The query must also be executable and shall not violate any SPARQL query syntax.",
            expected_result=self.query_from_algebra,
            actual_result=self.query_from_query_from_algebra,
        )

        return test

    def test_property_path__alternative_path(self):
        query_tree = parser.parseQuery(self.query_text)
        query_algebra = algebra.translateQuery(query_tree)
        self.query_from_algebra = translateAlgebra(query_algebra)

        query_tree_2 = parser.parseQuery(self.query_from_algebra)
        query_algebra_2 = algebra.translateQuery(query_tree_2)
        self.query_from_query_from_algebra = translateAlgebra(query_algebra_2)
        _pprint_query(self.query_from_query_from_algebra)

        test = Test(
            test_number=27,
            tc_desc="Test if an alternative path gets properly translated into the query text. "
            "The query must also be executable and shall not violate any SPARQL query syntax.",
            expected_result=self.query_from_algebra,
            actual_result=self.query_from_query_from_algebra,
        )

        return test

    def test_property_path__inverse_path(self):
        query_tree = parser.parseQuery(self.query_text)
        query_algebra = algebra.translateQuery(query_tree)
        self.query_from_algebra = translateAlgebra(query_algebra)

        query_tree_2 = parser.parseQuery(self.query_from_algebra)
        query_algebra_2 = algebra.translateQuery(query_tree_2)
        self.query_from_query_from_algebra = translateAlgebra(query_algebra_2)
        _pprint_query(self.query_from_query_from_algebra)

        test = Test(
            test_number=28,
            tc_desc="Test if an inverse path gets properly translated into the query text. "
            "The query must also be executable and shall not violate any SPARQL query syntax.",
            expected_result=self.query_from_algebra,
            actual_result=self.query_from_query_from_algebra,
        )

        return test

    def test_property_path__negated_property_set(self):
        tc_desc = (
            "Test if a negated property set gets properly translated into the query text. "
            "The query must also be executable and shall not violate any SPARQL query syntax."
        )
        query_tree = parser.parseQuery(self.query_text)
        query_algebra = algebra.translateQuery(query_tree)
        try:
            self.query_from_algebra = translateAlgebra(query_algebra)
        except TypeError as e:
            print(e)
            return Test(
                test_number=29,
                tc_desc=tc_desc,
                expected_result="0",
                actual_result="Not executable. n3() method of NegatedPath class should be fixed. ",
            )

        query_tree_2 = parser.parseQuery(self.query_from_algebra)
        query_algebra_2 = algebra.translateQuery(query_tree_2)
        self.query_from_query_from_algebra = translateAlgebra(query_algebra_2)
        _pprint_query(self.query_from_query_from_algebra)

        test = Test(
            test_number=29,
            tc_desc=tc_desc,
            expected_result=self.query_from_algebra,
            actual_result=self.query_from_query_from_algebra,
        )

        return test

    def test_property_path__one_or_more_path(self):
        query_tree = parser.parseQuery(self.query_text)
        query_algebra = algebra.translateQuery(query_tree)
        self.query_from_algebra = translateAlgebra(query_algebra)

        query_tree_2 = parser.parseQuery(self.query_from_algebra)
        query_algebra_2 = algebra.translateQuery(query_tree_2)
        self.query_from_query_from_algebra = translateAlgebra(query_algebra_2)
        _pprint_query(self.query_from_query_from_algebra)

        test = Test(
            test_number=30,
            tc_desc="Test if a oneOrMore path gets properly translated into the query text. "
            "The query must also be executable and shall not violate any SPARQL query syntax.",
            expected_result=self.query_from_algebra,
            actual_result=self.query_from_query_from_algebra,
        )

        return test

    def test_property_path__sequence_path(self):
        query_tree = parser.parseQuery(self.query_text)
        query_algebra = algebra.translateQuery(query_tree)
        self.query_from_algebra = translateAlgebra(query_algebra)

        query_tree_2 = parser.parseQuery(self.query_from_algebra)
        query_algebra_2 = algebra.translateQuery(query_tree_2)
        self.query_from_query_from_algebra = translateAlgebra(query_algebra_2)
        _pprint_query(self.query_from_query_from_algebra)

        test = Test(
            test_number=31,
            tc_desc="Test if a sequence path gets properly translated into the query text. "
            "The query must also be executable and shall not violate any SPARQL query syntax.",
            expected_result=self.query_from_algebra,
            actual_result=self.query_from_query_from_algebra,
        )

        return test

    def test_property_path__zero_or_more_path(self):
        query_tree = parser.parseQuery(self.query_text)
        query_algebra = algebra.translateQuery(query_tree)
        self.query_from_algebra = translateAlgebra(query_algebra)

        query_tree_2 = parser.parseQuery(self.query_from_algebra)
        query_algebra_2 = algebra.translateQuery(query_tree_2)
        self.query_from_query_from_algebra = translateAlgebra(query_algebra_2)
        _pprint_query(self.query_from_query_from_algebra)

        test = Test(
            test_number=32,
            tc_desc="Test if a zeroOrMore path gets properly translated into the query text. "
            "The query must also be executable and shall not violate any SPARQL query syntax.",
            expected_result=self.query_from_algebra,
            actual_result=self.query_from_query_from_algebra,
        )

        return test

    def test_property_path__zero_or_one_path(self):
        query_tree = parser.parseQuery(self.query_text)
        query_algebra = algebra.translateQuery(query_tree)
        self.query_from_algebra = translateAlgebra(query_algebra)

        query_tree_2 = parser.parseQuery(self.query_from_algebra)
        query_algebra_2 = algebra.translateQuery(query_tree_2)
        self.query_from_query_from_algebra = translateAlgebra(query_algebra_2)
        _pprint_query(self.query_from_query_from_algebra)

        test = Test(
            test_number=33,
            tc_desc="Test if a zeroOrOne path gets properly translated into the query text. "
            "The query must also be executable and shall not violate any SPARQL query syntax.",
            expected_result=self.query_from_algebra,
            actual_result=self.query_from_query_from_algebra,
        )

        return test

    def test_solution_modifiers__distinct(self):
        query_tree = parser.parseQuery(self.query_text)
        query_algebra = algebra.translateQuery(query_tree)
        self.query_from_algebra = translateAlgebra(query_algebra)

        query_tree_2 = parser.parseQuery(self.query_from_algebra)
        query_algebra_2 = algebra.translateQuery(query_tree_2)
        self.query_from_query_from_algebra = translateAlgebra(query_algebra_2)
        _pprint_query(self.query_from_query_from_algebra)

        test = Test(
            test_number=34,
            tc_desc='Test if "distinct" gets properly translated into the query text. '
            "The query must also be executable and shall not violate any SPARQL query syntax.",
            expected_result=self.query_from_algebra,
            actual_result=self.query_from_query_from_algebra,
        )

        return test

    def test_solution_modifiers__order_by(self):
        query_tree = parser.parseQuery(self.query_text)
        query_algebra = algebra.translateQuery(query_tree)
        self.query_from_algebra = translateAlgebra(query_algebra)

        query_tree_2 = parser.parseQuery(self.query_from_algebra)
        query_algebra_2 = algebra.translateQuery(query_tree_2)
        self.query_from_query_from_algebra = translateAlgebra(query_algebra_2)
        _pprint_query(self.query_from_query_from_algebra)

        test = Test(
            test_number=35,
            tc_desc='Test if "order by" gets properly translated into the query text. '
            "The query must also be executable and shall not violate any SPARQL query syntax.",
            expected_result=self.query_from_algebra,
            actual_result=self.query_from_query_from_algebra,
        )

        return test

    def test_solution_modifiers__reduced(self):
        query_tree = parser.parseQuery(self.query_text)
        query_algebra = algebra.translateQuery(query_tree)
        self.query_from_algebra = translateAlgebra(query_algebra)

        query_tree_2 = parser.parseQuery(self.query_from_algebra)
        query_algebra_2 = algebra.translateQuery(query_tree_2)
        self.query_from_query_from_algebra = translateAlgebra(query_algebra_2)
        _pprint_query(self.query_from_query_from_algebra)

        test = Test(
            test_number=36,
            tc_desc='Test if "reduced" gets properly translated into the query text. '
            "The query must also be executable and shall not violate any SPARQL query syntax.",
            expected_result=self.query_from_algebra,
            actual_result=self.query_from_query_from_algebra,
        )

        return test

    def test_solution_modifiers__slice(self):
        query_tree = parser.parseQuery(self.query_text)
        query_algebra = algebra.translateQuery(query_tree)
        self.query_from_algebra = translateAlgebra(query_algebra)

        query_tree_2 = parser.parseQuery(self.query_from_algebra)
        query_algebra_2 = algebra.translateQuery(query_tree_2)
        self.query_from_query_from_algebra = translateAlgebra(query_algebra_2)
        _pprint_query(self.query_from_query_from_algebra)

        test = Test(
            test_number=37,
            tc_desc="Test if slice get properly translated into the limit and offset. "
            "The query must also be executable and shall not violate any SPARQL query syntax.",
            expected_result=self.query_from_algebra,
            actual_result=self.query_from_query_from_algebra,
        )

        return test

    def test_solution_modifiers__to_multiset(self):
        query_tree = parser.parseQuery(self.query_text)
        query_algebra = algebra.translateQuery(query_tree)
        self.query_from_algebra = translateAlgebra(query_algebra)

        query_tree_2 = parser.parseQuery(self.query_from_algebra)
        query_algebra_2 = algebra.translateQuery(query_tree_2)
        self.query_from_query_from_algebra = translateAlgebra(query_algebra_2)
        _pprint_query(self.query_from_query_from_algebra)

        test = Test(
            test_number=38,
            tc_desc="Test if subqueries get properly translated into the query text. "
            "The query must also be executable and shall not violate any SPARQL query syntax.",
            expected_result=self.query_from_algebra,
            actual_result=self.query_from_query_from_algebra,
        )

        return test

    def test_integration__complex_query1(self):
        query_tree = parser.parseQuery(self.query_text)
        query_algebra = algebra.translateQuery(query_tree)
        self.query_from_algebra = translateAlgebra(query_algebra)

        query_tree_2 = parser.parseQuery(self.query_from_algebra)
        query_algebra_2 = algebra.translateQuery(query_tree_2)
        self.query_from_query_from_algebra = translateAlgebra(query_algebra_2)
        _pprint_query(self.query_from_query_from_algebra)

        test = Test(
            test_number=39,
            tc_desc="Test a query with multiple graph patterns and solution modifiers "
            "gets properly translated into the query text. "
            "The query must also be executable and shall not violate any SPARQL query syntax.",
            expected_result=self.query_from_algebra,
            actual_result=self.query_from_query_from_algebra,
        )

        return test


t = TestAlgebraToTest(annotated_tests=False)
t.run_tests()
t.print_test_results()
