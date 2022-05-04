import os
from dataclasses import dataclass
from pathlib import PurePosixPath, PureWindowsPath
from test.utils import GraphHelper, affix_tuples, file_uri_to_path
from typing import Optional

import pytest

from rdflib.graph import ConjunctiveGraph, Graph
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
    format: str
    ignore_blanks: bool
    lhs: str
    rhs: str


@pytest.mark.parametrize(
    "test_case",
    [
        SetsEqualTestCase(
            equal=False,
            format="turtle",
            ignore_blanks=False,
            lhs="""
            @prefix eg: <ex:> .
            _:a _:b _:c .
            eg:o0 eg:p0 eg:s0 .
            eg:o1 eg:p1 eg:s1 .
            """,
            rhs="""
            @prefix eg: <ex:> .
            eg:o0 eg:p0 eg:s0 .
            eg:o1 eg:p1 eg:s1 .
            """,
        ),
        SetsEqualTestCase(
            equal=True,
            format="turtle",
            ignore_blanks=True,
            lhs="""
            @prefix eg: <ex:> .
            _:a _:b _:c .
            eg:o0 eg:p0 eg:s0 .
            eg:o1 eg:p1 eg:s1 .
            """,
            rhs="""
            @prefix eg: <ex:> .
            eg:o0 eg:p0 eg:s0 .
            eg:o1 eg:p1 eg:s1 .
            """,
        ),
        SetsEqualTestCase(
            equal=True,
            format="turtle",
            ignore_blanks=False,
            lhs="""
            <ex:o0> <ex:p0> <ex:s0> .
            <ex:o1> <ex:p1> <ex:s1> .
            """,
            rhs="""
            @prefix eg: <ex:> .
            eg:o0 eg:p0 eg:s0 .
            eg:o1 eg:p1 eg:s1 .
            """,
        ),
        SetsEqualTestCase(
            equal=False,
            format="turtle",
            ignore_blanks=False,
            lhs="""
            <ex:o0> <ex:p0> <ex:s0> .
            <ex:o1> <ex:p1> <ex:s1> .
            <ex:o2> <ex:p2> <ex:s2> .
            """,
            rhs="""
            @prefix eg: <ex:> .
            eg:o0 eg:p0 eg:s0 .
            eg:o1 eg:p1 eg:s1 .
            """,
        ),
    ],
)
def test_assert_sets_equal(test_case: SetsEqualTestCase):
    """
    GraphHelper.sets_equals and related functions work correctly in both
    positive and negative cases.
    """
    lhs_graph: Graph = Graph().parse(data=test_case.lhs, format=test_case.format)
    rhs_graph: Graph = Graph().parse(data=test_case.rhs, format=test_case.format)

    public_id = URIRef("example:graph")
    lhs_cgraph: ConjunctiveGraph = ConjunctiveGraph()
    lhs_cgraph.parse(data=test_case.lhs, format=test_case.format, publicID=public_id)

    rhs_cgraph: ConjunctiveGraph = ConjunctiveGraph()
    rhs_cgraph.parse(data=test_case.rhs, format=test_case.format, publicID=public_id)

    assert isinstance(lhs_cgraph, ConjunctiveGraph)
    assert isinstance(rhs_cgraph, ConjunctiveGraph)
    graph: Graph
    cgraph: ConjunctiveGraph
    for graph, cgraph in ((lhs_graph, lhs_cgraph), (rhs_graph, rhs_cgraph)):
        GraphHelper.assert_sets_equals(graph, graph, True)
        GraphHelper.assert_sets_equals(cgraph, cgraph, True)
        GraphHelper.assert_triple_sets_equals(graph, graph, True)
        GraphHelper.assert_triple_sets_equals(cgraph, cgraph, True)
        GraphHelper.assert_quad_sets_equals(cgraph, cgraph, True)

    if not test_case.equal:
        with pytest.raises(AssertionError):
            GraphHelper.assert_sets_equals(
                lhs_graph, rhs_graph, test_case.ignore_blanks
            )
        with pytest.raises(AssertionError):
            GraphHelper.assert_sets_equals(
                lhs_cgraph, rhs_cgraph, test_case.ignore_blanks
            )
        with pytest.raises(AssertionError):
            GraphHelper.assert_triple_sets_equals(
                lhs_graph, rhs_graph, test_case.ignore_blanks
            )
        with pytest.raises(AssertionError):
            GraphHelper.assert_triple_sets_equals(
                lhs_cgraph, rhs_cgraph, test_case.ignore_blanks
            )
        with pytest.raises(AssertionError):
            GraphHelper.assert_quad_sets_equals(
                lhs_cgraph, rhs_cgraph, test_case.ignore_blanks
            )
    else:
        GraphHelper.assert_sets_equals(lhs_graph, rhs_graph, test_case.ignore_blanks)
        GraphHelper.assert_sets_equals(lhs_cgraph, rhs_cgraph, test_case.ignore_blanks)
        GraphHelper.assert_triple_sets_equals(
            lhs_graph, rhs_graph, test_case.ignore_blanks
        )
        GraphHelper.assert_triple_sets_equals(
            lhs_cgraph, rhs_cgraph, test_case.ignore_blanks
        )
        GraphHelper.assert_quad_sets_equals(
            lhs_cgraph, rhs_cgraph, test_case.ignore_blanks
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
