import os
from contextlib import ExitStack
from dataclasses import dataclass
from pathlib import PurePosixPath, PureWindowsPath
from test.utils import (
    COLLAPSED_BNODE,
    BNodeHandling,
    GraphHelper,
    affix_tuples,
    file_uri_to_path,
)
from typing import Any, List, Optional, Tuple, Type, Union

import pytest

from rdflib.graph import ConjunctiveGraph, Dataset, Graph
from rdflib.term import URIRef


def check(
    file_uri: str,
    expected_windows_path: Optional[str],
    expected_posix_path: Optional[str],
) -> None:
    if expected_windows_path is not None:
        expected_windows_path_object = PureWindowsPath(expected_windows_path)
    if expected_posix_path is not None:
        expected_posix_path_object = PurePosixPath(expected_posix_path)

    if expected_windows_path is not None:
        if os.name == "nt":
            assert file_uri_to_path(file_uri) == expected_windows_path_object
        assert (
            file_uri_to_path(file_uri, PureWindowsPath) == expected_windows_path_object
        )

    if expected_posix_path is not None:
        if os.name != "nt":
            assert file_uri_to_path(file_uri) == expected_posix_path_object
        assert file_uri_to_path(file_uri, PurePosixPath) == expected_posix_path_object


@pytest.mark.parametrize(
    "file_uri,expected_windows_path,expected_posix_path",
    [
        (
            r"file:///C:/Windows/System32/Drivers/etc/hosts",
            r"C:\Windows\System32\Drivers\etc\hosts",
            r"/C:/Windows/System32/Drivers/etc/hosts",
        ),
        (
            r"file:///C%3A/Windows/System32/Drivers/etc/hosts",
            None,
            r"/C:/Windows/System32/Drivers/etc/hosts",
        ),
        (
            r"file:///C:/some%20dir/some%20file",
            r"C:\some dir\some file",
            r"/C:/some dir/some file",
        ),
        (
            r"file:///C%3A/some%20dir/some%20file",
            None,
            r"/C:/some dir/some file",
        ),
        (
            r"file:///C:/Python27/Scripts/pip.exe",
            r"C:\Python27\Scripts\pip.exe",
            r"/C:/Python27/Scripts/pip.exe",
        ),
        (
            r"file:///C:/yikes/paths%20with%20spaces.txt",
            r"C:\yikes\paths with spaces.txt",
            r"/C:/yikes/paths with spaces.txt",
        ),
        (
            r"file://localhost/c:/WINDOWS/clock.avi",
            r"c:\WINDOWS\clock.avi",
            r"/c:/WINDOWS/clock.avi",
        ),
        (r"file:///home/example/.profile", None, r"/home/example/.profile"),
        (r"file:///c|/path/to/file", r"c:\path\to\file", r"/c|/path/to/file"),
        (r"file:/c|/path/to/file", r"c:\path\to\file", r"/c|/path/to/file"),
        (r"file:c|/path/to/file", r"c:\path\to\file", r"c|/path/to/file"),
        (r"file:///c:/path/to/file", r"c:\path\to\file", r"/c:/path/to/file"),
        (r"file:/c:/path/to/file", r"c:\path\to\file", r"/c:/path/to/file"),
        (r"file:c:/path/to/file", r"c:\path\to\file", r"c:/path/to/file"),
        (r"file:/path/to/file", None, r"/path/to/file"),
        (r"file:///home/user/some%20file.txt", None, r"/home/user/some file.txt"),
        (
            r"file:///C:/some%20dir/some%20file.txt",
            r"C:\some dir\some file.txt",
            r"/C:/some dir/some file.txt",
        ),
    ],
)
def test_paths(
    file_uri: str,
    expected_windows_path: Optional[str],
    expected_posix_path: Optional[str],
) -> None:
    check(file_uri, expected_windows_path, expected_posix_path)


@dataclass
class SetsEqualTestCase:
    equal: bool
    format: Union[str, Tuple[str, str]]
    bnode_handling: BNodeHandling
    lhs: str
    rhs: str

    @property
    def lhs_format(self) -> str:
        if isinstance(self.format, tuple):
            return self.format[0]
        return self.format

    @property
    def rhs_format(self) -> str:
        if isinstance(self.format, tuple):
            return self.format[1]
        return self.format


@pytest.mark.parametrize(
    "test_case",
    [
        SetsEqualTestCase(
            equal=False,
            format="turtle",
            bnode_handling=BNodeHandling.COMPARE,
            lhs="""
            @prefix eg: <example:> .
            _:a _:b _:c .
            eg:o0 eg:p0 eg:s0 .
            eg:o1 eg:p1 eg:s1 .
            """,
            rhs="""
            @prefix eg: <example:> .
            eg:o0 eg:p0 eg:s0 .
            eg:o1 eg:p1 eg:s1 .
            """,
        ),
        SetsEqualTestCase(
            equal=True,
            format="turtle",
            bnode_handling=BNodeHandling.EXCLUDE,
            lhs="""
            @prefix eg: <example:> .
            _:a _:b _:c .
            eg:o0 eg:p0 eg:s0 .
            eg:o1 eg:p1 eg:s1 .
            """,
            rhs="""
            @prefix eg: <example:> .
            eg:o0 eg:p0 eg:s0 .
            eg:o1 eg:p1 eg:s1 .
            """,
        ),
        SetsEqualTestCase(
            equal=True,
            format="turtle",
            bnode_handling=BNodeHandling.COLLAPSE,
            lhs="""
            @prefix eg: <example:> .
            _:a _:b _:c .
            _:z _:b _:c .
            eg:o0 eg:p0 eg:s0 .
            eg:o1 eg:p1 eg:s1 .
            """,
            rhs=f"""
            @prefix eg: <example:> .
            <{COLLAPSED_BNODE}> <{COLLAPSED_BNODE}> <{COLLAPSED_BNODE}>.
            eg:o0 eg:p0 eg:s0 .
            eg:o1 eg:p1 eg:s1 .
            """,
        ),
        SetsEqualTestCase(
            equal=True,
            format="turtle",
            bnode_handling=BNodeHandling.COMPARE,
            lhs="""
            <example:o0> <example:p0> <example:s0> .
            <example:o1> <example:p1> <example:s1> .
            """,
            rhs="""
            @prefix eg: <example:> .
            eg:o0 eg:p0 eg:s0 .
            eg:o1 eg:p1 eg:s1 .
            """,
        ),
        SetsEqualTestCase(
            equal=False,
            format="turtle",
            bnode_handling=BNodeHandling.COMPARE,
            lhs="""
            <example:o0> <example:p0> <example:s0> .
            <example:o1> <example:p1> <example:s1> .
            <example:o2> <example:p2> <example:s2> .
            """,
            rhs="""
            @prefix eg: <example:> .
            eg:o0 eg:p0 eg:s0 .
            eg:o1 eg:p1 eg:s1 .
            """,
        ),
        SetsEqualTestCase(
            equal=True,
            format=("nquads", "trig"),
            bnode_handling=BNodeHandling.EXCLUDE,
            lhs="""
            <example:o0> <example:p0> <example:s0> .
            <example:o1> <example:p1> <example:s1> .
            <example:o2> <example:p2> <example:s2> .
            """,
            rhs="""
            @prefix eg: <example:> .
            eg:o0 eg:p0 eg:s0 .
            eg:o1 eg:p1 eg:s1 .
            eg:o2 eg:p2 eg:s2 .
            """,
        ),
        SetsEqualTestCase(
            equal=True,
            format=("nquads", "trig"),
            bnode_handling=BNodeHandling.COMPARE,
            lhs="""
            <example:o0> <example:p0> <example:s0> .
            <example:o1> <example:p1> <example:s1> <example:g1>.
            <example:o2> <example:p2> <example:s2> <example:g2> .
            """,
            rhs="""
            @prefix eg: <example:> .
            eg:o0 eg:p0 eg:s0 .
            eg:g1 {
                eg:o1 eg:p1 eg:s1 .
            }
            eg:g2 {
                eg:o2 eg:p2 eg:s2 .
            }
            """,
        ),
        SetsEqualTestCase(
            equal=True,
            format="n3",
            bnode_handling=BNodeHandling.COMPARE,
            lhs="""
            { <example:ss0> <example:sp0> <example:so0> } <example:p0> {}.
            """,
            rhs="""
            @prefix eg: <example:> .
            { eg:ss0 eg:sp0 eg:so0 } eg:p0 {}.
            """,
        ),
        SetsEqualTestCase(
            equal=True,
            format="n3",
            bnode_handling=BNodeHandling.COMPARE,
            lhs="""
            { <example:ss0> <example:sp0> <example:so0> } <example:p0> {}.
            """,
            rhs="""
            @prefix eg: <example:> .
            { eg:ss0 eg:sp0 eg:so0 } eg:p0 {}.
            """,
        ),
        SetsEqualTestCase(
            equal=True,
            format="n3",
            bnode_handling=BNodeHandling.COMPARE,
            lhs="""
            { { <example:sss0> <example:ssp0> <example:sso0> } <example:sp0> <example:so0> } <example:p0> {}.
            """,
            rhs="""
            @prefix eg: <example:> .
            { { eg:sss0 eg:ssp0 eg:sso0 } eg:sp0 eg:so0 } eg:p0 {}.
            """,
        ),
    ],
)
def test_assert_sets_equal(test_case: SetsEqualTestCase):
    """
    GraphHelper.sets_equals and related functions work correctly in both
    positive and negative cases.
    """
    lhs_graph: Graph = Graph().parse(data=test_case.lhs, format=test_case.lhs_format)
    rhs_graph: Graph = Graph().parse(data=test_case.rhs, format=test_case.rhs_format)

    public_id = URIRef("example:graph")
    lhs_cgraph: ConjunctiveGraph = ConjunctiveGraph()
    lhs_cgraph.parse(
        data=test_case.lhs, format=test_case.lhs_format, publicID=public_id
    )

    rhs_cgraph: ConjunctiveGraph = ConjunctiveGraph()
    rhs_cgraph.parse(
        data=test_case.rhs, format=test_case.rhs_format, publicID=public_id
    )

    assert isinstance(lhs_cgraph, ConjunctiveGraph)
    assert isinstance(rhs_cgraph, ConjunctiveGraph)
    graph: Graph
    cgraph: ConjunctiveGraph
    for graph, cgraph in ((lhs_graph, lhs_cgraph), (rhs_graph, rhs_cgraph)):
        GraphHelper.assert_sets_equals(graph, graph, BNodeHandling.COLLAPSE)
        GraphHelper.assert_sets_equals(cgraph, cgraph, BNodeHandling.COLLAPSE)
        GraphHelper.assert_triple_sets_equals(graph, graph, BNodeHandling.COLLAPSE)
        GraphHelper.assert_triple_sets_equals(cgraph, cgraph, BNodeHandling.COLLAPSE)
        GraphHelper.assert_quad_sets_equals(cgraph, cgraph, BNodeHandling.COLLAPSE)

    if not test_case.equal:
        with pytest.raises(AssertionError):
            GraphHelper.assert_sets_equals(
                lhs_graph, rhs_graph, test_case.bnode_handling
            )
        with pytest.raises(AssertionError):
            GraphHelper.assert_sets_equals(
                lhs_cgraph, rhs_cgraph, test_case.bnode_handling
            )
        with pytest.raises(AssertionError):
            GraphHelper.assert_triple_sets_equals(
                lhs_graph, rhs_graph, test_case.bnode_handling
            )
        with pytest.raises(AssertionError):
            GraphHelper.assert_triple_sets_equals(
                lhs_cgraph, rhs_cgraph, test_case.bnode_handling
            )
        with pytest.raises(AssertionError):
            GraphHelper.assert_quad_sets_equals(
                lhs_cgraph, rhs_cgraph, test_case.bnode_handling
            )
    else:
        GraphHelper.assert_sets_equals(lhs_graph, rhs_graph, test_case.bnode_handling)
        GraphHelper.assert_sets_equals(lhs_cgraph, rhs_cgraph, test_case.bnode_handling)
        GraphHelper.assert_triple_sets_equals(
            lhs_graph, rhs_graph, test_case.bnode_handling
        )
        GraphHelper.assert_triple_sets_equals(
            lhs_cgraph, rhs_cgraph, test_case.bnode_handling
        )
        GraphHelper.assert_quad_sets_equals(
            lhs_cgraph, rhs_cgraph, test_case.bnode_handling
        )


@pytest.mark.parametrize(
    ["tuples", "prefix", "suffix", "expected_result"],
    [
        (
            [("a",), ("b",), ("c",)],
            None,
            None,
            [("a",), ("b",), ("c",)],
        ),
        (
            [("a",), ("b",), ("c",)],
            (1, 2),
            None,
            [
                (1, 2, "a"),
                (1, 2, "b"),
                (1, 2, "c"),
            ],
        ),
        (
            [("a",), ("b",), ("c",)],
            None,
            (3, 4),
            [
                ("a", 3, 4),
                ("b", 3, 4),
                ("c", 3, 4),
            ],
        ),
    ],
)
def test_prefix_tuples(
    tuples: List[Tuple[Any, ...]],
    prefix: Tuple[Any, ...],
    suffix: Tuple[Any, ...],
    expected_result: List[Tuple[Any, ...]],
) -> None:
    assert expected_result == list(affix_tuples(prefix, tuples, suffix))


@pytest.mark.parametrize(
    ["graph_type", "format", "lhs", "rhs", "expected_result"],
    [
        (
            Dataset,
            "trig",
            """
            @prefix eg: <example:> .

            _:b0 eg:p0 eg:o0.
            eg:s1 eg:p1 eg:o1.

            eg:g0 {
                _:g0b0 eg:g0p0 eg:g0o0.
                eg:g0s1 eg:g0p1 eg:g0o1.
            }
            """,
            """
            @prefix eg: <example:> .

            _:b1 eg:p0 eg:o0.
            eg:s1 eg:p1 eg:o1.

            eg:g0 {
                _:g0b1 eg:g0p0 eg:g0o0.
                eg:g0s1 eg:g0p1 eg:g0o1.
            }
            """,
            None,
        ),
        (
            Dataset,
            "trig",
            """
            @prefix eg: <example:> .

            eg:g0 {
                _:b0 eg:g0p0 eg:g0o0.
                eg:g0s1 eg:g0p1 eg:g0o1.
            }
            """,
            """
            @prefix eg: <example:> .

            eg:g0 {
                _:b1 eg:g0p0 eg:g0o1.
                eg:g0s1 eg:g0p1 eg:g0o1.
            }
            """,
            AssertionError,
        ),
        (
            Dataset,
            "trig",
            """
            @prefix eg: <example:> .

            eg:g0 {
                _:b0 eg:g0p0 eg:g0o0.
                eg:g0s1 eg:g0p1 eg:g0o1.
            }
            """,
            """
            @prefix eg: <example:> .

            eg:g0 {
                _:b1 eg:g0p0 eg:g0o0.
                eg:g0s1 eg:g0p1 eg:g0o1.
            }

            eg:g1 {
                _:b0 eg:g1p0 eg:g1o0.
                eg:g1s1 eg:g1p1 eg:g1o1.
            }
            """,
            AssertionError,
        ),
    ],
)
def test_assert_cgraph_isomorphic(
    graph_type: Type[ConjunctiveGraph],
    format: str,
    lhs: str,
    rhs: str,
    expected_result: Union[None, Type[Exception]],
) -> None:
    lhs_graph = graph_type()
    lhs_graph.parse(data=lhs, format=format)
    rhs_graph = graph_type()
    rhs_graph.parse(data=rhs, format=format)
    catcher: Optional[pytest.ExceptionInfo[Exception]] = None
    with ExitStack() as xstack:
        if expected_result is not None:
            catcher = xstack.enter_context(pytest.raises(expected_result))
        GraphHelper.assert_cgraph_isomorphic(lhs_graph, rhs_graph, exclude_bnodes=True)
    if expected_result is None:
        assert catcher is None
    else:
        assert catcher is not None
