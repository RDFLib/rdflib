"""
This module contains test utilities.

The tests for test utilities should be placed inside `test.utils.test`
(`test/utils/tests/`).
"""

from __future__ import annotations

import enum
import pprint
from collections.abc import Callable, Collection
from typing import TYPE_CHECKING, Any, Optional, TypeVar, Union, cast

import pytest
from _pytest.mark.structures import Mark, MarkDecorator, ParameterSet

import rdflib.compare
import rdflib.plugin
from rdflib import BNode, ConjunctiveGraph, Graph
from rdflib.graph import Dataset
from rdflib.plugin import Plugin
from rdflib.term import IdentifiedNode, Identifier, Literal, Node, URIRef

if TYPE_CHECKING:
    from collections.abc import Generator, Iterable, Sequence

    import typing_extensions as te

    from rdflib.graph import _TripleType

PluginT = TypeVar("PluginT")


__all__ = ["file_uri_to_path"]


def get_unique_plugins(
    type_: type[PluginT],
) -> dict[type[PluginT], set[Plugin[PluginT]]]:
    result: dict[type[PluginT], set[Plugin[PluginT]]] = {}
    for plugin in rdflib.plugin.plugins(None, type_):
        cls = plugin.getClass()
        plugins = result.setdefault(cls, set())
        plugins.add(plugin)
    return result


def get_unique_plugin_names(type_: type[PluginT]) -> set[str]:
    result: set[str] = set()
    unique_plugins = get_unique_plugins(type_)
    for type_, plugin_set in unique_plugins.items():
        result.add(next(iter(plugin_set)).name)
    return result


GHNode = Union[Identifier, frozenset[tuple[Identifier, Identifier, Identifier]]]
GHTriple = tuple[GHNode, GHNode, GHNode]
GHTripleSet = set[GHTriple]
GHTripleFrozenSet = frozenset[GHTriple]
GHQuad = tuple[GHNode, GHNode, GHNode, Identifier]
GHQuadSet = set[GHQuad]
GHQuadFrozenSet = frozenset[GHQuad]

NodeT = TypeVar("NodeT", bound=GHNode)

COLLAPSED_BNODE = URIRef("urn:fdc:rdflib.github.io:20220522:collapsed-bnode")


class BNodeHandling(str, enum.Enum):
    COMPARE = "compare"  # Compare BNodes as normal
    EXCLUDE = "exclude"  # Exclude blanks from comparison
    COLLAPSE = "collapse"  # Collapse all blank nodes to one IRI


class GraphHelper:
    """
    Provides methods which are useful for working with graphs.
    """

    @classmethod
    def add_triples(cls, graph: Graph, triples: Iterable[_TripleType]) -> Graph:
        for triple in triples:
            graph.add(triple)
        return graph

    @classmethod
    def node(
        cls, node: Node, bnode_handling: BNodeHandling = BNodeHandling.COMPARE
    ) -> GHNode:
        """
        Return the identifier of the provided node.
        """
        if isinstance(node, Graph):
            xset = cast(GHNode, cls.triple_or_quad_set(node, bnode_handling))
            return xset

        return cast(Identifier, node)

    @classmethod
    def nodes(
        cls,
        nodes: tuple[Node, ...],
        bnode_handling: BNodeHandling = BNodeHandling.COMPARE,
    ) -> tuple[GHNode, ...]:
        """
        Return the identifiers of the provided nodes.
        """
        result = []
        for node in nodes:
            result.append(cls.node(node, bnode_handling))
        return tuple(result)

    @classmethod
    def _contains_bnodes(cls, nodes: tuple[GHNode, ...]) -> bool:
        """
        Return true if any of the nodes are BNodes.
        """
        for node in nodes:
            if isinstance(node, BNode):
                return True
        return False

    @classmethod
    def _collapse_bnodes(cls, nodes: tuple[NodeT, ...]) -> tuple[NodeT, ...]:
        """
        Return BNodes as COLLAPSED_BNODE
        """
        result: list[NodeT] = []
        for node in nodes:
            if isinstance(node, BNode):
                result.append(cast(NodeT, COLLAPSED_BNODE))
            else:
                result.append(node)
        return tuple(result)

    @classmethod
    def triple_set(
        cls, graph: Graph, bnode_handling: BNodeHandling = BNodeHandling.COMPARE
    ) -> GHTripleFrozenSet:
        result: GHTripleSet = set()
        for sn, pn, on in graph.triples((None, None, None)):
            s, p, o = cls.nodes((sn, pn, on), bnode_handling)
            if bnode_handling == BNodeHandling.EXCLUDE and cls._contains_bnodes(
                (s, p, o)
            ):
                continue
            elif bnode_handling == BNodeHandling.COLLAPSE:
                s, p, o = cls._collapse_bnodes((s, p, o))
            # if bnode_handling == BNodeHandling.EXCLUDE (
            #     isinstance(s, BNode) or isinstance(p, BNode) or isinstance(o, BNode)
            # ):
            #     continue
            result.add((s, p, o))
        return frozenset(result)

    @classmethod
    def triple_sets(
        cls,
        graphs: Iterable[Graph],
        bnode_handling: BNodeHandling = BNodeHandling.COMPARE,
    ) -> list[GHTripleFrozenSet]:
        """
        Extracts the set of all triples from the supplied Graph.
        """
        result: list[GHTripleFrozenSet] = []
        for graph in graphs:
            result.append(cls.triple_set(graph, bnode_handling))
        return result

    @classmethod
    def quad_set(
        cls,
        graph: ConjunctiveGraph,
        bnode_handling: BNodeHandling = BNodeHandling.COMPARE,
    ) -> GHQuadFrozenSet:
        """
        Extracts the set of all quads from the supplied ConjunctiveGraph.
        """
        result: GHQuadSet = set()
        for sn, pn, on, gn in graph.quads((None, None, None, None)):
            gn_id: Identifier
            if isinstance(graph, Dataset):
                assert isinstance(gn, Identifier)
                gn_id = gn  # type: ignore[unreachable]
            elif isinstance(graph, ConjunctiveGraph):
                assert isinstance(gn, Graph)
                gn_id = gn.identifier
            else:
                raise ValueError(f"invalid graph type {type(graph)}: {graph!r}")
            s, p, o = cls.nodes((sn, pn, on), bnode_handling)
            if bnode_handling == BNodeHandling.EXCLUDE and cls._contains_bnodes(
                (s, p, o, gn_id)
            ):
                continue
            elif bnode_handling == BNodeHandling.COLLAPSE:
                s, p, o, gn_id = cast(GHQuad, cls._collapse_bnodes((s, p, o, gn_id)))
            quad: GHQuad = (s, p, o, gn_id)
            result.add(quad)
        return frozenset(result)

    @classmethod
    def triple_or_quad_set(
        cls, graph: Graph, bnode_handling: BNodeHandling = BNodeHandling.COMPARE
    ) -> Union[GHQuadFrozenSet, GHTripleFrozenSet]:
        """
        Extracts quad or triple sets depending on whether or not the graph is
        ConjunctiveGraph or a normal Graph.
        """
        if isinstance(graph, ConjunctiveGraph):
            return cls.quad_set(graph, bnode_handling)
        return cls.triple_set(graph, bnode_handling)

    @classmethod
    def assert_triple_sets_equals(
        cls,
        lhs: Graph,
        rhs: Graph,
        bnode_handling: BNodeHandling = BNodeHandling.COMPARE,
        negate: bool = False,
    ) -> None:
        """
        Asserts that the triple sets in the two graphs are equal.
        """
        lhs_set = cls.triple_set(lhs, bnode_handling) if isinstance(lhs, Graph) else lhs
        rhs_set = cls.triple_set(rhs, bnode_handling) if isinstance(rhs, Graph) else rhs
        if not negate:
            assert lhs_set == rhs_set
        else:
            assert lhs_set != rhs_set

    @classmethod
    def assert_quad_sets_equals(
        cls,
        lhs: Union[ConjunctiveGraph, GHQuadSet],
        rhs: Union[ConjunctiveGraph, GHQuadSet],
        bnode_handling: BNodeHandling = BNodeHandling.COMPARE,
        negate: bool = False,
    ) -> None:
        """
        Asserts that the quads sets in the two graphs are equal.
        """
        lhs_set = cls.quad_set(lhs, bnode_handling) if isinstance(lhs, Graph) else lhs
        rhs_set = cls.quad_set(rhs, bnode_handling) if isinstance(rhs, Graph) else rhs
        if not negate:
            assert lhs_set == rhs_set
        else:
            assert lhs_set != rhs_set

    @classmethod
    def assert_collection_graphs_equal(
        cls, lhs: ConjunctiveGraph, rhs: ConjunctiveGraph
    ) -> None:
        """
        Assert that all graphs in the provided collections are equal,
        comparing named graphs with identically named graphs.
        """
        cls.assert_triple_sets_equals(lhs.default_context, rhs.default_context)
        graph_names = cls.non_default_graph_names(lhs) | cls.non_default_graph_names(
            rhs
        )
        for identifier in graph_names:
            cls.assert_triple_sets_equals(
                lhs.get_context(identifier), rhs.get_context(identifier)
            )

    @classmethod
    def assert_sets_equals(
        cls,
        lhs: Union[Graph, GHTripleSet, GHQuadSet],
        rhs: Union[Graph, GHTripleSet, GHQuadSet],
        bnode_handling: BNodeHandling = BNodeHandling.COMPARE,
        negate: bool = False,
    ) -> None:
        """
        Asserts that that ther quad or triple sets from the two graphs are equal.
        """
        lhs_set = (
            cls.triple_or_quad_set(lhs, bnode_handling)
            if isinstance(lhs, Graph)
            else lhs
        )
        rhs_set = (
            cls.triple_or_quad_set(rhs, bnode_handling)
            if isinstance(rhs, Graph)
            else rhs
        )
        if not negate:
            assert lhs_set == rhs_set
        else:
            assert lhs_set != rhs_set

    @classmethod
    def format_set(
        cls,
        item_set: Union[GHQuadSet, GHQuadFrozenSet, GHTripleSet, GHTripleFrozenSet],
        indent: int = 1,
        sort: bool = False,
    ) -> str:
        def _key(node: Union[GHTriple, GHQuad, GHNode]):
            val: Any = node
            if isinstance(node, tuple):
                val = tuple(_key(item) for item in node)
            if isinstance(node, frozenset):
                for triple in node:
                    nodes = cls.nodes(triple)
                    val = tuple(_key(item) for item in nodes)
            key = (f"{type(node)}", val)
            return key

        use_item_set = sorted(item_set, key=_key) if sort else item_set
        return pprint.pformat(use_item_set, indent)

    @classmethod
    def format_graph_set(cls, graph: Graph, indent: int = 1, sort: bool = False) -> str:
        return cls.format_set(cls.triple_or_quad_set(graph), indent, sort)

    @classmethod
    def assert_isomorphic(
        cls, lhs: Graph, rhs: Graph, message: str | None = None
    ) -> None:
        """
        This asserts that the two graphs are isomorphic, providing a nicely
        formatted error message if they are not.
        """

        # TODO FIXME: This should possibly raise an error when used on a ConjunctiveGraph
        def format_report(message: str | None = None) -> str:
            in_both, in_lhs, in_rhs = rdflib.compare.graph_diff(lhs, rhs)
            preamle = "" if message is None else f"{message}\n"
            return (
                f"{preamle}in both:\n"
                f"{cls.format_graph_set(in_both)}"
                "\nonly in first:\n"
                f"{cls.format_graph_set(in_lhs, sort = True)}"
                "\nonly in second:\n"
                f"{cls.format_graph_set(in_rhs, sort = True)}"
            )

        assert rdflib.compare.isomorphic(lhs, rhs), format_report(message)

    @classmethod
    def assert_cgraph_isomorphic(
        cls,
        lhs: ConjunctiveGraph,
        rhs: ConjunctiveGraph,
        exclude_bnodes: bool,
        message: str | None = None,
    ) -> None:
        def get_contexts(cgraph: ConjunctiveGraph) -> dict[URIRef, Graph]:
            result = {}
            for context in cgraph.contexts():
                if isinstance(context.identifier, BNode):
                    if exclude_bnodes:
                        continue
                    else:
                        raise AssertionError("BNode labelled graphs not supported")
                elif isinstance(context.identifier, URIRef):
                    if len(context) == 0:
                        # If a context has no triples it does not exist in a
                        # meaningful way.
                        continue
                    result[context.identifier] = context
                else:
                    raise AssertionError(
                        f"unsupported context identifier {context.identifier}"
                    )
            return result

        lhs_contexts = get_contexts(lhs)
        rhs_contexts = get_contexts(rhs)
        assert (
            lhs_contexts.keys() == rhs_contexts.keys()
        ), f"must have same context ids in LHS and RHS (exclude_bnodes={exclude_bnodes})"
        for id, lhs_context in lhs_contexts.items():
            cls.assert_isomorphic(lhs_context, rhs_contexts[id], message)

    @classmethod
    def strip_literal_datatypes(cls, graph: Graph, datatypes: set[URIRef]) -> None:
        """
        Strips datatypes in the provided set from literals in the graph.
        """
        for object in graph.objects():
            if not isinstance(object, Literal):
                continue
            if object.datatype is None:
                continue
            if object.datatype in datatypes:
                object._datatype = None

    @classmethod
    def non_default_graph_names(
        cls, container: ConjunctiveGraph
    ) -> set[IdentifiedNode]:
        return set(context.identifier for context in container.contexts()) - {
            container.default_context.identifier
        }

    @classmethod
    def non_default_graphs(cls, container: ConjunctiveGraph) -> Sequence[Graph]:
        result = []
        for name in cls.non_default_graph_names(container):
            result.append(container.get_context(name))
        return result


def eq_(lhs, rhs, msg=None):
    """
    This function mimicks the similar function from nosetest. Ideally nothing
    should use it but there is a lot of code that still does and it's fairly
    simple to just keep this small pollyfill here for now.
    """
    if msg:
        assert lhs == rhs, msg
    else:
        assert lhs == rhs


ParamsT = TypeVar("ParamsT", bound=tuple)
MarksType: te.TypeAlias = Collection[Union[MarkDecorator, Mark]]
MarkListType: te.TypeAlias = list[Union[MarkDecorator, Mark]]
MarkType: te.TypeAlias = Union[MarkDecorator, MarksType]

MarkerType: te.TypeAlias = Callable[..., Optional[MarkType]]


def marks_to_list(mark: MarkType) -> MarkListType:
    if isinstance(mark, (MarkDecorator, Mark)):
        return [mark]
    elif isinstance(mark, list):
        return mark
    return list(*mark)


def pytest_mark_filter(
    param_sets: Iterable[Union[ParamsT, ParameterSet]],
    mark_dict: dict[ParamsT, MarksType],
) -> Generator[ParameterSet, None, None]:
    """
    Adds marks to test parameters. Useful for adding xfails to test parameters.
    """
    for param_set in param_sets:
        if isinstance(param_set, ParameterSet):
            # param_set.marks = [*param_set.marks, *marks.get(param_set.values, ())]
            yield pytest.param(
                *param_set.values,
                id=param_set.id,
                marks=[
                    *param_set.marks,
                    *mark_dict.get(
                        cast(ParamsT, param_set.values), cast(MarksType, ())
                    ),
                ],
            )
        else:
            yield pytest.param(
                *param_set, marks=mark_dict.get(param_set, cast(MarksType, ()))
            )


def affix_tuples(
    prefix: tuple[Any, ...] | None,
    tuples: Iterable[tuple[Any, ...]],
    suffix: tuple[Any, ...] | None,
) -> Generator[tuple[Any, ...], None, None]:
    if prefix is None:
        prefix = tuple()
    if suffix is None:
        suffix = tuple()
    for item in tuples:
        yield (*prefix, *item, *suffix)


def ensure_suffix(value: str, suffix: str) -> str:
    if not value.endswith(suffix):
        value = f"{value}{suffix}"
    return value


def idfns(*idfns: Callable[[Any], str | None]) -> Callable[[Any], str | None]:
    """
    Returns an ID function which will try each of the provided ID
    functions in order.

    Args:
        idfns: The ID functions to try.

    Returns:
        An ID function which will try each of the provided ID functions.
    """

    def _idfns(value: Any) -> str | None:
        for idfn in idfns:
            result = idfn(value)
            if result is not None:
                return result
        return None

    return _idfns


from test.utils.iri import file_uri_to_path  # noqa: E402
