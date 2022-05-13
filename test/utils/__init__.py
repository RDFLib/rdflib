"""
This module contains test utilities.

The tests for test utilities should be placed inside `test.utils.test`
(``test/utils/tests/``).
"""

from __future__ import print_function

import datetime
import email.message
import os
import random
import sys
import unittest
from contextlib import AbstractContextManager, contextmanager
from http.server import BaseHTTPRequestHandler, HTTPServer, SimpleHTTPRequestHandler
from pathlib import PurePath, PureWindowsPath
from threading import Thread
from traceback import print_exc
from types import TracebackType
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Collection,
    Dict,
    Generator,
    Iterable,
    Iterator,
    List,
    NamedTuple,
    Optional,
    Set,
    Tuple,
    Type,
    TypeVar,
    Union,
    cast,
)
from unittest.mock import MagicMock, Mock
from urllib.error import HTTPError
from urllib.parse import ParseResult, parse_qs, unquote, urlparse
from urllib.request import urlopen

import isodate
import pytest
from _pytest.mark.structures import Mark, MarkDecorator, ParameterSet
from nturl2path import url2pathname as nt_url2pathname

import rdflib.compare
import rdflib.plugin
from rdflib import BNode, ConjunctiveGraph, Graph
from rdflib.plugin import Plugin
from rdflib.term import Identifier, Literal, Node, URIRef

PluginT = TypeVar("PluginT")


def get_unique_plugins(
    type: Type[PluginT],
) -> Dict[Type[PluginT], Set[Plugin[PluginT]]]:
    result: Dict[Type[PluginT], Set[Plugin[PluginT]]] = {}
    for plugin in rdflib.plugin.plugins(None, type):
        cls = plugin.getClass()
        plugins = result.setdefault(cls, set())
        plugins.add(plugin)
    return result


def get_unique_plugin_names(type: Type[PluginT]) -> Set[str]:
    result: Set[str] = set()
    unique_plugins = get_unique_plugins(type)
    for type, plugin_set in unique_plugins.items():
        result.add(next(iter(plugin_set)).name)
    return result


IdentifierTriple = Tuple[Identifier, Identifier, Identifier]
IdentifierTripleSet = Set[IdentifierTriple]
IdentifierQuad = Tuple[Identifier, Identifier, Identifier, Identifier]
IdentifierQuadSet = Set[IdentifierQuad]


class GraphHelper:
    """
    Provides methods which are useful for working with graphs.
    """

    @classmethod
    def identifier(self, node: Node) -> Identifier:
        """
        Return the identifier of the provided node.
        """
        if isinstance(node, Graph):
            return node.identifier
        else:
            return cast(Identifier, node)

    @classmethod
    def identifiers(cls, nodes: Tuple[Node, ...]) -> Tuple[Identifier, ...]:
        """
        Return the identifiers of the provided nodes.
        """
        result = []
        for node in nodes:
            result.append(cls.identifier(node))
        return tuple(result)

    @classmethod
    def triple_set(
        cls, graph: Graph, exclude_blanks: bool = False
    ) -> IdentifierTripleSet:
        result = set()
        for sn, pn, on in graph.triples((None, None, None)):
            s, p, o = cls.identifiers((sn, pn, on))
            if exclude_blanks and (
                isinstance(s, BNode) or isinstance(p, BNode) or isinstance(o, BNode)
            ):
                continue
            result.add((s, p, o))
        return result

    @classmethod
    def triple_sets(
        cls, graphs: Iterable[Graph], exclude_blanks: bool = False
    ) -> List[IdentifierTripleSet]:
        """
        Extracts the set of all triples from the supplied Graph.
        """
        result: List[IdentifierTripleSet] = []
        for graph in graphs:
            result.append(cls.triple_set(graph, exclude_blanks))
        return result

    @classmethod
    def quad_set(
        cls, graph: ConjunctiveGraph, exclude_blanks: bool = False
    ) -> IdentifierQuadSet:
        """
        Extracts the set of all quads from the supplied ConjunctiveGraph.
        """
        result = set()
        for sn, pn, on, gn in graph.quads((None, None, None, None)):
            s, p, o, g = cls.identifiers((sn, pn, on, gn))
            if exclude_blanks and (
                isinstance(s, BNode)
                or isinstance(p, BNode)
                or isinstance(o, BNode)
                or isinstance(g, BNode)
            ):
                continue
            result.add((s, p, o, g))
        return result

    @classmethod
    def triple_or_quad_set(
        cls, graph: Graph, exclude_blanks: bool = False
    ) -> Union[IdentifierQuadSet, IdentifierTripleSet]:
        """
        Extracts quad or triple sets depending on whether or not the graph is
        ConjunctiveGraph or a normal Graph.
        """
        if isinstance(graph, ConjunctiveGraph):
            return cls.quad_set(graph, exclude_blanks)
        return cls.triple_set(graph, exclude_blanks)

    @classmethod
    def assert_triple_sets_equals(
        cls, lhs: Graph, rhs: Graph, exclude_blanks: bool = False
    ) -> None:
        """
        Asserts that the triple sets in the two graphs are equal.
        """
        lhs_set = cls.triple_set(lhs, exclude_blanks)
        rhs_set = cls.triple_set(rhs, exclude_blanks)
        assert lhs_set == rhs_set

    @classmethod
    def assert_quad_sets_equals(
        cls, lhs: ConjunctiveGraph, rhs: ConjunctiveGraph, exclude_blanks: bool = False
    ) -> None:
        """
        Asserts that the quads sets in the two graphs are equal.
        """
        lhs_set = cls.quad_set(lhs, exclude_blanks)
        rhs_set = cls.quad_set(rhs, exclude_blanks)
        assert lhs_set == rhs_set

    @classmethod
    def assert_sets_equals(
        cls, lhs: Graph, rhs: Graph, exclude_blanks: bool = False
    ) -> None:
        """
        Asserts that that ther quad or triple sets from the two graphs are equal.
        """
        lhs_set = cls.triple_or_quad_set(lhs, exclude_blanks)
        rhs_set = cls.triple_or_quad_set(rhs, exclude_blanks)
        assert lhs_set == rhs_set

    @classmethod
    def format_set(
        cls,
        item_set: Union[IdentifierQuadSet, IdentifierTripleSet],
        prefix: str = "  ",
        sort: bool = False,
    ) -> str:
        items = []
        use_item_set = sorted(item_set) if sort else item_set
        for item in use_item_set:
            items.append(f"{prefix}{item}")
        return "\n".join(items)

    @classmethod
    def format_graph_set(
        cls, graph: Graph, prefix: str = "  ", sort: bool = False
    ) -> str:
        return cls.format_set(cls.triple_or_quad_set(graph), prefix, sort)

    @classmethod
    def assert_isomorphic(
        cls, lhs: Graph, rhs: Graph, message: Optional[str] = None
    ) -> None:
        """
        This asserts that the two graphs are isomorphic, providing a nicely
        formatted error message if they are not.
        """

        def format_report(message: Optional[str] = None) -> str:
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
    def strip_literal_datatypes(cls, graph: Graph, datatypes: Set[URIRef]) -> None:
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


PurePathT = TypeVar("PurePathT", bound=PurePath)


def file_uri_to_path(
    file_uri: str,
    path_class: Type[PurePathT] = PurePath,  # type: ignore[assignment]
    url2pathname: Optional[Callable[[str], str]] = None,
) -> PurePathT:
    """
    This function returns a pathlib.PurePath object for the supplied file URI.

    :param str file_uri: The file URI ...
    :param class path_class: The type of path in the file_uri. By default it uses
        the system specific path pathlib.PurePath, to force a specific type of path
        pass pathlib.PureWindowsPath or pathlib.PurePosixPath
    :returns: the pathlib.PurePath object
    :rtype: pathlib.PurePath
    """
    is_windows_path = isinstance(path_class(), PureWindowsPath)
    file_uri_parsed = urlparse(file_uri)
    if url2pathname is None:
        if is_windows_path:
            url2pathname = nt_url2pathname
        else:
            url2pathname = unquote
    pathname = url2pathname(file_uri_parsed.path)
    result = path_class(pathname)
    return result


ParamsT = TypeVar("ParamsT", bound=tuple)
Marks = Collection[Union[Mark, MarkDecorator]]


def pytest_mark_filter(
    param_sets: Iterable[Union[ParamsT, ParameterSet]], mark_dict: Dict[ParamsT, Marks]
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
                    *mark_dict.get(cast(ParamsT, param_set.values), cast(Marks, ())),
                ],
            )
        else:
            yield pytest.param(
                *param_set, marks=mark_dict.get(param_set, cast(Marks, ()))
            )
