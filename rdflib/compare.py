"""
A collection of utilities for canonicalizing and inspecting graphs.

Among other things, they solve of the problem of deterministic bnode
comparisons.

Warning: the time to canonicalize bnodes may increase exponentially on
degenerate larger graphs. Use with care!

Example of comparing two graphs:

```python
>>> g1 = Graph().parse(format='n3', data='''
...     @prefix : <http://example.org/ns#> .
...     <http://example.org> :rel
...         <http://example.org/same>,
...         [ :label "Same" ],
...         <http://example.org/a>,
...         [ :label "A" ] .
... ''')
>>> g2 = Graph().parse(format='n3', data='''
...     @prefix : <http://example.org/ns#> .
...     <http://example.org> :rel
...         <http://example.org/same>,
...         [ :label "Same" ],
...         <http://example.org/b>,
...         [ :label "B" ] .
... ''')
>>>
>>> iso1 = to_isomorphic(g1)
>>> iso2 = to_isomorphic(g2)

```

These are not isomorphic

```python
>>> iso1 == iso2
False

```

Diff the two graphs:

```python
>>> in_both, in_first, in_second = graph_diff(iso1, iso2)

```

Present in both:

```python
>>> def dump_nt_sorted(g):
...     for l in sorted(g.serialize(format='nt').splitlines()):
...         if l: print(l.decode('ascii'))
>>> dump_nt_sorted(in_both) #doctest: +SKIP
<http://example.org>
    <http://example.org/ns#rel> <http://example.org/same> .
<http://example.org>
    <http://example.org/ns#rel> _:cbcaabaaba17fecbc304a64f8edee4335e .
_:cbcaabaaba17fecbc304a64f8edee4335e
    <http://example.org/ns#label> "Same" .
```

Only in first:

```python
>>> dump_nt_sorted(in_first) #doctest: +SKIP
<http://example.org>
    <http://example.org/ns#rel> <http://example.org/a> .
<http://example.org>
    <http://example.org/ns#rel> _:cb124e4c6da0579f810c0ffe4eff485bd9 .
_:cb124e4c6da0579f810c0ffe4eff485bd9
    <http://example.org/ns#label> "A" .
```

Only in second:

```python
>>> dump_nt_sorted(in_second) #doctest: +SKIP
<http://example.org>
    <http://example.org/ns#rel> <http://example.org/b> .
<http://example.org>
    <http://example.org/ns#rel> _:cb558f30e21ddfc05ca53108348338ade8 .
_:cb558f30e21ddfc05ca53108348338ade8
    <http://example.org/ns#label> "B" .
```
"""

from __future__ import annotations

# TODO:
# - Doesn't handle quads.
# - Add warning and/or safety mechanism before working on large graphs?
# - use this in existing Graph.isomorphic?

__all__ = [
    "IsomorphicGraph",
    "to_isomorphic",
    "isomorphic",
    "to_canonical_graph",
    "graph_diff",
    "similar",
]

from collections import defaultdict
from datetime import datetime
from hashlib import sha256
from typing import (
    TYPE_CHECKING,
    Callable,
    Dict,
    Iterator,
    List,
    Optional,
    Set,
    Tuple,
    Union,
)

from rdflib.graph import ConjunctiveGraph, Graph, ReadOnlyGraphAggregate, _TripleType
from rdflib.term import BNode, IdentifiedNode, Literal, Node, TripleTerm, URIRef

if TYPE_CHECKING:
    from _hashlib import HASH


def _get_bnodes_from_term(term: Node) -> Set[BNode]:
    """Extract all blank nodes from a term, recursing into TripleTerms.

    RDF 1.2 introduces triple terms (see
    https://www.w3.org/TR/rdf12-concepts/#section-triple-terms) which may
    contain blank nodes in their subject and object positions. For graph
    canonicalization and isomorphism checking, we need to discover *all*
    blank nodes that participate in a graph -- including those embedded
    inside triple terms that appear as objects of asserted triples.

    Per the RDF 1.2 abstract model:
      - A triple term's **subject** is always an IRI or blank node (never
        a nested TripleTerm, since triple terms can only appear in the
        object position of a triple).
      - A triple term's **predicate** is always an IRI.
      - A triple term's **object** may be an IRI, blank node, literal, or
        another (nested) triple term.

    This function therefore:
      1. Returns ``{term}`` immediately if the term itself is a BNode.
      2. For a TripleTerm, collects BNodes from the subject and object
         positions, recursing into nested TripleTerms in the object.
      3. Returns the empty set for IRIs and Literals.

    Args:
        term: Any RDF node (BNode, URIRef, Literal, or TripleTerm).

    Returns:
        The set of all BNodes reachable within this term.
    """
    if isinstance(term, BNode):
        return {term}
    elif isinstance(term, TripleTerm):
        result: Set[BNode] = set()
        if isinstance(term.subject, BNode):
            result.add(term.subject)
        if isinstance(term.object, BNode):
            result.add(term.object)
        elif isinstance(term.object, TripleTerm):
            result.update(_get_bnodes_from_term(term.object))
        return result
    return set()


def _remap_triple_term(tt: TripleTerm, mapping: Dict[BNode, BNode]) -> TripleTerm:
    """Apply a blank node mapping to a TripleTerm, producing a new TripleTerm.

    During graph canonicalization and isomorphism checking, blank nodes are
    relabeled (e.g., to canonical ``cb<hash>`` identifiers or to a mock BNode
    for similarity checks). When a blank node appears *inside* an RDF 1.2
    triple term -- either as the subject or the object -- those embedded
    BNodes must be remapped consistently with how they are remapped at the
    graph level.

    This function walks the TripleTerm structure and replaces any BNode that
    appears in the provided ``mapping`` dict. Because the RDF 1.2 spec allows
    nested triple terms only in the **object** position, we recurse into the
    object when it is itself a TripleTerm, but never into the subject.

    Args:
        tt: The TripleTerm whose embedded BNodes should be remapped.
        mapping: A dictionary mapping original BNodes to their replacements.

    Returns:
        A new TripleTerm with BNodes replaced according to the mapping.
        If no BNodes in the TripleTerm appear in the mapping, the returned
        TripleTerm may still be a new instance.
    """
    s: Union[URIRef, BNode] = (
        mapping.get(tt.subject, tt.subject)
        if isinstance(tt.subject, BNode)
        else tt.subject
    )
    o: Union[URIRef, BNode, Literal, TripleTerm] = tt.object
    if isinstance(o, BNode):
        o = mapping.get(o, o)
    elif isinstance(o, TripleTerm):
        o = _remap_triple_term(o, mapping)
    return TripleTerm(s, tt.predicate, o)


def _total_seconds(td):
    result = td.days * 24 * 60 * 60
    result += td.seconds
    result += td.microseconds / 1000000.0
    return result


class _runtime:  # noqa: N801
    def __init__(self, label):
        self.label = label

    def __call__(self, f):
        if self.label is None:
            self.label = f.__name__ + "_runtime"

        def wrapped_f(*args, **kwargs):
            start = datetime.now()
            result = f(*args, **kwargs)
            if "stats" in kwargs and kwargs["stats"] is not None:
                stats = kwargs["stats"]
                stats[self.label] = _total_seconds(datetime.now() - start)
            return result

        return wrapped_f


class _call_count:  # noqa: N801
    def __init__(self, label):
        self.label = label

    def __call__(self, f):
        if self.label is None:
            self.label = f.__name__ + "_runtime"

        def wrapped_f(*args, **kwargs):
            if "stats" in kwargs and kwargs["stats"] is not None:
                stats = kwargs["stats"]
                if self.label not in stats:
                    stats[self.label] = 0
                stats[self.label] += 1
            return f(*args, **kwargs)

        return wrapped_f


class IsomorphicGraph(ConjunctiveGraph):
    """An implementation of the RGDA1 graph digest algorithm.

    An implementation of RGDA1 (publication below),
    a combination of Sayers & Karp's graph digest algorithm using
    sum and SHA-256 <http://www.hpl.hp.com/techreports/2003/HPL-2003-235R1.pdf>
    and traces <http://pallini.di.uniroma1.it>, an average case
    polynomial time algorithm for graph canonicalization.

    McCusker, J. P. (2015). WebSig: A Digital Signature Framework for the Web.
    Rensselaer Polytechnic Institute, Troy, NY.
    http://gradworks.umi.com/3727015.pdf
    """

    def __init__(self, **kwargs):
        super(IsomorphicGraph, self).__init__(**kwargs)

    def __eq__(self, other):
        """Graph isomorphism testing."""
        if not isinstance(other, IsomorphicGraph):
            return False
        elif len(self) != len(other):
            return False
        return self.internal_hash() == other.internal_hash()

    def __ne__(self, other):
        """Negative graph isomorphism testing."""
        return not self.__eq__(other)

    def __hash__(self):
        return super(IsomorphicGraph, self).__hash__()

    def graph_digest(self, stats=None):
        """Synonym for IsomorphicGraph.internal_hash."""
        return self.internal_hash(stats=stats)

    def internal_hash(self, stats=None):
        """
        This is defined instead of `__hash__` to avoid a circular recursion
        scenario with the Memory store for rdflib which requires a hash lookup
        in order to return a generator of triples.
        """
        return _TripleCanonicalizer(self).to_hash(stats=stats)


HashFunc = Callable[[str], int]
ColorItem = Tuple[Union[int, str], URIRef, Union[int, str]]
ColorItemTuple = Tuple[ColorItem, ...]
HashCache = Optional[Dict[ColorItemTuple, str]]
Stats = Dict[str, Union[int, str]]


class Color:
    def __init__(
        self,
        nodes: List[IdentifiedNode],
        hashfunc: HashFunc,
        color: ColorItemTuple = (),
        hash_cache: HashCache = None,
    ):
        if hash_cache is None:
            hash_cache = {}
        self._hash_cache = hash_cache
        self.color = color
        self.nodes = nodes
        self.hashfunc = hashfunc
        self._hash_color = None

    def __str__(self):
        nodes, color = self.key()
        return "Color %s (%s nodes)" % (color, nodes)

    def key(self):
        return (len(self.nodes), self.hash_color())

    def hash_color(self, color: Optional[Tuple[ColorItem, ...]] = None) -> str:
        if color is None:
            color = self.color
        if color in self._hash_cache:
            return self._hash_cache[color]

        def stringify(x):
            if isinstance(x, Node):
                return x.n3()
            else:
                return str(x)

        if isinstance(color, Node):
            return stringify(color)
        value = 0
        for triple in color:
            value += self.hashfunc(" ".join([stringify(x) for x in triple]))
        val: str = "%x" % value
        self._hash_cache[color] = val
        return val

    def distinguish(self, W: Color, graph: Graph):  # noqa: N803
        colors: Dict[str, Color] = {}
        for n in self.nodes:
            new_color: Tuple[ColorItem, ...] = list(self.color)  # type: ignore[assignment]
            for node in W.nodes:
                new_color += [  # type: ignore[operator]
                    (1, p, W.hash_color()) for s, p, o in graph.triples((n, None, node))
                ]
                new_color += [  # type: ignore[operator]
                    (W.hash_color(), p, 3) for s, p, o in graph.triples((node, None, n))
                ]
            new_color = tuple(new_color)
            new_hash_color = self.hash_color(new_color)

            if new_hash_color not in colors:
                c = Color([], self.hashfunc, new_color, hash_cache=self._hash_cache)
                colors[new_hash_color] = c
            colors[new_hash_color].nodes.append(n)
        return colors.values()

    def discrete(self):
        return len(self.nodes) == 1

    def copy(self):
        return Color(
            self.nodes[:], self.hashfunc, self.color, hash_cache=self._hash_cache
        )


_HashT = Callable[[], "HASH"]


class _TripleCanonicalizer:
    def __init__(self, graph: Graph, hashfunc: _HashT = sha256):
        self.graph = graph

        def _hashfunc(s: str):
            h = hashfunc()
            h.update(str(s).encode("utf8"))
            return int(h.hexdigest(), 16)

        self._hash_cache: HashCache = {}
        self.hashfunc = _hashfunc

    def _discrete(self, coloring: List[Color]) -> bool:
        return len([c for c in coloring if not c.discrete()]) == 0

    def _initial_color(self) -> List[Color]:
        """Finds an initial color for the graph.

        Finds an initial color of the graph by finding all blank nodes and
        non-blank nodes that are adjacent. Nodes that are not adjacent to blank
        nodes are not included, as they are a) already colored (by URI or literal)
        and b) do not factor into the color of any blank node.

        RDF 1.2 TripleTerm handling:
            Triple terms (``<<( s p o )>>``) may contain embedded blank nodes
            in their subject or object positions. For correct canonicalization,
            the algorithm must handle two classes of BNodes differently:

            **Graph-level BNodes** (those that appear as a direct subject,
            predicate, or object in asserted triples) are collected into a
            single initial color class and refined by ``Color.distinguish()``
            which uses ``graph.triples()`` to find their structural edges.

            **Embedded-only BNodes** (those that appear exclusively inside
            TripleTerms and never directly in asserted triple positions) are
            invisible to ``graph.triples()`` queries, so ``distinguish()``
            cannot differentiate them. To solve this, we record each embedded
            BNode's *structural context* -- its position within the TripleTerm
            (subject vs object), the asserted triple's subject and predicate,
            and the other non-bnode terms in the TripleTerm. Embedded-only
            BNodes are then grouped by this context and assigned distinct
            initial colors, ensuring that BNodes in different structural
            positions produce different canonical hashes deterministically.

            Additionally:
            1. BNodes embedded inside TripleTerms are discovered via
               ``_get_bnodes_from_term`` and included in the bnode set.
            2. The TripleTerm itself is added to "others" as a composite value
               for coloring (it is not a blank node, even though it contains
               blank nodes).
            3. Each embedded BNode is registered as a neighbor of the asserted
               triple's subject (used as supplementary structural data).
        """
        bnodes: Set[BNode] = set()
        others = set()
        self._neighbors = defaultdict(set)
        # RDF 1.2: Track structural context for BNodes embedded in TripleTerms.
        # BNodes that appear only inside TripleTerms are invisible to
        # graph.triples() queries, so Color.distinguish() cannot differentiate
        # them from other embedded BNodes. We record contextual information
        # (their position and surrounding terms in the TripleTerm) so that we
        # can assign them distinguishing initial colors.
        self._embedded_bnode_contexts: Dict[BNode, Set[tuple]] = defaultdict(set)
        # Collect graph-level BNodes (those appearing directly as s/p/o in
        # asserted triples) in the same pass to avoid a second iteration.
        graph_level_bnodes: Set[BNode] = set()
        for s, p, o in self.graph:
            # Track graph-level BNodes as we encounter them.
            if isinstance(s, BNode):
                graph_level_bnodes.add(s)
            if isinstance(p, BNode):
                graph_level_bnodes.add(p)
            if isinstance(o, BNode):
                graph_level_bnodes.add(o)

            # RDF 1.2: Extract BNodes embedded inside TripleTerms in object
            # position. These must participate in the canonicalization just
            # like top-level BNodes.
            embedded_bnodes: Set[BNode] = set()
            if isinstance(o, TripleTerm):
                embedded_bnodes = _get_bnodes_from_term(o)
                # Record structural context for each embedded BNode.
                # This enables distinguish-by-context for BNodes that are
                # invisible to graph.triples().
                self._record_triple_term_context(o, s, p)

            b = set([x for x in (s, p, o) if isinstance(x, BNode)]) | embedded_bnodes
            if len(b) > 0:
                # Collect non-bnode, non-TripleTerm terms as "others" for
                # coloring. Only `o` can be a TripleTerm per the RDF model.
                for term in (s, p, o):
                    if term not in b and not isinstance(term, TripleTerm):
                        others.add(term)
                # Add the TripleTerm itself to "others" for coloring. It acts
                # as a distinguishing label (like a literal or IRI) but is not
                # a bnode.
                if isinstance(o, TripleTerm):
                    others.add(o)
                bnodes |= b
                if isinstance(s, BNode):
                    self._neighbors[s].add(o)
                if isinstance(o, BNode):
                    self._neighbors[o].add(s)
                elif isinstance(o, TripleTerm):
                    # Each BNode embedded in a TripleTerm is considered a
                    # neighbor of the asserted triple's subject. This ensures
                    # that the coloring algorithm can distinguish graphs where
                    # the same BNode appears inside different TripleTerms.
                    for bn in embedded_bnodes:
                        self._neighbors[bn].add(s)
                if isinstance(p, BNode):
                    self._neighbors[p].add(s)
                    self._neighbors[p].add(p)
        if len(bnodes) > 0:
            # Separate embedded-only BNodes into distinct initial color
            # classes based on their structural context within TripleTerms.
            # BNodes that also appear at the graph level are handled normally
            # by distinguish() since graph.triples() can see them.
            embedded_only = bnodes - graph_level_bnodes
            graph_bnodes = bnodes & graph_level_bnodes

            # Group embedded-only BNodes by their structural context hash
            # so that structurally equivalent BNodes get the same color.
            embedded_color_groups: Dict[str, List[BNode]] = defaultdict(list)
            for bn in embedded_only:
                # Create a hashable context key from the sorted string
                # representations of the BNode's structural contexts.
                ctx = self._embedded_bnode_contexts.get(bn, set())
                ctx_key = str(sorted(str(c) for c in ctx))
                embedded_color_groups[ctx_key].append(bn)

            # Build the initial coloring:
            # - One color for all graph-level BNodes (they will be refined by
            #   distinguish() using graph.triples()).
            # - Separate colors for each group of embedded-only BNodes that
            #   share the same structural context. Each group receives a
            #   unique initial color derived from its context key, ensuring
            #   that BNodes in different positions produce different canonical
            #   hashes even when they cannot be reached by graph.triples().
            bnode_colors: List[Color] = []
            if graph_bnodes:
                bnode_colors.append(
                    Color(
                        list(graph_bnodes), self.hashfunc, hash_cache=self._hash_cache
                    )
                )
            for ctx_key, group in embedded_color_groups.items():
                # Use the context key as the initial color so that BNodes in
                # different structural positions start with different colors
                # and thus produce different canonical labels.
                # We wrap it in a tuple-of-tuples structure compatible with
                # Color.hash_color() which expects ColorItemTuple.
                context_color: Tuple = (
                    (ctx_key, URIRef("urn:rdflib:tt-ctx"), ctx_key),
                )
                bnode_colors.append(
                    Color(
                        list(group),
                        self.hashfunc,
                        context_color,
                        hash_cache=self._hash_cache,
                    )
                )

            return bnode_colors + [
                # type error: List item 0 has incompatible type "Union[IdentifiedNode, Literal]"; expected "IdentifiedNode"
                # type error: Argument 3 to "Color" has incompatible type "Union[IdentifiedNode, Literal]"; expected "Tuple[Tuple[Union[int, str], URIRef, Union[int, str]], ...]"
                Color([x], self.hashfunc, x, hash_cache=self._hash_cache)  # type: ignore[list-item, arg-type]
                for x in others
            ]
        else:
            return []

    @staticmethod
    def _describe_term(term: Node) -> str:
        """Return a position-stable descriptor for a term, masking BNode identity.

        Used by ``_record_triple_term_context`` to build structural context
        tuples without leaking specific BNode labels (which would defeat the
        purpose of position-based coloring).
        """
        if isinstance(term, BNode):
            return "_:*"
        elif isinstance(term, TripleTerm):
            return "<<TripleTerm>>"
        return term.n3()

    def _record_triple_term_context(
        self, tt: TripleTerm, graph_subject: Node, graph_predicate: Node
    ) -> None:
        """Record structural context for BNodes embedded in a TripleTerm.

        For each BNode found inside the TripleTerm, we record a tuple
        describing its position and the surrounding non-bnode terms. This
        contextual information is used during initial coloring to distinguish
        BNodes that appear only inside TripleTerms (and are thus invisible
        to graph.triples() queries used by Color.distinguish()).

        The context tuple for a BNode in the **subject** position of a
        TripleTerm is: ``("tt_subject", graph_subject, graph_predicate,
        tt.predicate, <object_descriptor>)``

        The context tuple for a BNode in the **object** position is:
        ``("tt_object", graph_subject, graph_predicate, <subject_descriptor>,
        tt.predicate)``

        Where descriptors for non-bnode terms are their n3() representation,
        and descriptors for BNode terms are the placeholder string "_:*".

        Args:
            tt: The TripleTerm to scan.
            graph_subject: The subject of the asserted triple containing this
                TripleTerm.
            graph_predicate: The predicate of the asserted triple containing
                this TripleTerm.
        """
        desc = self._describe_term
        obj_desc = desc(tt.object)
        subj_desc = desc(tt.subject)
        gs = desc(graph_subject)
        gp = desc(graph_predicate)

        if isinstance(tt.subject, BNode):
            self._embedded_bnode_contexts[tt.subject].add(
                ("tt_subject", gs, gp, tt.predicate.n3(), obj_desc)
            )
        if isinstance(tt.object, BNode):
            self._embedded_bnode_contexts[tt.object].add(
                ("tt_object", gs, gp, subj_desc, tt.predicate.n3())
            )
        elif isinstance(tt.object, TripleTerm):
            # Recurse into nested TripleTerms
            self._record_triple_term_context(tt.object, graph_subject, graph_predicate)

    def _individuate(self, color, individual):
        new_color = list(color.color)
        new_color.append((len(color.nodes),))

        color.nodes.remove(individual)
        c = Color(
            [individual], self.hashfunc, tuple(new_color), hash_cache=self._hash_cache
        )
        return c

    def _get_candidates(self, coloring: List[Color]) -> Iterator[Tuple[Node, Color]]:
        for c in [c for c in coloring if not c.discrete()]:
            for node in c.nodes:
                yield node, c

    def _refine(self, coloring: List[Color], sequence: List[Color]) -> List[Color]:
        sequence = sorted(sequence, key=lambda x: x.key(), reverse=True)
        coloring = coloring[:]
        while len(sequence) > 0 and not self._discrete(coloring):
            W = sequence.pop()  # noqa: N806
            for c in coloring[:]:
                if len(c.nodes) > 1 or isinstance(c.nodes[0], BNode):
                    colors = sorted(
                        c.distinguish(W, self.graph),
                        key=lambda x: x.key(),
                        reverse=True,
                    )
                    coloring.remove(c)
                    coloring.extend(colors)
                    try:
                        si = sequence.index(c)
                        sequence = sequence[:si] + colors + sequence[si + 1 :]
                    except ValueError:
                        sequence = colors[1:] + sequence
        combined_colors: List[Color] = []
        combined_color_map: Dict[str, Color] = dict()
        for color in coloring:
            color_hash = color.hash_color()
            # This is a hash collision, and be combined into a single color for individuation.
            if color_hash in combined_color_map:
                combined_color_map[color_hash].nodes.extend(color.nodes)
            else:
                combined_colors.append(color)
                combined_color_map[color_hash] = color
        return combined_colors

    @_runtime("to_hash_runtime")
    def to_hash(self, stats: Optional[Stats] = None):
        result = 0
        for triple in self.canonical_triples(stats=stats):
            result += self.hashfunc(" ".join([x.n3() for x in triple]))
        if stats is not None:
            stats["graph_digest"] = "%x" % result
        return result

    def _experimental_path(self, coloring: List[Color]) -> List[Color]:
        coloring = [c.copy() for c in coloring]
        while not self._discrete(coloring):
            color = [x for x in coloring if not x.discrete()][0]
            node = color.nodes[0]
            new_color = self._individuate(color, node)
            coloring.append(new_color)
            coloring = self._refine(coloring, [new_color])
        return coloring

    def _create_generator(
        self,
        colorings: List[List[Color]],
        groupings: Optional[Dict[Node, Set[Node]]] = None,
    ) -> Dict[Node, Set[Node]]:
        if not groupings:
            groupings = defaultdict(set)
        for group in zip(*colorings):
            g = set([c.nodes[0] for c in group])
            for n in group:
                g |= groupings[n]
            for n in g:
                groupings[n] = g
        return groupings

    @_call_count("individuations")
    def _traces(
        self,
        coloring: List[Color],
        stats: Optional[Stats] = None,
        depth: List[int] = [0],
    ) -> List[Color]:
        if stats is not None and "prunings" not in stats:
            stats["prunings"] = 0
        depth[0] += 1
        candidates = self._get_candidates(coloring)
        best: List[List[Color]] = []
        best_score = None
        best_experimental_score = None
        last_coloring = None
        generator: Dict[Node, Set[Node]] = defaultdict(set)
        visited: Set[Node] = set()
        for candidate, color in candidates:
            if candidate in generator:
                v = generator[candidate] & visited
                if len(v) > 0:
                    visited.add(candidate)
                    continue
            visited.add(candidate)
            coloring_copy: List[Color] = []
            color_copy = None
            for c in coloring:
                c_copy = c.copy()
                coloring_copy.append(c_copy)
                if c == color:
                    color_copy = c_copy
            new_color = self._individuate(color_copy, candidate)
            coloring_copy.append(new_color)
            refined_coloring = self._refine(coloring_copy, [new_color])
            color_score = tuple([c.key() for c in refined_coloring])
            experimental = self._experimental_path(coloring_copy)
            experimental_score = set([c.key() for c in experimental])
            if last_coloring:
                # type error: Statement is unreachable
                generator = self._create_generator(  # type: ignore[unreachable]
                    [last_coloring, experimental], generator
                )
            last_coloring = experimental
            if best_score is None or best_score < color_score:  # type: ignore[unreachable]
                best = [refined_coloring]
                best_score = color_score
                best_experimental_score = experimental_score
            elif best_score > color_score:  # type: ignore[unreachable]
                # prune this branch.
                if stats is not None and isinstance(stats["prunings"], int):
                    stats["prunings"] += 1
            elif experimental_score != best_experimental_score:
                best.append(refined_coloring)
            else:
                # prune this branch.
                if stats is not None and isinstance(stats["prunings"], int):
                    stats["prunings"] += 1
        discrete: List[List[Color]] = [x for x in best if self._discrete(x)]
        if len(discrete) == 0:
            best_score = None
            best_depth = None
            for coloring in best:
                d = [depth[0]]
                new_color = self._traces(coloring, stats=stats, depth=d)
                color_score = tuple([c.key() for c in refined_coloring])
                if best_score is None or color_score > best_score:  # type: ignore[unreachable]
                    discrete = [new_color]
                    best_score = color_score
                    best_depth = d[0]
            depth[0] = best_depth  # type: ignore[assignment]
        return discrete[0]

    def canonical_triples(self, stats: Optional[Stats] = None):
        if stats is not None:
            start_coloring = datetime.now()
        coloring = self._initial_color()
        if stats is not None:
            stats["triple_count"] = len(self.graph)
            stats["adjacent_nodes"] = max(0, len(coloring) - 1)
        coloring = self._refine(coloring, coloring[:])
        if stats is not None:
            stats["initial_coloring_runtime"] = _total_seconds(
                datetime.now() - start_coloring
            )
            stats["initial_color_count"] = len(coloring)

        if not self._discrete(coloring):
            depth = [0]
            coloring = self._traces(coloring, stats=stats, depth=depth)
            if stats is not None:
                stats["tree_depth"] = depth[0]
        elif stats is not None:
            stats["individuations"] = 0
            stats["tree_depth"] = 0
        if stats is not None:
            stats["color_count"] = len(coloring)

        bnode_labels: Dict[Node, str] = dict(
            [(c.nodes[0], c.hash_color()) for c in coloring]
        )
        if stats is not None:
            stats["canonicalize_triples_runtime"] = _total_seconds(
                datetime.now() - start_coloring
            )
        for triple in self.graph:
            result = tuple(self._canonicalize_bnodes(triple, bnode_labels))
            yield result

    def _canonicalize_bnodes(
        self,
        triple: _TripleType,
        labels: Dict[Node, str],
    ):
        """Yield canonicalized terms for a triple, replacing BNodes with
        deterministic canonical labels.

        For each term in the triple:
          - **BNode**: replaced with a new BNode whose identifier is
            ``cb<hash>`` where ``<hash>`` is the canonical color computed
            by the coloring algorithm.
          - **TripleTerm** (RDF 1.2): any BNodes embedded inside the triple
            term are remapped using the same canonical labels via
            ``_remap_triple_term``. This ensures that a BNode appearing both
            at the graph level and inside a TripleTerm receives the same
            canonical identifier, preserving structural consistency.
          - **Other terms** (URIRef, Literal): yielded unchanged.

        Args:
            triple: A 3-tuple (subject, predicate, object) from the graph.
            labels: A mapping from BNode -> canonical hash string, as
                computed by the coloring/individualization algorithm.

        Yields:
            The canonicalized terms in order (subject, predicate, object).
        """
        for term in triple:
            if isinstance(term, BNode):
                yield BNode(value="cb%s" % labels[term])
            elif isinstance(term, TripleTerm):
                # Remap any bnodes inside the TripleTerm to their canonical
                # labels so that isomorphic graphs produce identical TripleTerms.
                bnode_mapping = {
                    bn: BNode(value="cb%s" % labels[bn])
                    for bn in _get_bnodes_from_term(term)
                    if bn in labels
                }
                if bnode_mapping:
                    yield _remap_triple_term(term, bnode_mapping)
                else:
                    yield term
            else:
                yield term


def to_isomorphic(graph: Graph) -> IsomorphicGraph:
    if isinstance(graph, IsomorphicGraph):
        return graph
    result = IsomorphicGraph()
    if hasattr(graph, "identifier"):
        result = IsomorphicGraph(identifier=graph.identifier)
    result += graph
    return result


def isomorphic(graph1: Graph, graph2: Graph) -> bool:
    """Compare graph for equality.

    Uses an algorithm to compute unique hashes which takes bnodes into account.

    Example:
        ```python
        >>> g1 = Graph().parse(format='n3', data='''
        ...     @prefix : <http://example.org/ns#> .
        ...     <http://example.org> :rel <http://example.org/a> .
        ...     <http://example.org> :rel <http://example.org/b> .
        ...     <http://example.org> :rel [ :label "A bnode." ] .
        ... ''')
        >>> g2 = Graph().parse(format='n3', data='''
        ...     @prefix ns: <http://example.org/ns#> .
        ...     <http://example.org> ns:rel [ ns:label "A bnode." ] .
        ...     <http://example.org> ns:rel <http://example.org/b>,
        ...             <http://example.org/a> .
        ... ''')
        >>> isomorphic(g1, g2)
        True
        >>> g3 = Graph().parse(format='n3', data='''
        ...     @prefix : <http://example.org/ns#> .
        ...     <http://example.org> :rel <http://example.org/a> .
        ...     <http://example.org> :rel <http://example.org/b> .
        ...     <http://example.org> :rel <http://example.org/c> .
        ... ''')
        >>> isomorphic(g1, g3)
        False

        ```
    """
    gd1 = _TripleCanonicalizer(graph1).to_hash()
    gd2 = _TripleCanonicalizer(graph2).to_hash()
    return gd1 == gd2


def to_canonical_graph(
    g1: Graph, stats: Optional[Stats] = None
) -> ReadOnlyGraphAggregate:
    """Creates a canonical, read-only graph.

    Creates a canonical, read-only graph where all bnode id:s are based on
    deterministical SHA-256 checksums, correlated with the graph contents.
    """
    graph = Graph()
    graph += _TripleCanonicalizer(g1).canonical_triples(stats=stats)
    return ReadOnlyGraphAggregate([graph])


def graph_diff(g1: Graph, g2: Graph) -> Tuple[Graph, Graph, Graph]:
    """Returns three sets of triples: "in both", "in first" and "in second"."""
    # bnodes have deterministic values in canonical graphs:
    cg1 = to_canonical_graph(g1)
    cg2 = to_canonical_graph(g2)
    in_both = cg1 * cg2
    in_first = cg1 - cg2
    in_second = cg2 - cg1
    return (in_both, in_first, in_second)


_MOCK_BNODE = BNode()


def similar(g1: Graph, g2: Graph):
    """Checks if the two graphs are "similar".

    Checks if the two graphs are "similar", by comparing sorted triples where
    all bnodes have been replaced by a singular mock bnode (the
    `_MOCK_BNODE`).

    This is a much cheaper, but less reliable, alternative to the comparison
    algorithm in `isomorphic`.
    """
    return all(t1 == t2 for (t1, t2) in _squashed_graphs_triples(g1, g2))


def _squashed_graphs_triples(g1: Graph, g2: Graph):
    for t1, t2 in zip(sorted(_squash_graph(g1)), sorted(_squash_graph(g2))):
        yield t1, t2


def _squash_graph(graph: Graph):
    return (_squash_bnodes(triple) for triple in graph)


def _squash_bnodes(triple):
    """Replace all BNodes in a triple with a singular mock BNode.

    This is used by the ``similar()`` function as a cheap approximation of
    graph isomorphism. By replacing every BNode with the same mock value,
    two graphs can be compared structurally without needing full
    canonicalization.

    RDF 1.2 TripleTerm handling:
        When the object of a triple is a TripleTerm that contains embedded
        BNodes (in subject or object position), those embedded BNodes are
        also replaced with the mock BNode via ``_remap_triple_term``. This
        ensures that TripleTerms with different BNodes are treated as
        structurally equivalent for the purposes of the similarity check,
        mirroring how top-level BNodes are squashed.

    Args:
        triple: A 3-tuple (subject, predicate, object) from the graph.

    Returns:
        A new tuple where all BNodes (including those inside TripleTerms)
        have been replaced with ``_MOCK_BNODE``.
    """

    def _squash_term(t):
        if isinstance(t, BNode):
            return _MOCK_BNODE
        elif isinstance(t, TripleTerm):
            bnodes = _get_bnodes_from_term(t)
            if bnodes:
                mapping = {bn: _MOCK_BNODE for bn in bnodes}
                return _remap_triple_term(t, mapping)
            return t
        return t

    return tuple(_squash_term(t) for t in triple)
