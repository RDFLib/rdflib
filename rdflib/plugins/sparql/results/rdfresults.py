from __future__ import annotations

from typing import IO, TYPE_CHECKING, Any, Optional, cast

from rdflib.graph import Graph
from rdflib.namespace import RDF, Namespace
from rdflib.query import Result, ResultParser
from rdflib.term import Literal, Variable

if TYPE_CHECKING:
    from rdflib.graph import _ObjectType
    from rdflib.term import IdentifiedNode

RS = Namespace("http://www.w3.org/2001/sw/DataAccess/tests/result-set#")


class RDFResultParser(ResultParser):
    """This ResultParser is only used for DAWG standardised SPARQL tests."""

    def parse(self, source: IO | Graph, **kwargs: Any) -> Result:
        return RDFResult(source, **kwargs)


class RDFResult(Result):
    def __init__(self, source: IO | Graph, **kwargs: Any):
        if not isinstance(source, Graph):
            graph = Graph()
            graph.parse(source, **kwargs)
        else:
            graph = source

        rs = graph.value(predicate=RDF.type, object=RS.ResultSet)
        # there better be only one :)

        if rs is None:
            type_ = "CONSTRUCT"

            # use a new graph
            g = Graph()
            g += graph
            askAnswer: Literal | None = None
        else:
            askAnswer = cast(Optional[Literal], graph.value(rs, RS.boolean))

            if askAnswer is not None:
                type_ = "ASK"
            else:
                type_ = "SELECT"

        Result.__init__(self, type_)

        if type_ == "SELECT":
            self.vars = [
                # Technically we should check for QuotedGraph here, to make MyPy happy
                Variable(v.identifier if isinstance(v, Graph) else v)  # type: ignore[unreachable]
                for v in graph.objects(rs, RS.resultVariable)
            ]

            self.bindings = []

            for s in graph.objects(rs, RS.solution):
                sol: dict[Variable, IdentifiedNode | Literal] = {}
                for b in graph.objects(s, RS.binding):
                    var_name: _ObjectType | str | None = graph.value(b, RS.variable)
                    if var_name is None:
                        continue
                    # Technically we should check for QuotedGraph here, to make MyPy happy
                    elif isinstance(var_name, Graph):  # type: ignore[unreachable]
                        var_name = var_name.identifier  # type: ignore[unreachable]
                    var_val = graph.value(b, RS.value)
                    if var_val is None:
                        continue
                    elif isinstance(var_val, (Graph, Variable)):
                        raise ValueError(f"Malformed rdf result binding {var_name}")
                    sol[Variable(var_name)] = var_val
                self.bindings.append(sol)
        elif type_ == "ASK":
            if askAnswer is None:
                raise Exception("Malformed boolean in ask answer!")
            self.askAnswer = askAnswer.value
            if askAnswer.value is None:
                raise Exception("Malformed boolean in ask answer!")
        elif type_ == "CONSTRUCT":
            self.graph = g
