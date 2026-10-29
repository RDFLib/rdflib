"""Deterministic graph views and ordering helpers for RDF/XML serializers."""

from __future__ import annotations

from contextlib import AbstractContextManager
from dataclasses import dataclass
from typing import Optional, Protocol

from rdflib.compare import to_canonical_graph
from rdflib.graph import Dataset, Graph
from rdflib.namespace import NAME_START_CATEGORIES, RDF, split_uri
from rdflib.term import BNode, Identifier, Literal, Node, URIRef

__all__ = [
    "CanonicalSerializerStore",
    "canonical_option",
    "ordered_predicate_objects",
    "ordered_subjects",
    "term_sort_key",
]


_TermKey = tuple[int, str, str, str]


class _HasStore(Protocol):
    store: Graph


@dataclass(frozen=True)
class CanonicalNamespacePlan:
    """A prefix plan derived only from namespaces required by RDF content."""

    bindings: tuple[tuple[str, URIRef], ...]

    @classmethod
    def from_graph(cls, graph: Graph) -> CanonicalNamespacePlan:
        required: set[URIRef] = set()
        candidates = set(graph.predicates()).union(graph.objects(None, RDF.type))
        for term in candidates:
            if not isinstance(term, URIRef):
                continue
            try:
                namespace, _ = split_uri(term, NAME_START_CATEGORIES)
            except ValueError:
                continue
            required.add(URIRef(namespace))

        required.discard(URIRef(str(RDF)))
        required.discard(URIRef("http://www.w3.org/XML/1998/namespace"))
        bindings = [("rdf", URIRef(str(RDF)))]
        bindings.extend(
            (f"ns{index}", namespace)
            for index, namespace in enumerate(sorted(required, key=str), start=1)
        )
        bindings.append(("xml", URIRef("http://www.w3.org/XML/1998/namespace")))
        return cls(tuple(bindings))

    def apply(self, graph: Graph) -> None:
        for prefix, namespace in self.bindings:
            graph.bind(prefix, namespace, replace=True)


def canonical_option(value: object) -> bool:
    """Validate the opt-in flag without treating arbitrary values as true."""

    if isinstance(value, bool):
        return value
    raise TypeError("canon must be a boolean")


def term_sort_key(term: Node) -> _TermKey:
    """Return a total, stable key for RDF terms used by RDF/XML."""

    if isinstance(term, URIRef):
        return (0, str(term), "", "")
    if isinstance(term, BNode):
        return (1, str(term), "", "")
    if isinstance(term, Literal):
        return (
            2,
            str(term),
            str(term.datatype or ""),
            term.language or "",
        )
    return (3, type(term).__name__, str(term), "")


def ordered_subjects(graph: Graph) -> list[Node]:
    """Return each subject once in deterministic RDF-term order."""

    return sorted(set(graph.subjects()), key=term_sort_key)


def ordered_predicate_objects(
    graph: Graph, subject: Identifier
) -> list[tuple[Node, Node]]:
    """Return a subject's predicate/object pairs in deterministic order."""

    pairs = graph.predicate_objects(subject)
    return sorted(
        pairs,
        key=lambda pair: (term_sort_key(pair[0]), term_sort_key(pair[1])),
    )


def first_ordered_object(
    graph: Graph, subject: Identifier, predicate: Identifier
) -> Optional[Node]:
    values = sorted(graph.objects(subject, predicate), key=term_sort_key)
    return values[0] if values else None


def collection_cells(graph: Graph, head: Identifier) -> list[Node]:
    """Return cells in a well-formed list without following cycles forever."""

    cells: list[Node] = []
    seen: set[Node] = set()
    current: Node = head
    while current != RDF.nil and current not in seen:
        seen.add(current)
        cells.append(current)
        rests = list(graph.objects(current, RDF.rest))
        firsts = list(graph.objects(current, RDF.first))
        if len(rests) != 1 or len(firsts) != 1:
            break
        current = rests[0]
    return cells


def is_safe_collection(graph: Graph, head: Identifier) -> bool:
    """Return whether RDF/XML collection syntax preserves this list exactly.

    Collection syntax hides the list cells. It is therefore unsafe for named
    cells, shared tails, cycles, malformed links, or cells carrying statements
    other than exactly one ``rdf:first`` and one ``rdf:rest``.
    """

    if not isinstance(head, BNode):
        return False
    cells = collection_cells(graph, head)
    if not cells:
        return False

    expected: Node = head
    for index, cell in enumerate(cells):
        if cell != expected or not isinstance(cell, BNode):
            return False
        firsts = list(graph.objects(cell, RDF.first))
        rests = list(graph.objects(cell, RDF.rest))
        if len(firsts) != 1 or len(rests) != 1:
            return False
        if not isinstance(firsts[0], (BNode, URIRef)):
            return False
        if isinstance(firsts[0], BNode):
            references = list(graph.triples((None, None, firsts[0])))
            if references != [(cell, RDF.first, firsts[0])]:
                return False
        predicates = list(graph.predicates(cell, None))
        if len(predicates) != 2 or set(predicates) != {RDF.first, RDF.rest}:
            return False

        incoming = list(graph.triples((None, None, cell)))
        if len(incoming) != 1:
            return False
        if index:
            previous = cells[index - 1]
            if incoming[0] != (previous, RDF.rest, cell):
                return False
        expected = rests[0]

    return expected == RDF.nil


class CanonicalSerializerStore(AbstractContextManager[Graph]):
    """Restore the original serializer store after using a canonical copy."""

    def __init__(
        self,
        serializer: _HasStore,
        enabled: bool,
    ):
        self.serializer = serializer
        self.enabled = enabled
        self.original = serializer.store
        self.canonical: Optional[Graph] = None

    def __enter__(self) -> Graph:
        if not self.enabled:
            return self.original
        self.canonical = _canonical_graph(self.original)
        self.serializer.store = self.canonical
        return self.canonical

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.serializer.store = self.original
        self.canonical = None


def _canonical_graph(source: Graph) -> Graph:
    canonical_source = Graph(store="Memory", bind_namespaces="none")
    for subject, predicate, object in source.triples((None, None, None)):
        if isinstance(object, Literal) and object.language:
            object = Literal(str(object), lang=object.language.lower(), normalize=False)
        canonical_source.add((subject, predicate, object))

    target = Graph(
        store="Memory",
        identifier=(
            source.default_graph.identifier
            if isinstance(source, Dataset)
            else source.identifier
        ),
        bind_namespaces="none",
    )
    for triple in to_canonical_graph(canonical_source):
        target.add(triple)
    plan = CanonicalNamespacePlan.from_graph(target)
    plan.apply(target)
    return target
