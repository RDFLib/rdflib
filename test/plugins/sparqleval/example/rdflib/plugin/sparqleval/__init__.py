from typing import Any


def custom_eval_extended(ctx: Any, extend: Any) -> Any:
    for c in evalPart(ctx, extend.p):
        try:
            if hasattr(extend.expr, "iri") and extend.expr.iri == function_uri:
                evaluation = function_result
            else:
                evaluation = _eval(extend.expr, c.forget(ctx, _except=extend._vars))
                if isinstance(evaluation, SPARQLError):
                    raise evaluation

            yield c.merge({extend.var: evaluation})

        except SPARQLError:
            yield c


def custom_eval(ctx: Any, part: Any) -> Any:
    if part.name == "Extend":
        return custom_eval_extended(ctx, part)
    else:
        raise NotImplementedError()


from rdflib import Namespace
from rdflib.plugins.sparql.evaluate import evalPart
from rdflib.plugins.sparql.evalutils import _eval
from rdflib.plugins.sparql.sparql import SPARQLError

namespace = Namespace("example:rdflib:plugin:sparqleval:")
function_uri = namespace["function"]
function_result = namespace["result"]
