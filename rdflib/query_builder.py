from __future__ import unicode_literals

from rdflib import Variable, URIRef

AGGREGATE_FUNCTION_LIST = ["SUM", "AVG", "COUNT", "SET", "MIN", "MAX", "GROUPCONTACT", "SAMPLE"]
FUNCTION_EXPRESSION_SUPPORTED_LIST = [
    "ASC", "DESC", "IRI", "ISBLANK", "ISLITERAL", "ISIRI", "ISNUMERIC", "BNODE",
    "ABS", "IF", "RAND", "UUID", "STRUUID", "MD5", "SHA1", "SHA256",
    "SHA384", "SHA512", "COALESCE", "CEIL", "FLOOR", "ROUND", "REGEX",
    "REPLACE", "STRDT", "STRLANG", "CONCAT", "STRSTARTS", "STRENDS",
    "STRBEFORE", "STRAFTER", "CONTAINS", "ENCODE_FOR_URI", "SUBSTR",
    "STRLEN", "STR", "LCASE", "LANGMATCHES", "NOW", "YEAR", "MONTH",
    "DAY", "HOURS", "MINUTES", "SECONDS", "TIMEZONE", "TZ", "UCASE",
    "LANG", "DATATYPE", "SAMETERM", "BOUND", "EXISTS"
]


def is_variable_supported(variable):
    return hasattr(variable, "n3")


class STATEMENT(tuple):
    def __new__(cls, statement):
        if len(statement) == 3:
            s, p, o = statement
            if is_variable_supported(s) and is_variable_supported(
                    p) and is_variable_supported(o):
                return tuple.__new__(STATEMENT, (s, p, o))
            else:
                raise Exception(
                    "Values in the statement {} are not of acceptable types.".format(
                        statement
                    )
                )
        else:
            raise Exception("Statement has to be a tuple in the format (s, p, o)")

    def n3(self):
        return self[0].n3() + " " + self[1].n3() + " " + self[2].n3() + " ."


class Operators(object):

    @staticmethod
    def GT(left, right):
        if is_variable_supported(left) and is_variable_supported(right):
            return CONDITIONAL_STATEMENT(left, ">", right)
        else:
            raise Exception("Operands are not of acceptable type.")

    @staticmethod
    def LT(left, right):
        if is_variable_supported(left) and is_variable_supported(right):
            return CONDITIONAL_STATEMENT(left, "<", right)
        else:
            raise Exception("Operands are not of acceptable type.")

    @staticmethod
    def EQ(left, right):
        if is_variable_supported(left) and is_variable_supported(right):
            return CONDITIONAL_STATEMENT(left, "=", right)
        else:
            raise Exception("Operands are not of acceptable type.")

    @staticmethod
    def NE(left, right):
        if is_variable_supported(left) and is_variable_supported(right):
            return CONDITIONAL_STATEMENT(left, "!=", right)
        else:
            raise Exception("Operands are not of acceptable type.")

    @staticmethod
    def GE(left, right):
        if is_variable_supported(left) and is_variable_supported(right):
            return CONDITIONAL_STATEMENT(left, ">=", right)
        else:
            raise Exception("Operands are not of acceptable type.")

    @staticmethod
    def LE(left, right):
        if is_variable_supported(left) and is_variable_supported(right):
            return CONDITIONAL_STATEMENT(left, "<=", right)
        else:
            raise Exception("Operands are not of acceptable type.")

    @staticmethod
    def AND(left, right):
        if is_variable_supported(left) and is_variable_supported(right):
            return CONDITIONAL_STATEMENT(left, "&&", right)
        else:
            raise Exception("Operands are not of acceptable type.")

    @staticmethod
    def OR(left, right):
        if is_variable_supported(left) and is_variable_supported(right):
            return CONDITIONAL_STATEMENT(left, "||", right)
        else:
            raise Exception("Operands are not of acceptable type.")

    @staticmethod
    def IN(left, *args):
        if not is_variable_supported(left):
            raise Exception("Operands are not of acceptable type.")
        for var in args:
            if not is_variable_supported(var):
                raise Exception("Operands are not of acceptable type.")

        return CONDITIONAL_STATEMENT(left, "IN", *args)


class OPTIONAL(STATEMENT):
    def __new__(cls, statement):
        stmt = super(OPTIONAL, cls).__new__(cls, statement)
        return tuple.__new__(OPTIONAL, stmt)

    def n3(self):
        return "OPTIONAL { " + super().n3() + " }" + " ."


class CONDITIONAL_STATEMENT(STATEMENT):
    def __new__(cls, left, operator, *args):
        return tuple.__new__(CONDITIONAL_STATEMENT, (left, operator, args))

    def n3(self):
        n3_string = self[0].n3() + " " + self[1] + " "
        if len(self[2]) == 1:
            n3_string += self[2][0].n3()
        else:
            n3_string += "( "
            for i in range(len(self[2])):
                n3_string += self[2][i].n3()
                if i < len(self[2]) - 1:
                    n3_string += ", "
            n3_string += " )"

        return n3_string


class Aggregates(STATEMENT):
    def __new__(cls, function, statement):
        if not is_variable_supported(statement):
            raise Exception(
                "Statement in aggregate function {} not of acceptable type.".format(
                    function
                )
            )
        if function not in AGGREGATE_FUNCTION_LIST:
            raise Exception(
                "Aggregate Function {} not supported".format(
                    function
                )
            )

        return tuple.__new__(Aggregates, (function, statement))

    @staticmethod
    def create_aggregate(function_name):
        def new(cls, statement):
            return Aggregates.__new__(cls, function_name, statement)

        return type(str(function_name), (Aggregates,), dict(__new__=new))

    def n3(self):
        return self[0] + "( " + self[1].n3() + " )"


class FunctionExpressions(STATEMENT):
    def __new__(cls, function_expression, *args):
        for statement in args:
            if not is_variable_supported(statement):
                raise Exception(
                    "Statement {} in function expression {} not of acceptable type.".format(
                        statement, function_expression
                    )
                )

        if isinstance(function_expression, str):
            function_expression = function_expression.upper()

        if function_expression not in FUNCTION_EXPRESSION_SUPPORTED_LIST:
            raise Exception(
                "Function expression {} not supported".format(
                    function_expression)
            )

        return tuple.__new__(FunctionExpressions, (function_expression, args))

    @staticmethod
    def create_function_expressions(function_expression):
        def new(cls, *args):
            return FunctionExpressions.__new__(cls, function_expression, *args)

        return type(str(function_expression), (FunctionExpressions,), dict(__new__=new))

    def n3(self):
        n3_string = self[0] + " ( "
        for i in range(len(self[1])):
            n3_string += self[1][i].n3()
            if i < len(self[1]) - 1:
                n3_string += ", "
        n3_string += " )"
        return n3_string


for function in AGGREGATE_FUNCTION_LIST:
    setattr(Aggregates, function, Aggregates.create_aggregate(function))

for function_expression in FUNCTION_EXPRESSION_SUPPORTED_LIST:
    setattr(FunctionExpressions, function_expression,
            FunctionExpressions.create_function_expressions(function_expression))


class FILTER(STATEMENT):
    def __new__(cls, expression):
        if not is_variable_supported(expression):
            raise Exception(
                "Expression {} in FILTER not of acceptable type".format(
                    expression
                )
            )

        return tuple.__new__(FILTER, (expression,))

    def n3(self):
        return "FILTER ( " + self[0].n3() + " ) ."


class FOR_GRAPH(STATEMENT):
    def __new__(cls, *args, name=None):
        if name and not is_variable_supported(name):
            raise Exception("GRAPH name not of acceptable type.")

        statements = []
        for stmt in args:
            if not is_variable_supported(stmt):
                statements.append(STATEMENT(stmt))
            else:
                statements.append(stmt)

        return tuple.__new__(FOR_GRAPH, (name, statements))

    def n3(self):
        n3_string = ""
        if self[0]:
            n3_string += "GRAPH " + self[0].n3() + " "
        n3_string += "{ \n"

        for var in self[1]:
            n3_string += var.n3() + " \n"

        n3_string += "\n}  ."
        return n3_string


class QueryBuilder:
    class QueryString(str):
        def __new__(cls, query):
            return str.__new__(cls, query)

        def n3(self):
            return "{\n" + self + "\n}"

    def __init__(self):
        self.query = ""
        self.is_DISTINCT = False
        self.SELECT_variables_direct = []
        self.SELECT_variables_with_alias = {}
        self.INSERT_variables_direct = []
        self.DELETE_variables_direct = []
        self.WHERE_statements = []
        self.GROUP_BY_expressions = []
        self.ORDER_BY_expressions = []
        self.move_to_graph = None
        self.move_from_graph = None
        self.move_silent = False
        self.add_to_graph = None
        self.add_from_graph = None
        self.add_silent = False

        self.limit = None
        self.offset = None

    def SELECT(self, *args, distinct=False, **kwargs):
        self.is_DISTINCT = distinct

        for var in args:
            if isinstance(var, Aggregates):
                raise Exception(
                    "Alias not provided for {}".format(
                        var[1].n3()
                    )
                )
            if not is_variable_supported(var):
                raise Exception("Argument not of valid type.")

            self.SELECT_variables_direct.append(var)

        for var_name, var in kwargs.items():
            if not is_variable_supported(var):
                raise Exception("Argument not of valid type.")

            self.SELECT_variables_with_alias[Variable(var_name)] = var

        return self

    def MOVE(self, move_from_graph=URIRef("DEFAULT"), move_to_graph=URIRef("DEFAULT"), move_silent=False):
        if not is_variable_supported(move_from_graph):
            raise Exception("from_graph name not of acceptable type.")
        if not is_variable_supported(move_to_graph):
            raise Exception("to_graph name not of acceptable type.")
        self.move_from_graph = move_from_graph
        self.move_to_graph = move_to_graph
        self.move_silent = move_silent
        return self

    def ADD(self, add_from_graph=URIRef("DEFAULT"), add_to_graph=URIRef("DEFAULT"), add_silent=False):
        if not is_variable_supported(add_from_graph):
            raise Exception("from_graph name not of acceptable type.")
        if not is_variable_supported(add_to_graph):
            raise Exception("to_graph name not of acceptable type.")
        self.add_from_graph = add_from_graph
        self.add_to_graph = add_to_graph
        self.add_silent = add_silent
        return self

    def INSERT(self, *args):
        for statement in args:
            if not is_variable_supported(statement):
                self.INSERT_variables_direct.append(STATEMENT(statement))
            else:
                self.INSERT_variables_direct.append(statement)

        return self

    def DELETE(self, *args):
        for statement in args:
            if not is_variable_supported(statement):
                self.DELETE_variables_direct.append(STATEMENT(statement))
            else:
                self.DELETE_variables_direct.append(statement)

        return self

    def WHERE(self, *args, **kwargs):
        for statement in args:
            if not is_variable_supported(statement):
                self.WHERE_statements.append(STATEMENT(statement))
            else:
                self.WHERE_statements.append(statement)

        return self

    def LIMIT(self, value):
        self.limit = value

        return self

    def OFFSET(self, value):
        self.offset = value

        return self

    def GROUP_BY(self, *args):
        for var in args:
            if is_variable_supported(var):
                self.GROUP_BY_expressions.append(var)
            else:
                raise Exception("Expression passed in ORDER_BY is not valid.")

        return self

    def ORDER_BY(self, *args):
        for var in args:
            if is_variable_supported(var):
                self.ORDER_BY_expressions.append(var)
            else:
                raise Exception("Expression passed in ORDER_BY is not valid.")

        return self

    def build_select(self):
        if len(self.SELECT_variables_direct) + len(self.SELECT_variables_with_alias) > 0:
            self.query += "SELECT "

            if self.is_DISTINCT:
                self.query += "DISTINCT "

            for var in self.SELECT_variables_direct:
                self.query += var.n3() + " "

            for var_alias, var_expression in self.SELECT_variables_with_alias.items():
                self.query += "(" + var_expression.n3() + " as " + var_alias.n3() + ") "

            self.query += " \n"

    def build_move(self):
        if self.move_from_graph is not None and self.move_to_graph is not None:
            self.query += "MOVE "
            if self.move_silent:
                self.query += "SILENT "
            if self.move_from_graph.n3().lower() == "<default>":
                self.query += "DEFAULT"
            else:
                self.query += "GRAPH " + self.move_from_graph.n3()
            self.query += " TO "
            if self.move_to_graph.n3().lower() == "<default>":
                self.query += "DEFAULT"
            else:
                self.query += "GRAPH " + self.move_to_graph.n3()
            self.query += " \n"

    def build_add(self):
        if self.add_from_graph is not None and self.add_to_graph is not None:
            self.query += "ADD "
            if self.add_silent:
                self.query += "SILENT "
            if self.add_from_graph.n3().lower() == "<default>":
                self.query += "DEFAULT"
            else:
                self.query += "GRAPH " + self.add_from_graph.n3()
            self.query += " TO "
            if self.add_to_graph.n3().lower() == "<default>":
                self.query += "DEFAULT"
            else:
                self.query += "GRAPH " + self.add_to_graph.n3()
            self.query += " \n"

    def build_insert(self):
        if len(self.INSERT_variables_direct) > 0:
            self.query += "INSERT { \n"

            for var in self.INSERT_variables_direct:
                self.query += var.n3() + " "

            self.query += "\n} \n"

    def build_delete(self):
        if len(self.DELETE_variables_direct) > 0:
            self.query += "DELETE { \n"

            for var in self.DELETE_variables_direct:
                self.query += var.n3() + " "

            self.query += "\n} \n"

    def build_where(self):
        if self.move_from_graph is None and self.add_from_graph is None:
            if len(self.WHERE_statements) == 0:
                raise Exception("Query must have at least one WHERE statement.")

            self.query += "WHERE {" + " \n"

            for statement in self.WHERE_statements:
                self.query += statement.n3() + " \n"

            self.query += "}" + " \n"
        else:
            if len(self.WHERE_statements) > 0:
                raise Exception("WHERE unexpected with MOVE/ADD")

    def build_group_by_order_by(self):
        if len(self.GROUP_BY_expressions) > 0:
            self.query += "GROUP BY "
            for var in self.GROUP_BY_expressions:
                self.query += var.n3() + " "
            self.query += "\n"

        if len(self.ORDER_BY_expressions) > 0:
            self.query += "ORDER BY "
            for var in self.ORDER_BY_expressions:
                self.query += var.n3() + " "
            self.query += "\n"

    def build_limit_offset(self):
        if self.limit:
            self.query += "LIMIT " + str(self.limit) + " \n"

        if self.offset:
            self.query += "OFFSET " + str(self.offset) + " \n"

    def build(self):
        self.build_select()
        self.build_insert()
        self.build_delete()
        self.build_move()
        self.build_add()
        self.build_where()

        self.build_group_by_order_by()
        self.build_limit_offset()

        return QueryBuilder.QueryString(self.query)


if __name__ == "__main__":
    # query = QueryBuilder().INSERT(
    #         Variable("p"),
    #         Variable("o"),
    #         Variable("s")
    # ).WHERE(
    #     (Variable("s"), Variable("p"), Variable("o")),
    #     (Variable("o"), RDF.type, Variable("v")),
    #     OPTIONAL(
    #         (Variable("o"), RDFS.subClassOf, OWL.thing)
    #     ),
    #     FOR_GRAPH(
    #         FILTER(
    #             Operators.AND(
    #                 Operators.GE(Variable("v"), Literal(5)),
    #                 Operators.LT(Variable("v"), Literal(13))
    #             )
    #         ),
    #         name=URIRef("arshgraph_name_2")
    #     ),
    #     FOR_GRAPH(
    #         FILTER(
    #             Operators.IN(
    #                 Variable("v"),
    #                 Literal("literal_string_1"),
    #                 Literal("12", datatype=XSD.integer)
    #             )
    #         )
    #     )
    # ).GROUP_BY(
    #     Variable("v"),
    #     Variable("s")
    # ).ORDER_BY(
    #     Variable("v"),
    #     FUNCTION_EXPR.ASC(Variable("s"))
    # ).LIMIT(
    #     100
    # ).OFFSET(
    #     20
    # ).build()
    # print(query)

    query = QueryBuilder().ADD(
        add_from_graph=URIRef("default"),
        add_to_graph=URIRef("arshdeep"),
        add_silent=False
    ).build()

    print(query)
