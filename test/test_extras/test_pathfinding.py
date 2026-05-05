import pytest

from rdflib import BNode, Graph, Literal, Namespace
from rdflib.extras.pathfinding import (
    PathResult,
    TraversalDirection,
    _build_end_check_fn,
    _build_expand_fn,
    _build_namespace_map,
    _choose_direction,
    _is_sparql_pattern,
    _prepare_and_validate,
    _resolve_origins,
    find_paths,
)

EX = Namespace("http://example.org/")
NS = {"ex": str(EX)}


@pytest.fixture()
def linear_graph() -> Graph:
    """A -> B -> C -> D via ex:knows, plus a shortcut B -> D."""
    g = Graph()
    g.bind("ex", EX)
    g.add((EX.Alice, EX.knows, EX.Bob))
    g.add((EX.Bob, EX.knows, EX.Carol))
    g.add((EX.Carol, EX.knows, EX.Dave))
    g.add((EX.Bob, EX.knows, EX.Dave))
    return g


@pytest.fixture()
def cyclic_graph() -> Graph:
    """A -> B -> C -> A (cycle) via ex:knows."""
    g = Graph()
    g.bind("ex", EX)
    g.add((EX.A, EX.knows, EX.B))
    g.add((EX.B, EX.knows, EX.C))
    g.add((EX.C, EX.knows, EX.A))
    return g


@pytest.fixture()
def diamond_graph() -> Graph:
    """Diamond: A -> B, A -> C, B -> D, C -> D via ex:knows."""
    g = Graph()
    g.bind("ex", EX)
    g.add((EX.A, EX.knows, EX.B))
    g.add((EX.A, EX.knows, EX.C))
    g.add((EX.B, EX.knows, EX.D))
    g.add((EX.C, EX.knows, EX.D))
    return g


@pytest.fixture()
def multi_pred_graph() -> Graph:
    """Graph with multiple predicates between nodes."""
    g = Graph()
    g.bind("ex", EX)
    g.add((EX.Alice, EX.knows, EX.Bob))
    g.add((EX.Bob, EX.worksWith, EX.Carol))
    g.add((EX.Carol, EX.knows, EX.Dave))
    return g


@pytest.fixture()
def manager_graph(linear_graph: Graph) -> Graph:
    """linear_graph extended with role annotations."""
    linear_graph.add((EX.Dave, EX.role, EX.Manager))
    linear_graph.add((EX.Carol, EX.role, EX.Manager))
    linear_graph.add((EX.Alice, EX.department, EX.Engineering))
    linear_graph.add((EX.Bob, EX.department, EX.Engineering))
    return linear_graph


def _path_nodes(result: PathResult) -> list[str]:
    """Extract node local names from a PathResult for easy assertion."""
    names = [str(result.start).rsplit("/", 1)[-1]]
    names.extend(str(s.node).rsplit("/", 1)[-1] for s in result.steps)
    return names


def _path_node_sets(results: list[PathResult]) -> set[tuple[str, ...]]:
    """Convert results to a set of node-name tuples for order-independent comparison."""
    return {tuple(_path_nodes(r)) for r in results}


class TestIsSparqlPattern:
    """Unit tests for _is_sparql_pattern."""

    @pytest.mark.parametrize(
        "value, expected",
        [
            pytest.param("?start ex:knows ?end", True, id="sparql_pattern"),
            pytest.param("", True, id="empty_string"),
            pytest.param(
                TraversalDirection.FORWARD, True, id="str_enum_not_identifier"
            ),
            pytest.param(EX.knows, False, id="uriref"),
            pytest.param(None, False, id="none"),
            pytest.param(42, False, id="integer"),
            pytest.param([EX.Alice], False, id="list"),
            pytest.param(BNode(), False, id="bnode"),
            pytest.param(Literal("hello"), False, id="literal"),
        ],
    )
    def test_is_sparql_pattern(self, value, expected):
        assert _is_sparql_pattern(value) is expected


class TestPrepareAndValidate:
    """Unit tests for _prepare_and_validate."""

    def test_valid_select_query(self):
        """A well-formed SELECT with the required variable succeeds."""
        q = "SELECT DISTINCT ?start WHERE { ?start ex:knows ex:Bob }"
        prepared = _prepare_and_validate(q, NS, {"start"}, "test")
        assert prepared is not None

    def test_valid_ask_query(self):
        """A well-formed ASK with the required variable succeeds."""
        q = "ASK WHERE { ?end ex:role ex:Manager }"
        prepared = _prepare_and_validate(q, NS, {"end"}, "test")
        assert prepared is not None

    def test_missing_single_variable_raises(self):
        """Missing a required variable raises ValueError."""
        q = "SELECT ?x WHERE { ?x ex:knows ex:Bob }"
        with pytest.raises(ValueError, match="start"):
            _prepare_and_validate(q, NS, {"start"}, "Start pattern")

    def test_missing_multiple_variables_raises(self):
        """Missing multiple required variables lists them all."""
        q = "SELECT ?x WHERE { ?x ex:knows ?y }"
        with pytest.raises(ValueError, match="end") as exc_info:
            _prepare_and_validate(q, NS, {"start", "end"}, "Path pattern")
        assert "start" in str(exc_info.value)

    def test_extra_variables_allowed(self):
        """Extra variables beyond the required set are fine."""
        q = "SELECT * WHERE { ?start ex:knows ?end . ?start ex:worksAt ?company }"
        prepared = _prepare_and_validate(q, NS, {"start", "end"}, "test")
        assert prepared is not None

    def test_namespace_resolution(self):
        """Prefixes from ns_map are resolved correctly."""
        ns = {"ex": "http://example.org/"}
        q = "SELECT ?start WHERE { ?start ex:knows ex:Bob }"
        prepared = _prepare_and_validate(q, ns, {"start"}, "test")
        assert prepared is not None

    def test_error_message_includes_pattern(self):
        """Error message includes the original query string."""
        q = "SELECT ?x WHERE { ?x ex:knows ex:Bob }"
        with pytest.raises(ValueError, match=r"SELECT \?x WHERE"):
            _prepare_and_validate(q, NS, {"start"}, "test")

    def test_error_message_includes_label(self):
        """Error message includes the human-readable label."""
        q = "SELECT ?x WHERE { ?x ex:knows ex:Bob }"
        with pytest.raises(ValueError, match="My custom label"):
            _prepare_and_validate(q, NS, {"start"}, "My custom label")


class TestChooseDirection:
    """Unit tests for _choose_direction."""

    @pytest.mark.parametrize(
        "start, end, expected",
        [
            pytest.param(
                EX.Alice, None, TraversalDirection.FORWARD, id="id_start-none_end"
            ),
            pytest.param(
                None, EX.Alice, TraversalDirection.REVERSE, id="none_start-id_end"
            ),
            pytest.param(
                EX.Alice, EX.Bob, TraversalDirection.FORWARD, id="id_start-id_end-tie"
            ),
            pytest.param(
                None, None, TraversalDirection.FORWARD, id="none_start-none_end-tie"
            ),
            pytest.param(
                "?start ex:knows ex:Bob",
                EX.Dave,
                TraversalDirection.REVERSE,
                id="pattern_start-id_end",
            ),
            pytest.param(
                EX.Alice,
                "?end ex:role ex:Manager",
                TraversalDirection.FORWARD,
                id="id_start-pattern_end",
            ),
            pytest.param(
                [EX.Alice, EX.Bob],
                EX.Dave,
                TraversalDirection.REVERSE,
                id="iter_start-id_end",
            ),
            pytest.param(
                EX.Alice,
                [EX.Bob, EX.Carol],
                TraversalDirection.FORWARD,
                id="id_start-iter_end",
            ),
            pytest.param(
                "?start ex:dept ex:Eng",
                [EX.B, EX.C],
                TraversalDirection.REVERSE,
                id="pattern_start-iter_end",
            ),
            pytest.param(
                [EX.A, EX.B],
                "?end ex:role ex:Manager",
                TraversalDirection.FORWARD,
                id="iter_start-pattern_end",
            ),
            pytest.param(
                None,
                "?end ex:role ex:Manager",
                TraversalDirection.REVERSE,
                id="none_start-pattern_end",
            ),
            pytest.param(
                "?start ex:knows ex:Bob",
                None,
                TraversalDirection.FORWARD,
                id="pattern_start-none_end",
            ),
            pytest.param(
                None, [EX.A], TraversalDirection.REVERSE, id="none_start-iter_end"
            ),
            pytest.param(
                [EX.A], None, TraversalDirection.FORWARD, id="iter_start-none_end"
            ),
        ],
    )
    def test_direction_selection(self, start, end, expected):
        result = _choose_direction(start, end)
        assert result == expected
        assert isinstance(result, TraversalDirection)


class TestResolveOrigins:
    """Unit tests for _resolve_origins."""

    def test_single_identifier(self, linear_graph: Graph):
        """Single Identifier returns a singleton set."""
        result = _resolve_origins(EX.Alice, linear_graph, {}, "start")
        assert result == {EX.Alice}

    def test_iterable_of_identifiers(self, linear_graph: Graph):
        """Iterable of Identifiers is materialized into a set."""
        result = _resolve_origins([EX.Alice, EX.Bob], linear_graph, {}, "start")
        assert result == {EX.Alice, EX.Bob}

    def test_generator_consumed(self, linear_graph: Graph):
        """Generator is consumed into a set."""

        def gen():
            yield EX.Alice
            yield EX.Bob

        result = _resolve_origins(gen(), linear_graph, {}, "start")
        assert result == {EX.Alice, EX.Bob}

    def test_empty_iterable(self, linear_graph: Graph):
        """Empty iterable returns empty set."""
        result = _resolve_origins([], linear_graph, {}, "start")
        assert result == set()

    def test_none_returns_all_nodes(self):
        """None returns all subjects and objects in the graph."""
        g = Graph()
        g.bind("ex", EX)
        g.add((EX.A, EX.knows, EX.B))
        g.add((EX.B, EX.knows, EX.C))
        result = _resolve_origins(None, g, {}, "start")
        assert EX.A in result
        assert EX.B in result
        assert EX.C in result
        # EX.knows is a predicate, not a subject/object node
        assert EX.knows not in result

    def test_sparql_pattern(self, linear_graph: Graph):
        """SPARQL pattern string compiles and executes a SELECT query."""
        ns_map = _build_namespace_map(linear_graph, NS)
        pattern = "?start ex:knows ex:Bob"
        result = _resolve_origins(pattern, linear_graph, ns_map, "start")
        assert EX.Alice in result

    def test_sparql_pattern_no_matches(self):
        """SPARQL pattern that matches nothing returns empty set."""
        g = Graph()
        g.bind("ex", EX)
        g.add((EX.A, EX.knows, EX.B))
        ns_map = _build_namespace_map(g, NS)
        pattern = "?start ex:friendOf ex:B"
        result = _resolve_origins(pattern, g, ns_map, "start")
        assert result == set()

    def test_set_of_identifiers(self, linear_graph: Graph):
        """Set of Identifiers is returned as-is (materialized)."""
        result = _resolve_origins({EX.Alice, EX.Carol}, linear_graph, {}, "start")
        assert result == {EX.Alice, EX.Carol}

    def test_sparql_pattern_with_end_var(self):
        """SPARQL pattern with origin_var='end' (reverse direction) compiles correctly."""
        g = Graph()
        g.bind("ex", EX)
        g.add((EX.Alice, EX.knows, EX.Bob))
        g.add((EX.Carol, EX.knows, EX.Bob))
        ns_map = _build_namespace_map(g, NS)
        pattern = "?end ex:knows ex:Bob"
        result = _resolve_origins(pattern, g, ns_map, "end")
        assert EX.Alice in result
        assert EX.Carol in result

    def test_sparql_pattern_missing_variable_returns_empty(self):
        """SPARQL pattern not binding the origin variable returns empty set.

        When the user's pattern uses ?x instead of ?start, the compiled
        SELECT DISTINCT ?start query returns rows where ?start is unbound,
        which are filtered out, yielding an empty set.
        """
        g = Graph()
        g.bind("ex", EX)
        g.add((EX.A, EX.knows, EX.B))
        ns_map = _build_namespace_map(g, NS)
        result = _resolve_origins("?x ex:knows ex:B", g, ns_map, "start")
        assert result == set()


class TestBuildExpandFn:
    """Unit tests for _build_expand_fn."""

    @pytest.fixture()
    def simple_graph(self) -> Graph:
        g = Graph()
        g.bind("ex", EX)
        g.add((EX.A, EX.knows, EX.B))
        g.add((EX.A, EX.likes, EX.C))
        g.add((EX.B, EX.knows, EX.C))
        return g

    # --- Unbound path (path=None) ---

    def test_unbound_forward_yields_all_predicates(self, simple_graph: Graph):
        """path=None, forward: yields all (object, step) with edge set."""
        expand = _build_expand_fn(None, simple_graph, {}, forward=True)
        results = list(expand(EX.A))
        neighbors = {node for node, _ in results}
        assert EX.B in neighbors
        assert EX.C in neighbors
        # Each step should have an edge
        for _, step in results:
            assert step.edge is not None
            assert step.length == 1

    def test_unbound_reverse_yields_subjects(self, simple_graph: Graph):
        """path=None, reverse: yields subjects that point to the given node."""
        expand = _build_expand_fn(None, simple_graph, {}, forward=False)
        results = list(expand(EX.C))
        neighbors = {node for node, _ in results}
        assert EX.A in neighbors  # A -likes-> C
        assert EX.B in neighbors  # B -knows-> C
        for _, step in results:
            assert step.edge is not None

    def test_unbound_no_neighbors(self, simple_graph: Graph):
        """path=None on a node with no outgoing edges yields nothing."""
        expand = _build_expand_fn(None, simple_graph, {}, forward=True)
        results = list(expand(EX.C))
        assert results == []

    # --- URIRef path ---

    def test_uriref_forward(self, simple_graph: Graph):
        """URIRef path, forward: yields only objects matching that predicate."""
        expand = _build_expand_fn(EX.knows, simple_graph, {}, forward=True)
        results = list(expand(EX.A))
        neighbors = {node for node, _ in results}
        assert neighbors == {EX.B}
        for _, step in results:
            assert step.edge is None  # URIRef path doesn't set edge
            assert step.length == 1

    def test_uriref_reverse(self, simple_graph: Graph):
        """URIRef path, reverse: yields subjects with that predicate to the node."""
        expand = _build_expand_fn(EX.knows, simple_graph, {}, forward=False)
        results = list(expand(EX.B))
        neighbors = {node for node, _ in results}
        assert neighbors == {EX.A}

    def test_uriref_no_match(self, simple_graph: Graph):
        """URIRef path with no matching triples yields nothing."""
        expand = _build_expand_fn(EX.friendOf, simple_graph, {}, forward=True)
        results = list(expand(EX.A))
        assert results == []

    # --- Property path ---

    def test_property_path_forward(self):
        """rdflib Path object, forward: applies the full path as one step."""
        g = Graph()
        g.bind("ex", EX)
        g.add((EX.A, EX.knows, EX.B))
        g.add((EX.B, EX.likes, EX.C))
        expand = _build_expand_fn(EX.knows / EX.likes, g, {}, forward=True)
        results = list(expand(EX.A))
        neighbors = {node for node, _ in results}
        assert EX.C in neighbors

    def test_property_path_reverse(self):
        """rdflib Path object, reverse: applies the full path in reverse."""
        g = Graph()
        g.bind("ex", EX)
        g.add((EX.A, EX.knows, EX.B))
        g.add((EX.B, EX.likes, EX.C))
        expand = _build_expand_fn(EX.knows / EX.likes, g, {}, forward=False)
        results = list(expand(EX.C))
        neighbors = {node for node, _ in results}
        assert EX.A in neighbors

    # --- SPARQL pattern path ---

    def test_sparql_forward_basic(self, simple_graph: Graph):
        """SPARQL pattern, forward: binds ?start and reads ?end."""
        ns_map = _build_namespace_map(simple_graph, NS)
        expand = _build_expand_fn(
            "?start ex:knows ?end", simple_graph, ns_map, forward=True
        )
        results = list(expand(EX.A))
        neighbors = {node for node, _ in results}
        assert neighbors == {EX.B}

    def test_sparql_reverse(self, simple_graph: Graph):
        """SPARQL pattern, reverse: binds ?end and reads ?start."""
        ns_map = _build_namespace_map(simple_graph, NS)
        expand = _build_expand_fn(
            "?start ex:knows ?end", simple_graph, ns_map, forward=False
        )
        results = list(expand(EX.B))
        neighbors = {node for node, _ in results}
        assert neighbors == {EX.A}

    def test_sparql_extra_bindings(self):
        """SPARQL pattern with extra variables populates step.bindings."""
        g = Graph()
        g.bind("ex", EX)
        g.add((EX.A, EX.worksAt, EX.Acme))
        g.add((EX.B, EX.worksAt, EX.Acme))
        g.add((EX.A, EX.knows, EX.B))
        ns_map = _build_namespace_map(g, NS)
        pattern = "?start ex:worksAt ?company . ?end ex:worksAt ?company . ?start ex:knows ?end"
        expand = _build_expand_fn(pattern, g, ns_map, forward=True)
        results = list(expand(EX.A))
        assert len(results) >= 1
        _, step = results[0]
        assert step.bindings is not None
        assert "company" in step.bindings
        assert step.bindings["company"] == EX.Acme

    def test_sparql_with_length_variable(self):
        """SPARQL pattern binding ?length uses it as step weight."""
        g = Graph()
        g.bind("ex", EX)
        g.add((EX.e1, EX.fromNode, EX.A))
        g.add((EX.e1, EX.toNode, EX.B))
        g.add((EX.e1, EX.weight, Literal(5.0)))
        ns_map = _build_namespace_map(g, NS)
        pattern = (
            "?edge ex:fromNode ?start . ?edge ex:toNode ?end . ?edge ex:weight ?length"
        )
        expand = _build_expand_fn(pattern, g, ns_map, forward=True)
        results = list(expand(EX.A))
        assert len(results) == 1
        _, step = results[0]
        assert step.length == 5.0
        assert step.bindings is None or "length" not in step.bindings

    def test_sparql_with_length_and_extra_bindings(self):
        """SPARQL pattern binding ?length excludes it from bindings but keeps others."""
        g = Graph()
        g.bind("ex", EX)
        g.add((EX.e1, EX.fromNode, EX.A))
        g.add((EX.e1, EX.toNode, EX.B))
        g.add((EX.e1, EX.weight, Literal(5.0)))
        g.add((EX.e1, EX.label, Literal("highway")))
        ns_map = _build_namespace_map(g, NS)
        pattern = (
            "?edge ex:fromNode ?start . ?edge ex:toNode ?end . "
            "?edge ex:weight ?length . ?edge ex:label ?edgeLabel"
        )
        expand = _build_expand_fn(pattern, g, ns_map, forward=True)
        results = list(expand(EX.A))
        assert len(results) == 1
        _, step = results[0]
        assert step.length == 5.0
        assert step.bindings is not None
        assert "edgeLabel" in step.bindings
        assert "length" not in step.bindings

    def test_sparql_missing_start_variable_raises(self):
        """SPARQL pattern missing ?start raises ValueError."""
        g = Graph()
        g.bind("ex", EX)
        ns_map = _build_namespace_map(g, NS)
        with pytest.raises(ValueError, match="start"):
            _build_expand_fn("?x ex:knows ?end", g, ns_map, forward=True)

    def test_sparql_missing_end_variable_raises(self):
        """SPARQL pattern missing ?end raises ValueError."""
        g = Graph()
        g.bind("ex", EX)
        ns_map = _build_namespace_map(g, NS)
        with pytest.raises(ValueError, match="end"):
            _build_expand_fn("?start ex:knows ?x", g, ns_map, forward=True)


class TestBuildEndCheckFn:
    """Unit tests for _build_end_check_fn."""

    @pytest.fixture()
    def role_graph(self) -> Graph:
        g = Graph()
        g.bind("ex", EX)
        g.add((EX.Alice, EX.role, EX.Manager))
        g.add((EX.Bob, EX.role, EX.Engineer))
        g.add((EX.Carol, EX.role, EX.Manager))
        return g

    # --- None (unbound) ---

    def test_none_matches_everything(self, role_graph: Graph):
        """end_spec=None: every node is valid, known_end_nodes is None."""
        check_fn, known = _build_end_check_fn(None, role_graph, {}, "end")
        assert known is None
        assert check_fn(EX.Alice) is True
        assert check_fn(EX.Bob) is True
        assert check_fn(EX.Nonexistent) is True

    # --- Single Identifier ---

    def test_single_identifier_matches_only_that_node(self, role_graph: Graph):
        """end_spec=Identifier: only that node matches."""
        check_fn, known = _build_end_check_fn(EX.Alice, role_graph, {}, "end")
        assert known == frozenset({EX.Alice})
        assert check_fn(EX.Alice) is True
        assert check_fn(EX.Bob) is False

    # --- Iterable of Identifiers ---

    def test_iterable_matches_members(self, role_graph: Graph):
        """end_spec=iterable: members match, non-members don't."""
        check_fn, known = _build_end_check_fn(
            [EX.Alice, EX.Carol], role_graph, {}, "end"
        )
        assert known == frozenset({EX.Alice, EX.Carol})
        assert check_fn(EX.Alice) is True
        assert check_fn(EX.Carol) is True
        assert check_fn(EX.Bob) is False

    def test_empty_iterable_matches_nothing(self, role_graph: Graph):
        """end_spec=[]: no node matches."""
        check_fn, known = _build_end_check_fn([], role_graph, {}, "end")
        assert known == frozenset()
        assert check_fn(EX.Alice) is False

    def test_set_of_identifiers(self, role_graph: Graph):
        """end_spec=set: works like iterable."""
        check_fn, known = _build_end_check_fn({EX.Bob}, role_graph, {}, "end")
        assert known == frozenset({EX.Bob})
        assert check_fn(EX.Bob) is True
        assert check_fn(EX.Alice) is False

    # --- SPARQL pattern ---

    def test_sparql_pattern_matches(self, role_graph: Graph):
        """end_spec=str: ASK query validates matching nodes."""
        ns_map = _build_namespace_map(role_graph, NS)
        pattern = "?end ex:role ex:Manager"
        check_fn, known = _build_end_check_fn(pattern, role_graph, ns_map, "end")
        assert known is None  # SPARQL pattern → unknown end set
        assert check_fn(EX.Alice) is True  # Alice is a Manager
        assert check_fn(EX.Carol) is True  # Carol is a Manager
        assert check_fn(EX.Bob) is False  # Bob is an Engineer

    def test_sparql_pattern_no_matches(self, role_graph: Graph):
        """SPARQL pattern that matches no node returns False for all."""
        ns_map = _build_namespace_map(role_graph, NS)
        pattern = "?end ex:role ex:Director"
        check_fn, known = _build_end_check_fn(pattern, role_graph, ns_map, "end")
        assert known is None
        assert check_fn(EX.Alice) is False
        assert check_fn(EX.Bob) is False

    # --- known_end_nodes correctness ---

    def test_known_end_nodes_none_for_unbound(self, role_graph: Graph):
        """Unbound end → known_end_nodes is None."""
        _, known = _build_end_check_fn(None, role_graph, {}, "end")
        assert known is None

    def test_known_end_nodes_frozenset_for_identifier(self, role_graph: Graph):
        """Single Identifier → known_end_nodes is frozenset of that node."""
        _, known = _build_end_check_fn(EX.Alice, role_graph, {}, "end")
        assert isinstance(known, frozenset)
        assert known == frozenset({EX.Alice})

    def test_known_end_nodes_frozenset_for_iterable(self, role_graph: Graph):
        """Iterable → known_end_nodes is frozenset of those nodes."""
        _, known = _build_end_check_fn([EX.Alice, EX.Bob], role_graph, {}, "end")
        assert isinstance(known, frozenset)
        assert known == frozenset({EX.Alice, EX.Bob})

    def test_known_end_nodes_none_for_sparql(self, role_graph: Graph):
        """SPARQL pattern → known_end_nodes is None."""
        ns_map = _build_namespace_map(role_graph, NS)
        pattern = "?end ex:role ex:Manager"
        _, known = _build_end_check_fn(pattern, role_graph, ns_map, "end")
        assert known is None

    def test_sparql_pattern_with_start_var(self):
        """SPARQL pattern with end_var='start' (reverse direction) compiles correctly."""
        g = Graph()
        g.bind("ex", EX)
        g.add((EX.Alice, EX.dept, EX.Engineering))
        g.add((EX.Bob, EX.dept, EX.Sales))
        ns_map = _build_namespace_map(g, NS)
        pattern = "?start ex:dept ex:Engineering"
        check_fn, known = _build_end_check_fn(pattern, g, ns_map, "start")
        assert known is None
        assert check_fn(EX.Alice) is True
        assert check_fn(EX.Bob) is False

    def test_sparql_pattern_missing_variable_raises(self):
        """SPARQL pattern missing the required variable raises ValueError."""
        g = Graph()
        g.bind("ex", EX)
        ns_map = _build_namespace_map(g, NS)
        with pytest.raises(ValueError, match="end"):
            _build_end_check_fn("?x ex:role ex:Manager", g, ns_map, "end")


class TestBasicTraversal:
    """Fixed start, fixed predicate, fixed end — single and multiple paths."""

    def test_single_path(self, linear_graph: Graph):
        results = find_paths(linear_graph, start=EX.Alice, path=EX.knows, end=EX.Carol)
        assert len(results) == 1
        assert results[0].start == EX.Alice
        assert results[0].end == EX.Carol
        assert len(results[0].steps) == 2
        assert results[0].steps[-1].node == EX.Carol

    def test_multiple_paths(self, linear_graph: Graph):
        results = find_paths(
            linear_graph,
            start=EX.Alice,
            path=EX.knows,
            end=EX.Dave,
            shortest=False,
        )
        paths = _path_node_sets(results)
        assert ("Alice", "Bob", "Dave") in paths
        assert ("Alice", "Bob", "Carol", "Dave") in paths
        assert len(results) == 2

    def test_no_path_exists(self, linear_graph: Graph):
        results = find_paths(linear_graph, start=EX.Dave, path=EX.knows, end=EX.Alice)
        assert results == []

    def test_direct_neighbor(self, linear_graph: Graph):
        results = find_paths(linear_graph, start=EX.Alice, path=EX.knows, end=EX.Bob)
        assert len(results) == 1
        assert len(results[0].steps) == 1
        assert results[0].steps[0].node == EX.Bob


class TestShortestMode:
    """Verify only minimum-length paths returned; multiple shortest of same length."""

    def test_shortest_picks_shorter(self, linear_graph: Graph):
        results = find_paths(
            linear_graph,
            start=EX.Alice,
            path=EX.knows,
            end=EX.Dave,
        )
        assert len(results) == 1
        assert len(results[0].steps) == 2  # Alice -> Bob -> Dave

    def test_multiple_shortest_same_length(self, diamond_graph: Graph):
        results = find_paths(
            diamond_graph,
            start=EX.A,
            path=EX.knows,
            end=EX.D,
        )
        assert len(results) == 2
        for r in results:
            assert len(r.steps) == 2

    def test_shortest_zero_length(self, linear_graph: Graph):
        """When start == end, zero-length path is the shortest."""
        results = find_paths(
            linear_graph,
            start=EX.Alice,
            path=EX.knows,
            end=EX.Alice,
        )
        assert len(results) == 1
        assert results[0].steps == []

    def test_shortest_per_end_node(self):
        """shortest=True keeps the shortest path(s) per end node, not globally.

        Graph: A -knows-> B -knows-> C -knows-> D
                           B -knows-> D  (shortcut)

        With end=None and terminate_on_first_match=False:
        - Shortest to B is length 1 (A->B)
        - Shortest to C is length 2 (A->B->C)
        - Shortest to D is length 2 (A->B->D), NOT length 3 (A->B->C->D)
        """
        g = Graph()
        g.bind("ex", EX)
        g.add((EX.A, EX.knows, EX.B))
        g.add((EX.B, EX.knows, EX.C))
        g.add((EX.C, EX.knows, EX.D))
        g.add((EX.B, EX.knows, EX.D))

        results = find_paths(
            g,
            start=EX.A,
            path=EX.knows,
            end=None,
            shortest=True,
            terminate_on_first_match=False,
            max_length=10,
        )

        # Group results by end node
        by_end: dict = {}
        for r in results:
            by_end.setdefault(r.end, []).append(r)

        # A has zero-length path (shortest to self)
        assert len(by_end[EX.A][0].steps) == 0

        # B: shortest is length 1
        assert all(len(r.steps) == 1 for r in by_end[EX.B])

        # C: shortest is length 2
        assert all(len(r.steps) == 2 for r in by_end[EX.C])

        # D: shortest is length 2 (via B->D shortcut), NOT length 3
        assert all(len(r.steps) == 2 for r in by_end[EX.D])

    def test_shortest_does_not_stop_early(self):
        """BFS continues past first found path to find shortest to farther nodes.

        Graph: A -knows-> B -knows-> C
        With shortest=True, end=None, we should find paths to B AND C,
        not just stop after finding B.
        """
        g = Graph()
        g.bind("ex", EX)
        g.add((EX.A, EX.knows, EX.B))
        g.add((EX.B, EX.knows, EX.C))

        results = find_paths(
            g,
            start=EX.A,
            path=EX.knows,
            end=None,
            shortest=True,
            terminate_on_first_match=False,
            max_length=10,
        )

        ends = {r.end for r in results}
        assert EX.A in ends  # zero-length
        assert EX.B in ends  # length 1
        assert EX.C in ends  # length 2 — BFS didn't stop after finding B

    def test_shortest_multiple_same_length_per_end(self):
        """Multiple paths of same shortest length to same end are all kept.

        Diamond: A -> B -> D, A -> C -> D
        Both paths to D are length 2; both should be returned.
        """
        g = Graph()
        g.bind("ex", EX)
        g.add((EX.A, EX.knows, EX.B))
        g.add((EX.A, EX.knows, EX.C))
        g.add((EX.B, EX.knows, EX.D))
        g.add((EX.C, EX.knows, EX.D))

        results = find_paths(
            g,
            start=EX.A,
            path=EX.knows,
            end=EX.D,
            shortest=True,
        )

        assert len(results) == 2
        paths = _path_node_sets(results)
        assert ("A", "B", "D") in paths
        assert ("A", "C", "D") in paths


class TestUnboundPath:
    """Verify edge predicates captured in steps when path=None."""

    def test_edge_captured(self, linear_graph: Graph):
        results = find_paths(linear_graph, start=EX.Alice, path=None, end=EX.Bob)
        assert len(results) == 1
        step = results[0].steps[0]
        assert step.node == EX.Bob
        assert step.edge == EX.knows
        assert step.bindings is None

    def test_multi_predicate_edges(self, multi_pred_graph: Graph):
        results = find_paths(multi_pred_graph, start=EX.Alice, path=None, end=EX.Dave)
        assert len(results) >= 1
        # Path should be Alice -knows-> Bob -worksWith-> Carol -knows-> Dave
        r = results[0]
        edges = [s.edge for s in r.steps]
        assert EX.knows in edges
        assert EX.worksWith in edges


class TestQueryPath:
    """Verify extra bindings captured; multiple bindings produce distinct paths."""

    def test_extra_bindings_captured(self):
        g = Graph()
        g.bind("ex", EX)
        g.add((EX.Alice, EX.worksAt, EX.Acme))
        g.add((EX.Bob, EX.worksAt, EX.Acme))
        g.add((EX.Alice, EX.knows, EX.Bob))

        results = find_paths(
            g,
            start=EX.Alice,
            path="?start ex:worksAt ?company . ?end ex:worksAt ?company . ?start ex:knows ?end",
            end=EX.Bob,
            initNs=NS,
        )
        assert len(results) >= 1
        step = results[0].steps[0]
        assert step.bindings is not None
        assert "company" in step.bindings
        assert step.bindings["company"] == EX.Acme

    def test_no_extra_bindings_when_only_start_end(self):
        g = Graph()
        g.bind("ex", EX)
        g.add((EX.Alice, EX.knows, EX.Bob))

        results = find_paths(
            g,
            start=EX.Alice,
            path="?start ex:knows ?end",
            end=EX.Bob,
            initNs=NS,
        )
        assert len(results) == 1
        step = results[0].steps[0]
        # No extra variables beyond ?start and ?end
        assert step.bindings is None or step.bindings == {}


class TestPatternStart:
    """Verify eager evaluation of start pattern to set of start nodes."""

    def test_pattern_start_selects_correct_nodes(self, manager_graph: Graph):
        results = find_paths(
            manager_graph,
            start="?start ex:department ex:Engineering",
            path=EX.knows,
            end=EX.Dave,
            initNs=NS,
        )
        starts = {r.start for r in results}
        # Alice and Bob are in Engineering
        assert EX.Alice in starts or EX.Bob in starts
        # All results should end at Dave
        assert all(r.end == EX.Dave for r in results)

    def test_pattern_start_no_matches(self):
        g = Graph()
        g.bind("ex", EX)
        g.add((EX.Alice, EX.knows, EX.Bob))
        results = find_paths(
            g,
            start="?start ex:department ex:Engineering",
            path=EX.knows,
            end=EX.Bob,
            initNs=NS,
        )
        assert results == []


class TestPatternEnd:
    """Verify ASK-based filtering and terminate_on_first_match behavior."""

    def test_pattern_end_filters_correctly(self, manager_graph: Graph):
        results = find_paths(
            manager_graph,
            start=EX.Alice,
            path=EX.knows,
            end="?end ex:role ex:Manager",
            shortest=False,
            initNs=NS,
        )
        assert len(results) >= 1
        for r in results:
            assert r.end in (EX.Dave, EX.Carol)

    def test_terminate_on_first_match_true(self, manager_graph: Graph):
        """With terminate_on_first_match=True, each path stops at first Manager."""
        results = find_paths(
            manager_graph,
            start=EX.Alice,
            path=EX.knows,
            end="?end ex:role ex:Manager",
            shortest=False,
            terminate_on_first_match=True,
            initNs=NS,
        )
        # Should find Carol (via Bob) as the first Manager on that path
        # Should NOT continue past Carol to find Dave on the same path
        path_ends = {r.end for r in results}
        assert EX.Carol in path_ends

    def test_terminate_on_first_match_false(self, manager_graph: Graph):
        """With terminate_on_first_match=False, paths continue past Managers."""
        results = find_paths(
            manager_graph,
            start=EX.Alice,
            path=EX.knows,
            end="?end ex:role ex:Manager",
            shortest=False,
            terminate_on_first_match=False,
            initNs=NS,
        )
        path_ends = {r.end for r in results}
        # Should find both Carol and Dave as Managers
        assert EX.Carol in path_ends
        assert EX.Dave in path_ends


class TestReverseDirection:
    """Verify results are correct when BFS runs in reverse."""

    def test_unbound_start_fixed_end(self, linear_graph: Graph):
        """Unbound start + fixed end triggers reverse direction."""
        results = find_paths(
            linear_graph,
            start=None,
            path=EX.knows,
            end=EX.Dave,
        )
        # Shortest paths to Dave: Bob->Dave and Carol->Dave (length 1)
        # Plus zero-length Dave->Dave
        assert len(results) >= 1
        for r in results:
            assert r.end == EX.Dave

    def test_reverse_matches_forward(self, diamond_graph: Graph):
        """Forward and reverse should find the same paths."""
        forward = find_paths(
            diamond_graph,
            start=EX.A,
            path=EX.knows,
            end=EX.D,
            shortest=False,
        )
        # Pattern start triggers forward; pattern end with fixed start also forward
        # But None start + fixed end triggers reverse
        reverse = find_paths(
            diamond_graph,
            start=None,
            path=EX.knows,
            end=EX.D,
            shortest=False,
            max_length=2,
            terminate_on_first_match=False,
        )
        # Both should find A->B->D and A->C->D among results
        fwd_from_a = {tuple(_path_nodes(r)) for r in forward if r.start == EX.A}
        rev_from_a = {tuple(_path_nodes(r)) for r in reverse if r.start == EX.A}
        assert fwd_from_a == rev_from_a

    def test_pattern_start_fixed_end_reverses(self, manager_graph: Graph):
        """str start + Identifier end triggers reverse."""
        results = find_paths(
            manager_graph,
            start="?start ex:department ex:Engineering",
            path=EX.knows,
            end=EX.Dave,
            initNs=NS,
        )
        assert len(results) >= 1
        assert all(r.end == EX.Dave for r in results)


class TestCycleDetection:
    """Graph with cycles; verify no infinite loops; cyclic paths discarded."""

    def test_no_infinite_loop(self, cyclic_graph: Graph):
        """BFS on a cyclic graph terminates."""
        results = find_paths(
            cyclic_graph,
            start=EX.A,
            path=EX.knows,
            end=EX.C,
        )
        assert len(results) >= 1
        # A -> B -> C
        assert any(len(r.steps) == 2 for r in results)

    def test_cycle_not_revisited(self, cyclic_graph: Graph):
        """No path should visit the same node twice."""
        results = find_paths(
            cyclic_graph,
            start=EX.A,
            path=EX.knows,
            end=None,
            shortest=False,
            terminate_on_first_match=False,
            max_length=10,
        )
        for r in results:
            visited = [r.start] + [s.node for s in r.steps]
            assert len(visited) == len(
                set(visited)
            ), f"Duplicate node in path: {visited}"


class TestZeroLengthPaths:
    """Node is both start and end."""

    def test_fixed_start_equals_fixed_end(self, linear_graph: Graph):
        results = find_paths(linear_graph, start=EX.Alice, path=EX.knows, end=EX.Alice)
        assert len(results) == 1
        assert results[0].start == EX.Alice
        assert results[0].end == EX.Alice
        assert results[0].steps == []

    def test_zero_length_with_pattern_end(self, manager_graph: Graph):
        """Alice is in Engineering; if end pattern matches Alice, zero-length path."""
        results = find_paths(
            manager_graph,
            start=EX.Alice,
            path=EX.knows,
            end="?end ex:department ex:Engineering",
            initNs=NS,
        )
        zero_len = [r for r in results if r.steps == []]
        assert len(zero_len) == 1
        assert zero_len[0].start == EX.Alice
        assert zero_len[0].end == EX.Alice


class TestSelfLoops:
    """Triple (A, p, A) does not produce a path beyond zero-length."""

    def test_self_loop_no_extra_paths(self):
        g = Graph()
        g.bind("ex", EX)
        g.add((EX.A, EX.knows, EX.A))  # self-loop

        results = find_paths(g, start=EX.A, path=EX.knows, end=EX.A)
        # Only the zero-length path; the self-loop is a cycle
        assert len(results) == 1
        assert results[0].steps == []

    def test_self_loop_with_other_edges(self):
        g = Graph()
        g.bind("ex", EX)
        g.add((EX.A, EX.knows, EX.A))  # self-loop
        g.add((EX.A, EX.knows, EX.B))

        results = find_paths(g, start=EX.A, path=EX.knows, end=EX.B)
        assert len(results) == 1
        assert results[0].steps[0].node == EX.B


class TestMaxLength:
    """Verify max_length limits cumulative weighted path length."""

    def test_max_length_zero(self, linear_graph: Graph):
        """max_length=0 returns only zero-length paths."""
        results = find_paths(
            linear_graph,
            start=EX.Alice,
            path=EX.knows,
            end=EX.Alice,
            max_length=0,
        )
        assert len(results) == 1
        assert results[0].steps == []

    def test_max_length_zero_no_match(self, linear_graph: Graph):
        """max_length=0 with different start/end returns nothing."""
        results = find_paths(
            linear_graph,
            start=EX.Alice,
            path=EX.knows,
            end=EX.Dave,
            max_length=0,
        )
        assert results == []

    def test_max_length_limits_path_length(self, linear_graph: Graph):
        """max_length=1 should not find Alice->Bob->Dave (cumulative length 2)."""
        results = find_paths(
            linear_graph,
            start=EX.Alice,
            path=EX.knows,
            end=EX.Dave,
            max_length=1,
        )
        assert results == []

    def test_max_length_allows_exact_length(self, linear_graph: Graph):
        """max_length=2 should find Alice->Bob->Dave (cumulative length exactly 2)."""
        results = find_paths(
            linear_graph,
            start=EX.Alice,
            path=EX.knows,
            end=EX.Dave,
            max_length=2,
        )
        assert len(results) == 1
        assert len(results[0].steps) == 2

    def test_max_length_negative_raises(self, linear_graph: Graph):
        with pytest.raises(ValueError, match="non-negative"):
            find_paths(
                linear_graph,
                start=EX.Alice,
                path=EX.knows,
                end=EX.Dave,
                max_length=-1,
            )

    def test_max_length_with_weighted_paths(self):
        """max_length applies to cumulative weighted length, not hop count.

        Graph (reified edges):
            e1: A -> B, weight 3
            e2: B -> C, weight 4
            e3: A -> C, weight 10

        max_length=7 should find A->B->C (weight 3+4=7) but NOT A->C (weight 10).
        """
        g = Graph()
        g.bind("ex", EX)
        g.add((EX.e1, EX.fromNode, EX.A))
        g.add((EX.e1, EX.toNode, EX.B))
        g.add((EX.e1, EX.weight, Literal(3.0)))
        g.add((EX.e2, EX.fromNode, EX.B))
        g.add((EX.e2, EX.toNode, EX.C))
        g.add((EX.e2, EX.weight, Literal(4.0)))
        g.add((EX.e3, EX.fromNode, EX.A))
        g.add((EX.e3, EX.toNode, EX.C))
        g.add((EX.e3, EX.weight, Literal(10.0)))

        path_pattern = (
            "?edge ex:fromNode ?start . ?edge ex:toNode ?end . ?edge ex:weight ?length"
        )

        results = find_paths(
            g,
            start=EX.A,
            path=path_pattern,
            end=EX.C,
            shortest=False,
            terminate_on_first_match=False,
            max_length=7,
            initNs=NS,
        )
        # Only the 2-hop path (weight 7) should be found; the 1-hop (weight 10) is excluded
        assert len(results) == 1
        assert results[0].length == 7.0
        assert len(results[0].steps) == 2

    def test_max_length_excludes_shorter_hop_heavier_path(self):
        """A 1-hop path with weight > max_length is excluded even though it has fewer hops.

        Graph (reified edges):
            e1: A -> B, weight 100

        max_length=50 should NOT find A->B (weight 100 > 50).
        """
        g = Graph()
        g.bind("ex", EX)
        g.add((EX.e1, EX.fromNode, EX.A))
        g.add((EX.e1, EX.toNode, EX.B))
        g.add((EX.e1, EX.weight, Literal(100.0)))

        path_pattern = (
            "?edge ex:fromNode ?start . ?edge ex:toNode ?end . ?edge ex:weight ?length"
        )

        results = find_paths(
            g,
            start=EX.A,
            path=path_pattern,
            end=EX.B,
            max_length=50,
            initNs=NS,
        )
        assert results == []

    def test_max_length_float_value(self):
        """max_length accepts float values for weighted path limits.

        Graph (reified edges):
            e1: A -> B, weight 2.5
            e2: B -> C, weight 2.5

        max_length=5.0 should find A->B->C (weight 5.0, exactly at limit).
        max_length=4.9 should NOT find A->B->C (weight 5.0 > 4.9).
        """
        g = Graph()
        g.bind("ex", EX)
        g.add((EX.e1, EX.fromNode, EX.A))
        g.add((EX.e1, EX.toNode, EX.B))
        g.add((EX.e1, EX.weight, Literal(2.5)))
        g.add((EX.e2, EX.fromNode, EX.B))
        g.add((EX.e2, EX.toNode, EX.C))
        g.add((EX.e2, EX.weight, Literal(2.5)))

        path_pattern = (
            "?edge ex:fromNode ?start . ?edge ex:toNode ?end . ?edge ex:weight ?length"
        )

        # Exactly at limit: should be found
        results = find_paths(
            g,
            start=EX.A,
            path=path_pattern,
            end=EX.C,
            shortest=False,
            terminate_on_first_match=False,
            max_length=5.0,
            initNs=NS,
        )
        assert len(results) == 1
        assert results[0].length == 5.0

        # Just below limit: should NOT be found
        results = find_paths(
            g,
            start=EX.A,
            path=path_pattern,
            end=EX.C,
            shortest=False,
            terminate_on_first_match=False,
            max_length=4.9,
            initNs=NS,
        )
        assert results == []

    def test_max_length_unweighted_equivalent_to_hop_count(self, linear_graph: Graph):
        """For unweighted paths, max_length is equivalent to hop count.

        Graph: Alice -> Bob -> Carol -> Dave, plus Bob -> Dave shortcut.

        max_length=3, shortest=False: should find all paths with <= 3 hops.
        """
        results = find_paths(
            linear_graph,
            start=EX.Alice,
            path=EX.knows,
            end=EX.Dave,
            shortest=False,
            max_length=3,
        )
        # Both Alice->Bob->Dave (2 hops) and Alice->Bob->Carol->Dave (3 hops)
        assert len(results) == 2
        lengths = sorted(r.length for r in results)
        assert lengths == [2, 3]


class TestEmptyGraph:
    """Returns [] for empty graph."""

    def test_empty_graph_returns_empty(self):
        g = Graph()
        results = find_paths(g, start=EX.Alice, path=EX.knows, end=EX.Bob)
        assert results == []

    def test_empty_graph_zero_length(self):
        """Even with start==end, empty graph has no nodes to validate."""
        g = Graph()
        results = find_paths(g, start=EX.Alice, path=EX.knows, end=EX.Alice)
        # Alice is a fixed Identifier, so zero-length path is still valid
        assert len(results) == 1
        assert results[0].steps == []


class TestUnboundStartEnd:
    """Produces all acyclic paths (test with small graph)."""

    def test_all_paths_small_graph(self):
        g = Graph()
        g.bind("ex", EX)
        g.add((EX.A, EX.knows, EX.B))
        g.add((EX.B, EX.knows, EX.C))

        results = find_paths(
            g,
            start=None,
            path=EX.knows,
            end=None,
            terminate_on_first_match=False,
            max_length=5,
        )
        # Should include paths from all nodes
        starts = {r.start for r in results}
        assert EX.A in starts
        assert EX.B in starts

    def test_fully_unbound_raises(self):
        g = Graph()
        with pytest.raises(ValueError, match="(?i)at least one"):
            find_paths(g)


class TestPropertyPaths:
    """Sequence, alternative, inverse paths."""

    def test_sequence_path(self):
        g = Graph()
        g.bind("ex", EX)
        g.add((EX.Alice, EX.knows, EX.Bob))
        g.add((EX.Bob, EX.friendOf, EX.Carol))

        results = find_paths(
            g, start=EX.Alice, path=EX.knows / EX.friendOf, end=EX.Carol
        )
        assert len(results) == 1
        assert results[0].steps[0].node == EX.Carol
        assert results[0].steps[0].edge is None  # property path, no edge

    def test_alternative_path(self):
        g = Graph()
        g.bind("ex", EX)
        g.add((EX.Alice, EX.knows, EX.Bob))
        g.add((EX.Alice, EX.friendOf, EX.Carol))

        results = find_paths(
            g,
            start=EX.Alice,
            path=EX.knows | EX.friendOf,
            end=None,
            shortest=False,
        )
        ends = {r.end for r in results}
        assert EX.Alice in ends  # zero-length
        assert EX.Bob in ends
        assert EX.Carol in ends

    def test_inverse_path(self):
        g = Graph()
        g.bind("ex", EX)
        g.add((EX.Alice, EX.knows, EX.Bob))

        results = find_paths(g, start=EX.Bob, path=~EX.knows, end=EX.Alice)
        assert len(results) == 1
        assert results[0].steps[0].node == EX.Alice


class TestInitNs:
    """Verify prefix resolution in pattern strings."""

    def test_initns_resolves_prefixes(self, linear_graph: Graph):
        results = find_paths(
            linear_graph,
            start="?start ex:knows ex:Bob",
            path=EX.knows,
            end=EX.Dave,
            initNs={"ex": "http://example.org/"},
        )
        assert len(results) >= 1

    def test_initns_overrides_graph_ns(self):
        """initNs takes precedence over graph namespace_manager."""
        g = Graph()
        other = Namespace("http://other.org/")
        g.bind("ex", other)  # graph binds ex to wrong namespace
        g.add((EX.Alice, EX.knows, EX.Bob))

        results = find_paths(
            g,
            start="?start ex:knows ex:Bob",
            path=EX.knows,
            end=EX.Bob,
            initNs={"ex": "http://example.org/"},  # override
        )
        assert len(results) == 1


class TestBlankNodes:
    """BNodes as start, end, intermediate."""

    def test_bnode_as_intermediate(self):
        g = Graph()
        g.bind("ex", EX)
        b = BNode()
        g.add((EX.Alice, EX.knows, b))
        g.add((b, EX.knows, EX.Bob))

        results = find_paths(g, start=EX.Alice, path=EX.knows, end=EX.Bob)
        assert len(results) == 1
        assert results[0].steps[0].node == b
        assert results[0].steps[1].node == EX.Bob

    def test_bnode_as_start(self):
        g = Graph()
        g.bind("ex", EX)
        b = BNode()
        g.add((b, EX.knows, EX.Alice))

        results = find_paths(g, start=b, path=EX.knows, end=EX.Alice)
        assert len(results) == 1
        assert results[0].start == b

    def test_bnode_as_end(self):
        g = Graph()
        g.bind("ex", EX)
        b = BNode()
        g.add((EX.Alice, EX.knows, b))

        results = find_paths(g, start=EX.Alice, path=EX.knows, end=b)
        assert len(results) == 1
        assert results[0].end == b


class TestErrorHandling:
    """Validate error conditions."""

    def test_start_pattern_missing_variable(self):
        g = Graph()
        with pytest.raises(ValueError, match="start"):
            find_paths(
                g,
                start="?x ex:knows ex:Bob",
                path=EX.knows,
                end=EX.Bob,
                initNs=NS,
            )

    def test_end_pattern_missing_variable(self):
        g = Graph()
        with pytest.raises(ValueError, match="end"):
            find_paths(
                g,
                start=EX.Alice,
                path=EX.knows,
                end="?x ex:role ex:Manager",
                initNs=NS,
            )

    def test_path_pattern_missing_start(self):
        g = Graph()
        with pytest.raises(ValueError, match="start"):
            find_paths(
                g,
                start=EX.Alice,
                path="?x ex:knows ?end",
                end=EX.Bob,
                initNs=NS,
            )

    def test_path_pattern_missing_end(self):
        g = Graph()
        with pytest.raises(ValueError, match="end"):
            find_paths(
                g,
                start=EX.Alice,
                path="?start ex:knows ?x",
                end=EX.Bob,
                initNs=NS,
            )


class TestIterableStartEnd:
    """start and end accept an iterable of Identifiers."""

    def test_list_start(self, linear_graph: Graph):
        """Pass a list of start nodes."""
        results = find_paths(
            linear_graph,
            start=[EX.Alice, EX.Bob],
            path=EX.knows,
            end=EX.Dave,
            shortest=False,
            terminate_on_first_match=False,
        )
        starts = {r.start for r in results}
        assert EX.Alice in starts
        assert EX.Bob in starts
        assert all(r.end == EX.Dave for r in results)

    def test_set_start(self, linear_graph: Graph):
        """Pass a set of start nodes."""
        results = find_paths(
            linear_graph,
            start={EX.Bob, EX.Carol},
            path=EX.knows,
            end=EX.Dave,
        )
        starts = {r.start for r in results}
        # Both Bob and Carol can reach Dave
        assert starts <= {EX.Bob, EX.Carol}
        assert len(results) >= 2

    def test_list_end(self, linear_graph: Graph):
        """Pass a list of end nodes."""
        results = find_paths(
            linear_graph,
            start=EX.Alice,
            path=EX.knows,
            end=[EX.Bob, EX.Carol],
            terminate_on_first_match=False,
        )
        ends = {r.end for r in results}
        assert EX.Bob in ends
        assert EX.Carol in ends

    def test_set_end(self, linear_graph: Graph):
        """Pass a set of end nodes."""
        results = find_paths(
            linear_graph,
            start=EX.Alice,
            path=EX.knows,
            end={EX.Bob, EX.Dave},
            terminate_on_first_match=False,
        )
        ends = {r.end for r in results}
        assert EX.Bob in ends
        assert EX.Dave in ends

    def test_iterable_start_direction(self):
        """Iterable start + fixed end should go forward (iterable < single Identifier)."""
        g = Graph()
        g.bind("ex", EX)
        g.add((EX.A, EX.knows, EX.C))
        g.add((EX.B, EX.knows, EX.C))

        results = find_paths(
            g,
            start=[EX.A, EX.B],
            path=EX.knows,
            end=EX.C,
        )
        assert len(results) == 2
        starts = {r.start for r in results}
        assert starts == {EX.A, EX.B}

    def test_iterable_end_reverses_over_pattern(self):
        """Iterable end is more specific than pattern start, so should reverse."""
        g = Graph()
        g.bind("ex", EX)
        g.add((EX.A, EX.knows, EX.B))
        g.add((EX.A, EX.knows, EX.C))
        g.add((EX.A, EX.dept, EX.Eng))

        results = find_paths(
            g,
            start="?start ex:dept ex:Eng",
            path=EX.knows,
            end=[EX.B, EX.C],
            initNs=NS,
        )
        ends = {r.end for r in results}
        assert EX.B in ends
        assert EX.C in ends

    def test_generator_start(self, linear_graph: Graph):
        """Generators are consumed once and work as start."""

        def gen():
            yield EX.Alice
            yield EX.Bob

        results = find_paths(
            linear_graph,
            start=gen(),
            path=EX.knows,
            end=EX.Dave,
            shortest=False,
            terminate_on_first_match=False,
        )
        starts = {r.start for r in results}
        assert EX.Alice in starts
        assert EX.Bob in starts

    def test_empty_iterable_start(self, linear_graph: Graph):
        """Empty iterable start returns no results."""
        results = find_paths(
            linear_graph,
            start=[],
            path=EX.knows,
            end=EX.Dave,
        )
        assert results == []

    def test_empty_iterable_end(self, linear_graph: Graph):
        """Empty iterable end returns no results (no valid end nodes)."""
        results = find_paths(
            linear_graph,
            start=EX.Alice,
            path=EX.knows,
            end=[],
            shortest=False,
            terminate_on_first_match=False,
            max_length=3,
        )
        assert results == []


class TestShortestPruning:
    """Verify the pruning optimization when shortest=True and end nodes are known."""

    def test_pruning_single_end_node(self):
        """With a single known end node, paths longer than the shortest are pruned.

        Graph: A -> B -> C -> D -> E
                    B -> E  (shortcut, length 2 from A)

        Shortest path A->E is length 2 (A->B->E).
        The path A->B->C->D->E (length 4) should be pruned and not appear
        even with shortest=False-like BFS exploration, because the pruning
        discards partial paths longer than the known shortest.
        """
        g = Graph()
        g.bind("ex", EX)
        g.add((EX.A, EX.knows, EX.B))
        g.add((EX.B, EX.knows, EX.C))
        g.add((EX.C, EX.knows, EX.D))
        g.add((EX.D, EX.knows, EX.E))
        g.add((EX.B, EX.knows, EX.E))  # shortcut

        results = find_paths(
            g,
            start=EX.A,
            path=EX.knows,
            end=EX.E,
            shortest=True,
        )
        assert len(results) == 1
        assert len(results[0].steps) == 2  # A -> B -> E

    def test_pruning_multiple_end_nodes(self):
        """With multiple known end nodes, pruning activates once all are found.

        Graph: A -> B -> C -> D
                    B -> D  (shortcut)

        end=[C, D]:
        - Shortest to C is length 2 (A->B->C)
        - Shortest to D is length 2 (A->B->D)
        - max shortest = 2
        - Partial paths of length > 2 are pruned, so A->B->C->D (length 3)
          is never explored.
        """
        g = Graph()
        g.bind("ex", EX)
        g.add((EX.A, EX.knows, EX.B))
        g.add((EX.B, EX.knows, EX.C))
        g.add((EX.C, EX.knows, EX.D))
        g.add((EX.B, EX.knows, EX.D))  # shortcut

        results = find_paths(
            g,
            start=EX.A,
            path=EX.knows,
            end=[EX.C, EX.D],
            shortest=True,
            terminate_on_first_match=False,
        )
        # Should find shortest to C (length 2) and shortest to D (length 2)
        by_end: dict = {}
        for r in results:
            by_end.setdefault(r.end, []).append(r)

        assert all(len(r.steps) == 2 for r in by_end[EX.C])
        assert all(len(r.steps) == 2 for r in by_end[EX.D])

    def test_pruning_preserves_ties(self):
        """Pruning must not discard paths of equal length to the same end.

        Diamond: A -> B -> D, A -> C -> D
        Both paths to D are length 2; both must be returned.
        """
        g = Graph()
        g.bind("ex", EX)
        g.add((EX.A, EX.knows, EX.B))
        g.add((EX.A, EX.knows, EX.C))
        g.add((EX.B, EX.knows, EX.D))
        g.add((EX.C, EX.knows, EX.D))

        results = find_paths(
            g,
            start=EX.A,
            path=EX.knows,
            end=EX.D,
            shortest=True,
        )
        assert len(results) == 2
        paths = _path_node_sets(results)
        assert ("A", "B", "D") in paths
        assert ("A", "C", "D") in paths

    def test_pruning_with_set_end(self):
        """Pruning works when end is a set of Identifiers.

        Graph: A -> B -> C -> D -> E
                              D -> F

        end={E, F}:
        - Shortest to E is length 4 (A->B->C->D->E)
        - Shortest to F is length 4 (A->B->C->D->F)
        - max shortest = 4
        - Partial paths of length > 4 are pruned.
        """
        g = Graph()
        g.bind("ex", EX)
        g.add((EX.A, EX.knows, EX.B))
        g.add((EX.B, EX.knows, EX.C))
        g.add((EX.C, EX.knows, EX.D))
        g.add((EX.D, EX.knows, EX.E))
        g.add((EX.D, EX.knows, EX.F))

        results = find_paths(
            g,
            start=EX.A,
            path=EX.knows,
            end={EX.E, EX.F},
            shortest=True,
            terminate_on_first_match=False,
        )
        ends = {r.end for r in results}
        assert EX.E in ends
        assert EX.F in ends
        assert all(len(r.steps) == 4 for r in results)

    def test_pruning_not_active_for_pattern_end(self):
        """Pruning is NOT active when end is a SPARQL pattern (unknown set).

        This test verifies correctness — the optimization should be skipped
        for SPARQL pattern ends since the full set of end nodes is not known.
        """
        g = Graph()
        g.bind("ex", EX)
        g.add((EX.A, EX.knows, EX.B))
        g.add((EX.B, EX.knows, EX.C))
        g.add((EX.B, EX.role, EX.Manager))
        g.add((EX.C, EX.role, EX.Manager))

        results = find_paths(
            g,
            start=EX.A,
            path=EX.knows,
            end="?end ex:role ex:Manager",
            shortest=True,
            terminate_on_first_match=False,
            initNs=NS,
        )
        ends = {r.end for r in results}
        # Both B and C are Managers; shortest to B is 1, shortest to C is 2
        assert EX.B in ends
        assert EX.C in ends

    def test_pruning_not_active_for_unbound_end(self):
        """Pruning is NOT active when end is None (unbound).

        All reachable nodes should still be found.
        """
        g = Graph()
        g.bind("ex", EX)
        g.add((EX.A, EX.knows, EX.B))
        g.add((EX.B, EX.knows, EX.C))

        results = find_paths(
            g,
            start=EX.A,
            path=EX.knows,
            end=None,
            shortest=True,
            terminate_on_first_match=False,
            max_length=5,
        )
        ends = {r.end for r in results}
        assert EX.A in ends  # zero-length
        assert EX.B in ends
        assert EX.C in ends

    def test_pruning_with_asymmetric_shortest_lengths(self):
        """End nodes at different depths; pruning uses the max shortest length.

        Graph: A -> B -> C -> D
                         C -> E

        end=[B, E]:
        - Shortest to B is length 1 (A->B)
        - Shortest to E is length 3 (A->B->C->E)
        - max shortest = 3
        - Partial paths of length > 3 are pruned.
        - But paths of length <= 3 are NOT pruned, so A->B->C->D (length 3)
          is still explored (though D is not a valid end, so no result).
        """
        g = Graph()
        g.bind("ex", EX)
        g.add((EX.A, EX.knows, EX.B))
        g.add((EX.B, EX.knows, EX.C))
        g.add((EX.C, EX.knows, EX.D))
        g.add((EX.C, EX.knows, EX.E))

        results = find_paths(
            g,
            start=EX.A,
            path=EX.knows,
            end=[EX.B, EX.E],
            shortest=True,
            terminate_on_first_match=False,
        )
        by_end: dict = {}
        for r in results:
            by_end.setdefault(r.end, []).append(r)

        assert len(by_end[EX.B]) == 1
        assert len(by_end[EX.B][0].steps) == 1

        assert len(by_end[EX.E]) == 1
        assert len(by_end[EX.E][0].steps) == 3

    def test_pruning_with_zero_length_end(self):
        """When start is also a known end node, zero-length path is found.

        Graph: A -> B -> C
        end=[A, C]:
        - Shortest to A is 0 (zero-length)
        - Shortest to C is 2
        - max shortest = 2
        - Pruning activates after both are found.
        """
        g = Graph()
        g.bind("ex", EX)
        g.add((EX.A, EX.knows, EX.B))
        g.add((EX.B, EX.knows, EX.C))

        results = find_paths(
            g,
            start=EX.A,
            path=EX.knows,
            end=[EX.A, EX.C],
            shortest=True,
            terminate_on_first_match=False,
        )
        by_end: dict = {}
        for r in results:
            by_end.setdefault(r.end, []).append(r)

        assert len(by_end[EX.A]) == 1
        assert by_end[EX.A][0].steps == []  # zero-length

        assert len(by_end[EX.C]) == 1
        assert len(by_end[EX.C][0].steps) == 2


class TestWeightedLength:
    """Verify PathStep.length, PathResult.length, and shortest-path logic
    when a SPARQL path pattern binds ?length."""

    def test_step_length_default_is_1_for_uriref(self):
        """Non-SPARQL paths always produce steps with length=1."""
        g = Graph()
        g.bind("ex", EX)
        g.add((EX.A, EX.knows, EX.B))

        results = find_paths(g, start=EX.A, path=EX.knows, end=EX.B)
        assert len(results) == 1
        assert results[0].steps[0].length == 1
        assert results[0].length == 1

    def test_step_length_default_is_1_for_unbound(self):
        """Unbound path (path=None) always produces steps with length=1."""
        g = Graph()
        g.bind("ex", EX)
        g.add((EX.A, EX.knows, EX.B))

        results = find_paths(g, start=EX.A, path=None, end=EX.B)
        assert len(results) == 1
        assert results[0].steps[0].length == 1
        assert results[0].steps[0].edge == EX.knows
        assert results[0].length == 1

    def test_step_length_default_is_1_for_sparql_without_length_var(self):
        """SPARQL path without ?length produces steps with length=1."""
        g = Graph()
        g.bind("ex", EX)
        g.add((EX.A, EX.knows, EX.B))

        results = find_paths(
            g,
            start=EX.A,
            path="?start ex:knows ?end",
            end=EX.B,
            initNs=NS,
        )
        assert len(results) == 1
        assert results[0].steps[0].length == 1
        assert results[0].length == 1

    def test_step_length_from_length_variable(self):
        """SPARQL path binding ?length uses that value as step length."""
        g = Graph()
        g.bind("ex", EX)
        g.add((EX.A, EX.connectsTo, EX.B))
        g.add((EX.A, EX.distance, Literal(5.0)))

        results = find_paths(
            g,
            start=EX.A,
            path="?start ex:connectsTo ?end . ?start ex:distance ?length",
            end=EX.B,
            initNs=NS,
        )
        assert len(results) == 1
        assert results[0].steps[0].length == 5.0
        assert results[0].length == 5.0
        # ?length should NOT appear in bindings
        step = results[0].steps[0]
        assert step.bindings is None or "length" not in step.bindings

    def test_cumulative_length_across_steps(self):
        """PathResult.length is the sum of step lengths."""
        g = Graph()
        g.bind("ex", EX)
        g.add((EX.A, EX.connectsTo, EX.B))
        g.add((EX.A, EX.distance, Literal(3.0)))
        g.add((EX.B, EX.connectsTo, EX.C))
        g.add((EX.B, EX.distance, Literal(7.0)))

        results = find_paths(
            g,
            start=EX.A,
            path="?start ex:connectsTo ?end . ?start ex:distance ?length",
            end=EX.C,
            shortest=False,
            initNs=NS,
        )
        assert len(results) == 1
        assert results[0].steps[0].length == 3.0
        assert results[0].steps[1].length == 7.0
        assert results[0].length == 10.0

    def test_shortest_uses_weighted_length(self):
        """shortest=True picks the path with lower cumulative weighted length,
        even if it has more hops.

        Graph:
            A -connectsTo-> B (distance 10)
            A -connectsTo-> C (distance 1)
            C -connectsTo-> B (distance 2)

        Two paths A->B:
            Direct:  A->B, length=10 (1 hop)
            Via C:   A->C->B, length=1+2=3 (2 hops)

        shortest=True should pick the 2-hop path (length 3).
        """
        g = Graph()
        g.bind("ex", EX)
        g.add((EX.A, EX.connectsTo, EX.B))
        g.add((EX.A, EX.distance, Literal(10.0)))
        g.add((EX.A, EX.connectsTo, EX.C))
        # A's distance is already 10 for A->B, but we need per-edge weights.
        # Use a reified-edge pattern instead:
        # Edge triples: (edge, from, A), (edge, to, B), (edge, weight, 10)
        g2 = Graph()
        g2.bind("ex", EX)
        # Edge e1: A -> B, weight 10
        g2.add((EX.e1, EX.fromNode, EX.A))
        g2.add((EX.e1, EX.toNode, EX.B))
        g2.add((EX.e1, EX.weight, Literal(10.0)))
        # Edge e2: A -> C, weight 1
        g2.add((EX.e2, EX.fromNode, EX.A))
        g2.add((EX.e2, EX.toNode, EX.C))
        g2.add((EX.e2, EX.weight, Literal(1.0)))
        # Edge e3: C -> B, weight 2
        g2.add((EX.e3, EX.fromNode, EX.C))
        g2.add((EX.e3, EX.toNode, EX.B))
        g2.add((EX.e3, EX.weight, Literal(2.0)))

        path_pattern = (
            "?edge ex:fromNode ?start . ?edge ex:toNode ?end . ?edge ex:weight ?length"
        )

        results = find_paths(
            g2,
            start=EX.A,
            path=path_pattern,
            end=EX.B,
            shortest=True,
            terminate_on_first_match=False,
            initNs=NS,
        )
        # Should pick A->C->B (length 3) over A->B (length 10)
        assert len(results) == 1
        assert results[0].length == 3.0
        assert len(results[0].steps) == 2  # 2 hops

    def test_shortest_all_paths_with_weights(self):
        """shortest=False returns all paths; each has correct weighted length."""
        g = Graph()
        g.bind("ex", EX)
        # Edge e1: A -> B, weight 10
        g.add((EX.e1, EX.fromNode, EX.A))
        g.add((EX.e1, EX.toNode, EX.B))
        g.add((EX.e1, EX.weight, Literal(10.0)))
        # Edge e2: A -> C, weight 1
        g.add((EX.e2, EX.fromNode, EX.A))
        g.add((EX.e2, EX.toNode, EX.C))
        g.add((EX.e2, EX.weight, Literal(1.0)))
        # Edge e3: C -> B, weight 2
        g.add((EX.e3, EX.fromNode, EX.C))
        g.add((EX.e3, EX.toNode, EX.B))
        g.add((EX.e3, EX.weight, Literal(2.0)))

        path_pattern = (
            "?edge ex:fromNode ?start . ?edge ex:toNode ?end . ?edge ex:weight ?length"
        )

        results = find_paths(
            g,
            start=EX.A,
            path=path_pattern,
            end=EX.B,
            shortest=False,
            terminate_on_first_match=False,
            initNs=NS,
        )
        lengths = sorted(r.length for r in results)
        assert 3.0 in lengths  # A->C->B
        assert 10.0 in lengths  # A->B

    def test_zero_length_path_has_length_zero(self):
        """Zero-length path (start==end) has length=0."""
        g = Graph()
        g.bind("ex", EX)
        g.add((EX.A, EX.knows, EX.B))

        results = find_paths(g, start=EX.A, path=EX.knows, end=EX.A)
        assert len(results) == 1
        assert results[0].length == 0
        assert results[0].steps == []

    def test_length_not_in_bindings(self):
        """?length is consumed by the length field and excluded from bindings."""
        g = Graph()
        g.bind("ex", EX)
        g.add((EX.e1, EX.fromNode, EX.A))
        g.add((EX.e1, EX.toNode, EX.B))
        g.add((EX.e1, EX.weight, Literal(5.0)))
        g.add((EX.e1, EX.label, Literal("highway")))

        path_pattern = (
            "?edge ex:fromNode ?start . "
            "?edge ex:toNode ?end . "
            "?edge ex:weight ?length . "
            "?edge ex:label ?edgeLabel"
        )

        results = find_paths(
            g,
            start=EX.A,
            path=path_pattern,
            end=EX.B,
            initNs=NS,
        )
        assert len(results) == 1
        step = results[0].steps[0]
        assert step.length == 5.0
        assert step.bindings is not None
        assert "edgeLabel" in step.bindings
        assert "length" not in step.bindings

    def test_path_result_length_matches_step_sum(self):
        """PathResult.length always equals sum of step lengths."""
        g = Graph()
        g.bind("ex", EX)
        g.add((EX.A, EX.knows, EX.B))
        g.add((EX.B, EX.knows, EX.C))
        g.add((EX.C, EX.knows, EX.D))

        results = find_paths(
            g,
            start=EX.A,
            path=EX.knows,
            end=EX.D,
            shortest=False,
        )
        for r in results:
            assert r.length == sum(s.length for s in r.steps)

    def test_non_numeric_length_raises_type_error(self):
        """?length bound to a non-numeric value raises TypeError."""
        g = Graph()
        g.bind("ex", EX)
        g.add((EX.e1, EX.fromNode, EX.A))
        g.add((EX.e1, EX.toNode, EX.B))
        g.add((EX.e1, EX.weight, Literal("not-a-number")))

        path_pattern = (
            "?edge ex:fromNode ?start . ?edge ex:toNode ?end . ?edge ex:weight ?length"
        )

        with pytest.raises(TypeError, match=r"\?length must be numeric"):
            find_paths(
                g,
                start=EX.A,
                path=path_pattern,
                end=EX.B,
                initNs=NS,
            )

    def test_negative_length_raises_value_error(self):
        """?length bound to a negative value raises ValueError."""
        g = Graph()
        g.bind("ex", EX)
        g.add((EX.e1, EX.fromNode, EX.A))
        g.add((EX.e1, EX.toNode, EX.B))
        g.add((EX.e1, EX.weight, Literal(-5.0)))

        path_pattern = (
            "?edge ex:fromNode ?start . ?edge ex:toNode ?end . ?edge ex:weight ?length"
        )

        with pytest.raises(ValueError, match=r"\?length must be non-negative"):
            find_paths(
                g,
                start=EX.A,
                path=path_pattern,
                end=EX.B,
                initNs=NS,
            )
