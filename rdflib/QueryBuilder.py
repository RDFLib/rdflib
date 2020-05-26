from __future__ import unicode_literals

from rdflib import Variable, Literal, URIRef, RDF, OWL, RDFS


def is_acceptable_query_variable(variable):
    return isinstance(variable, (Variable, Literal, URIRef))


class STATEMENT(tuple):
    def __new__(cls, statement):
        if len(statement) == 3:
            s, p, o = statement
            if is_acceptable_query_variable(s) and is_acceptable_query_variable(
                    p) and is_acceptable_query_variable(o):
                return tuple.__new__(STATEMENT, (s, p, o))
        else:
            raise Exception("Statement has to be a tuple in the format (s, p, o)")

    def n3(self):
        return self[0].n3() + " " + self[1].n3() + " " + self[2].n3()


class OPTIONAL(STATEMENT):
    def __new__(cls, statement):
        stmt = super(OPTIONAL, cls).__new__(cls, statement)
        return tuple.__new__(OPTIONAL, stmt)

    def n3(self):
        return "OPTIONAL { " + super().n3() + " }"


class QueryBuilder:
    def __init__(self):
        self.query = ""
        self.SELECT_variables_direct = []
        self.is_DISTINCT = False
        self.SELECT_variables_with_alias = {}
        self.WHERE_statements = []

    def SELECT(self, *args, distinct=False, **kwargs):
        self.is_DISTINCT = distinct

        for var in args:
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

    def build_select(self):
        self.query += "SELECT "

        if self.is_DISTINCT:
            self.query += "DISTINCT "

        for var in self.SELECT_variables_direct:
            self.query += var.n3() + " "

        for var_alias, var_expression in self.SELECT_variables_with_alias.items():
            self.query += "(" + var_expression.n3() + " as " + var_alias.n3() + ")"

        self.query += "\n"

    def build_where(self):
        if len(self.WHERE_statements) == 0:
            raise Exception("Query must have at least one WHERE statement.")

        self.query += "WHERE {" + "\n"

        for statement in self.WHERE_statements:
            self.query += statement.n3() + " ." + "\n"

        self.query += "}" + "\n"

    def build(self):
        self.build_select()
        self.build_where()

        return self.query


if __name__ == "__main__":
    query = QueryBuilder().SELECT(
        Variable("s"),
        Variable("p"),
        x=Variable("o"),
        value=Variable("v"),
        distinct=True
    ).WHERE(
        (Variable("s"), Variable("p"), Variable("o")),
        (Variable("o"), RDF.type, Variable("v")),
        OPTIONAL((Variable("o"), RDFS.subClassOf, OWL.thing))
    ).build()
    print(query)
