"""
Move a VALUES clause to the left of the join.
This is normally smart as this is often a much shorter list than what is generated
by the other expression.
"""

from typing import Any

from rdflib.plugins.sparql.sparql import Query


class ValuesToTheLeftOfTheJoin:
    @classmethod
    def translate(cls, query: Query) -> Query:
        main = query.algebra
        query.algebra = ValuesToTheLeftOfTheJoin._optimize_node(main)
        return query

    @classmethod
    def _optimize_node(cls, cv: Any) -> Any:
        if cv.name == "Join":
            if cv.p1.name != "ToMultiSet" and "ToMultiSet" == cv.p2.name:
                cv.update(p1=cv.p2, p2=cv.p1)
            else:
                op1 = ValuesToTheLeftOfTheJoin._optimize_node(cv.p1)
                op2 = ValuesToTheLeftOfTheJoin._optimize_node(cv.p2)
                cv.update(op1, op2)
            return cv
        elif cv.p is not None:
            cv.p.update(ValuesToTheLeftOfTheJoin._optimize_node(cv.p))
        elif cv.p1 is not None and cv.p2 is not None:
            cv.p1.update(ValuesToTheLeftOfTheJoin._optimize_node(cv.p1))
            cv.p2.update(ValuesToTheLeftOfTheJoin._optimize_node(cv.p2))
        elif cv.p1 is not None:
            cv.p1.update(ValuesToTheLeftOfTheJoin._optimize_node(cv.p1))
        return cv
