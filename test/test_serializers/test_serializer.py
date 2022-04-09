import logging
import enum
import inspect
import itertools
import sys
import unittest
from rdflib import RDF, Graph, Literal, Namespace, URIRef
from tempfile import TemporaryDirectory
from contextlib import ExitStack
from io import IOBase
from pathlib import Path, PurePath
from tempfile import TemporaryDirectory
from test.testutils import GraphHelper, get_unique_plugins
from typing import (
    IO,
    Any,
    Dict,
    Iterable,
    NamedTuple,
    Optional,
    Set,
    TextIO,
    Tuple,
    Union,
    cast,
)

from rdflib import Graph
from rdflib.graph import ConjunctiveGraph
from rdflib.namespace import Namespace
from rdflib.plugin import PluginException
from rdflib.serializer import Serializer

EG = Namespace("http://example.com/")


class DestinationType(str, enum.Enum):
    PATH = enum.auto()
    PURE_PATH = enum.auto()
    PATH_STR = enum.auto()
    IO_BYTES = enum.auto()
    TEXT_IO = enum.auto()


class DestinationFactory:
    _counter: int = 0

    def __init__(self, tmpdir: Path) -> None:
        self.tmpdir = tmpdir

    def make(
        self,
        type: DestinationType,
        stack: Optional[ExitStack] = None,
    ) -> Tuple[Union[str, Path, PurePath, IO[bytes], TextIO], Path]:
        self._counter += 1
        count = self._counter
        path = self.tmpdir / f"file-{type}-{count:05d}"
        if type is DestinationType.PATH:
            return (path, path)
        if type is DestinationType.PURE_PATH:
            return (PurePath(path), path)
        if type is DestinationType.PATH_STR:
            return (f"{path}", path)
        if type is DestinationType.IO_BYTES:
            return (
                path.open("wb")
                if stack is None
                else stack.enter_context(path.open("wb")),
                path,
            )
        if type is DestinationType.TEXT_IO:
            return (
                path.open("w")
                if stack is None
                else stack.enter_context(path.open("w")),
                path,
            )
        raise ValueError(f"unsupported type {type}")


class GraphType(str, enum.Enum):
    QUAD = enum.auto()
    TRIPLE = enum.auto()


class FormatInfo(NamedTuple):
    serializer_name: str
    deserializer_name: str
    graph_types: Set[GraphType]
    encodings: Set[str]


class FormatInfos(Dict[str, FormatInfo]):
    def add_format(
        self,
        serializer_name: str,
        *,
        deserializer_name: Optional[str] = None,
        graph_types: Set[GraphType],
        encodings: Set[str],
    ) -> None:
        self[serializer_name] = FormatInfo(
            serializer_name,
            serializer_name if deserializer_name is None else deserializer_name,
            {GraphType.QUAD, GraphType.TRIPLE} if graph_types is None else graph_types,
            encodings,
        )

    def select(
        self,
        *,
        name: Optional[Set[str]] = None,
        graph_type: Optional[Set[GraphType]] = None,
    ) -> Iterable[FormatInfo]:
        for format in self.values():
            if graph_type is not None and not graph_type.isdisjoint(format.graph_types):
                yield format
            if name is not None and format.serializer_name in name:
                yield format

    @classmethod
    def make_graph(self, format_info: FormatInfo) -> Graph:
        if GraphType.QUAD in format_info.graph_types:
            return ConjunctiveGraph()
        else:
            return Graph()

    @classmethod
    def make(cls) -> "FormatInfos":
        result = cls()

        flexible_formats = {
            "trig",
        }
        for format in flexible_formats:
            result.add_format(
                format,
                graph_types={GraphType.TRIPLE, GraphType.QUAD},
                encodings={"utf-8"},
            )

        triple_only_formats = {
            "turtle",
            "nt11",
            "xml",
            "n3",
        }
        for format in triple_only_formats:
            result.add_format(
                format, graph_types={GraphType.TRIPLE}, encodings={"utf-8"}
            )

        quad_only_formats = {
            "nquads",
            "trix",
            "json-ld",
        }
        for format in quad_only_formats:
            result.add_format(format, graph_types={GraphType.QUAD}, encodings={"utf-8"})

        result.add_format(
            "pretty-xml",
            deserializer_name="xml",
            graph_types={GraphType.TRIPLE},
            encodings={"utf-8"},
        )
        result.add_format(
            "ntriples",
            graph_types={GraphType.TRIPLE},
            encodings={"ascii"},
        )

        return result


format_infos = FormatInfos.make()


def assert_graphs_equal(
    test_case: unittest.TestCase, lhs: Graph, rhs: Graph, check_context: bool = True
) -> None:
    lhs_has_quads = hasattr(lhs, "quads")
    rhs_has_quads = hasattr(rhs, "quads")
    lhs_set: Set[Any]
    rhs_set: Set[Any]
    if lhs_has_quads and rhs_has_quads and check_context:
        lhs = cast(ConjunctiveGraph, lhs)
        rhs = cast(ConjunctiveGraph, rhs)
        lhs_set, rhs_set = GraphHelper.quad_sets([lhs, rhs])
    else:
        lhs_set, rhs_set = GraphHelper.triple_sets([lhs, rhs])
    test_case.assertEqual(lhs_set, rhs_set)
    test_case.assertTrue(len(lhs_set) > 0)
    test_case.assertTrue(len(rhs_set) > 0)

from typing import Tuple, cast

import pytest
import itertools

from rdflib.graph import ConjunctiveGraph

from test.testutils import GraphHelper


@pytest.mark.parametrize(
    "format, tuple_index, is_keyword",
    [
        (format, tuple_index, keyword)
        for format, (tuple_index, keyword) in itertools.product(
            ["turtle", "n3", "trig"],
            [
                (0, False),
                (1, True),
                (2, False),
            ],
        )
    ]
    + [("trig", 3, False)],
)
def test_rdf_type(format: str, tuple_index: int, is_keyword: bool) -> None:
    NS = Namespace("example:")
    graph = ConjunctiveGraph()
    graph.bind("eg", NS)
    nodes = [NS.subj, NS.pred, NS.obj, NS.graph]
    nodes[tuple_index] = RDF.type
    quad = cast(Tuple[URIRef, URIRef, URIRef, URIRef], tuple(nodes))
    graph.add(quad)
    data = graph.serialize(format=format)
    logging.info("data = %s", data)
    assert NS in data
    if is_keyword:
        assert str(RDF) not in data
    else:
        assert str(RDF) in data
    parsed_graph = ConjunctiveGraph()
    parsed_graph.parse(data=data, format=format)
    GraphHelper.assert_triple_sets_equals(graph, parsed_graph)


class TestSerialize(unittest.TestCase):
    def setUp(self) -> None:
        self.triple = (
            EG["subject"],
            EG["predicate"],
            Literal("日本語の表記体系", lang="jpx"),
        )
        self.context = EG["graph"]
        self.quad = (*self.triple, self.context)

        conjunctive_graph = ConjunctiveGraph()
        conjunctive_graph.add(self.quad)
        self.graph = conjunctive_graph

        query = """
        CONSTRUCT { ?subject ?predicate ?object } WHERE {
            ?subject ?predicate ?object
        } ORDER BY ?object
        """
        self.result = self.graph.query(query)
        self.assertIsNotNone(self.result.graph)

        self._tmpdir = TemporaryDirectory()
        self.tmpdir = Path(self._tmpdir.name)

        return super().setUp()

    def tearDown(self) -> None:
        self._tmpdir.cleanup()

    def test_graph(self) -> None:
        quad_set = GraphHelper.quad_set(self.graph)
        self.assertEqual(quad_set, {self.quad})

    def test_all_formats_specified(self) -> None:
        plugins = get_unique_plugins(Serializer)
        for plugin_refs in plugins.values():
            names = {plugin_ref.name for plugin_ref in plugin_refs}
            self.assertNotEqual(
                names.intersection(format_infos.keys()),
                set(),
                f"serializers does not include any of {names}",
            )

    def test_serialize_to_neturl(self) -> None:
        with self.assertRaises(ValueError) as raised:
            self.graph.serialize(
                destination="http://example.com/", format="nt", encoding="utf-8"
            )
        self.assertIn("destination", f"{raised.exception}")

    def test_serialize_to_fileurl(self):
        with TemporaryDirectory() as td:
            tfpath = Path(td) / "out.nt"
            tfurl = tfpath.as_uri()
            self.assertRegex(tfurl, r"^file:")
            self.assertFalse(tfpath.exists())
            self.graph.serialize(destination=tfurl, format="nt", encoding="utf-8")
            self.assertTrue(tfpath.exists())
            graph_check = Graph()
            graph_check.parse(source=tfpath, format="nt")
        self.assertEqual(self.triple, next(iter(graph_check)))

    def test_serialize_badformat(self) -> None:
        with self.assertRaises(PluginException) as raised:
            self.graph.serialize(destination="http://example.com/", format="badformat")
        self.assertIn("badformat", f"{raised.exception}")

    def test_str(self) -> None:
        """
        This function tests serialization of graphs to strings, either directly
        or from query results.

        This function also checks that the various string serialization
        overloads are correct.
        """
        for format in format_infos.keys():
            format_info = format_infos[format]

            def check(data: str, check_context: bool = True) -> None:
                with self.subTest(format=format, caller=inspect.stack()[1]):
                    self.assertIsInstance(data, str)

                    graph_check = FormatInfos.make_graph(format_info)
                    graph_check.parse(data=data, format=format_info.deserializer_name)
                    assert_graphs_equal(self, self.graph, graph_check, check_context)

            if format == "turtle":
                check(self.graph.serialize())
                check(self.graph.serialize(None))
            check(self.graph.serialize(None, format))
            check(self.graph.serialize(None, format, encoding=None))
            check(self.graph.serialize(None, format, None, None))
            check(self.graph.serialize(None, format=format))
            check(self.graph.serialize(None, format=format, encoding=None))

            if GraphType.TRIPLE not in format_info.graph_types:
                # tests below are only for formats that can work with context-less graphs.
                continue

            if format == "turtle":
                check(self.result.serialize(), False)
                check(self.result.serialize(None), False)
            check(self.result.serialize(None, format=format), False)
            check(self.result.serialize(None, None, format), False)
            check(self.result.serialize(None, None, format=format), False)
            check(self.result.serialize(None, encodin=None, format=format), False)
            check(
                self.result.serialize(destination=None, encoding=None, format=format),
                False,
            )

    def test_bytes(self) -> None:
        """
        This function tests serialization of graphs to bytes, either directly or
        from query results.

        This function also checks that the various bytes serialization overloads
        are correct.
        """
        for (format, encoding) in itertools.chain(
            *(
                itertools.product({format_info.serializer_name}, format_info.encodings)
                for format_info in format_infos.values()
            )
        ):
            format_info = format_infos[format]

            def check(data: bytes, check_context: bool = True) -> None:
                with self.subTest(
                    format=format, encoding=encoding, caller=inspect.stack()[1]
                ):
                    # self.check_data_bytes(data, format=format, encoding=encoding)
                    self.assertIsInstance(data, bytes)

                    # double check that encoding is right
                    data_str = data.decode(encoding)
                    graph_check = FormatInfos.make_graph(format_info)
                    graph_check.parse(
                        data=data_str, format=format_info.deserializer_name
                    )
                    assert_graphs_equal(self, self.graph, graph_check, check_context)

                    # actual check
                    # TODO FIXME : handle other encodings
                    if encoding == "utf-8":
                        graph_check = FormatInfos.make_graph(format_info)
                        graph_check.parse(
                            data=data, format=format_info.deserializer_name
                        )
                        assert_graphs_equal(
                            self, self.graph, graph_check, check_context
                        )

            if format == "turtle":
                check(self.graph.serialize(encoding=encoding))
            check(self.graph.serialize(None, format, encoding=encoding))
            check(self.graph.serialize(None, format, None, encoding=encoding))
            check(self.graph.serialize(None, format, encoding=encoding))
            check(self.graph.serialize(None, format=format, encoding=encoding))

            if GraphType.TRIPLE not in format_info.graph_types:
                # tests below are only for formats that can work with context-less graphs.
                continue

            if format == "turtle":
                check(self.result.serialize(encoding=encoding), False)
                check(self.result.serialize(None, encoding), False)
            check(self.result.serialize(encoding=encoding, format=format), False)
            check(self.result.serialize(None, encoding, format), False)
            check(self.result.serialize(None, encoding=encoding, format=format), False)
            check(
                self.result.serialize(
                    destination=None, encoding=encoding, format=format
                ),
                False,
            )

    def test_file(self) -> None:
        """
        This function tests serialization of graphs to destinations, either directly or
        from query results.

        This function also checks that the various bytes serialization overloads
        are correct.
        """
        dest_factory = DestinationFactory(self.tmpdir)

        for (format, encoding, dest_type) in itertools.chain(
            *(
                itertools.product(
                    {format_info.serializer_name},
                    format_info.encodings,
                    set(DestinationType).difference({DestinationType.TEXT_IO}),
                )
                for format_info in format_infos.values()
            )
        ):
            format_info = format_infos[format]
            with ExitStack() as stack:
                dest_path: Path
                _dest: Union[str, Path, PurePath, IO[bytes]]

                def dest() -> Union[str, Path, PurePath, IO[bytes]]:
                    nonlocal dest_path
                    nonlocal _dest
                    _dest, dest_path = cast(
                        Tuple[Union[str, Path, PurePath, IO[bytes]], Path],
                        dest_factory.make(dest_type, stack),
                    )
                    return _dest

                def _check(check_context: bool = True) -> None:
                    with self.subTest(
                        format=format,
                        encoding=encoding,
                        dest_type=dest_type,
                        caller=inspect.stack()[2],
                    ):
                        if isinstance(_dest, IOBase):  # type: ignore[unreachable]
                            _dest.flush()

                        source = Path(dest_path)

                        # double check that encoding is right
                        data_str = source.read_text(encoding=encoding)
                        graph_check = FormatInfos.make_graph(format_info)
                        graph_check.parse(
                            data=data_str, format=format_info.deserializer_name
                        )
                        assert_graphs_equal(
                            self, self.graph, graph_check, check_context
                        )

                        self.assertTrue(source.exists())
                        # actual check
                        # TODO FIXME : This should work for all encodings, not just utf-8
                        if encoding == "utf-8":
                            graph_check = FormatInfos.make_graph(format_info)
                            graph_check.parse(
                                source=source, format=format_info.deserializer_name
                            )
                            assert_graphs_equal(
                                self, self.graph, graph_check, check_context
                            )

                        dest_path.unlink()

                def check_a(graph: Graph) -> None:
                    _check()

                if (format, encoding) == ("turtle", "utf-8"):
                    check_a(self.graph.serialize(dest()))
                    check_a(self.graph.serialize(dest(), encoding=None))
                if format == "turtle":
                    check_a(self.graph.serialize(dest(), encoding=encoding))
                if encoding == sys.getdefaultencoding():
                    check_a(self.graph.serialize(dest(), format))
                    check_a(self.graph.serialize(dest(), format, None))
                    check_a(self.graph.serialize(dest(), format, None, None))

                check_a(self.graph.serialize(dest(), format, encoding=encoding))
                check_a(self.graph.serialize(dest(), format, None, encoding))

                if GraphType.TRIPLE not in format_info.graph_types:
                    # tests below are only for formats that can work with context-less graphs.
                    continue

                def check_b(none: None) -> None:
                    _check(False)

                if format == "turtle":
                    check_b(self.result.serialize(dest(), encoding))
                    check_b(
                        self.result.serialize(
                            destination=cast(str, dest()),
                            encoding=encoding,
                        )
                    )
                check_b(self.result.serialize(dest(), encoding=encoding, format=format))
                check_b(
                    self.result.serialize(
                        destination=dest(), encoding=encoding, format=format
                    )
                )
                check_b(
                    self.result.serialize(
                        destination=dest(), encoding=None, format=format
                    )
                )
                check_b(self.result.serialize(destination=dest(), format=format))
