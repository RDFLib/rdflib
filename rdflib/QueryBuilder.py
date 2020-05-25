from __future__ import unicode_literals


def convert_alias_to_variable(alias):
    return "?" + alias


class Variable:
    def __init__(self, variable_name):
        self.variable_name = variable_name

    def get_variable_name(self):
        return self.variable_name

    def get_sparql_variable(self):
        return "?" + self.variable_name


class QueryBuilder:
    def __init__(self):
        self.query = ""
        self.SELECT_variables_direct = []
        self.SELECT_variables_with_alias = {}
        self.WHERE_statements = []

    def SELECT(self, *args, **kwargs):
        for var in args:
            if not isinstance(var, Variable):
                raise Exception("Argument can be only of type 'Variable'.")

            self.SELECT_variables_direct.append(var)

        for var_name, var in kwargs.items():
            if not isinstance(var, Variable):
                raise Exception("Argument can be only of type 'Variable'.")

            self.SELECT_variables_with_alias[var_name] = var

        return self

    def WHERE(self, *args):
        for statement in args:
            if isinstance(statement, tuple):
                if len(statement) == 3:
                    s, p, o = statement
                    if isinstance(s, Variable) and isinstance(p, Variable) and isinstance(o, Variable):
                        self.WHERE_statements.append((s, p, o))

                    else:
                        raise Exception("s, p, o in the statement has to be of type 'Variable'")
                else:
                    raise Exception("Statement has to be a tuple in the format (s, p, o)")

        return self

    def build(self):
        self.query += "SELECT "
        for var in self.SELECT_variables_direct:
            self.query += var.get_sparql_variable() + " "

        for var_name, var in self.SELECT_variables_with_alias.items():
            self.query += "(" + var.get_sparql_variable() + " as " + convert_alias_to_variable(var_name) + ")"

        self.query += "\n"

        if len(self.WHERE_statements) == 0:
            raise Exception("Query must have atleast one WHERE statement")

        self.query += "WHERE {\n"
        for s, p, o in self.WHERE_statements:
            self.query += s.get_sparql_variable() + " " + p.get_sparql_variable() + " " + o.get_sparql_variable() + " ."
        self.query += "\n}"

        return self.query


if __name__ == "__main__":
    query = QueryBuilder().SELECT(
        Variable("s"),
        Variable("p"),
        x=Variable("o")
    ).WHERE(
        (Variable("s"), Variable("p"), Variable("o"))
    ).build()
    print(query)
