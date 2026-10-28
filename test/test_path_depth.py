import sys
from collections import Counter

import pytest

from rdflib import RDF, Dataset, Graph, Literal, URIRef
from rdflib.paths import AlternativePath, InvPath, MulPath, Path, SequencePath

P = URIRef("urn:p")
Q = URIRef("urn:q")
A, B, C, D = (URIRef("urn:" + x) for x in "abcd")
DEPTH = 1200
LONG_DEPTHS = (sys.getrecursionlimit() + 137, sys.getrecursionlimit() + 373)


@pytest.fixture
def guard_evaluation(monkeypatch):
    def protect(graph):
        def no_limit_change(*args, **kwargs):
            pytest.fail("path evaluation changed the recursion limit")

        def no_mutation(*args, **kwargs):
            pytest.fail("path evaluation mutated the supplied graph")

        monkeypatch.setattr(sys, "setrecursionlimit", no_limit_change)
        for target in (graph, graph.store):
            for name in ("add", "addN", "remove"):
                monkeypatch.setattr(target, name, no_mutation)

    return protect


def nested(path):
    for _ in range(DEPTH):
        path = InvPath(InvPath(path))
    return path


def chain(length=DEPTH):
    graph = Graph()
    nodes = [URIRef("urn:n:" + str(i)) for i in range(length + 1)]
    for a, b in zip(nodes, nodes[1:]):
        graph.add((a, P, b))
    return graph, nodes


@pytest.mark.parametrize("modifier", ["+", "*"])
@pytest.mark.parametrize("direction", ["forward", "reverse", "both"])
@pytest.mark.parametrize("length", LONG_DEPTHS)
def test_long_reachability(modifier, direction, length, guard_evaluation):
    graph, nodes = chain(length)
    original = set(graph)
    guard_evaluation(graph)
    limit = sys.getrecursionlimit()
    path = MulPath(P, modifier)
    source = None if direction == "reverse" else nodes[0]
    target = None if direction == "forward" else nodes[-1]
    actual = Counter(path.eval(graph, source, target))
    if direction == "both":
        expected = [(nodes[0], nodes[-1])]
    elif direction == "forward":
        expected = [(nodes[0], n) for n in nodes[modifier == "+" :]]
    else:
        expected = [(n, nodes[-1]) for n in nodes[: len(nodes) - (modifier == "+")]]
    assert actual == Counter(expected)
    assert sys.getrecursionlimit() == limit
    assert set(graph) == original


@pytest.mark.parametrize("direction", ["forward", "reverse", "both", "unbound"])
@pytest.mark.parametrize("length", LONG_DEPTHS)
def test_long_sequence(direction, length, guard_evaluation):
    graph, nodes = chain(length)
    guard_evaluation(graph)
    source = nodes[0] if direction in ("forward", "both") else None
    target = nodes[-1] if direction in ("reverse", "both") else None
    path = SequencePath(*([P] * length))
    assert list(path.eval(graph, source, target)) == [(nodes[0], nodes[-1])]


def assert_chain_pairs(pairs, nodes, zero=False):
    remaining = {
        source: set(nodes[index + (not zero) :]) for index, source in enumerate(nodes)
    }
    for source, target in pairs:
        assert source in remaining and target in remaining[source]
        remaining[source].remove(target)
    assert not any(remaining.values())


@pytest.mark.parametrize("modifier", ["+", "*"])
@pytest.mark.parametrize("length", LONG_DEPTHS)
def test_unbound_long_reachability(modifier, length, guard_evaluation):
    graph, nodes = chain(length)
    guard_evaluation(graph)
    assert_chain_pairs(MulPath(P, modifier).eval(graph), nodes, modifier == "*")


@pytest.mark.parametrize("direction", ["forward", "reverse"])
@pytest.mark.parametrize("kind", ["reachability", "sequence"])
@pytest.mark.parametrize("length", LONG_DEPTHS)
def test_long_graph_traversal(direction, kind, length, guard_evaluation):
    graph, nodes = chain(length)
    guard_evaluation(graph)
    path = MulPath(P, "+") if kind == "reachability" else SequencePath(*([P] * length))
    if direction == "forward":
        actual = graph.objects(nodes[0], path)
        expected = nodes[1:] if kind == "reachability" else [nodes[-1]]
    else:
        actual = graph.subjects(path, nodes[-1])
        expected = nodes[:-1] if kind == "reachability" else [nodes[0]]
    assert Counter(actual) == Counter(expected)


@pytest.mark.parametrize("direction", ["forward", "reverse", "both", "unbound"])
def test_nested_alternatives_preserve_multiplicity(direction):
    graph = Graph()
    graph.add((A, P, B))
    graph.add((A, Q, B))
    path = nested(AlternativePath(P, Q))
    source = A if direction in ("forward", "both") else None
    target = B if direction in ("reverse", "both") else None
    assert Counter(path.eval(graph, source, target)) == Counter({(A, B): 2})


def test_nested_sequences_join_and_retain_distinct_routes():
    graph = Graph()
    for triple in [(A, P, B), (A, P, C), (B, Q, D), (C, Q, D)]:
        graph.add(triple)
    path = SequencePath(nested(P), nested(Q))
    assert Counter(path.eval(graph, A, D)) == Counter({(A, D): 2})


@pytest.mark.parametrize("kind", ["sequence_alternative", "repetition", "mixed"])
@pytest.mark.parametrize("length", LONG_DEPTHS)
def test_deeply_nested_operators(kind, length, guard_evaluation):
    graph = Graph()
    graph.add((A, P, A if kind == "mixed" else B))
    guard_evaluation(graph)
    path = P
    for _ in range(length):
        if kind == "repetition":
            path = MulPath(path, "?")
        elif kind == "mixed":
            path = InvPath(MulPath(SequencePath(AlternativePath(path, Q)), "+"))
        else:
            path = SequencePath(AlternativePath(path))
    expected = {(A, A), (A, B)} if kind == "repetition" else {(A, B)}
    if kind == "mixed":
        expected = {(A, A)}
    assert Counter(path.eval(graph, A, None)) == Counter(expected)


@pytest.mark.parametrize("modifier", ["?", "*", "+"])
@pytest.mark.parametrize(
    "direction", ["forward", "reverse", "both", "self", "miss", "unbound"]
)
def test_composed_reachability_cycles(modifier, direction, guard_evaluation):
    graph = Graph()
    for triple in [(A, P, B), (B, Q, C), (C, P, D), (D, Q, A)]:
        graph.add(triple)
    guard_evaluation(graph)
    unit = AlternativePath(SequencePath(P, Q), SequencePath(P, Q))
    path = MulPath(nested(unit), modifier)
    expected = {(A, C), (C, A)}
    if modifier in ("*", "+"):
        expected |= {(A, A), (C, C)}
    if modifier in ("?", "*"):
        expected |= {(node, node) for node in (A, B, C, D)}
    source, target = {
        "forward": (A, None),
        "reverse": (None, C),
        "both": (A, C),
        "self": (A, A),
        "miss": (A, B),
        "unbound": (None, None),
    }[direction]
    expected = {
        (s, o)
        for s, o in expected
        if (source is None or s == source) and (target is None or o == target)
    }
    assert Counter(path.eval(graph, source, target)) == Counter(expected)


@pytest.mark.parametrize("alternative", [False, True])
def test_unbound_optional_fanout(alternative, guard_evaluation):
    graph = Graph()
    graph.add((A, P, B))
    graph.add((A, Q if alternative else P, C))
    guard_evaluation(graph)
    unit = AlternativePath(P, Q, P) if alternative else P
    path = MulPath(unit, "?")
    expected = Counter({(A, A): 1, (B, B): 1, (C, C): 1, (A, B): 1, (A, C): 1})
    for expression in (path, nested(path)):
        assert Counter(expression.eval(graph)) == expected


@pytest.mark.parametrize("modifier", ["+", "*"])
@pytest.mark.parametrize("direction", ["forward", "reverse", "empty_reverse"])
def test_alternative_after_bound_repetition(modifier, direction, guard_evaluation):
    graph = Graph()
    for triple in [(A, P, B), (D, P, B), (A, Q, C), (C, Q, B)]:
        graph.add(triple)
    guard_evaluation(graph)
    path = AlternativePath(MulPath(P, modifier), Q, Q)
    source, target, pairs = {
        "forward": (A, None, [(A, B), (A, C), (A, C)]),
        "reverse": (None, B, [(A, B), (D, B), (C, B), (C, B)]),
        "empty_reverse": (None, C, [(A, C), (A, C)]),
    }[direction]
    if modifier == "*":
        node = source if source is not None else target
        pairs.append((node, node))
    for expression in (path, nested(path)):
        assert Counter(expression.eval(graph, source, target)) == Counter(pairs)


@pytest.mark.parametrize("modifier", ["?", "*"])
def test_unbound_zero_length_includes_object_only_terms(modifier):
    graph = Graph()
    literal = Literal("tail")
    graph.add((A, P, B))
    graph.add((B, Q, literal))
    path = MulPath(nested(P), modifier)
    expected = {(A, A), (B, B), (literal, literal), (A, B)}
    assert Counter(path.eval(graph)) == Counter(expected)


def test_first_false_skips_initial_zero_length_result():
    graph = Graph()
    graph.add((A, P, B))
    path = MulPath(nested(P), "*")
    assert list(path.eval(graph, A, None, first=False)) == [(A, B)]


@pytest.mark.parametrize("direction", ["forward", "reverse"])
def test_empty_graph_zero_length_with_bound_endpoint(direction):
    path = MulPath(nested(P), "*")
    source, target = (A, None) if direction == "forward" else (None, A)
    assert list(path.eval(Graph(), source, target)) == [(A, A)]


def test_dataset_views_remain_isolated():
    dataset = Dataset()
    left = dataset.graph(URIRef("urn:left"))
    right = dataset.graph(URIRef("urn:right"))
    left.add((A, P, B))
    right.add((B, P, C))
    path = MulPath(nested(P), "+")
    assert list(left.objects(A, path)) == [B]
    assert list(right.subjects(path, C)) == [B]
    assert list(left.objects(A, path)) == [B]
    assert set(dataset.quads()) == {
        (A, P, B, left.identifier),
        (B, P, C, right.identifier),
    }


def test_interleaved_and_repeated_evaluations_do_not_share_state():
    graph = Graph()
    for triple in [(A, P, B), (B, P, C), (C, P, A), (D, Q, C)]:
        graph.add(triple)
    path = MulPath(nested(P), "+")
    first = path.eval(graph, A, None)
    second = path.eval(graph, B, None)
    first_head, second_head = next(first), next(second)
    assert Counter([first_head, *first]) == Counter((A, n) for n in (A, B, C))
    assert Counter([second_head, *second]) == Counter((B, n) for n in (A, B, C))
    assert Counter(path.eval(graph, A, None)) == Counter((A, n) for n in (A, B, C))


class ObservedPath(Path):
    def __init__(self, events, fail=False):
        self.events = events
        self.fail = fail
        self.iterators = []

    def eval(self, graph, subj=None, obj=None):
        iterator = self._results()
        # Keep ownership so garbage collection cannot mask missing close calls.
        self.iterators.append(iterator)
        return iterator

    def _results(self):
        self.events.append("start")
        try:
            yield A, B
            self.events.append("resume")
            if self.fail:
                raise LookupError("custom path failure")
            yield A, C
        finally:
            self.events.append("close")

    def n3(self, namespace_manager=None):
        return "<urn:observed>"


def test_custom_path_prefix_close_is_lazy():
    events = []
    path = nested(ObservedPath(events))
    iterator = path.eval(Graph())
    limit = sys.getrecursionlimit()
    assert events == []
    assert next(iterator) == (A, B)
    assert events == ["start"]
    assert sys.getrecursionlimit() == limit
    iterator.close()
    assert events == ["start", "close"]


def test_custom_path_error_propagates_and_closes():
    events = []
    iterator = nested(ObservedPath(events, fail=True)).eval(Graph())
    assert next(iterator) == (A, B)
    with pytest.raises(LookupError):
        next(iterator)
    assert events == ["start", "resume", "close"]


def test_sequence_prefix_close_is_lazy():
    graph = Graph()
    graph.add((B, Q, D))
    graph.add((C, Q, D))
    events = []
    path = SequencePath(nested(ObservedPath(events, fail=True)), Q)
    iterator = path.eval(graph)
    assert events == []
    assert next(iterator) == (A, D)
    assert events == ["start"]
    iterator.close()
    assert events == ["start", "close"]


@pytest.mark.parametrize("modifier", ["?", "*", "+"])
@pytest.mark.parametrize("bound", [False, True])
def test_repetition_prefix_close_is_lazy(modifier, bound):
    events = []
    path = MulPath(nested(ObservedPath(events, fail=True)), modifier)
    iterator = path.eval(Graph(), A if bound else None)
    assert events == []
    if bound and modifier in ("?", "*"):
        assert next(iterator) == (A, A)
        assert events == []
    assert next(iterator) == (A, B)
    assert events and all(event == "start" for event in events)
    started = len(events)
    iterator.close()
    assert events == ["start"] * started + ["close"] * started


@pytest.mark.parametrize("delegate", [False, True])
@pytest.mark.parametrize("builtin", [InvPath, SequencePath, AlternativePath, MulPath])
def test_subclasses_can_inherit_or_delegate_builtin_evaluation(delegate, builtin):
    calls = []

    class Inherited(builtin):
        pass

    class Delegated(builtin):
        def eval(self, graph, subj=None, obj=None):
            calls.append((subj, obj))
            return super().eval(graph, subj, obj)

    graph = Graph()
    graph.add((A, P, B))
    kind = Delegated if delegate else Inherited
    path = kind(P, "+") if builtin is MulPath else kind(P)
    source, target = (B, A) if builtin is InvPath else (A, B)
    assert list(nested(path).eval(graph, source, target)) == [(source, target)]
    assert calls == ([(source, target)] if delegate else [])


def test_unrelated_alternative_is_not_evaluated_for_prefix():
    graph = Graph()
    graph.add((A, P, B))
    events = []
    path = AlternativePath(nested(P), ObservedPath(events))
    iterator = path.eval(graph, A, None)
    assert next(iterator) == (A, B)
    iterator.close()
    assert events == []


def test_graph_errors_are_not_swallowed():
    class BrokenGraph(Graph):
        def triples(self, triple):
            yield from super().triples(triple)
            if not isinstance(triple[1], Path):
                raise OSError("store is unavailable")

    graph = BrokenGraph()
    graph.add((A, P, B))
    iterator = nested(P).eval(graph, A, None)
    assert next(iterator) == (A, B)
    with pytest.raises(OSError):
        next(iterator)


def test_sparql_long_rdf_list():
    """Reading a long RDF list must not exhaust the Python stack (issue #1967)."""
    graph = Graph()
    nodes = [URIRef(f"urn:list:{index}") for index in range(LONG_DEPTHS[0])]
    for index, node in enumerate(nodes):
        graph.add((node, RDF.first, Literal(index)))
        rest = nodes[index + 1] if index + 1 < len(nodes) else RDF.nil
        graph.add((node, RDF.rest, rest))

    rows = graph.query(
        "SELECT ?item WHERE { ?head rdf:rest*/rdf:first ?item }",
        initBindings={"head": nodes[0]},
        initNs={"rdf": RDF},
    )
    assert Counter(row[0] for row in rows) == Counter(map(Literal, range(len(nodes))))


@pytest.mark.parametrize("direction", ["forward", "reverse", "both", "unbound"])
def test_sparql_long_chain(direction, guard_evaluation):
    graph, nodes = chain()
    guard_evaluation(graph)
    bindings = {}
    if direction in ("forward", "both"):
        bindings["start"] = nodes[0]
    if direction in ("reverse", "both"):
        bindings["end"] = nodes[-1]
    rows = graph.query(
        "SELECT ?start ?end WHERE { ?start <urn:p>+ ?end }",
        initBindings=bindings,
    )
    pairs = ((row[0], row[1]) for row in rows)
    if direction == "unbound":
        assert_chain_pairs(pairs, nodes)
    elif direction == "both":
        assert list(pairs) == [(nodes[0], nodes[-1])]
    elif direction == "forward":
        assert Counter(pairs) == Counter((nodes[0], n) for n in nodes[1:])
    else:
        assert Counter(pairs) == Counter((n, nodes[-1]) for n in nodes[:-1])
