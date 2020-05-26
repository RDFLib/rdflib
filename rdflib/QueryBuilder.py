from __future__ import unicode_literals

from rdflib import Variable, Literal, URIRef


class QueryBuilder:
    def __init__(self):
        self.query = ""
        self.SELECT_variables_direct = []
        self.is_DISTINCT = False
        self.SELECT_variables_with_alias = {}
        self.WHERE_statements = []

    @staticmethod
    def _is_acceptable_query_variable(variable):
        return isinstance(variable, (Variable, Literal, URIRef))

    def SELECT(self, *args, distinct=False, **kwargs):
        self.is_DISTINCT = distinct

        for var in args:
            if not self._is_acceptable_query_variable(var):
                raise Exception("Argument not of valid type.")

            self.SELECT_variables_direct.append(var)

        for var_name, var in kwargs.items():
            if not self._is_acceptable_query_variable(var):
                raise Exception("Argument not of valid type.")

            self.SELECT_variables_with_alias[Variable(var_name)] = var

        return self

    def process_where_statement(self, append_to_array, *args):
        for statement in args:
            if isinstance(statement, tuple):
                if len(statement) == 3:
                    s, p, o = statement
                    if self._is_acceptable_query_variable(s) and self._is_acceptable_query_variable(
                            p) and self._is_acceptable_query_variable(o):
                        append_to_array.append((s, p, o))

                    else:
                        raise Exception("s, p, o in the statement not of valid type.")
                else:
                    raise Exception("Statement has to be a tuple in the format (s, p, o)")

    def WHERE(self, *args, **kwargs):
        self.process_where_statement(self.WHERE_statements, *args)

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
            raise Exception("Query must have at least one WHERE statement")

        self.query += "WHERE {\n"
        for s, p, o in self.WHERE_statements:
            self.query += s.n3() + " " + p.n3() + " " + o.n3() + " ."
        self.query += "\n}"

    def build(self):
        self.build_select()
        self.build_where()

        return self.query


if __name__ == "__main__":
    query = QueryBuilder().SELECT(
        Variable("s"),
        Variable("p"),
        distinct=True,
        x=Variable("o")
    ).WHERE(
        (Variable("s"), Variable("p"), Variable("o"))
    ).build()
    print(query)
