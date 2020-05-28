import unittest

from rdflib import Variable, RDF, OWL, RDFS, Literal, URIRef
from rdflib.query_builder import QueryBuilder, Aggregates, OPTIONAL, FILTER, Operators, FunctionExpressions, FOR_GRAPH


class TestQueryBuilder_Issue790(unittest.TestCase):
    def setUp(self):
        self.var_s = Variable("s")
        self.var_p = Variable("p")
        self.var_p2 = Variable("p2")
        self.var_o = Variable("o")
        self.var_v = Variable("v")
        self.var_unacceptable = "s"
        self.literal_5 = Literal(5)
        self.literal_13 = Literal(13)
        self.literal_20 = Literal(20)
        self.literal_30 = Literal(30)

        self.add_query_from_default = "ADD DEFAULT TO GRAPH <Graph_1> "
        self.add_query_to_default = "ADD GRAPH <Graph_1> TO DEFAULT "
        self.add_query_without_default = "ADD GRAPH <Graph_1> TO GRAPH <Graph_2> "
        self.add_query_with_silent = "ADD SILENT GRAPH <Graph_1> TO GRAPH <Graph_2> "
        self.move_query_from_default = "MOVE DEFAULT TO GRAPH <Graph_1> "
        self.move_query_to_default = "MOVE GRAPH <Graph_1> TO DEFAULT "
        self.move_query_without_default = "MOVE GRAPH <Graph_1> TO GRAPH <Graph_2> "
        self.move_query_with_silent = "MOVE SILENT GRAPH <Graph_1> TO GRAPH <Graph_2> "
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
        self.group_by_query = "SELECT ?o  WHERE { ?s ?p ?o . } GROUP BY ?o "
        self.delete_query = "DELETE { ?s ?p ?o } WHERE { ?s ?p ?o . ?o ?p2 ?v . } "
        self.for_graph_query = "SELECT ?s ?p ?o  WHERE { ?s ?p ?o . GRAPH <graph_name_1> { ?o ?p2 ?v . OPTI" \
                               "ONAL { ?s ?p ?o . } . }  . } "
        self.nested_query = "SELECT ?s ?p ?o  WHERE { FILTER ( ?o IN {SELECT ?s  WHERE { ?s ?p2 ?o . } } ) . } "
        self.function_expr_multiple_parameters = "SELECT ?s  WHERE { ?s ?p ?o . FILTER ( CONTAINS ( LCASE ( ?o " \
                                                 "), \"hey\" ) ) . } "
        self.basic_query = "SELECT ?s (?o as ?x)  WHERE { ?s ?p ?o . } "
        self.full_query = "SELECT DISTINCT ?s ?p (?o as ?x) (AVG( ?v ) as ?value) (SUM( ?v ) as ?sum_value)  " \
                          "WHERE { ?s ?p ?o . ?o <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> ?v . OPTIO" \
                          "NAL { ?o <http://www.w3.org/2000/01/rdf-schema#subClassOf> <http://www.w3.org/2002" \
                          "/07/owl#thing> . } . FILTER ( ?v >= \"5\"^^<http://www.w3.org/2001/XMLSchema#integ" \
                          "er> && ?v < \"13\"^^<http://www.w3.org/2001/XMLSchema#integer> || ?v >= \"20\"^^<h" \
                          "ttp://www.w3.org/2001/XMLSchema#integer> && ?v < \"30\"^^<http://www.w3.org/2001/X" \
                          "MLSchema#integer> ) . } ORDER BY ?v ASC ( ?s ) LIMIT 100 OFFSET 20 "

    def test_full_query_should_pass(self):
        query = QueryBuilder().SELECT(
            self.var_s,
            self.var_p,
            x=self.var_o,
            value=Aggregates.AVG(self.var_v),
            sum_value=Aggregates.SUM(self.var_v),
            distinct=True
        ).WHERE(
            (self.var_s, self.var_p, self.var_o),
            (self.var_o, RDF.type, self.var_v),
            OPTIONAL(
                (self.var_o, RDFS.subClassOf, OWL.thing)
            ),
            FILTER(
                Operators.OR(
                    Operators.AND(
                        Operators.GE(self.var_v, self.literal_5),
                        Operators.LT(self.var_v, self.literal_13)
                    ),
                    Operators.AND(
                        Operators.GE(self.var_v, self.literal_20),
                        Operators.LT(self.var_v, self.literal_30)
                    )
                )
            )
        ).ORDER_BY(
            self.var_v,
            FunctionExpressions.ASC(self.var_s)
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

    def test_query_insert_should_pass(self):
        query = QueryBuilder().INSERT(
            self.var_s,
            self.var_p,
            self.var_o,
        ).WHERE(
            (self.var_s, self.var_p, self.var_o)
        ).build()
        self.assertEqual(self.insert_query, query.replace("\n", ""), msg="QueryBuilder not performing insert correctly")

    def test_query_insert_with_incorrect_parameter_raises_Exception(self):
        with self.assertRaises(Exception):
            QueryBuilder().INSERT(
                self.var_unacceptable,
                self.var_p,
                self.var_o
            ).WHERE(
                (self.var_s, self.var_p, self.var_o)
            ).build()

    def test_query_operators_should_pass(self):
        query = QueryBuilder().SELECT(
            self.var_v
        ).WHERE(
            (self.var_s, self.var_p, self.var_v),
            FILTER(
                Operators.GT(self.var_v, self.literal_5)
            )
        ).build()
        self.assertEqual(self.operator_query_gt, query.replace("\n", ""),
                         msg="QueryBuilder not returning correct operator GT query.")

        query = QueryBuilder().SELECT(
            self.var_v
        ).WHERE(
            (self.var_s, self.var_p, self.var_v),
            FILTER(
                Operators.LT(self.var_v, self.literal_5)
            )
        ).build()
        self.assertEqual(self.operator_query_lt, query.replace("\n", ""),
                         msg="QueryBuilder not returning correct operator LT query.")

        query = QueryBuilder().SELECT(
            self.var_v
        ).WHERE(
            (self.var_s, self.var_p, self.var_v),
            FILTER(
                Operators.EQ(self.var_v, self.literal_5)
            )
        ).build()
        self.assertEqual(self.operator_query_eq, query.replace("\n", ""),
                         msg="QueryBuilder not returning correct operator EQ query.")

        query = QueryBuilder().SELECT(
            self.var_v
        ).WHERE(
            (self.var_s, self.var_p, self.var_v),
            FILTER(
                Operators.NE(self.var_v, self.literal_5)
            )
        ).build()
        self.assertEqual(self.operator_query_ne, query.replace("\n", ""),
                         msg="QueryBuilder not returning correct operator NE query.")

        query = QueryBuilder().SELECT(
            self.var_v
        ).WHERE(
            (self.var_s, self.var_p, self.var_v),
            FILTER(
                Operators.GE(self.var_v, self.literal_5)
            )
        ).build()
        self.assertEqual(self.operator_query_ge, query.replace("\n", ""),
                         msg="QueryBuilder not returning correct operator GE query.")

        query = QueryBuilder().SELECT(
            self.var_v
        ).WHERE(
            (self.var_s, self.var_p, self.var_v),
            FILTER(
                Operators.LE(self.var_v, self.literal_5)
            )
        ).build()
        self.assertEqual(self.operator_query_le, query.replace("\n", ""),
                         msg="QueryBuilder not returning correct operator LE query.")

        query = QueryBuilder().SELECT(
            self.var_v
        ).WHERE(
            (self.var_s, self.var_p, self.var_v),
            FILTER(
                Operators.IN(self.literal_5, self.var_v, self.literal_5)
            )
        ).build()
        self.assertEqual(self.operator_query_in, query.replace("\n", ""),
                         msg="QueryBuilder not returning correct operator IN query.")

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
                x=Aggregates.SUM(self.var_unacceptable)
            ).WHERE(
                (self.var_s, self.var_p, self.var_o)
            ).build()

    def test_query_with_aggregate_without_alias_raises_Exception(self):
        with self.assertRaises(Exception):
            QueryBuilder().SELECT(
                Aggregates.SUM(self.var_o)
            ).WHERE(
                (self.var_s, self.var_p, self.var_o)
            ).build()

        with self.assertRaises(Exception):
            QueryBuilder().SELECT(
                Aggregates.SUM(self.var_unacceptable)
            ).WHERE(
                (self.var_s, self.var_p, self.var_o)
            ).build()

    def test_query_function_expr_with_unacceptable_variable_raises_Exception(self):
        with self.assertRaises(Exception):
            QueryBuilder().SELECT(
                self.var_s,
                x=Aggregates.SUM(self.var_o)
            ).WHERE(
                (self.var_s, self.var_p, self.var_o),
                FILTER(Operators.EQ(FunctionExpressions.LCASE(self.var_unacceptable), Literal("hey")))
            ).build()

        with self.assertRaises(Exception):
            QueryBuilder().SELECT(
                self.var_s,
                x=Aggregates.SUM(self.var_o)
            ).WHERE(
                (self.var_s, self.var_p, self.var_o),
                FILTER(FunctionExpressions.CONTAINS(self.var_unacceptable, "hey"))
            ).build()

    def test_query_with_incorrect_expression_in_filter_raises_Exception(self):
        with self.assertRaises(Exception):
            QueryBuilder().SELECT(
                self.var_s,
                x=Aggregates.SUM(self.var_o)
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

    def test_query_with_group_by_should_pass(self):
        query = QueryBuilder().SELECT(
            self.var_o
        ).WHERE(
            (self.var_s, self.var_p, self.var_o)
        ).GROUP_BY(
            self.var_o
        ).build()
        self.assertEqual(self.group_by_query, query.replace("\n", ""),
                         msg="QueryBuilder not returning correct group by query.")

    def test_query_with_group_by_incorrect_parameter_raises_Exception(self):
        with self.assertRaises(Exception):
            QueryBuilder().SELECT(
                self.var_o
            ).WHERE(
                (self.var_s, self.var_p, self.var_o)
            ).GROUP_BY(
                self.var_unacceptable
            ).build()

    def test_query_with_delete_should_pass(self):
        query = QueryBuilder().DELETE(
            self.var_s, self.var_p, self.var_o
        ).WHERE(
            (self.var_s, self.var_p, self.var_o),
            (self.var_o, self.var_p2, self.var_v)
        ).build()
        self.assertEqual(self.delete_query, query.replace("\n", ""),
                         msg="QueryBuilder not returning correct delete query.")

    def test_query_with_delete_incorrect_parameter_raises_Exception(self):
        with self.assertRaises(Exception):
            QueryBuilder().DELETE(
                self.var_s, self.var_p, self.var_unacceptable
            ).WHERE(
                (self.var_s, self.var_p, self.var_o),
                (self.var_o, self.var_p2, self.var_v)
            ).build()

    def test_query_with_order_by_incorrect_parameter_raises_Exception(self):
        with self.assertRaises(Exception):
            QueryBuilder().SELECT(
                self.var_s
            ).WHERE(
                (self.var_s, self.var_p, self.var_o)
            ).GROUP_BY(
                self.var_s
            ).ORDER_BY(
                self.var_unacceptable
            ).build()

    def test_query_for_graph_should_pass(self):
        query = QueryBuilder().SELECT(
            self.var_s, self.var_p, self.var_o
        ).WHERE(
            (self.var_s, self.var_p, self.var_o),
            FOR_GRAPH(
                (self.var_o, self.var_p2, self.var_v),
                OPTIONAL(
                    (self.var_s, self.var_p, self.var_o)
                ),
                name=URIRef("graph_name_1")
            )
        ).build()
        self.assertEqual(self.for_graph_query, query.replace("\n", ""),
                         msg="QueryBuilder not returning correct query for FOR_GRAPH functions.")

    def test_query_for_graph_name_unacceptable_raises_Exception(self):
        with self.assertRaises(Exception):
            QueryBuilder().SELECT(
                self.var_s, self.var_p, self.var_o
            ).WHERE(
                (self.var_s, self.var_p, self.var_o),
                FOR_GRAPH(
                    (self.var_o, self.var_p2, self.var_v),
                    name="graph_name_1"
                )
            ).build()

    def test_query_with_nested_query_should_pass(self):
        query = QueryBuilder().SELECT(
            self.var_s, self.var_p, self.var_o
        ).WHERE(
            FILTER(
                Operators.IN(
                    self.var_o,
                    QueryBuilder().SELECT(
                        self.var_s
                    ).WHERE(
                        (self.var_s, self.var_p2, self.var_o)
                    ).build()
                )
            )
        ).build()
        self.assertEqual(self.nested_query, query.replace("\n", ""),
                         msg="QueryBuilder not returning correct query for nested queries.")

    def test_query_function_expr_with_multiple_paramters_should_pass(self):
        query = QueryBuilder().SELECT(
            self.var_s
        ).WHERE(
            (self.var_s, self.var_p, self.var_o),
            FILTER(FunctionExpressions.CONTAINS(FunctionExpressions.LCASE(self.var_o), Literal("hey")))
        ).build()
        self.assertEqual(self.function_expr_multiple_parameters, query.replace("\n", ""),
                         msg="QueryBuilder not returning correct query for function expr with multiple parameters.")

    def test_query_move_should_pass(self):
        query = QueryBuilder().MOVE(
            move_from_graph=URIRef("default"),
            move_to_graph=URIRef("Graph_1")
        ).build()
        self.assertEqual(self.move_query_from_default, query.replace("\n", ""), msg="QueryBuilder not returning correct query for move")

        query = QueryBuilder().MOVE(
            move_from_graph=URIRef("Graph_1"),
            move_to_graph=URIRef("default")
        ).build()
        self.assertEqual(self.move_query_to_default, query.replace("\n", ""), msg="QueryBuilder not returning correct query for move")

        query = QueryBuilder().MOVE(
            move_from_graph=URIRef("Graph_1"),
            move_to_graph=URIRef("Graph_2")
        ).build()
        self.assertEqual(self.move_query_without_default, query.replace("\n", ""),
                         msg="QueryBuilder not returning correct query for move")

        query = QueryBuilder().MOVE(
            move_from_graph=URIRef("Graph_1"),
            move_to_graph=URIRef("Graph_2"),
            move_silent=True
        ).build()
        self.assertEqual(self.move_query_with_silent, query.replace("\n", ""),
                         msg="QueryBuilder not returning correct query for move with Silent")

    def test_query_move_with_where_raises_exception(self):
        with self.assertRaises(Exception):
            QueryBuilder().MOVE(
                move_from_graph=URIRef("default"),
                move_to_graph=URIRef("Graph_1")
            ).WHERE(
                (self.var_s, self.var_o, self.var_p)
            ).build()

    def test_query_move_graph_name_unacceptable_raises_exception(self):
        with self.assertRaises(Exception):
            QueryBuilder().MOVE(
                move_from_graph="default",
                move_to_graph=URIRef("Graph_1")
            ).build()

        with self.assertRaises(Exception):
            QueryBuilder().MOVE(
                move_from_graph=URIRef("default"),
                move_to_graph="Graph_1"
            ).build()

    def test_query_add_should_pass(self):
        query = QueryBuilder().ADD(
            add_from_graph=URIRef("default"),
            add_to_graph=URIRef("Graph_1")
        ).build()
        self.assertEqual(self.add_query_from_default, query.replace("\n", ""), msg="QueryBuilder not returning correct query for add")

        query = QueryBuilder().ADD(
            add_from_graph=URIRef("Graph_1"),
            add_to_graph=URIRef("default")
        ).build()
        self.assertEqual(self.add_query_to_default, query.replace("\n", ""), msg="QueryBuilder not returning correct query for add")

        query = QueryBuilder().ADD(
            add_from_graph=URIRef("Graph_1"),
            add_to_graph=URIRef("Graph_2")
        ).build()
        self.assertEqual(self.add_query_without_default, query.replace("\n", ""),
                         msg="QueryBuilder not returning correct query for ADD")

        query = QueryBuilder().ADD(
            add_from_graph=URIRef("Graph_1"),
            add_to_graph=URIRef("Graph_2"),
            add_silent=True
        ).build()
        self.assertEqual(self.add_query_with_silent, query.replace("\n", ""),
                         msg="QueryBuilder not returning correct query for add with Silent")

    def test_query_add_with_where_raises_exception(self):
        with self.assertRaises(Exception):
            QueryBuilder().ADD(
                add_from_graph=URIRef("default"),
                add_to_graph=URIRef("Graph_1")
            ).WHERE(
                (self.var_s, self.var_o, self.var_p)
            ).build()

    def test_query_add_graph_name_unacceptable_raises_exception(self):
        with self.assertRaises(Exception):
            QueryBuilder().ADD(
                add_from_graph="default",
                add_to_graph=URIRef("Graph_1")
            ).build()

        with self.assertRaises(Exception):
            QueryBuilder().ADD(
                add_from_graph=URIRef("default"),
                add_to_graph="Graph_1"
            ).build()
