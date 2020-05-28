import unittest

from rdflib import Variable, RDF, OWL, RDFS, Literal, URIRef
from rdflib.query_builder import QueryBuilder, AGGREGATE, OPTIONAL, FILTER, Operators, FUNCTION_EXPR, FOR_GRAPH


class TestQueryBuilder_Issue790(unittest.TestCase):
    def setUp(self):
        self.var_s = Variable("s")
        self.var_p = Variable("p")
        self.var_o = Variable("o")
        self.var_v = Variable("v")
        self.var_unacceptable = "s"
        self.literal_5 = Literal(5)
        self.literal_13 = Literal(13)
        self.insert_query = "INSERT { ?s ?p ?o } WHERE { ?s ?p ?o . } "
        self.operator_query_gt = "SELECT ?v  WHERE { ?s ?p ?v . FILTER ( ?v > " \
                                 "\"5\"^^<http://www.w3.org/2001/XMLSchema#integer> ) . } "
        self.operator_query_lt = "SELECT ?v  WHERE { ?s ?p ?v . FILTER ( ?v < " \
                                 "\"5\"^^<http://www.w3.org/2001/XMLSchema#integer> ) . } "
        self.operator_query_eq = "SELECT ?v  WHERE { ?s ?p ?v . FILTER ( ?v = " \
                                 "\"5\"^^<http://www.w3.org/2001/XMLSchema#integer> ) . } "
        self.operator_query_ne = "SELECT ?v  WHERE { ?s ?p ?v . FILTER ( ?v != " \
                                 "\"5\"^^<http://www.w3.org/2001/XMLSchema#integer> ) . } "
        self.operator_query_ge = "SELECT ?v  WHERE { ?s ?p ?v . FILTER ( ?v >= " \
                                 "\"5\"^^<http://www.w3.org/2001/XMLSchema#integer> ) . } "
        self.operator_query_le = "SELECT ?v  WHERE { ?s ?p ?v . FILTER ( ?v <= " \
                                 "\"5\"^^<http://www.w3.org/2001/XMLSchema#integer> ) . } "
        self.operator_query_in = "SELECT ?v  WHERE { ?s ?p ?v . FILTER ( " \
                                 "\"5\"^^<http://www.w3.org/2001/XMLSchema#integer> IN ( ?v, " \
                                 "\"5\"^^<http://www.w3.org/2001/XMLSchema#integer> ) ) . } "
        self.basic_query = "SELECT ?s (?o as ?x)  WHERE { ?s ?p ?o . } "
        self.full_query = "SELECT DISTINCT ?s ?p (?o as ?x) (AVG( ?v ) as ?value) (SUM( ?v ) as ?sum_value)" \
                          "  WHERE { ?s ?p ?o . ?o <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> ?v . O" \
                          "PTIONAL { ?o <http://www.w3.org/2000/01/rdf-schema#subClassOf> <http://www.w3.or" \
                          "g/2002/07/owl#thing> } . FILTER ( ?v >= \"5\"^^<http://www.w3.org/2001/XMLSchema" \
                          "#integer> && ?v < \"13\"^^<http://www.w3.org/2001/XMLSchema#integer> ) . } ORDE" \
                          "R BY ?v ASC ( ?s ) LIMIT 100 OFFSET 20 "

    def test_full_query_should_pass(self):
        query = QueryBuilder().SELECT(
            self.var_s,
            self.var_p,
            x=self.var_o,
            value=AGGREGATE.AVG(self.var_v),
            sum_value=AGGREGATE.SUM(self.var_v),
            distinct=True
        ).WHERE(
            (self.var_s, self.var_p, self.var_o),
            (self.var_o, RDF.type, self.var_v),
            OPTIONAL(
                (self.var_o, RDFS.subClassOf, OWL.thing)
            ),
            FILTER(
                Operators.AND(
                    Operators.GE(self.var_v, self.literal_5),
                    Operators.LT(self.var_v, self.literal_13)
                )
            )
        ).ORDER_BY(
            self.var_v,
            FUNCTION_EXPR.ASC(self.var_s)
        ).LIMIT(
            100
        ).OFFSET(
            20
        ).build()
        self.assertEqual(self.full_query, query.replace("\n", ""), msg="QueryBuilder not returning correct full query.")

    def test_basic_query_should_pass(self):
        query = QueryBuilder().SELECT(
            self.var_s,
            x=self.var_o
        ).WHERE(
            (self.var_s, self.var_p, self.var_o)
        ).build()
        self.assertEqual(self.basic_query, query.replace("\n", ""),
                         msg="QueryBuilder not returning correct basic query.")

    def test_query_insert(self):
        query = QueryBuilder().INSERT(
                self.var_s,
                self.var_p,
                self.var_o,
            ).WHERE(
                (self.var_s, self.var_p, self.var_o)
        ).build()
        self.assertEqual(self.insert_query, query.replace("\n", ""), msg="QueryBuilder not performing insert correctly")

    def test_query_operators_should_pass(self):
        query = QueryBuilder().SELECT(
            self.var_v
        ).WHERE(
            (self.var_s, self.var_p, self.var_v),
            FILTER(
                Operators.GT(self.var_v, self.literal_5)
            )
        ).build()
        self.assertEqual(self.operator_query_gt, query.replace("\n", ""), msg="QueryBuilder not returning correct "
                                                                           "operator GT query.")

        query = QueryBuilder().SELECT(
            self.var_v
        ).WHERE(
            (self.var_s, self.var_p, self.var_v),
            FILTER(
                Operators.LT(self.var_v, self.literal_5)
            )
        ).build()
        self.assertEqual(self.operator_query_lt, query.replace("\n", ""), msg="QueryBuilder not returning correct "
                                                                           "operator LT query.")

        query = QueryBuilder().SELECT(
            self.var_v
        ).WHERE(
            (self.var_s, self.var_p, self.var_v),
            FILTER(
                Operators.EQ(self.var_v, self.literal_5)
            )
        ).build()
        self.assertEqual(self.operator_query_eq, query.replace("\n", ""), msg="QueryBuilder not returning correct "
                                                                           "operator EQ query.")

        query = QueryBuilder().SELECT(
            self.var_v
        ).WHERE(
            (self.var_s, self.var_p, self.var_v),
            FILTER(
                Operators.NE(self.var_v, self.literal_5)
            )
        ).build()
        self.assertEqual(self.operator_query_ne, query.replace("\n", ""), msg="QueryBuilder not returning correct "
                                                                           "operator NE query.")

        query = QueryBuilder().SELECT(
            self.var_v
        ).WHERE(
            (self.var_s, self.var_p, self.var_v),
            FILTER(
                Operators.GE(self.var_v, self.literal_5)
            )
        ).build()
        self.assertEqual(self.operator_query_ge, query.replace("\n", ""), msg="QueryBuilder not returning correct "
                                                                           "operator GE query.")

        query = QueryBuilder().SELECT(
            self.var_v
        ).WHERE(
            (self.var_s, self.var_p, self.var_v),
            FILTER(
                Operators.LE(self.var_v, self.literal_5)
            )
        ).build()
        self.assertEqual(self.operator_query_le, query.replace("\n", ""), msg="QueryBuilder not returning correct "
                                                                           "operator LE query.")

        query = QueryBuilder().SELECT(
            self.var_v
        ).WHERE(
            (self.var_s, self.var_p, self.var_v),
            FILTER(
                Operators.IN(self.literal_5, self.var_v, self.literal_5)
            )
        ).build()
        self.assertEqual(self.operator_query_in, query.replace("\n", ""), msg="QueryBuilder not returning correct "
                                                                              "operator IN query.")

    def test_query_with_incorrect_expression_in_operators_raises_Exception(self):

        with self.assertRaises(Exception):
            QueryBuilder().SELECT(
                self.var_s
            ).WHERE(
                (self.var_s, self.var_p, self.var_o),
                FILTER(
                    Operators.GT("string", self.literal_5)
                )
            ).build()

        with self.assertRaises(Exception):
            QueryBuilder().SELECT(
                self.var_s
            ).WHERE(
                (self.var_s, self.var_p, self.var_o),
                FILTER(
                    Operators.GT(self.literal_5, "string")
                )
            ).build()

        with self.assertRaises(Exception):
            QueryBuilder().SELECT(
                self.var_s
            ).WHERE(
                (self.var_s, self.var_p, self.var_o),
                FILTER(
                    Operators.LT("string", self.literal_5)
                )
            ).build()

        with self.assertRaises(Exception):
            QueryBuilder().SELECT(
                self.var_s
            ).WHERE(
                (self.var_s, self.var_p, self.var_o),
                FILTER(
                    Operators.LT(self.literal_5, "string")
                )
            ).build()

        with self.assertRaises(Exception):
            QueryBuilder().SELECT(
                self.var_s
            ).WHERE(
                (self.var_s, self.var_p, self.var_o),
                FILTER(
                    Operators.EQ("string", self.literal_5)
                )
            ).build()

        with self.assertRaises(Exception):
            QueryBuilder().SELECT(
                self.var_s
            ).WHERE(
                (self.var_s, self.var_p, self.var_o),
                FILTER(
                    Operators.EQ(self.literal_5, "string")
                )
            ).build()

        with self.assertRaises(Exception):
            QueryBuilder().SELECT(
                self.var_s
            ).WHERE(
                (self.var_s, self.var_p, self.var_o),
                FILTER(
                    Operators.NE("string", self.literal_5)
                )
            ).build()

        with self.assertRaises(Exception):
            QueryBuilder().SELECT(
                self.var_s
            ).WHERE(
                (self.var_s, self.var_p, self.var_o),
                FILTER(
                    Operators.NE(self.literal_5, "string")
                )
            ).build()

        with self.assertRaises(Exception):
            QueryBuilder().SELECT(
                self.var_s
            ).WHERE(
                (self.var_s, self.var_p, self.var_o),
                FILTER(
                    Operators.GE("string", self.literal_5)
                )
            ).build()

        with self.assertRaises(Exception):
            QueryBuilder().SELECT(
                self.var_s
            ).WHERE(
                (self.var_s, self.var_p, self.var_o),
                FILTER(
                    Operators.GE(self.literal_5, "string")
                )
            ).build()

        with self.assertRaises(Exception):
            QueryBuilder().SELECT(
                self.var_s
            ).WHERE(
                (self.var_s, self.var_p, self.var_o),
                FILTER(
                    Operators.LE("string", self.literal_5)
                )
            ).build()

        with self.assertRaises(Exception):
            QueryBuilder().SELECT(
                self.var_s
            ).WHERE(
                (self.var_s, self.var_p, self.var_o),
                FILTER(
                    Operators.LE(self.literal_5, "string")
                )
            ).build()

        with self.assertRaises(Exception):
            QueryBuilder().SELECT(
                self.var_s
            ).WHERE(
                (self.var_s, self.var_p, self.var_o),
                FILTER(
                    Operators.AND(
                        Operators.LE(self.var_s, self.literal_5),
                        "string"
                    )
                )
            ).build()

        with self.assertRaises(Exception):
            QueryBuilder().SELECT(
                self.var_s
            ).WHERE(
                (self.var_s, self.var_p, self.var_o),
                FILTER(
                    Operators.AND(
                        "string",
                        Operators.LE(self.var_s, self.literal_5)

                    )
                )
            ).build()

        with self.assertRaises(Exception):
            QueryBuilder().SELECT(
                self.var_s
            ).WHERE(
                (self.var_s, self.var_p, self.var_o),
                FILTER(
                    Operators.OR(
                        Operators.LE(self.var_s, self.literal_5),
                        "string"
                    )
                )
            ).build()

        with self.assertRaises(Exception):
            QueryBuilder().SELECT(
                self.var_s
            ).WHERE(
                (self.var_s, self.var_p, self.var_o),
                FILTER(
                    Operators.OR(
                        "string",
                        Operators.LE(self.var_s, self.literal_5)

                    )
                )
            ).build()

        with self.assertRaises(Exception):
            QueryBuilder().SELECT(
                self.var_v
            ).WHERE(
                (self.var_s, self.var_p, self.var_v),
                FILTER(
                    Operators.IN(self.var_unacceptable, self.var_v, self.literal_5)
                )
            ).build()

        with self.assertRaises(Exception):
            QueryBuilder().SELECT(
                self.var_v
            ).WHERE(
                (self.var_s, self.var_p, self.var_v),
                FILTER(
                    Operators.IN(self.literal_5, self.var_v, self.var_unacceptable)
                )
            ).build()


    def test_query_without_where_raises_Exception(self):
        with self.assertRaises(Exception):
            QueryBuilder().SELECT(self.var_s).build()

    def test_query_incorrect_parameter_type_in_select_raises_Exception(self):
        with self.assertRaises(Exception):
            QueryBuilder().SELECT(self.var_unacceptable)

        with self.assertRaises(Exception):
            QueryBuilder().SELECT(a=self.var_unacceptable)

    def test_query_where_tuple_size2_as_arguments_raises_Exception(self):
        with self.assertRaises(Exception):
            QueryBuilder().SELECT(
                self.var_s
            ).WHERE(
                (self.var_p, self.var_o)
            )

    def test_query_where_incorrect_parameters_as_arguments_raises_Exception(self):
        with self.assertRaises(Exception):
            QueryBuilder().SELECT(
                self.var_s
            ).WHERE(
                (self.var_p, self.var_unacceptable, self.var_o)
            )

        with self.assertRaises(Exception):
            QueryBuilder().SELECT(
                self.var_s
            ).WHERE(
                (self.var_unacceptable, self.var_p, self.var_o)
            )

        with self.assertRaises(Exception):
            QueryBuilder().SELECT(
                self.var_s
            ).WHERE(
                (self.var_p, self.var_o, self.var_unacceptable)
            )

        with self.assertRaises(Exception):
            QueryBuilder().SELECT(
                self.var_s
            ).WHERE(
                self.var_unacceptable
            )

    def test_query_aggregate_with_unacceptable_variable_raises_Exception(self):
        with self.assertRaises(Exception):
            QueryBuilder().SELECT(
                x=AGGREGATE.SUM(self.var_unacceptable)
            ).WHERE(
                (self.var_s, self.var_p, self.var_o)
            ).build()

    def test_query_with_aggregate_without_alias_raises_Exception(self):
        with self.assertRaises(Exception):
            QueryBuilder().SELECT(
                AGGREGATE.SUM(self.var_o)
            ).WHERE(
                (self.var_s, self.var_p, self.var_o)
            ).build()

        with self.assertRaises(Exception):
            QueryBuilder().SELECT(
                AGGREGATE.SUM(self.var_unacceptable)
            ).WHERE(
                (self.var_s, self.var_p, self.var_o)
            ).build()

    def test_query_function_expr_with_unacceptable_variable_raises_Exception(self):
        with self.assertRaises(Exception):
            QueryBuilder().SELECT(
                self.var_s,
                x=AGGREGATE.SUM(self.var_o)
            ).WHERE(
                (self.var_s, self.var_p, self.var_o),
                FILTER(Operators.EQ(FUNCTION_EXPR.LCASE(self.var_unacceptable), Literal("hey")))
            ).build()

        with self.assertRaises(Exception):
            QueryBuilder().SELECT(
                self.var_s,
                x=AGGREGATE.SUM(self.var_o)
            ).WHERE(
                (self.var_s, self.var_p, self.var_o),
                FILTER(FUNCTION_EXPR.CONTAINS(self.var_unacceptable, "hey"))
            ).build()

    def test_query_with_incorrect_expression_in_filter_raises_Exception(self):
        with self.assertRaises(Exception):
            QueryBuilder().SELECT(
                self.var_s,
                x=AGGREGATE.SUM(self.var_o)
            ).WHERE(
                (self.var_s, self.var_p, self.var_o),
                FILTER(self.var_unacceptable)
            ).build()

    def test_query_with_incorrect_function_name(self):
        with self.assertRaises(Exception):
            QueryBuilder().SELECT(
                self.var_s,
                x=AGGREGATE("MUL", self.var_o)
            ).WHERE(
                (self.var_s, self.var_p, self.var_o),
            ).build()

        with self.assertRaises(Exception):
            QueryBuilder().SELECT(
                self.var_s,
                x=FUNCTION_EXPR("SUBSTRING", self.var_o)
            ).WHERE(
                (self.var_s, self.var_p, self.var_o),
            ).build()
