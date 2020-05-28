from __future__ import unicode_literals

from rdflib import Variable, URIRef, RDF, RDFS, Literal, XSD, OWL

# list of supported aggregate functions
AGGREGATE_FUNCTION_LIST = ["SUM", "AVG", "COUNT", "SET", "MIN", "MAX", "GROUPCONTACT", "SAMPLE"]
# list of supported functions expressions
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
    """
    Function to check the input variable in query.
    The variable should have a n3() function that provides the n triple format output.

    :param variable: individual to be checked.
    :return: boolean
    """
    return hasattr(variable, "n3")


class STATEMENT(tuple):
    """
    Class to store triples in format of tuples.

    This object is used to define an n3() function for triples
    given as input in form of tuples. It extends tuple class and
    the objects can be accessed in a similar manner.

    Each triple has to be a tuple of length 3, in format (s, p, o).

    Made to be used internally and not be called by user.
    """
    def __new__(cls, statement):
        """
        Function to define the new object created using STATEMENT class.
        There should be 3 variables in the statement and all should be supported.

        :param statement: the variable to be converted to the given class.
        :return: tuple type STATEMENT
        """
        # has to be of length 3 (s, p, o)
        if len(statement) == 3:
            s, p, o = statement
            # check the variable support
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
        """
        Function to provide the n triple format of the object.
        Each triple in its n3() format is: "?s ?p ?o ."

        :return: string
        """
        return self[0].n3() + " " + self[1].n3() + " " + self[2].n3() + " ."


class Operators(object):
    """
    Class is meant to be used with FILTER while making a conditional query.

    To be used as:
    >> Operators.GT(var1, var2)
    The above statement gives an output of var1 > var2.

    This class can be nested inside itself to produce a complex expression.
    """
    @staticmethod
    def GT(left, right):
        """
        Greater than operator. Accepts only 2 arguments.

        :param left: left argument for the operator
        :param right: right argument for the operator
        :return: CONDITIONAL_STATEMENT, storing the details.
        """
        # check the variables support in both arguments
        if is_variable_supported(left) and is_variable_supported(right):
            return CONDITIONAL_STATEMENT(left, ">", right)
        else:
            raise Exception("Operands are not of acceptable type.")

    @staticmethod
    def LT(left, right):
        """
        Less than operator. Accepts only 2 arguments.

        :param left: left argument for the operator
        :param right: right argument for the operator
        :return: CONDITIONAL_STATEMENT, storing the details.
        """
        # check the variables support in both arguments
        if is_variable_supported(left) and is_variable_supported(right):
            return CONDITIONAL_STATEMENT(left, "<", right)
        else:
            raise Exception("Operands are not of acceptable type.")

    @staticmethod
    def EQ(left, right):
        """
        Equality operator. Accepts only 2 arguments.

        :param left: left argument for the operator
        :param right: right argument for the operator
        :return: CONDITIONAL_STATEMENT, storing the details.
        """
        # check the variables support in both arguments
        if is_variable_supported(left) and is_variable_supported(right):
            return CONDITIONAL_STATEMENT(left, "=", right)
        else:
            raise Exception("Operands are not of acceptable type.")

    @staticmethod
    def NE(left, right):
        """
        Unequality operator. Accepts only 2 arguments.

        :param left: left argument for the operator
        :param right: right argument for the operator
        :return: CONDITIONAL_STATEMENT, storing the details.
        """
        # check the variables support in both arguments
        if is_variable_supported(left) and is_variable_supported(right):
            return CONDITIONAL_STATEMENT(left, "!=", right)
        else:
            raise Exception("Operands are not of acceptable type.")

    @staticmethod
    def GE(left, right):
        """
        Greater than and equal to operator. Accepts only 2 arguments.

        :param left: left argument for the operator
        :param right: right argument for the operator
        :return: CONDITIONAL_STATEMENT, storing the details.
        """
        # check the variables support in both arguments
        if is_variable_supported(left) and is_variable_supported(right):
            return CONDITIONAL_STATEMENT(left, ">=", right)
        else:
            raise Exception("Operands are not of acceptable type.")

    @staticmethod
    def LE(left, right):
        """
        Less than and equal to operator. Accepts only 2 arguments.

        :param left: left argument for the operator
        :param right: right argument for the operator
        :return: CONDITIONAL_STATEMENT, storing the details.
        """
        # check the variables support in both arguments
        if is_variable_supported(left) and is_variable_supported(right):
            return CONDITIONAL_STATEMENT(left, "<=", right)
        else:
            raise Exception("Operands are not of acceptable type.")

    @staticmethod
    def AND(left, right):
        """
        And operator. Accepts only 2 arguments.

        :param left: left argument for the operator
        :param right: right argument for the operator
        :return: CONDITIONAL_STATEMENT, storing the details.
        """
        # check the variables support in both arguments
        if is_variable_supported(left) and is_variable_supported(right):
            return CONDITIONAL_STATEMENT(left, "&&", right)
        else:
            raise Exception("Operands are not of acceptable type.")

    @staticmethod
    def OR(left, right):
        """
        Or operator. Accepts only 2 arguments.

        :param left: left argument for the operator
        :param right: right argument for the operator
        :return: CONDITIONAL_STATEMENT, storing the details.
        """
        # check the variables support in both arguments
        if is_variable_supported(left) and is_variable_supported(right):
            return CONDITIONAL_STATEMENT(left, "||", right)
        else:
            raise Exception("Operands are not of acceptable type.")

    @staticmethod
    def IN(left, *args):
        """
        IN operator. Accepts the cumpulsory left argument and multiple right arguments.

        The IN operator can have multiple values for comparison.

        :param left: left argument for the operator
        :param args: multiple right arguments for the operator
        :return: CONDITIONAL_STATEMENT, storing the details
        """
        # check the variables support in left argument
        if not is_variable_supported(left):
            raise Exception("Operands are not of acceptable type.")
        for var in args:
            if not is_variable_supported(var):
                raise Exception("Operands are not of acceptable type.")

        return CONDITIONAL_STATEMENT(left, "IN", *args)


class OPTIONAL(STATEMENT):
    """
    Class to be used by the user, to input an Optional tuples in the query.
    Usage as follows
    >> OPTIONAL ( (s, p, o) )
    Output: OPTIONAL { ?s ?p ?o . } .

    The optional conditional is also a statement, which can be used anywhere
    in the query. Thus, the STATEMENT class is extended for this purpose.
    """
    def __new__(cls, statement):
        """
        Function to create the OPTIONAL object.
        The input is converted to the super class object and stored as a tuple.

        :param statement: statement to be used as optional
        :return: OPTIONAL tuple object
        """
        stmt = super(OPTIONAL, cls).__new__(cls, statement)
        return tuple.__new__(OPTIONAL, stmt)

    def n3(self):
        """
        Function to provide the n triple format of the object.
        Each triple in its n3() format is: "OPTIONAL { ?s ?p ?o . } ."

        :return: string
        """
        return "OPTIONAL { " + super().n3() + " }" + " ."


class CONDITIONAL_STATEMENT(STATEMENT):
    """
    Class to store operator details in an object. It extends the
    the STATEMENT class, and can be used like it.

    This class is ,however, for internal use cases and shouldn't be used
    directly by the user.
    """
    def __new__(cls, left, operator, *args):
        """
        Function to create a new object of CONDITIONAL_STATEMENT and store as a tuple.
        No check is provided for the arguments, and should be passed after checking with
        is_variable_supported.

        :param left: left argument for the operator
        :param operator: operator string
        :param args: right arguments for the operator
        :return: CONDITIONAL_STATEMENT tuple object
        """
        return tuple.__new__(CONDITIONAL_STATEMENT, (left, operator, args))

    def n3(self):
        """
        Function to provide the n triple format of the object.
        Each triple in its n3() format is:
        1. If there is only one right argument: "?left op ?right"
        2. 2 or more right arguments: "?left op (?right1, ?right2, ?right, ...)"

        :return: string
        """
        n3_string = self[0].n3() + " " + self[1] + " "
        # check if there is only one right arguments for the operator
        if len(self[2]) == 1:
            n3_string += self[2][0].n3()
        else:
            # cover the comma separated arguments with circular brackets.
            n3_string += "( "
            for i in range(len(self[2])):
                n3_string += self[2][i].n3()
                if i < len(self[2]) - 1:
                    n3_string += ", "
            n3_string += " )"

        return n3_string


class Aggregates(STATEMENT):
    """
    Class used to define Aggregate Functions like MAX, MIN, SUM etc.
    Example - Aggregates.SUM(?s)

    """
    def __new__(cls, function, statement):
        """
        :param function: This contains the type of Aggregate function as specified in AGGREGATE_FUNCTION_LIST
        :param statement: Statement inside the function, a variable
        :return: tuple of (function, statement)
        """
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
        """
        Creates a class for the Aggregate function
        :param function_name: Aggregate Function Name
        :return: Class for the aggregate function
        """
        def new(cls, statement):
            return Aggregates.__new__(cls, function_name, statement)

        return type(str(function_name), (Aggregates,), dict(__new__=new))

    def n3(self):
        """
        Defines the n3 format for the output as string
        :rtype: object
        """
        return self[0] + "( " + self[1].n3() + " )"


class FunctionExpressions(STATEMENT):
    """
    Class used to define Function Expressions like ASC, DESC etc.
    Example - FunctionExpressions.ASC(?s)
    """
    def __new__(cls, function_expression, *args):
        """

        :param function_expression: This contains the type of function expressions as specified in
                                    FUNCTION_EXPRESSION_SUPPORTED_LIST
        :param args: Variables provided as arguments to the function
        :return: tuple of (function_expression, args)
        """
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
        """
        Creates a class for the various types of function expression
        :param function_expression: Function expression type
        :return: Class fotr the function expression
        """
        def new(cls, *args):
            return FunctionExpressions.__new__(cls, function_expression, *args)

        return type(str(function_expression), (FunctionExpressions,), dict(__new__=new))

    def n3(self):
        """
        Defines the n3 format for the output as string
        :rtype: str
        """
        n3_string = self[0] + " ( "
        for i in range(len(self[1])):
            n3_string += self[1][i].n3()
            if i < len(self[1]) - 1:
                n3_string += ", "
        n3_string += " )"
        return n3_string


# Initialising all the Aggregate functions
for function in AGGREGATE_FUNCTION_LIST:
    setattr(Aggregates, function, Aggregates.create_aggregate(function))

# Initialising all the function expressions
for function_expression in FUNCTION_EXPRESSION_SUPPORTED_LIST:
    setattr(FunctionExpressions, function_expression,
            FunctionExpressions.create_function_expressions(function_expression))


class FILTER(STATEMENT):
    """
    Class to apply filter statement in queries. The filter function is used
    as a statement and hence, extends the class STATEMENT.
    Used as follows
    >> FILTER(Operator.LT(var1, var2))
    Output: FILTER ( ?var1 < ?var2 ) .

    It only accepts one parameter which will cover the whole filter.
    """
    def __new__(cls, expression):
        """
        Function to create object of FILTER.
        It accepts only 1 paramter as the expression which is used
        to apply the filter on the query.

        :param expression: expression to be used for filtering.
        :return: FILTER tuple object
        """
        if not is_variable_supported(expression):
            raise Exception(
                "Expression {} in FILTER not of acceptable type".format(
                    expression
                )
            )

        return tuple.__new__(FILTER, (expression,))

    def n3(self):
        """
        Function to provide the n triple format of the object.
        Each triple in its n3() format is "FILTER ( expression )".

        :return: string
        """
        return "FILTER ( " + self[0].n3() + " ) ."


class FOR_GRAPH(STATEMENT):
    """
    Class to specify the graph for the statements and tuple in the query.
    This can be used while specifying graph in where, insert, delete, etc.

    This object can be passed as a statement in any function and hence, extends the STATEMENT class.
    Usage:
    >> FOR_GRAPH (
        (s, p, o),
        name=URIRef("graphname")
    )
    Output: GRAPH <graphname> {
        ?s ?p ?o
    }

    Other statements can be passed as arguments.
    The graph is assumed to be default if a name is not provided.
    """
    def __new__(cls, *args, name=None):
        """
        Function to create GRAPH specific statements.
        It can take multiple statements as objects, be it filter, optional, etc.
        The name is advisabel to be provided using URIRef.

        :param args: statements to be queried for the specific graph
        :param name: name of graph
        :return: FOR_GRAPH tuple object
        """
        # if name is present, it should be in the supported format
        if name and not is_variable_supported(name):
            raise Exception("GRAPH name not of acceptable type.")

        statements = []
        for stmt in args:
            # convert he statements to supported format if not already present
            if not is_variable_supported(stmt):
                statements.append(STATEMENT(stmt))
            else:
                statements.append(stmt)

        return tuple.__new__(FOR_GRAPH, (name, statements))

    def n3(self):
        """
        Function to provide the n triple format of the object.
        Each triple in its n3() format is:
        GRAPH <name> {
            stmt1 .
            stmt2 .
        } .

        :return: string
        """
        n3_string = ""
        if self[0]:
            n3_string += "GRAPH " + self[0].n3() + " "
        n3_string += "{ \n"

        for var in self[1]:
            n3_string += var.n3() + " \n"

        n3_string += "\n}  ."
        return n3_string


class QueryBuilder:
    """
    Class to convert the query into a SPARQL query
    """
    class QueryString(str):
        """
        Class to convert the datatype of the query object to string for the query to be used as a nested query
        """
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
        """
        Initialise and store variables, bindings for the SELECT statement

        :param args: stores the variables that are needed for the SELECT statement
        :param distinct: Boolean to check whether DISTINCT solution modifier to be used or not
        :param kwargs: stores the variables that are needed for the SELECT statement
        :return: self
        """
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
        """
        Initialise variables required for the MOVE query

        :param move_from_graph: Source Graph
        :param move_to_graph: Destination Graph
        :param move_silent: Boolean for SILENT Keyword
        :return: self
        """
        if not is_variable_supported(move_from_graph):
            raise Exception("from_graph name not of acceptable type.")
        if not is_variable_supported(move_to_graph):
            raise Exception("to_graph name not of acceptable type.")
        self.move_from_graph = move_from_graph
        self.move_to_graph = move_to_graph
        self.move_silent = move_silent
        return self

    def ADD(self, add_from_graph=URIRef("DEFAULT"), add_to_graph=URIRef("DEFAULT"), add_silent=False):
        """
        Initialise variables required for the ADD query

        :param add_from_graph: Source Graph
        :param add_to_graph: Destination Graph
        :param add_silent: Boolean for SILENT Keyword
        :return: self
        """
        if not is_variable_supported(add_from_graph):
            raise Exception("from_graph name not of acceptable type.")
        if not is_variable_supported(add_to_graph):
            raise Exception("to_graph name not of acceptable type.")
        self.add_from_graph = add_from_graph
        self.add_to_graph = add_to_graph
        self.add_silent = add_silent
        return self

    def INSERT(self, *args):
        """
        Initialise variables required for INSERT query

        :param args: Objects to be inserted in the INSERT query
        :return: self
        """
        for statement in args:
            if not is_variable_supported(statement):
                self.INSERT_variables_direct.append(STATEMENT(statement))
            else:
                self.INSERT_variables_direct.append(statement)

        return self

    def DELETE(self, *args):
        """
        Initialise variables required for DELETE query

        :param args: Objects to be inserted in the DELETE query
        :return: self
        """
        for statement in args:
            if not is_variable_supported(statement):
                self.DELETE_variables_direct.append(STATEMENT(statement))
            else:
                self.DELETE_variables_direct.append(statement)

        return self

    def WHERE(self, *args):
        """
        Initialise variables required for WHERE query

        :param args: Objects to be inserted in the WHERE query
        :return: self
        """
        for statement in args:
            if not is_variable_supported(statement):
                self.WHERE_statements.append(STATEMENT(statement))
            else:
                self.WHERE_statements.append(statement)

        return self

    def LIMIT(self, value):
        """
        Initialise variables required for LIMIT query

        :param value: value for the LIMIT query
        :return: self
        """
        self.limit = value

        return self

    def OFFSET(self, value):
        """
        Initialise variables required for OFFSET query

        :param value: value for the OFFSET query
        :return: self
        """
        self.offset = value

        return self

    def GROUP_BY(self, *args):
        """
        Initialise variables required for GROUP_BY query

        :param args: Objects required for the GROUP_BY query
        :return: self
        """
        for var in args:
            if is_variable_supported(var):
                self.GROUP_BY_expressions.append(var)
            else:
                raise Exception("Expression passed in ORDER_BY is not valid.")

        return self

    def ORDER_BY(self, *args):
        """
        Initialise variables required for ORDER_BY query

        :param args: Objects required for the ORDER_BY query
        :return: self
        """
        for var in args:
            if is_variable_supported(var):
                self.ORDER_BY_expressions.append(var)
            else:
                raise Exception("Expression passed in ORDER_BY is not valid.")

        return self

    def build_select(self):
        """
        Function to build the SELECT query using the initialised variables according to the SPARQL syntax
        """
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
        """
        Function to build the MOVE query using the initialised variables according to the SPARQL syntax
        """
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
        """
        Function to build the ADD query using the initialised variables according to the SPARQL syntax
        """
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
        """
        Function to build the INSERT query using the initialised variables according to the SPARQL syntax
        """
        if len(self.INSERT_variables_direct) > 0:
            self.query += "INSERT { \n"

            for var in self.INSERT_variables_direct:
                self.query += var.n3() + " "

            self.query += "\n} \n"

    def build_delete(self):
        """
        Function to build the DELETE query using the initialised variables according to the SPARQL syntax
        """
        if len(self.DELETE_variables_direct) > 0:
            self.query += "DELETE { \n"

            for var in self.DELETE_variables_direct:
                self.query += var.n3() + " "

            self.query += "\n} \n"

    def build_where(self):
        """
        Function to build the WHERE query using the initialised variables according to the SPARQL syntax
        """
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
        """
        Function to build the GROUP BY and ORDER BY query using the initialised variables according to the SPARQL syntax
        """
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
        """
        Function to build the LIMIT and OFFSET query using the initialised variables according to the SPARQL syntax
        """
        if self.limit:
            self.query += "LIMIT " + str(self.limit) + " \n"

        if self.offset:
            self.query += "OFFSET " + str(self.offset) + " \n"

    def build(self):
        """
        Function to build the query according to the SPARQL syntax
        :return: SPARQL query in str format
        """
        self.build_select()
        self.build_insert()
        self.build_delete()
        self.build_move()
        self.build_add()
        self.build_where()

        self.build_group_by_order_by()
        self.build_limit_offset()

        return QueryBuilder.QueryString(self.query)


# if __name__ == "__main__":
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
    #     FunctionExpressions.ASC(Variable("s"))
    # ).LIMIT(
    #     100
    # ).OFFSET(
    #     20
    # ).build()
    # print(query)
    #
    # query = QueryBuilder().ADD(
    #     add_from_graph=URIRef("default"),
    #     add_to_graph=URIRef("graph_1"),
    #     add_silent=False
    # ).build()
    #
    # print(query)
