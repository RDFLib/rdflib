"""
Dijkstra-based pathfinding utility for RDFLib graphs.

[`find_paths`][rdflib.extras.pathfinding.find_paths] is the
primary entry point.  It performs Dijkstra-style graph
traversal to find paths between start and end nodes in any rdflib
[`Graph`][rdflib.graph.Graph]-compatible object.  For unweighted paths
this reduces to breadth-first order.

## Capabilities

* **Fixed nodes, SPARQL patterns, or unbound** start / end
* **Fixed predicates, rdflib property paths, SPARQL patterns, or unbound**
  path traversal
* **Shortest-path mode**: Keep only the shortest path(s) per end node
* **Weighted path lengths**: When the path is a SPARQL pattern that binds
  ``?length``, each step carries a custom weight; shortest-path comparison
  uses cumulative weighted length instead of hop count
* **Max-length limits**: Cap the cumulative weighted path length (for
  unweighted paths this is equivalent to a hop-count limit)
* **Early termination**: Stop extending a path once it reaches a valid end
* **Automatic direction reversal**: Traversal starts from whichever side is
  more constrained
* **Per-path cycle detection** like in SPARQL property path evaluation

## Beyond SPARQL property paths

SPARQL property paths are powerful for reachability queries, but they have
significant limitations when you need more than a boolean "is there a path?" answer:

* **No intermediate-node access**: Property paths collapse the traversal
  into a single ``(start, end)`` binding. You cannot inspect or filter
  the nodes *along* the path.
* **No per-step metadata**: There is no way to capture edge predicates,
  variable bindings, or weights for each hop.
* **No weighted and/or shortest path**: SPARQL has no built-in mechanism
  for associating numeric costs with edges or to search for shortest path.
* **Limited termination control**: You cannot tell a property path to
  stop at the first node that satisfies an arbitrary pattern, or to
  continue past it.

``find_paths`` fills these gaps by combining pathfinding with optional
expressiveness of SPARQL graph patterns at every layer (start selection,
per-hop expansion, end validation).  Each discovered path is returned as
an ordered sequence of :class:`PathStep` objects carrying the node,
edge, bindings, and weighted length, information that is unavailable
from a property-path query.

## How does this differ from other pathfinding tools?

``find_paths`` relaxes several constraints sometimes found in
pathfinding functions in graph databases or other tools:

* **Flexible endpoints**: Some pathfinding tools require
  exactly one concrete start node and one concrete end node.
  ``find_paths`` accepts a single node, an iterable of nodes, a
  SPARQL WHERE-clause pattern, or ``None`` (fully unbound) for both
  start and end independently.  This makes it straightforward to
  search from *all nodes matching a pattern* to *all nodes matching
  another pattern* in a single call.

* **Per-step metadata**: Some shortest-path results
  return only the sequence of nodes (and sometimes edges).
  ``find_paths`` returns a :class:`PathStep` per hop carrying the
  node, edge predicate (when unbound), arbitrary SPARQL variable
  bindings, and a per-step weighted length, which is usually
  unavailable without post-processing.

* **Weighted shortest path with SPARQL-defined costs**: Most RDF
  stores have no built-in mechanism for associating numeric costs
  with edges and selecting the minimum-cost route.  By binding a
  ``?length`` variable in the hop pattern, ``find_paths`` uses
  a Dijkstra-style approach to find the shortest path,
  something that would otherwise typically require extracting a
  subgraph and running a separate algorithm using another library.

* **SPARQL graph patterns as hop definitions**: Rather than
  restricting hops to a single predicate or property-path expression,
  ``find_paths`` accepts an arbitrary SPARQL WHERE-clause body as the
  hop definition.  This allows multi-triple patterns per step (e.g.
  reified edges, intermediate nodes with type constraints) without
  needing to flatten the graph into a simpler structure first.

## Data types

Each discovered path is returned as a
[`PathResult`][rdflib.extras.pathfinding.PathResult] containing an ordered
list of [`PathStep`][rdflib.extras.pathfinding.PathStep] objects.

[`PathStep.length`][rdflib.extras.pathfinding.PathStep] is always ``1``
unless the path is a SPARQL string pattern that binds ``?length``, in which
case the numeric value of that variable is used.
[`PathResult.length`][rdflib.extras.pathfinding.PathResult] is the sum of
all step lengths (``0`` for zero-length paths where ``start == end``).

The contents of each step depend on the ``path`` argument type:

| ``path`` type | ``PathStep.node`` | ``PathStep.length`` | ``PathStep.edge`` | ``PathStep.bindings`` |
| --- | --- | --- | --- | --- |
| ``None`` (unbound) | Node reached | ``1`` | Predicate traversed | ``None`` |
| ``URIRef`` or ``Path`` | Node reached | ``1`` | ``None`` | ``None`` |
| ``str`` (SPARQL pattern) | Node reached | ``?length`` value or ``1`` | ``None`` | Extra variable bindings dict (excluding ``?length``) |

## Parameter quick-reference

| Parameter | Accepts | Default |
| --- | --- | --- |
| ``start`` | ``Identifier``, ``Iterable[Identifier]``, ``str`` (SPARQL pattern with ``?start``), or ``None`` | ``None`` |
| ``end`` | ``Identifier``, ``Iterable[Identifier]``, ``str`` (SPARQL pattern with ``?end``), or ``None`` | ``None`` |
| ``path`` | ``URIRef``, ``Path``, ``str`` (SPARQL pattern with ``?start`` and ``?end``), or ``None`` | ``None`` |
| ``shortest`` | ``bool`` | ``True`` |
| ``terminate_on_first_match`` | ``bool`` | ``True`` |
| ``max_length`` | ``int``, ``float``, or ``None`` | ``None`` |
| ``initNs`` | ``dict`` of prefix-to-namespace mappings | ``None`` |

## Examples

Setting up a small graph for several of the examples below:

```python
>>> from rdflib import Graph, Namespace
>>> from rdflib.extras.pathfinding import find_paths

>>> EX = Namespace("http://example.org/")
>>> g = Graph()
>>> g.bind("ex", EX)
>>> _ = g.add((EX.Alice, EX.knows, EX.Bob))
>>> _ = g.add((EX.Bob, EX.knows, EX.Carol))
>>> _ = g.add((EX.Carol, EX.knows, EX.Dave))
>>> _ = g.add((EX.Bob, EX.knows, EX.Dave))

```

### Simple predicate path

Find all paths from Alice to Dave via ``:knows``:

```python
>>> results = find_paths(g, start=EX.Alice, path=EX.knows, end=EX.Dave, shortest=False)
>>> len(results)
2

```

### Shortest path

```python
>>> results = find_paths(
...     g, start=EX.Alice, path=EX.knows, end=EX.Dave
... )
>>> len(results)
1
>>> len(results[0].steps)
2

```

### Unbound path (captures edge predicates)

When ``path=None``, every predicate is traversed and each step records the
edge used:

```python
>>> results = find_paths(g, start=EX.Alice, path=None, end=EX.Bob)
>>> results[0].steps[0].edge == EX.knows
True

```

### SPARQL pattern start

Use a WHERE-clause body to select start nodes dynamically:

```python
>>> results = find_paths(
...     g,
...     start="?start ex:knows ex:Bob",
...     path=EX.knows,
...     end=EX.Dave,
...     shortest=False,
... )
>>> len(results)
2

```

### SPARQL pattern end

Use an ASK-style pattern to filter valid end nodes:

```python
>>> _ = g.add((EX.Dave, EX.role, EX.Manager))
>>> results = find_paths(
...     g,
...     start=EX.Alice,
...     path=EX.knows,
...     end="?end ex:role ex:Manager",
... )
>>> all(r.end == EX.Dave for r in results)
True

```

### Exploring reachable nodes with ``max_length`` (cumulative path length)

```python
>>> results = find_paths(
...     g,
...     start=EX.Alice,
...     path=EX.knows,
...     end=None,
...     terminate_on_first_match=False,
...     max_length=2,
... )
>>> sorted(set(str(r.end).rsplit("/", 1)[-1] for r in results))
['Alice', 'Bob', 'Carol', 'Dave']

```

### Property Paths

rdflib Path objects are supported.
Each application of the full property path counts as one step:

```python
>>> _ = g.add((EX.Bob, EX.friendOf, EX.Frank))
>>> _ = g.add((EX.Dave, EX.friendOf, EX.Eve))
>>> results = find_paths(
...     g, start=EX.Alice, path=EX.knows / EX.friendOf, end=None,
...     shortest=False, terminate_on_first_match=False,
... )
>>> len(results) >= 1
True

```

### Weighted shortest path with ``?length``

When the path is a SPARQL pattern that binds ``?length``, each step's
weight is taken from that variable.  ``shortest=True`` then picks the
path with the lowest *cumulative weighted length*, even if it has more
hops.  The ``?length`` variable is consumed by
[`PathStep.length`][rdflib.extras.pathfinding.PathStep] and does
**not** appear in ``PathStep.bindings``.

In this example a logistics company models shipping routes between
warehouses.  Each route carries a cost.  The direct
route from the New York warehouse to London costs $950, but routing
through Rotterdam ($200 + $350 = $550) is cheaper despite the extra hop:

```python
>>> from rdflib import Literal
>>> routes = Graph()
>>> routes.bind("ex", EX)
>>> # Direct route: NewYork -> London, cost $950
>>> _ = routes.add((EX.route1, EX.origin, EX.NewYork))
>>> _ = routes.add((EX.route1, EX.destination, EX.London))
>>> _ = routes.add((EX.route1, EX.shippingCost, Literal(950.0)))
>>> # NewYork -> Rotterdam, cost $200
>>> _ = routes.add((EX.route2, EX.origin, EX.NewYork))
>>> _ = routes.add((EX.route2, EX.destination, EX.Rotterdam))
>>> _ = routes.add((EX.route2, EX.shippingCost, Literal(200.0)))
>>> # Rotterdam -> London, cost $350
>>> _ = routes.add((EX.route3, EX.origin, EX.Rotterdam))
>>> _ = routes.add((EX.route3, EX.destination, EX.London))
>>> _ = routes.add((EX.route3, EX.shippingCost, Literal(350.0)))
>>> results = find_paths(
...     routes,
...     start=EX.NewYork,
...     path="?route ex:origin ?start ; ex:destination ?end ; ex:shippingCost ?length",
...     end=EX.London,
...     shortest=True,
...     terminate_on_first_match=True,
... )
>>> len(results)                   # only the cheapest route
1
>>> results[0].length              # $200 + $350
550.0
>>> len(results[0].steps)          # 2 hops via Rotterdam
2

```

### Provenance: most recent causal activity from a department

Given a ``prov:Activity``, find the most causally recent ``prov:Activity``
that was started by someone from the Legal department.  The path pattern
walks backward through the PROV chain. Each step matches an entity that
was generated by one activity and used by the next, while the end pattern
filters for activities whose associated agent belongs to Legal:

```python
results = find_paths(
    graph,
    start=EX.MyActivity,
    path=PROV.used / PROV.wasGeneratedBy,
    # Stop at activites started by the legal department
    end="?end prov:wasStartedBy/org:memberOf ex:LegalDepartment",
    shortest=True,                  # Shortest path to that activity only
    terminate_on_first_match=True,  # Stop at the first match
    initNs={
        "prov": "http://www.w3.org/ns/prov#",
        "org":  "http://www.w3.org/ns/org#",
    },
)
activities = {path.end for path in results}
```

### Supply-chain lineage: raw materials in a finished product

From a ``ex:PhysicalObject`` (a subclass of ``prov:Entity``), find every
"original" physical object that went into it (e.g. all raw materials that were
combined through a chain of activities to produce a finished product).

Because the inputs and outputs of ``prov:Activity`` instances can include
entities that are *not* physical objects (documents, data records, etc.),
the path pattern explicitly checks that intermediate nodes must be
``ex:PhysicalObject`` instances.  This guarantees that only paths through
physical objects are traversed, preventing unrelated physical objects from
appearing in the results:

```python
results = find_paths(
    graph,
    # Find all upstream physical objects that are "original", i.e. have no further provenance
    start="?start a ex:PhysicalObject . FILTER NOT EXISTS {?start prov:wasGeneratedBy []}",
    # Ensure only paths through physical objects are traversed.
    path="?end prov:wasGeneratedBy/prov:used ?start . ?start a ex:PhysicalObject .",
    end=EX.FinishedProduct,
    initNs={
        "prov": "http://www.w3.org/ns/prov#",
    },
)
raw_materials = {path.start for path in results}
```

- Matt Goldberg, 2026
"""

from __future__ import annotations

import heapq
from collections.abc import Callable, Generator, Iterable
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, NamedTuple, Union, cast

if TYPE_CHECKING:
    import typing_extensions as te

    from rdflib.graph import _ObjectType, _SubjectType
    from rdflib.plugins.sparql.sparql import Query

from rdflib import Graph, URIRef, Variable
from rdflib.paths import Path
from rdflib.plugins.sparql import prepareQuery
from rdflib.query import ResultRow
from rdflib.term import Identifier


class TraversalDirection(str, Enum):
    """Traversal direction for :func:`_choose_direction`."""

    FORWARD = "forward"
    REVERSE = "reverse"


@dataclass(frozen=True)
class PathStep:
    """
    One step along a discovered path.

    Attributes:
        node: The node reached at this step.  Always present.
        length: The weighted length of this step.  Always present.
            Always ``1`` except when the path argument is a SPARQL string
            whose pattern binds a ``?length`` variable: in that case the
            numeric value of ``?length`` is used instead.
        edge: Populated only when the path argument is ``None`` (unbound).
            Contains the predicate (URIRef) traversed to reach *node*.
        bindings: Populated only when the path argument is a SPARQL
            string.  Dict mapping each extra variable name (str, without
            '?') to its bound value (Identifier) for this step's pattern
            match.  The ``?length`` variable, if present in the query, is
            consumed by the *length* field and **not** included here.
    """

    node: Identifier
    length: float
    edge: Identifier | None = None
    bindings: dict[str, Identifier] | None = None


@dataclass
class PathResult:
    """
    A single discovered path from *start* to *end*.

    Attributes:
        start: The starting node of the path.
        end: The ending node of the path.
        length: Total weighted length of the path (sum of step lengths).
            For a zero-length path (``start == end``), *length* is ``0``.
        steps: Ordered list of PathStep objects, one per edge traversed.
            ``steps[-1].node == end`` (always, when ``len(steps) > 0``).
            For a zero-length path (``start == end``), *steps* is ``[]``.
    """

    start: Identifier
    end: Identifier
    length: float = 0
    steps: list[PathStep] = field(default_factory=list)


# Union accepted for start / end parameters
_NodeSpec: te.TypeAlias = Union[Identifier, Iterable[Identifier], str, None]

# Union accepted for the path parameter
_PathSpec: te.TypeAlias = Union[URIRef, Path, str, None]

# Expansion function: current_node -> iterable of (neighbor, step)
_ExpandFn: te.TypeAlias = Callable[[Identifier], Iterable[tuple[Identifier, PathStep]]]

# End-validation function: candidate_node -> bool
_EndCheckFn: te.TypeAlias = Callable[[Identifier], bool]


def _build_namespace_map(
    graph: Graph,
    initNs: dict[str, str] | None,  # NOQA: N803 consistent capitalization of initNs
) -> dict[str, str]:
    """
    Merge graph namespace_manager bindings with caller-supplied *initNs*.

    Caller-supplied prefixes take precedence.

    Args:
        graph: The rdflib graph whose ``namespace_manager`` provides the base
            prefix bindings.
        initNs: Optional mapping of ``{prefix: namespace_uri}`` strings.  When
            not ``None``, these override any same-prefix binding from the
            graph.

    Returns:
        Combined namespace map suitable for ``prepareQuery(initNs=...)``.
    """
    ns_map: dict[str, str] = {
        prefix: str(ns) for prefix, ns in graph.namespace_manager.namespaces()
    }
    if initNs:
        ns_map.update(initNs)
    return ns_map


def _is_sparql_pattern(value: Union[_NodeSpec, _PathSpec]) -> te.TypeIs[str]:
    """
    Check whether *value* is a plain ``str`` representing a SPARQL pattern.

    Args:
        value: The value to test.

    Returns:
        ``True`` if *value* is a ``str`` but not an ``Identifier``.
    """
    return isinstance(value, str) and not isinstance(value, Identifier)


def _prepare_and_validate(
    query_string: str,
    ns_map: dict[str, str],
    required_vars: set[str],
    label: str,
) -> Query:
    """
    Prepare a SPARQL query and validate that it contains *required_vars*.

    Args:
        query_string: Full SPARQL query string.
        ns_map: Namespace prefix-to-URI mapping.
        required_vars: Set of variable names (without ``?``) that must appear
            in the query.
        label: Human-readable label for error messages.

    Returns:
        The prepared query object.

    Raises:
        ValueError: If any of *required_vars* is missing from the parsed
            algebra.
    """
    # Prepare the query once to reuse many times
    prepared = prepareQuery(query_string, initNs=ns_map)

    # Verify that all required variables exist in the pattern
    parsed_vars = {str(v) for v in prepared.algebra._vars}
    missing = required_vars - parsed_vars
    if missing:
        formatted = ", ".join(f"?{v}" for v in sorted(missing))
        raise ValueError(
            f"{label} must contain variable(s) {formatted}. "
            f"Parsed variables: {sorted('?' + v for v in parsed_vars)}. "
            f"Pattern: {query_string!r}"
        )

    return prepared


def _specificity(value: _NodeSpec) -> int:
    """
    Return a specificity score used by :func:`_choose_direction`.

    The traversal is more efficient when it starts from the more constrained
    (specific) side.  This function assigns an integer score so that the
    caller can compare start vs. end specificity.

    Scores (higher = more specific):

    - 3: single ``Identifier`` (exactly one node)
    - 2: iterable of ``Identifier`` (finite known set)
    - 1: SPARQL pattern ``str`` (set determined at query time)
    - 0: ``None`` (unbound: every node in the graph)

    Args:
        value: A start / end specification as accepted by
            :func:`find_paths`.

    Returns:
        Specificity score in the range ``[0, 3]``.
    """
    if isinstance(value, Identifier):
        return 3
    if _is_sparql_pattern(value):
        return 1
    if value is None:
        return 0
    # Assume iterable of Identifiers. Don't consume it in case it is a generator.
    return 2


def _choose_direction(
    start: _NodeSpec,
    end: _NodeSpec,
) -> TraversalDirection:
    """
    Decide whether the traversal should run forward or in reverse.

    The heuristic compares the specificity of *start* and *end* (via
    :func:`_specificity`).  When the end side is more constrained than
    the start side, the traversal is reversed so that it begins from the
    smaller frontier, reducing the number of paths explored.

    Specificity ranking (most to least): single ``Identifier`` >
    ``Iterable[Identifier]`` > ``str`` (SPARQL pattern) > ``None``
    (unbound).

    Args:
        start: The caller's start specification.
        end: The caller's end specification.

    Returns:
        :attr:`TraversalDirection.FORWARD` if start is at least as specific
        as end; :attr:`TraversalDirection.REVERSE` otherwise.
    """
    if _specificity(end) > _specificity(start):
        return TraversalDirection.REVERSE

    return TraversalDirection.FORWARD


def _resolve_origins(
    origin_spec: _NodeSpec,
    graph: Graph,
    ns_map: dict[str, str],
    origin_var: str,
) -> set[Identifier]:
    """
    Materialize the origin specification into a concrete set of nodes.

    Dispatches on the type of *origin_spec*:

    - ``Identifier``: returns a singleton set.
    - SPARQL pattern ``str``: compiles and executes a
      ``SELECT DISTINCT ?<origin_var>`` query against *graph* and
      collects the bound values.
    - ``None``: returns the union of all subjects and objects in *graph*
      (i.e. every node).
    - Any other iterable: materializes it into a ``set``.

    Args:
        origin_spec: The origin-side node specification.
        graph: The rdflib graph to query.
        ns_map: Namespace prefix-to-URI mapping for SPARQL compilation.
        origin_var: The SPARQL variable name (``"start"`` or ``"end"``) to
            extract from query result rows.

    Returns:
        The concrete set of origin nodes (may be empty).
    """
    if isinstance(origin_spec, Identifier):
        return {origin_spec}
    if _is_sparql_pattern(origin_spec):
        # Prepare SPARQL queries for string patterns if relevant
        # Origin pattern -> SELECT (to enumerate starting nodes)
        label = ("End" if origin_var == "end" else "Start") + " pattern (origin)"
        q = f"SELECT DISTINCT ?{origin_var} WHERE {{{origin_spec}}}"
        prepared = _prepare_and_validate(q, ns_map, {origin_var}, label)

        # Evaluate the query to ge the set of origin nodes
        results = graph.query(prepared)
        var = Variable(origin_var)
        return {
            cast("Identifier", row[var])
            for row in results
            if isinstance(row, ResultRow) and row[var] is not None
        }
    if origin_spec is None:
        # Unbound: all nodes in the graph
        return set(graph.subjects()) | set(graph.objects())
    # Iterable of Identifiers
    return set(origin_spec)


def _build_expand_fn(
    path_spec: _PathSpec,
    graph: Graph,
    ns_map: dict[str, str],
    forward: bool,
) -> _ExpandFn:
    """
    Build and return a one-hop expansion function for the traversal.

    The returned callable has the signature
    ``(node: Identifier) -> Iterable[tuple[Identifier, PathStep]]``
    and yields ``(neighbor, step)`` pairs reachable from *node* in
    a single step.

    The implementation dispatched depends on *path_spec*:

    - ``None`` (unbound): traverses every predicate in *graph*.
      Each step carries the predicate as ``PathStep.edge``.
    - ``URIRef`` or ``Path``: uses ``graph.objects`` / ``graph.subjects``
      with the given predicate or property-path object.
    - ``str`` (SPARQL pattern): compiles and executes a
      ``SELECT * WHERE { ... }`` query with ``?start`` or ``?end``
      bound to *node*.  Each step carries extra variable bindings in
      ``PathStep.bindings``.  If the pattern binds ``?length``, its
      numeric value is used as ``PathStep.length`` (and excluded from
      ``bindings``).

    When *forward* is ``False`` the traversal direction is reversed
    (objects -> subjects).

    Args:
        path_spec: The path specification.
        graph: The rdflib graph to traverse.
        ns_map: Namespace prefix-to-URI mapping for SPARQL compilation.
        forward: ``True`` for forward traversal, ``False`` for reverse.

    Returns:
        A callable ``(Identifier) -> Iterable[(Identifier, PathStep)]``.
    """

    if path_spec is None:
        # Unbound path: traverse all predicates; step carries edge predicate
        if forward:

            def _expand_unbound_fwd(
                node: Identifier,
            ) -> Generator[tuple[Identifier, PathStep], None, None]:
                for pred, obj in graph.predicate_objects(cast("_SubjectType", node)):
                    yield obj, PathStep(node=obj, length=1, edge=pred)

            return _expand_unbound_fwd
        else:

            def _expand_unbound_rev(
                node: Identifier,
            ) -> Generator[tuple[Identifier, PathStep], None, None]:
                for subj, pred in graph.subject_predicates(cast("_ObjectType", node)):
                    yield subj, PathStep(node=subj, length=1, edge=pred)

            return _expand_unbound_rev

    # URIRef or Path: traverse that path; no extra metadata
    if not _is_sparql_pattern(path_spec) and isinstance(path_spec, (URIRef, Path)):
        if forward:

            def _expand_path_fwd(
                node: Identifier,
            ) -> Generator[tuple[Identifier, PathStep], None, None]:
                for obj in graph.objects(cast("_SubjectType", node), path_spec):
                    yield obj, PathStep(node=obj, length=1)

            return _expand_path_fwd
        else:

            def _expand_path_rev(
                node: Identifier,
            ) -> Generator[tuple[Identifier, PathStep], None, None]:
                for subj in graph.subjects(path_spec, cast("_ObjectType", node)):
                    yield subj, PathStep(node=subj, length=1)

            return _expand_path_rev

    # str: SPARQL pattern; step carries extra bindings with optional ?length
    bind_var = Variable("start") if forward else Variable("end")
    read_var = Variable("end") if forward else Variable("start")

    # Path pattern -> SELECT * (for finding neighbors)
    q = f"SELECT * WHERE {{{path_spec}}}"
    _path_query = _prepare_and_validate(q, ns_map, {"start", "end"}, "Path pattern")

    def _expand_sparql(
        node: Identifier,
    ) -> Generator[tuple[Identifier, PathStep], None, None]:
        results = graph.query(
            _path_query,
            initBindings={bind_var: node},
        )
        for row in results:
            if not isinstance(row, ResultRow):
                continue
            neighbor = cast("Identifier", row[read_var])
            bindings = {
                str(v): row[v]
                for v in row.labels
                if str(v) not in ("start", "end") and row[v] is not None
            }
            # Extract ?length if bound
            if "length" in bindings:
                raw_length = bindings.pop("length")
                try:
                    step_length = float(raw_length)
                except (ValueError, TypeError) as exc:
                    raise TypeError(
                        f"?length must be numeric, got {raw_length.n3()} "
                    ) from exc
                if step_length < 0:
                    raise ValueError(
                        f"?length must be non-negative, got {raw_length.n3()}. "
                        + "Negative edge weights break the Dijkstra shortest-path guarantee."
                    )
            else:
                step_length = 1
            yield (
                neighbor,
                PathStep(
                    node=neighbor,
                    length=step_length,
                    bindings=cast(
                        "dict[str, Identifier] | None",
                        bindings if bindings else None,
                    ),
                ),
            )

    return _expand_sparql


def _build_end_check_fn(
    end_spec: _NodeSpec,
    graph: Graph,
    ns_map: dict[str, str],
    end_var: str,
) -> tuple[_EndCheckFn, frozenset[Identifier] | None]:
    """
    Build an end-node validation function and optionally a known-ends set.

    Returns a two-element tuple ``(check_fn, known_end_nodes)``:

    - ``check_fn``: a callable ``(Identifier) -> bool`` that returns
      ``True`` when the candidate node is a valid target.
    - ``known_end_nodes``: a ``frozenset`` of all valid end nodes when
      the target set is finite and known up-front (single ``Identifier``
      or iterable of ``Identifier``s).  ``None`` when the end set is
      open-ended (``None`` or SPARQL pattern).  This is used by the
      shortest-path pruning optimization in :func:`_traverse`.

    Dispatch by *end_spec* type:

    - ``None``: every node is a valid end (returns ``lambda: True``).
    - ``Identifier``: only that single node is valid.
    - SPARQL pattern ``str``: compiles and executes an ASK query with
      ``?<end_var>`` bound to the candidate.
    - Iterable of ``Identifier``: materializes into a ``frozenset``
      for O(1) membership testing.

    Args:
        end_spec: The target-side node specification.
        graph: The rdflib graph to query.
        ns_map: Namespace prefix-to-URI mapping for SPARQL compilation.
        end_var: The SPARQL variable name to bind when validating candidates.

    Returns:
        The validation function and (when determinable) the frozen set
        of known end nodes.
    """

    # Unbound: All nodes match, no specified end nodes
    if end_spec is None:
        return lambda _node: True, None

    # Single Identifier: Match only that node
    if isinstance(end_spec, Identifier):
        target = end_spec
        return lambda node: node == target, frozenset({target})

    # str (SPARQL pattern): Match if ASK is true when end node is pre-bound, no specified end nodes
    if _is_sparql_pattern(end_spec):
        var = Variable(end_var)

        # Target pattern -> ASK (to validate candidate end nodes)
        label = ("Start" if end_var == "start" else "End") + " pattern (target)"
        q = f"ASK WHERE {{{end_spec}}}"
        _end_query = _prepare_and_validate(q, ns_map, {end_var}, label)

        def _check_ask(node: Identifier) -> bool:
            result = graph.query(_end_query, initBindings={var: node})
            return bool(result.askAnswer)

        return _check_ask, None

    # Iterable of Identifiers: Materialize into a frozenset
    target_set = frozenset(end_spec)
    return (lambda node: node in target_set), target_set


def _reverse_path(
    traversal_origin: Identifier,
    reverse_steps: list[PathStep],
) -> list[PathStep]:
    """
    Transform reverse-collected steps into forward-order steps.

    When the traversal runs in reverse (end -> start), the steps are
    collected in reverse traversal order: each step's ``node`` is the
    node the traversal arrived *from* (in the caller's forward
    perspective).  This function re-orders the steps and reassigns
    ``node`` so that the resulting list reads from start to end as expected.

    Each step's ``length``, ``edge``, and ``bindings`` are preserved
    from the corresponding source step.

    Args:
        traversal_origin: The traversal origin node (the path's end node
            in forward order).
        reverse_steps: Steps collected during reverse traversal, in
            reverse order.

    Returns:
        Steps in forward order (start -> end).  Empty list if
        *reverse_steps* is empty.
    """
    if not reverse_steps:
        return []

    # In reverse order, step[i].node is the node the traversal came FROM.
    # Forward-order destinations: step[n-2].node, ..., step[0].node, traversal_origin
    reversed_steps = list(reversed(reverse_steps))
    forward_nodes = [s.node for s in reversed_steps[1:]] + [traversal_origin]

    return [
        PathStep(
            node=dest,
            length=source.length,
            edge=source.edge,
            bindings=source.bindings,
        )
        for source, dest in zip(reversed_steps, forward_nodes)
    ]


def _unreverse_results(results: list[PathResult]) -> None:
    """
    Fix results that were collected in reverse direction.

    Args:
        results: The list of results to fix up (modified in-place).
    """
    for result in results:
        # The traversal origin was the caller's end; the traversal
        # target was the caller's start.  Swap them back.
        origin_node = result.start
        result.start = result.end
        result.end = origin_node
        # Reverse the steps
        result.steps = _reverse_path(origin_node, result.steps)


class _PartialPath(NamedTuple):
    """Immutable representation of a partial path in the traversal frontier."""

    origin: Identifier
    current: Identifier
    visited: frozenset[Identifier]
    steps: tuple[PathStep, ...]


def _traverse(
    origin_nodes: set[Identifier],
    expand: _ExpandFn,
    is_valid_end: _EndCheckFn,
    shortest: bool,
    terminate_on_first_match: bool,
    max_length: float | None,
    known_end_nodes: frozenset[Identifier] | None = None,
) -> list[PathResult]:
    """
    Core traversal loop using a priority queue (Dijkstra-style).

    Paths are explored in order of increasing cumulative weighted length
    via a min-heap.  For unweighted paths (every step has ``length == 1``)
    this degrades to breadth-first order.

    When *shortest* is ``True``, the heap ordering guarantees that the
    first time a path reaches an end node, it is via the shortest
    (minimum cumulative weighted length) route.  Ties (multiple paths of
    the same minimum length to the same end node) are preserved: the
    traversal continues popping entries of equal length before moving on.

    When *shortest* is ``False``, all acyclic paths are collected without
    pruning.  The heap ordering is unused in this mode but adds only
    negligible overhead.

    Path length is the **cumulative weighted length**: the sum of each
    step's ``length`` attribute.  When the path is a SPARQL pattern that
    binds ``?length``, the step length equals that value. For all other
    paths, every every step has ``length == 1``, so cumulative length
    equals the hop count.

    **Max-length filtering**: when *max_length* is not ``None``, any
    newly expanded path whose cumulative weighted length exceeds
    *max_length* is discarded.

    **Cross-node cutoff**: when *shortest* is ``True`` **and**
    *known_end_nodes* is supplied (i.e. the caller knows the finite set
    of valid end nodes up-front), the shortest path length found so far
    is tracked for each end node via a ``settled`` dict.  Once
    every known end node has been reached at least once, the maximum of
    those settled lengths becomes a global cutoff: any partial path whose
    cumulative length exceeds the cutoff is discarded, because it cannot
    produce a shortest path to any remaining end node.

    Args:
        origin_nodes: Concrete set of starting nodes.
        expand: One-hop expansion callable
            ``(Identifier) -> Iterable[(Identifier, PathStep)]`` built
            by :func:`_build_expand_fn`.
        is_valid_end: Callable ``(Identifier) -> bool`` that returns
            ``True`` when a candidate node is a valid target, built by
            :func:`_build_end_check_fn`.
        shortest: If ``True``, keep only the shortest path(s) per end
            node by cumulative weighted length.
        terminate_on_first_match: If ``True``, stop extending a path
            once it reaches a valid end node.
        max_length: Maximum cumulative weighted path length.  ``None``
            means no limit.
        known_end_nodes: When not ``None``, the finite set of valid end
            nodes known up-front.  Enables early termination when all
            targets have been reached.

    Returns:
        All discovered paths matching the constraints.  When *shortest*
        is ``True``, only the minimum-length path(s) per end node are
        included.
    """

    results: list[PathResult] = []
    counter = 0  # tie-breaker for heap stability (FIFO among equal lengths)

    # Map nodes to corresponding shortest cumulative length found so far.
    # Because the heap pops in order of increasing length, the first
    # time an end node is reached its length is the shortest for that node.
    settled: dict[Identifier, float] = {}
    # If all end nodes are known and all end nodes are settled,
    # partial paths exceeding global_cutoff = max(settled.values()) are pruned
    # as they cannot possibly be a shortest path for any end node.
    global_cutoff: float | None = None

    # Zero-length paths: origin is also a valid end
    heap: list[tuple[float, int, _PartialPath]] = []
    for node in origin_nodes:
        if is_valid_end(node):
            results.append(PathResult(start=node, end=node, length=0, steps=[]))
            if shortest:
                settled[node] = 0.0
                # Update global cutoff if all known ends are settled
                if known_end_nodes is not None and len(settled) >= len(known_end_nodes):
                    global_cutoff = max(settled.values())
        entry = _PartialPath(node, node, frozenset({node}), ())
        heapq.heappush(heap, (0.0, counter, entry))
        counter += 1

    # Priority-queue traversal
    while heap:
        cumulative_length, _, partial = heapq.heappop(heap)
        origin, current, visited, steps = partial

        # Global cutoff: discard if this partial path already exceeds
        # the longest shortest-path among all known end nodes.
        if global_cutoff is not None and cumulative_length > global_cutoff:
            continue

        # Max-length check
        if max_length is not None and cumulative_length > max_length:
            continue

        # Record result if current node is a valid end.
        # Checking here guarantees that the heap ordering is respected.
        # The first time a path ending at a given node is popped, it has
        # the shortest cumulative length.
        if steps and is_valid_end(current):
            # Shortest pruning: skip if a strictly shorter path to
            # this end node was already settled.
            if shortest and current in settled and cumulative_length > settled[current]:
                continue

            results.append(
                PathResult(
                    start=origin,
                    end=current,
                    length=cumulative_length,
                    steps=list(steps),
                )
            )

            # Update settled state
            if shortest and current not in settled:
                settled[current] = cumulative_length
                # Update global cutoff once all known ends are settled
                if (
                    global_cutoff is None
                    and known_end_nodes is not None
                    and len(settled) >= len(known_end_nodes)
                ):
                    global_cutoff = max(settled.values())

            if terminate_on_first_match:
                continue  # do NOT expand further from this node

        # Expand neighbors
        for neighbor, new_step in expand(current):
            # Per-path cycle detection
            if neighbor in visited:
                continue

            new_cumulative_length = cumulative_length + new_step.length

            # Max-length check on the expanded path
            if max_length is not None and new_cumulative_length > max_length:
                continue

            # Global cutoff check on the expanded path
            if global_cutoff is not None and new_cumulative_length > global_cutoff:
                continue

            new_steps = (*steps, new_step)
            new_visited = visited | {neighbor}

            # Push onto the heap for later processing
            entry = _PartialPath(origin, neighbor, new_visited, new_steps)
            heapq.heappush(heap, (new_cumulative_length, counter, entry))
            counter += 1

    return results


def find_paths(
    graph: Graph,
    start: _NodeSpec = None,
    path: _PathSpec = None,
    end: _NodeSpec = None,
    shortest: bool = True,
    terminate_on_first_match: bool = True,
    max_length: float | None = None,
    initNs: (  # NOQA: N803 consistent capitalization of initNs
        dict[str, str] | None
    ) = None,
) -> list[PathResult]:
    """
    Find paths in an RDFLib graph.

    Args:
        graph: Any rdflib graph-like object.
        start: Fixed node, iterable of fixed nodes, SPARQL WHERE-clause
            body (must contain ``?start``), or ``None`` (unbound).
        path: Fixed predicate, rdflib property path, SPARQL WHERE-clause
            body (must contain ``?start`` and ``?end``), or ``None``
            (unbound).

            When *path* is a SPARQL string and the pattern binds a
            ``?length`` variable, its numeric value is used as the
            weighted length of each step (see :class:`PathStep`).  The
            ``?length`` variable is consumed and does **not** appear in
            ``PathStep.bindings``.  If ``?length`` is not bound, each
            step has ``length == 1``.
        end: Fixed node, iterable of fixed nodes, SPARQL WHERE-clause
            body (must contain ``?end``), or ``None`` (unbound).
        shortest: If ``True`` (the default), return only the shortest
            path(s) per end node.  "Shortest" is determined by
            cumulative weighted length (``PathResult.length``), which
            equals the hop count when no ``?length`` variable is bound.
            If multiple paths of the same minimum length reach the same
            end node, all are returned.  Set to ``False`` to return all
            discovered acyclic paths.
        terminate_on_first_match: If ``True``, stop extending a path
            once it reaches a valid end.
        max_length: Maximum cumulative weighted path length.  Only paths
            whose total length (``PathResult.length``) does not exceed
            this value are returned.  For non-SPARQL paths (or SPARQL
            paths that do not bind ``?length``), every step has
            ``length == 1``, so *max_length* is equivalent to a
            hop-count limit.  When the path is a SPARQL pattern that
            binds ``?length``, the limit applies to the sum of the
            per-step weights.
        initNs: Namespace prefix mapping merged with graph namespaces.

    Returns:
        All discovered paths matching the query constraints.

    Raises:
        ValueError: If all three of *start*, *path*, *end* are ``None``,
            or if a SPARQL pattern is missing required variables, or if
            *max_length* is negative.
    """

    if start is None and path is None and end is None:
        raise ValueError(
            "At least one of start, path, or end must be provided. "
            "A fully unbound query (all three None) is not supported."
        )

    if max_length is not None and max_length < 0:
        raise ValueError(f"max_length must be non-negative, got {max_length}")

    ns_map = _build_namespace_map(graph, initNs)

    # Determine search direction. Must be chosen before preparing queries so we know which
    # string pattern becomes a SELECT (origin) vs ASK (target).
    direction = _choose_direction(start, end)
    reversed_search = direction == TraversalDirection.REVERSE

    if reversed_search:
        origin_spec = end  # caller's end becomes traversal origin
        target_spec = start  # caller's start becomes traversal target
        origin_var = "end"
        target_var = "start"
    else:
        origin_spec = start
        target_spec = end
        origin_var = "start"
        target_var = "end"

    # Resolve origin nodes from which to start finding paths
    origin_nodes = _resolve_origins(origin_spec, graph, ns_map, origin_var)

    # Terminate early if no origins are found
    if not origin_nodes:
        return []

    # Build expansion function
    expand = _build_expand_fn(path, graph, ns_map, not reversed_search)

    # Build end-validation function
    is_valid_end, known_end_nodes = _build_end_check_fn(
        target_spec, graph, ns_map, target_var
    )

    # Execute traversal
    results = _traverse(
        origin_nodes=origin_nodes,
        expand=expand,
        is_valid_end=is_valid_end,
        shortest=shortest,
        terminate_on_first_match=terminate_on_first_match,
        max_length=max_length,
        known_end_nodes=known_end_nodes,
    )

    # If search was reversed, fix results accordingly
    if reversed_search:
        _unreverse_results(results)

    return results
