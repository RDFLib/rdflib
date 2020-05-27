import unittest

from rdflib import Variable, RDF, OWL, RDFS, Literal
from rdflib.query_builder import QueryBuilder, AGGREGATE, OPTIONAL, FILTER, Operators, FUNCTION_EXPR


class TestQueryBuilder_Issue790(unittest.TestCase):
    def setUp(self):
        self.var_s = Variable("s")
        self.var_p = Variable("p")
        self.var_o = Variable("o")
        self.var_v = Variable("v")
        self.var_unacceptable = "s"
        self.literal_5 = Literal(5)
        self.literal_13 = Literal(13)

        self.basic_query = "SELECT ?s (?o as ?x)  WHERE { ?s ?p ?o . } "
        self.full_query = "SELECT DISTINCT ?s ?p (?o as ?x) (AVG( ?v ) as ?value) (SUM( ?v ) as ?sum_value)" \
                          "  WHERE { ?s ?p ?o . ?o <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> ?v . O" \
                          "PTIONAL { ?o <http://www.w3.org/2000/01/rdf-schema#subClassOf> <http://www.w3.or" \
                          "g/2002/07/owl#thing> } . FILTER ( ?v >= \"5\"^^<http://www.w3.org/2001/XMLSchema" \
                          "#integer> && ?v < \"13\"^^<http://www.w3.org/2001/XMLSchema#integer> )  . } ORDE" \
                          "R BY ?v ASC ( ?s ) LIMIT 100 OFFSET 20 "

    def test_full_query(self):
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

    def test_basic_query(self):
        query = QueryBuilder().SELECT(
            self.var_s,
            x=self.var_o
        ).WHERE(
            (self.var_s, self.var_p, self.var_o)
        ).build()
        self.assertEqual(self.basic_query, query.replace("\n", ""),
                         msg="QueryBuilder not returning correct basic query.")

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

    def test_query_with_incorrect_expression_in_operators_raises_Exception(self):
        with self.assertRaises(Exception):
            QueryBuilder().SELECT(
                self.var_s,
                x=AGGREGATE.SUM(self.var_o)
            ).WHERE(
                (self.var_s, self.var_p, self.var_o),
                FILTER(Operators.EQ(FUNCTION_EXPR.LCASE(self.var_o), "hey"))
            ).build()
