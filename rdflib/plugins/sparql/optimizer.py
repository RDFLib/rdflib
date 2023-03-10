from __future__ import annotations

"""
This contains standard optimizers for sparql

"""
import re
from rdflib import Literal
from rdflib.plugins.sparql.operators import Builtin_CONTAINS, Builtin_REGEX
from rdflib.plugins.sparql.sparql import Query
from rdflib.plugins.sparql.algebra import CompValue, Join, Values, Expr
from typing import Any

"""
An interface for having optimizers that transform a query algebra hopefully
in an faster to evaluate version.
"""


class SPARQLOptimizer:
    def optimize(self, query: Query) -> Query:
        return query


class ValuesToTheLeftOfTheJoin(SPARQLOptimizer):

    def optimize(self, query: Query) -> Query:
        main = query.algebra
        query.algebra = self._optimize_node(main)
        return query

    def _optimize_node(self, cv: Any) -> Any:
        if cv.name == "Join":
            if cv.p1.name != "ToMultiSet" and "ToMultiSet" == cv.p2.name:
                cv.update(p1=cv.p2, p2=cv.p1)
            else:
                cv.update(self._optimize_node(cv.p1), self._optimize_node(cv.p2))
            return cv
        elif cv.p is not None:
            cv.p.update(self._optimize_node(cv.p))
        elif cv.p1 is not None and cv.p2 is not None:
            cv.p1.update(self._optimize_node(cv.p1))
            cv.p2.update(self._optimize_node(cv.p2))
        elif cv.p1 is not None:
            cv.p1.update(self._optimize_node(cv.p1))
        return cv
