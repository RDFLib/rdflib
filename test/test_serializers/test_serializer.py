import enum
import itertools
import logging
import re
from contextlib import contextmanager
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path, PurePath
from test.utils import GraphHelper, get_unique_plugins
from typing import (
    IO,
    Callable,
    Dict,
    Generator,
    List,
    Optional,
    Set,
    Tuple,
    Union,
    cast,
)

import pytest
from _pytest.mark.structures import Mark, MarkDecorator, ParameterSet

import rdflib
import rdflib.plugin
from rdflib import RDF, XSD, Graph, Literal, Namespace, URIRef
from rdflib.graph import DATASET_DEFAULT_GRAPH_ID, ConjunctiveGraph, Dataset
from rdflib.serializer import Serializer

EGSCHEMA = Namespace("example:")
EGURN = Namespace("urn:example:")
EGHTTP = Namespace("http://example.com/")


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


EG = Namespace("example:")


@pytest.fixture(scope="session")
def simple_graph() -> Graph:
    """
    This is a simple graph with no BNodes that can be used in tests.
    Assumptions/assertions should not be made about the triples in it, other
    than that it contains no blank nodes.
    """
    graph = Graph()
    graph.add((EGSCHEMA.subject, EGSCHEMA.predicate, EGSCHEMA.object))
    graph.add((EGSCHEMA.subject, EGSCHEMA.predicate, Literal(12)))
    graph.add(
        (
            EGHTTP.subject,
            EGHTTP.predicate,
            Literal("日本語の表記体系", lang="jpx"),
        )
    )
    graph.add((EGURN.subject, EGSCHEMA.predicate, EGSCHEMA.subject))
    graph.add(
        (EGSCHEMA.object, EGHTTP.predicate, Literal("XSD string", datatype=XSD.string))
    )
    return graph


@pytest.fixture(scope="session")
def simple_dataset() -> Dataset:
    """
    This is a simple dataset with no BNodes that can be used in tests.
    Assumptions/assertions should not be made about the quads in it, other
    than that it contains no blank nodes.
    """
    graph = Dataset()
    graph.default_context.add((EGSCHEMA.subject, EGSCHEMA.predicate, EGSCHEMA.object))
    graph.default_context.add((EGURN.subject, EGURN.predicate, EGURN.object))
    graph.default_context.add((EGHTTP.subject, EGHTTP.predicate, Literal("typeless")))
    graph.get_context(EGSCHEMA.graph).add(
        (EGSCHEMA.subject, EGSCHEMA.predicate, EGSCHEMA.object)
    )
    graph.get_context(EGSCHEMA.graph).add(
        (EGSCHEMA.subject, EGSCHEMA.predicate, Literal(12))
    )
    graph.get_context(EGSCHEMA.graph).add(
        (
            EGHTTP.subject,
            EGHTTP.predicate,
            Literal("日本語の表記体系", lang="jpx"),
        )
    )
    graph.get_context(EGSCHEMA.graph).add(
        (EGURN.subject, EGSCHEMA.predicate, EGSCHEMA.subject)
    )
    graph.get_context(EGURN.graph).add(
        (EGSCHEMA.subject, EGSCHEMA.predicate, EGSCHEMA.object)
    )
    graph.get_context(EGURN.graph).add(
        (EGSCHEMA.subject, EGHTTP.predicate, EGHTTP.object)
    )
    graph.get_context(EGURN.graph).add(
        (EGSCHEMA.subject, EGHTTP.predicate, Literal("XSD string", datatype=XSD.string))
    )
    return graph


def test_serialize_to_purepath(tmp_path: Path, simple_graph: Graph):
    tfpath = tmp_path / "out.nt"
    simple_graph.serialize(destination=tfpath, format="nt", encoding="utf-8")
    graph_check = Graph()
    graph_check.parse(source=tfpath, format="nt")

    GraphHelper.assert_triple_sets_equals(simple_graph, graph_check)


def test_serialize_to_path(tmp_path: Path, simple_graph: Graph):
    tfpath = tmp_path / "out.nt"
    simple_graph.serialize(destination=tfpath, format="nt", encoding="utf-8")
    graph_check = Graph()
    graph_check.parse(source=tfpath, format="nt")

    GraphHelper.assert_triple_sets_equals(simple_graph, graph_check)


def test_serialize_to_neturl(simple_graph: Graph):
    with pytest.raises(ValueError) as raised:
        simple_graph.serialize(
            destination="http://example.com/", format="nt", encoding="utf-8"
        )
    assert "destination" in f"{raised.value}"


def test_serialize_to_fileurl(tmp_path: Path, simple_graph: Graph):
    tfpath = tmp_path / "out.nt"
    tfurl = tfpath.as_uri()
    assert re.match(r"^file:", tfurl)
    assert not tfpath.exists()
    simple_graph.serialize(destination=tfurl, format="nt", encoding="utf-8")
    assert tfpath.exists()
    graph_check = Graph()
    graph_check.parse(source=tfpath, format="nt")
    GraphHelper.assert_triple_sets_equals(simple_graph, graph_check)


def test_serialize_badformat(simple_graph: Graph) -> None:
    # NOTE: This is using an fully qualified name because of reloading that
    # occurs in `test_plugins.py` which results in the the type identity being
    # different.
    with pytest.raises(rdflib.plugin.PluginException) as ctx:
        simple_graph.serialize(destination="http://example.com/", format="badformat")
    assert "badformat" in f"{ctx.value}"


@dataclass(frozen=True)
class DestRef:
    param: Union[Path, PurePath, str, IO[bytes]]
    path: Path


class DestinationType(str, enum.Enum):
    PATH = enum.auto()
    PURE_PATH = enum.auto()
    STR_PATH = enum.auto()
    BINARY_IO = enum.auto()
    RETURN = enum.auto()

    @contextmanager
    def make_ref(self, tmp_path: Path) -> Generator[Optional[DestRef], None, None]:
        path = tmp_path / f"file-{self.name}"
        if self is DestinationType.RETURN:
            yield None
        elif self is DestinationType.PATH:
            yield DestRef(path, path)
        elif self is DestinationType.PURE_PATH:
            yield DestRef(PurePath(path), path)
        elif self is DestinationType.STR_PATH:
            yield DestRef(f"{path}", path)
        elif self is DestinationType.BINARY_IO:
            with path.open("wb") as bfh:
                yield DestRef(bfh, path)
        else:
            raise ValueError(f"unsupported type {type!r}")


class GraphType(str, enum.Enum):
    QUAD = enum.auto()
    TRIPLE = enum.auto()


class GraphFormat(str, enum.Enum):
    TRIG = "trig"
    NQUADS = "nquads"
    TRIX = "trix"
    JSON_LD = "json-ld"
    TURTLE = "turtle"
    NT11 = "nt11"
    XML = "xml"
    N3 = "n3"
    NTRIPLES = "ntriples"
    HEXT = "hext"

    @classmethod
    @lru_cache(maxsize=None)
    def info_dict(cls) -> "GraphFormatInfoDict":
        return GraphFormatInfoDict.make(
            GraphFormatInfo(
                GraphFormat.TRIG,
                graph_types={GraphType.TRIPLE, GraphType.QUAD},
                encodings={"utf-8"},
            ),
            GraphFormatInfo(
                GraphFormat.NQUADS,
                # TODO FIXME: Currently nquads rejects requests to seralize
                # non-context-aware stores, this does not make a lot of sense and
                # should be fixed.
                #
                graph_types={GraphType.QUAD},
                encodings={"utf-8"},
            ),
            GraphFormatInfo(
                GraphFormat.TRIX,
                # TODO FIXME: Currently trix rejects requests to seralize
                # non-context-aware stores, this does not make a lot of sense and
                # should be fixed.
                #
                graph_types={GraphType.QUAD},
                encodings={"utf-8"},
            ),
            GraphFormatInfo(
                GraphFormat.JSON_LD,
                graph_types={GraphType.TRIPLE, GraphType.QUAD},
                encodings={"utf-8"},
            ),
            GraphFormatInfo(
                GraphFormat.TURTLE,
                graph_types={GraphType.TRIPLE},
                encodings={"utf-8"},
                serializer_list=["longturtle", "turtle"],
            ),
            GraphFormatInfo(
                GraphFormat.NT11,
                graph_types={GraphType.TRIPLE},
                encodings={"utf-8"},
            ),
            GraphFormatInfo(
                GraphFormat.XML,
                graph_types={GraphType.TRIPLE},
                encodings={"utf-8"},
                serializer_list=["xml", "pretty-xml"],
            ),
            GraphFormatInfo(
                GraphFormat.N3,
                graph_types={GraphType.TRIPLE},
                encodings={"utf-8"},
            ),
            GraphFormatInfo(
                GraphFormat.NTRIPLES,
                graph_types={GraphType.TRIPLE},
                encodings={"utf-8"},
            ),
            GraphFormatInfo(
                GraphFormat.HEXT,
                graph_types={GraphType.TRIPLE, GraphType.QUAD},
                encodings={"utf-8"},
            ),
        )

    @property
    def info(self) -> "GraphFormatInfo":
        return self.info_dict()[self]

    @classmethod
    @lru_cache(maxsize=None)
    def set(cls) -> Set["GraphFormat"]:
        return set(*cls)


@dataclass
class GraphFormatInfo:
    name: "GraphFormat"
    graph_types: Set[GraphType]
    encodings: Set[str]
    serializer_list: Optional[List[str]] = field(
        default=None, repr=False, hash=False, compare=False
    )
    deserializer_list: Optional[List[str]] = field(
        default=None, repr=False, hash=False, compare=False
    )
    serializers: List[str] = field(default_factory=list, init=False)
    deserializers: List[str] = field(default_factory=list, init=False)

    def __post_init__(self) -> None:
        self.serializers = (
            [self.name.value] if self.serializer_list is None else self.serializer_list
        )
        self.deserializers = (
            [self.name.value]
            if self.deserializer_list is None
            else self.deserializer_list
        )

    @property
    def serializer(self) -> "str":
        if not self.serializers:
            raise RuntimeError("no serializers for {self.name}")
        return self.serializers[0]

    @property
    def deserializer(self) -> "str":
        if not self.deserializers:
            raise RuntimeError("no deserializer for {self.name}")
        return self.deserializer[0]


class GraphFormatInfoDict(Dict[str, GraphFormatInfo]):
    @classmethod
    def make(cls, *graph_format: GraphFormatInfo) -> "GraphFormatInfoDict":
        result = cls()
        for item in graph_format:
            result[item.name] = item
        return result

    def serdes_dict(self) -> Tuple[Dict[str, GraphFormat], Dict[str, GraphFormat]]:
        serializer_dict: Dict[str, GraphFormat] = {}
        deserializer_dict: Dict[str, GraphFormat] = {}
        for format in self.values():
            for serializer in format.serializers:
                serializer_dict[serializer] = format.name
            for deserializer in format.deserializers:
                deserializer_dict[deserializer] = format.name
        return (serializer_dict, deserializer_dict)


serializer_dict, deserializer_dict = GraphFormat.info_dict().serdes_dict()


def test_all_serializers_specified() -> None:
    plugins = get_unique_plugins(Serializer)
    for plugin_refs in plugins.values():
        names = {plugin_ref.name for plugin_ref in plugin_refs}
        assert (
            set(serializer_dict.keys()) != set()
        ), f"serializers does not include any of {names}"


def make_serialize_parse_tests() -> Generator[ParameterSet, None, None]:
    """
    This function generates test parameters for test_serialize_parse.
    """
    xfails: Dict[
        Tuple[str, GraphType, DestinationType, Optional[str]],
        Union[MarkDecorator, Mark],
    ] = {}
    destination_types = set(DestinationType)
    for serializer_name, destination_type in itertools.product(
        serializer_dict.keys(), destination_types
    ):
        format = serializer_dict[serializer_name]
        encodings: Set[Optional[str]] = {*format.info.encodings, None}
        for encoding, graph_type in itertools.product(
            encodings, format.info.graph_types
        ):
            xfail = xfails.get(
                (serializer_name, graph_type, destination_type, encoding)
            )
            if not xfail:
                if serializer_name in ("trig") and graph_type is GraphType.TRIPLE:
                    xfail = pytest.mark.xfail(
                        raises=AssertionError,
                        reason="""
        TriG serializes non-context aware stores incorrectly, adding a blank
        node graph name which breaks round tripping.
                        """,
                    )
                if serializer_name in ("json-ld"):
                    xfail = pytest.mark.xfail(
                        raises=AssertionError,
                        reason="""
    JSON-LD is dropping datatype:
    -   rdflib.term.Literal('XSD string'),
    +   rdflib.term.Literal('XSD string', datatype=rdflib.term.URIRef('http://www.w3.org/2001/XMLSchema#string')),
                        """,
                    )
                elif serializer_name in ("hext") and graph_type is GraphType.QUAD:
                    xfail = pytest.mark.xfail(
                        raises=AssertionError,
                        reason="""
    hext is injecting datatype:
    -   rdflib.term.Literal('typeless', datatype=rdflib.term.URIRef('http://www.w3.org/2001/XMLSchema#string')),
    +   rdflib.term.Literal('typeless'),
    """,
                    )
            marks = (xfail,) if xfail is not None else ()
            yield pytest.param(
                (serializer_name, graph_type, destination_type, encoding),
                id=f"{serializer_name}-{graph_type.name}-{destination_type.name}-{encoding}",
                marks=marks,
            )


SerializeResultType = Union[bytes, str, Graph]


@pytest.mark.parametrize(
    ["args"],
    make_serialize_parse_tests(),
)
def test_serialize_parse(
    tmp_path: Path,
    simple_graph: Graph,
    simple_dataset: Dataset,
    args: Tuple[str, GraphType, DestinationType, Optional[str]],
) -> None:
    """
    Serialization works correctly with the given arguments and generates output
    that can be parsed to a graph that is identical to the original graph.
    """
    serializer_name, graph_type, destination_type, encoding = args
    format = serializer_dict[serializer_name]
    graph: Union[Graph, Dataset]
    if graph_type == GraphType.QUAD:
        graph = simple_dataset
    elif graph_type == GraphType.TRIPLE:
        graph = simple_graph
    else:
        raise ValueError(f"graph_type {graph_type!r} is not supported")
    with destination_type.make_ref(tmp_path) as dest_ref:
        destination = None if dest_ref is None else dest_ref.param
        serialize_result = graph.serialize(
            destination=destination,
            format=serializer_name,
            encoding=encoding,
        )

    logging.debug("serialize_result = %r, dest_ref = %s", serialize_result, dest_ref)

    if dest_ref is None:
        if encoding is None:
            assert isinstance(serialize_result, str)
            serialized_data = serialize_result
        else:
            assert isinstance(serialize_result, bytes)
            serialized_data = serialize_result.decode(encoding)
    else:
        assert isinstance(serialize_result, Graph)
        assert dest_ref.path.exists()
        serialized_data = dest_ref.path.read_bytes().decode(
            "utf-8" if encoding is None else encoding
        )

    logging.debug("serialized_data = %s", serialized_data)
    check_serialized(format, graph, serialized_data)


def check_serialized(format: GraphFormat, graph: Graph, data: str) -> None:
    graph_check = Dataset() if isinstance(graph, Dataset) else Graph()
    if not format.info.deserializers:
        return
    graph_check.parse(
        data=data,
        format=format.info.deserializers[0],
        publicID=DATASET_DEFAULT_GRAPH_ID,
    )
    logging.debug("graph = %r, graph_check = %r", graph, graph_check)
    GraphHelper.assert_sets_equals(graph, graph_check)


@dataclass
class SerializeArgs:
    format: str
    opt_dest_ref: Optional[DestRef]

    @property
    def dest_ref(self) -> DestRef:
        if self.opt_dest_ref is None:
            raise RuntimeError("dest_ref is None")
        return self.opt_dest_ref


SerializeFunctionType = Callable[[Graph, SerializeArgs], SerializeResultType]
StrSerializeFunctionType = Callable[[Graph, SerializeArgs], str]
BytesSerializeFunctionType = Callable[[Graph, SerializeArgs], bytes]
FileSerializeFunctionType = Callable[[Graph, SerializeArgs], Graph]


str_serialize_functions: List[StrSerializeFunctionType] = [
    lambda graph, args: graph.serialize(),
    lambda graph, args: graph.serialize(None),
    lambda graph, args: graph.serialize(None, args.format),
    lambda graph, args: graph.serialize(None, args.format, encoding=None),
    lambda graph, args: graph.serialize(None, args.format, None, None),
    lambda graph, args: graph.serialize(None, format=args.format),
    lambda graph, args: graph.serialize(None, format=args.format, encoding=None),
]


bytes_serialize_functions: List[BytesSerializeFunctionType] = [
    lambda graph, args: graph.serialize(encoding="utf-8"),
    lambda graph, args: graph.serialize(None, args.format, encoding="utf-8"),
    lambda graph, args: graph.serialize(None, args.format, None, "utf-8"),
    lambda graph, args: graph.serialize(None, args.format, None, encoding="utf-8"),
    lambda graph, args: graph.serialize(None, args.format, encoding="utf-8"),
    lambda graph, args: graph.serialize(None, format=args.format, encoding="utf-8"),
]


file_serialize_functions: List[FileSerializeFunctionType] = [
    lambda graph, args: graph.serialize(args.dest_ref.param),
    lambda graph, args: graph.serialize(args.dest_ref.param, encoding=None),
    lambda graph, args: graph.serialize(args.dest_ref.param, encoding="utf-8"),
    lambda graph, args: graph.serialize(args.dest_ref.param, args.format),
    lambda graph, args: graph.serialize(
        args.dest_ref.param, args.format, encoding=None
    ),
    lambda graph, args: graph.serialize(args.dest_ref.param, args.format, None, None),
    lambda graph, args: graph.serialize(
        args.dest_ref.param, args.format, encoding="utf-8"
    ),
    lambda graph, args: graph.serialize(
        args.dest_ref.param, args.format, None, encoding="utf-8"
    ),
    lambda graph, args: graph.serialize(
        args.dest_ref.param, args.format, None, "utf-8"
    ),
]


@pytest.mark.parametrize(
    ["destination_type", "serialize_function"],
    [
        *[
            (DestinationType.RETURN, str_serialize_function)
            for str_serialize_function in str_serialize_functions
        ],
        *[
            (DestinationType.RETURN, bytes_serialize_function)
            for bytes_serialize_function in bytes_serialize_functions
        ],
        *itertools.product(
            {
                DestinationType.BINARY_IO,
                DestinationType.PATH,
                DestinationType.PURE_PATH,
                DestinationType.STR_PATH,
            },
            file_serialize_functions,
        ),
    ],
)
def test_serialize_overloads(
    tmp_path: Path,
    simple_graph: Graph,
    destination_type: DestinationType,
    serialize_function: SerializeFunctionType,
) -> None:
    format = GraphFormat.TURTLE
    serializer = format.info.serializer

    with destination_type.make_ref(tmp_path) as dest_ref:
        serialize_result = serialize_function(
            simple_graph, SerializeArgs(format, dest_ref)
        )

    if isinstance(serialize_result, str):
        serialized_data = serialize_result
    elif isinstance(serialize_result, bytes):
        serialized_data = serialize_result.decode("utf-8")
    else:
        assert isinstance(serialize_result, Graph)
        assert dest_ref is not None
        assert dest_ref.path.exists()
        serialized_data = dest_ref.path.read_text(encoding="utf-8")

    check_serialized(format, simple_graph, serialized_data)
