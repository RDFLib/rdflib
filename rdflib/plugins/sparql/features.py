"""Structural feature inspection for parsed SPARQL queries."""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any, Optional, Union

from pyparsing import ParseResults

from rdflib.plugins.sparql.algebra import translatePrologue
from rdflib.plugins.sparql.parser import parseQuery
from rdflib.plugins.sparql.parserutils import CompValue
from rdflib.plugins.sparql.sparql import Prologue
from rdflib.term import URIRef, Variable

__all__ = ["QueryFeatures", "extract_query_features"]


_PATTERN_NAMES = {
    "Bind": "bind",
    "Filter": "filter",
    "GraphGraphPattern": "graph",
    "InlineData": "values",
    "ValuesClause": "values",
    "MinusGraphPattern": "minus",
    "OptionalGraphPattern": "optional",
    "ServiceGraphPattern": "service",
    "SubSelect": "subquery",
}

_MODIFIER_NAMES = {
    "GroupClause": "group",
    "HavingClause": "having",
    "OrderClause": "order",
}

_AGGREGATE_NAMES = {
    "Aggregate_Avg": "avg",
    "Aggregate_Count": "count",
    "Aggregate_GroupConcat": "group_concat",
    "Aggregate_Max": "max",
    "Aggregate_Min": "min",
    "Aggregate_Sample": "sample",
    "Aggregate_Sum": "sum",
}

_SPECIAL_EXPRESSIONS = {
    "Builtin_EXISTS": "exists",
    "Builtin_NOTEXISTS": "not_exists",
}

_OPERATOR_KEYS = {
    "RelationalExpression": "op",
    "AdditiveExpression": "op",
    "MultiplicativeExpression": "op",
}

_KEYWORD_ALIASES = {
    name.replace("_", ""): name
    for name in (
        "is_iri",
        "is_uri",
        "is_blank",
        "is_literal",
        "is_numeric",
        "same_term",
        "group_concat",
        "not_exists",
    )
}


@dataclass(frozen=True)
class QueryFeatures:
    """An immutable summary of syntax present in a SPARQL query.

    Names are lower-case SPARQL keywords. Function IRIs are kept as resolved
    strings, while built-in functions use their keyword name. The collections
    deliberately report presence rather than parse-tree occurrence counts:
    callers interested in routing, policy, or telemetry generally need to know
    whether a construct occurs anywhere, including inside subqueries.
    """

    query_form: str
    patterns: frozenset[str]
    modifiers: frozenset[str]
    functions: frozenset[str]
    aggregates: frozenset[str]
    operators: frozenset[str]
    variables: frozenset[Variable]
    default_graphs: tuple[URIRef, ...]
    named_graphs: tuple[URIRef, ...]
    _builtin_functions: frozenset[str] = field(default_factory=frozenset, repr=False)

    def uses(self, feature: str) -> bool:
        """Return whether *feature* appears in any feature category."""

        return bool(self.categories_for(feature))

    def categories_for(self, feature: str) -> frozenset[str]:
        """Return every category in which *feature* occurs."""

        normalized = _normalize_name(feature)
        categories = {
            category
            for category, values in self._feature_categories()
            if category != "functions" and normalized in values
        }
        if feature in self.functions or normalized in self._builtin_functions:
            categories.add("functions")
        return frozenset(categories)

    def uses_all(self, features: Iterable[str]) -> bool:
        """Return whether every requested feature occurs in the query."""

        return all(self.uses(feature) for feature in features)

    def uses_any(self, features: Iterable[str]) -> bool:
        """Return whether at least one requested feature occurs in the query."""

        return any(self.uses(feature) for feature in features)

    def iter_features(self) -> Iterable[tuple[str, str]]:
        """Yield categorized feature names in deterministic order."""

        for category, values in self._feature_categories():
            for value in sorted(values):
                yield category, value

    @property
    def feature_count(self) -> int:
        """Return the number of distinct categorized feature entries."""

        return sum(len(values) for _, values in self._feature_categories())

    @property
    def is_aggregate_query(self) -> bool:
        return bool(self.aggregates or "group" in self.modifiers)

    def _feature_categories(self) -> tuple[tuple[str, frozenset[str]], ...]:
        return (
            ("patterns", self.patterns),
            ("modifiers", self.modifiers),
            ("functions", self.functions),
            ("aggregates", self.aggregates),
            ("operators", self.operators),
        )

    def as_dict(self) -> dict[str, object]:
        """Return a deterministic JSON-friendly representation."""

        return {
            "query_form": self.query_form,
            "patterns": sorted(self.patterns),
            "modifiers": sorted(self.modifiers),
            "functions": sorted(self.functions),
            "aggregates": sorted(self.aggregates),
            "operators": sorted(self.operators),
            "variables": sorted(str(variable) for variable in self.variables),
            "default_graphs": [str(graph) for graph in self.default_graphs],
            "named_graphs": [str(graph) for graph in self.named_graphs],
        }


class _FeaturePrologue(Prologue):
    def absolutize(
        self, iri: Optional[Union[CompValue, str]]
    ) -> Optional[Union[CompValue, str]]:
        if isinstance(iri, URIRef):
            return URIRef(iri, base=self.base)
        return super().absolutize(iri)


class _FeatureCollector:
    def __init__(self, prologue: Prologue) -> None:
        self.prologue = prologue
        self.query_form = ""
        self.patterns: set[str] = set()
        self.modifiers: set[str] = set()
        self.functions: set[str] = set()
        self._builtin_functions: set[str] = set()
        self.aggregates: set[str] = set()
        self.operators: set[str] = set()
        self.variables: set[Variable] = set()
        self.default_graphs: list[URIRef] = []
        self.named_graphs: list[URIRef] = []
        self._seen: set[int] = set()

    def collect(self, parsed: ParseResults) -> QueryFeatures:
        query = _query_node(parsed)
        self.query_form = _query_form(query.name)
        self._visit(parsed)
        return QueryFeatures(
            query_form=self.query_form,
            patterns=frozenset(self.patterns),
            modifiers=frozenset(self.modifiers),
            functions=frozenset(self.functions),
            aggregates=frozenset(self.aggregates),
            operators=frozenset(self.operators),
            variables=frozenset(self.variables),
            default_graphs=tuple(self.default_graphs),
            named_graphs=tuple(self.named_graphs),
            _builtin_functions=frozenset(self._builtin_functions),
        )

    def _record_query(self, query: CompValue) -> None:
        modifier = query.modifier
        if modifier in {"DISTINCT", "REDUCED"}:
            self.modifiers.add(str(modifier).lower())

        limit_offset = query.limitoffset
        if isinstance(limit_offset, CompValue):
            if "limit" in limit_offset:
                self.modifiers.add("limit")
            if "offset" in limit_offset:
                self.modifiers.add("offset")

        clauses = query.datasetClause or []
        if not isinstance(clauses, (list, tuple, ParseResults)):
            clauses = [clauses]
        for clause in clauses:
            if not isinstance(clause, CompValue):
                continue
            default = self.prologue.absolutize(clause.default)
            named = self.prologue.absolutize(clause.named)
            if isinstance(default, URIRef):
                self.default_graphs.append(default)
            if isinstance(named, URIRef):
                self.named_graphs.append(named)

    def _visit(self, value: object) -> None:
        if isinstance(value, Variable):
            self.variables.add(value)
            return
        if isinstance(value, (str, bytes, URIRef)) or value is None:
            return

        if isinstance(value, (CompValue, ParseResults, Mapping, Sequence)):
            identity = id(value)
            if identity in self._seen:
                return
            self._seen.add(identity)

        if isinstance(value, CompValue):
            self._record_comp_value(value)
            for child in value.values():
                self._visit(child)
            return

        if isinstance(value, ParseResults):
            for child in value:
                self._visit(child)
            for child in value.values():
                self._visit(child)
            return

        if isinstance(value, Mapping):
            for key, child in value.items():
                self._visit(key)
                self._visit(child)
            return

        if isinstance(value, Sequence):
            for child in value:
                self._visit(child)
            return

        if isinstance(value, Iterable):
            for child in value:
                self._visit(child)

    def _record_comp_value(self, node: CompValue) -> None:
        name = node.name

        if name.endswith("Query") or name == "SubSelect":
            self._record_query(node)

        pattern = _PATTERN_NAMES.get(name)
        if pattern:
            self.patterns.add(pattern)
        if name == "GroupOrUnionGraphPattern" and len(node.graph or []) > 1:
            self.patterns.add("union")

        modifier = _MODIFIER_NAMES.get(name)
        if modifier:
            self.modifiers.add(modifier)

        aggregate = _AGGREGATE_NAMES.get(name)
        if aggregate:
            self.aggregates.add(aggregate)

        special = _SPECIAL_EXPRESSIONS.get(name)
        if special:
            self.patterns.add(special)

        if name.startswith("Builtin_") and special is None:
            function = _normalize_name(name.removeprefix("Builtin_"))
            self.functions.add(function)
            self._builtin_functions.add(function)
        elif name == "Function":
            iri = self.prologue.absolutize(node.iri)
            if isinstance(iri, URIRef):
                self.functions.add(str(iri))

        operator_key = _OPERATOR_KEYS.get(name)
        if operator_key:
            if operator_key in node:
                self._record_operator(node[operator_key])

        if name == "ConditionalOrExpression" and "other" in node and node["other"]:
            self.operators.add("||")
        elif name == "ConditionalAndExpression" and "other" in node and node["other"]:
            self.operators.add("&&")
        elif name == "UnaryNot":
            self.operators.add("!")
        elif name == "UnaryPlus":
            self.operators.add("unary+")
        elif name == "UnaryMinus":
            self.operators.add("unary-")

        if (
            name in {"PathEltOrInverse", "PathNegatedPropertySet", "DistinctPath"}
            or (name in {"PathAlternative", "PathSequence"} and len(node.part) > 1)
            or (name == "PathElt" and node.mod is not None)
        ):
            self.patterns.add("property_path")

    def _record_operator(self, operator: object) -> None:
        if operator is None:
            return
        if isinstance(operator, (list, tuple, ParseResults)):
            for item in operator:
                self._record_operator(item)
            return
        text = str(operator).strip()
        if text:
            self.operators.add(_normalize_name(text))


def extract_query_features(
    query: Union[str, ParseResults],
    *,
    init_ns: Optional[Mapping[str, Any]] = None,
) -> QueryFeatures:
    """Parse *query* and report syntax used anywhere in it.

    Namespace and base resolution use the same prologue rules as query
    preparation, without translating or mutating the query tree. Syntax errors
    are intentionally propagated from :func:`parseQuery`.
    """

    if isinstance(query, str):
        parsed = parseQuery(query)
    elif isinstance(query, ParseResults):
        parsed = query
    else:
        raise TypeError("query must be SPARQL text or parseQuery() output")

    _query_node(parsed)
    prologue = translatePrologue(parsed[0], None, init_ns, _FeaturePrologue())
    return _FeatureCollector(prologue).collect(parsed)


def _query_node(parsed: ParseResults) -> CompValue:
    if len(parsed) < 2 or not isinstance(parsed[1], CompValue):
        raise TypeError("query must be the result of parseQuery()")
    if parsed[1].name not in {
        "SelectQuery",
        "AskQuery",
        "ConstructQuery",
        "DescribeQuery",
    }:
        raise TypeError("query must be the result of parseQuery()")
    return parsed[1]


def _query_form(name: str) -> str:
    suffix = "Query"
    if name.endswith(suffix):
        name = name[: -len(suffix)]
    return _normalize_name(name)


def _normalize_name(name: str) -> str:
    if ":" in name or name.lower() in {
        "+",
        "-",
        "*",
        "/",
        "=",
        "!=",
        "<",
        ">",
        "<=",
        ">=",
        "&&",
        "||",
        "!",
        "unary+",
        "unary-",
    }:
        return name if ":" in name else name.lower()
    normalized = name.lower().replace("-", "_").replace(" ", "_")
    return _KEYWORD_ALIASES.get(normalized, normalized)
