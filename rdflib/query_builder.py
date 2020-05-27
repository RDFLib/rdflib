from __future__ import unicode_literals

from rdflib import Variable, Literal, URIRef, RDF, OWL, RDFS


def is_acceptable_query_variable(variable):
    return isinstance(variable, (CONDITIONAL_STATEMENT, FILTER, FUNCTION_EXPR, AGGREGATE, Variable, Literal, URIRef))


class STATEMENT(tuple):
    def __new__(cls, statement):
        if len(statement) == 3:
            s, p, o = statement
            if is_acceptable_query_variable(s) and is_acceptable_query_variable(
                    p) and is_acceptable_query_variable(o):
                return tuple.__new__(STATEMENT, (s, p, o))
            else:
                raise Exception("Values in the statement {} are not of acceptable types.".format(statement))
        else:
            raise Exception("Statement has to be a tuple in the format (s, p, o)")

    def n3(self):
        return self[0].n3() + " " + self[1].n3() + " " + self[2].n3()


class Operators(object):

    @staticmethod
    def GT(left, right):
        if is_acceptable_query_variable(left) and is_acceptable_query_variable(right):
            return CONDITIONAL_STATEMENT(left, ">", right)
        else:
            raise Exception("Operands are not of acceptable type.")

    @staticmethod
    def LT(left, right):
        if is_acceptable_query_variable(left) and is_acceptable_query_variable(right):
            return CONDITIONAL_STATEMENT(left, "<", right)
        else:
            raise Exception("Operands are not of acceptable type.")

    @staticmethod
    def EQ(left, right):
        if is_acceptable_query_variable(left) and is_acceptable_query_variable(right):
            return CONDITIONAL_STATEMENT(left, "=", right)
        else:
            raise Exception("Operands are not of acceptable type.")

    @staticmethod
    def NE(left, right):
        if is_acceptable_query_variable(left) and is_acceptable_query_variable(right):
            return CONDITIONAL_STATEMENT(left, "!=", right)
        else:
            raise Exception("Operands are not of acceptable type.")

    @staticmethod
    def GE(left, right):
        if is_acceptable_query_variable(left) and is_acceptable_query_variable(right):
            return CONDITIONAL_STATEMENT(left, ">=", right)
        else:
            raise Exception("Operands are not of acceptable type.")

    @staticmethod
    def LE(left, right):
        if is_acceptable_query_variable(left) and is_acceptable_query_variable(right):
            return CONDITIONAL_STATEMENT(left, "<=", right)
        else:
            raise Exception("Operands are not of acceptable type.")

    @staticmethod
    def AND(left, right):
        if is_acceptable_query_variable(left) and is_acceptable_query_variable(right):
            return CONDITIONAL_STATEMENT(left, "&&", right)
        else:
            raise Exception("Operands are not of acceptable type.")

    @staticmethod
    def OR(left, right):
        if is_acceptable_query_variable(left) and is_acceptable_query_variable(right):
            return CONDITIONAL_STATEMENT(left, "||", right)
        else:
            raise Exception("Operands are not of acceptable type.")


class OPTIONAL(STATEMENT):
    def __new__(cls, statement):
        stmt = super(OPTIONAL, cls).__new__(cls, statement)
        return tuple.__new__(OPTIONAL, stmt)

    def n3(self):
        return "OPTIONAL { " + super().n3() + " }"


class CONDITIONAL_STATEMENT(STATEMENT):
    def __new__(cls, left, operator, right):
        return tuple.__new__(CONDITIONAL_STATEMENT, (left, operator, right))

    def n3(self):
        return self[0].n3() + " " + self[1] + " " + self[2].n3()


list_function = ["SUM", "AVERAGE", "COUNT", "SET", "MIN", "MAX", "GROUPCONTACT", "SAMPLE"]


class AGGREGATE(STATEMENT):
    def __new__(cls, function, statement):
        if not is_acceptable_query_variable(statement):
            statement = Variable(statement)
        if function not in list_function:
            raise Exception("Aggregate Function %s not supported" % function)
        return tuple.__new__(AGGREGATE, (function, statement))

    def n3(self):
        return self[0] + "( " + self[1].n3() + " )"


supported_function_expression_list = [
    "ASC", "DESC", "IRI", "ISBLANK", "ISLITERAL", "ISIRI", "ISNUMERIC", "BNODE",
    "ABS", "IF", "RAND", "UUID", "STRUUID", "MD5", "SHA1", "SHA256",
    "SHA384", "SHA512", "COALESCE", "CEIL", "FLOOR", "ROUND", "REGEX",
    "REPLACE", "STRDT", "STRLANG", "CONCAT", "STRSTARTS", "STRENDS",
    "STRBEFORE", "STRAFTER", "CONTAINS", "ENCODE_FOR_URI", "SUBSTR",
    "STRLEN", "STR", "LCASE", "LANGMATCHES", "NOW", "YEAR", "MONTH",
    "DAY", "HOURS", "MINUTES", "SECONDS", "TIMEZONE", "TZ", "UCASE",
    "LANG", "DATATYPE", "SAMETERM", "BOUND", "EXISTS"
]


class FUNCTION_EXPR(STATEMENT):
    def __new__(cls, function_expression, *args):
        statements = []
        for stmt in args:
            if not is_acceptable_query_variable(stmt):
                stmt = Variable(stmt)
            statements.append(stmt)

        if function_expression:
            function_expression = function_expression.upper()

        if function_expression not in supported_function_expression_list:
            raise Exception("Function expression %s not supported" % function_expression)
        return tuple.__new__(FUNCTION_EXPR, (function_expression, statements))

    def n3(self):
        n3_string = self[0] + "( "
        for var in self[1]:
            n3_string += var.n3() + " "
        n3_string += ")"
        return n3_string


class FILTER(STATEMENT):
    def __new__(cls, expression):
        if not is_acceptable_query_variable(expression):
            expression = Variable(expression)

        return tuple.__new__(FILTER, (expression,))

    def n3(self):
        return "FILTER ( " + self[0].n3() + " )"


class QueryBuilder:

    class QUERY_STRING(str):
        def __new__(cls, query):
            return str.__new__(cls, query)

        def n3(self):
            return "{\n" + self + "\n}"

    def __init__(self):
        self.query = ""
        self.SELECT_variables_direct = []
        self.is_DISTINCT = False
        self.SELECT_variables_with_alias = {}
        self.WHERE_statements = []
        self.ORDER_BY_expressions = []

        self.limit = None
        self.offset = None

    def SELECT(self, *args, distinct=False, **kwargs):
        self.is_DISTINCT = distinct

        for var in args:
            if isinstance(var, AGGREGATE):
                raise Exception("Alias not provided for %s" % var[1].n3())
            if not is_acceptable_query_variable(var):
                raise Exception("Argument not of valid type.")
            self.SELECT_variables_direct.append(var)

        for var_name, var in kwargs.items():
            if not is_acceptable_query_variable(var):
                raise Exception("Argument not of valid type.")
            self.SELECT_variables_with_alias[Variable(var_name)] = var

        return self

    def WHERE(self, *args, **kwargs):
        for statement in args:
            if not hasattr(statement, "n3"):
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

    def ORDER_BY(self, *args):
        for var in args:
            if is_acceptable_query_variable(var):
                self.ORDER_BY_expressions.append(var)
            else:
                raise Exception("Expression passed in ORDER_BY is not valid.")

        return self

    def build_select(self):
        self.query += "SELECT "

        if self.is_DISTINCT:
            self.query += "DISTINCT "

        for var in self.SELECT_variables_direct:
            self.query += var.n3() + " "

        for var_alias, var_expression in self.SELECT_variables_with_alias.items():
            self.query += "(" + var_expression.n3() + " as " + var_alias.n3() + ") "

        self.query += " \n"

    def build_where(self):
        if len(self.WHERE_statements) == 0:
            raise Exception("Query must have at least one WHERE statement.")

        self.query += "WHERE {" + " \n"

        for statement in self.WHERE_statements:
            self.query += statement.n3() + " ." + " \n"

        self.query += "}" + " \n"

    def build_order_by(self):
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
        self.build_where()

        self.build_order_by()
        self.build_limit_offset()

        return QueryBuilder.QUERY_STRING(self.query)


if __name__ == "__main__":
    query = QueryBuilder().SELECT(
        Variable("s"),
        Variable("p"),
        x=Variable("o"),
        value=AGGREGATE("AVERAGE", "v"),
        sum_value=AGGREGATE("SUM", Variable("v")),
        distinct=True
    ).WHERE(
        (Variable("s"), Variable("p"), Variable("o")),
        (Variable("o"), RDF.type, Variable("v")),
        OPTIONAL(
            (Variable("o"), RDFS.subClassOf, OWL.thing)
        ),
        FILTER(
            Operators.AND(
                Operators.GE(Variable("v"), Literal(5)),
                Operators.LT(Variable("v"), Literal(13))
            )
        )
    ).ORDER_BY(
        Variable("v"),
        FUNCTION_EXPR("asc", Variable("s"))
    ).LIMIT(
        100
    ).OFFSET(
        20
    ).build()
    print(query.n3())
