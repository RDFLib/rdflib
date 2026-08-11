from __future__ import annotations

import copy
from collections.abc import Mapping
from typing import Any, Optional, Union

import rdflib
from rdflib.graph import Graph
from rdflib.plugins.inference import DeductiveClosure
from rdflib.plugins.inference.owlrl import OWLRL_Semantics
from rdflib.plugins.inference.rdfsclosure import RDFS_Semantics
from rdflib.query import Result
from rdflib.term import Identifier, Variable

# ruff: noqa: N803


class OWLRLProcessor(rdflib.query.Processor):
    def __init__(self, graph: Graph):
        self.graph = graph

    def query(  # type: ignore[override]
        self,
        strOrQuery: Union[str, Graph],
        initBindings: Mapping[Variable, Identifier] = {},
        initNs: Mapping[str, str] = {},
        base: Optional[str] = None,
        DEBUG: bool = False,
    ) -> Mapping[str, Any]:
        """
        Evaluate a query with the given initial bindings, and initial
        namespaces. The given base is used to resolve relative URIs in
        the query and will be overridden by any BASE given in the query.
        """
        if not isinstance(strOrQuery, Graph):
            self.graph.parse(data=strOrQuery, format="n3")
        else:
            self.graph += strOrQuery

        for p, n in initNs.items():
            self.graph.bind(p, n)

        working_graph = copy.deepcopy(self.graph)

        DeductiveClosure(OWLRL_Semantics).expand(working_graph)

        return {"type_": "CONSTRUCT", "graph": working_graph - self.graph}


class RDFSProcessor(rdflib.query.Processor):
    def __init__(self, graph: Graph):
        self.graph = graph

    def query(  # type: ignore[override]
        self,
        strOrQuery: Union[str, Graph],
        initBindings: Mapping[Variable, Identifier] = {},
        initNs: Mapping[str, str] = {},
        base: Optional[str] = None,
        DEBUG: bool = False,
    ) -> Mapping[str, Any]:
        """
        Evaluate a query with the given initial bindings, and initial
        namespaces. The given base is used to resolve relative URIs in
        the query and will be overridden by any BASE given in the query.
        """

        if not isinstance(strOrQuery, Graph):
            self.graph.parse(data=strOrQuery, format="n3")
        else:
            self.graph += strOrQuery

        for p, n in initNs.items():
            self.graph.bind(p, n)

        working_graph = copy.deepcopy(self.graph)

        DeductiveClosure(RDFS_Semantics).expand(working_graph)

        return {"type_": "CONSTRUCT", "graph": working_graph - self.graph}


class OWLRLUpdateProcessor(rdflib.query.UpdateProcessor):
    def __init__(self, graph: Graph):
        self.graph = graph

    def update(
        self,
        strOrQuery: Union[str, Graph],  # type: ignore[override]
        initBindings: Mapping[str, Identifier] = {},
        initNs: Mapping[str, str] = {},
    ) -> None:

        if not isinstance(strOrQuery, Graph):
            self.graph.parse(data=strOrQuery, format="n3")
        else:
            self.graph += strOrQuery

        for p, n in initNs.items():
            self.graph.bind(p, n)

        DeductiveClosure(OWLRL_Semantics).expand(self.graph)


class RDFSUpdateProcessor(rdflib.query.UpdateProcessor):
    def __init__(self, graph: Graph):
        self.graph = graph

    def update(
        self,
        strOrQuery: Union[str, Graph],  # type: ignore[override]
        initBindings: Mapping[str, Identifier] = {},
        initNs: Mapping[str, str] = {},
    ) -> None:

        if not isinstance(strOrQuery, Graph):
            self.graph.parse(data=strOrQuery, format="n3")
        else:
            self.graph += strOrQuery

        for p, n in initNs.items():
            self.graph.bind(p, n)

        DeductiveClosure(RDFS_Semantics).expand(self.graph)


class RuleResult(Result):
    def __init__(self, res: Mapping[str, Any]):
        self.graph = res.get("graph") or Graph()
