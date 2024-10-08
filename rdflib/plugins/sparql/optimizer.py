from __future__ import annotations

"""
This contains standard optimizers for sparql

"""
import re
from typing import Any, Callable

from rdflib import Literal
from rdflib.plugins.sparql.algebra import CompValue, Expr, Join, Values
from rdflib.plugins.sparql.operators import Builtin_CONTAINS, Builtin_REGEX
from rdflib.plugins.sparql.sparql import Query

"""
An interface for having optimizers that transform a query algebra hopefully
in an faster to evaluate version.
"""


class SPARQLOptimizer:
    def optimize(self, query: Query) -> Query:
        return query
