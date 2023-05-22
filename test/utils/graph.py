from __future__ import annotations

import enum
import importlib
import logging
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Type, Union

from rdflib.graph import Graph, _GraphT
from rdflib.util import guess_format

GraphSourceType = Union["GraphSource", Path]

PROJECT_ROOT = Path(__file__).parent.parent.parent


@dataclass(frozen=True)
class GraphSource:
    path: Path
    format: str
    public_id: Optional[str] = None

    @classmethod
    def from_path(cls, path: Path, public_id: Optional[str] = None) -> "GraphSource":
        format: Optional[str]
        if path.suffix == ".py":
            format = "python"
        else:
            format = guess_format(f"{path}")
        if format is None:
            raise ValueError(f"could not guess format for source {path}")

        return cls(path, format, public_id)

    @classmethod
    def from_paths(cls, *paths: Path) -> Tuple["GraphSource", ...]:
        result = []
        for path in paths:
            result.append(cls.from_path(path))
        return tuple(result)

    @classmethod
    def from_source(
        cls, source: GraphSourceType, public_id: Optional[str] = None
    ) -> "GraphSource":
        logging.debug("source(%s) = %r", id(source), source)
        if isinstance(source, Path):
            source = GraphSource.from_path(source)
        return source

    def load(
        self,
        graph: Optional[_GraphT] = None,
        public_id: Optional[str] = None,
        # type error: Incompatible default for argument "graph_type" (default has type "Type[Graph]", argument has type "Type[_GraphT]")
        # see https://github.com/python/mypy/issues/3737
        graph_type: Type[_GraphT] = Graph,  # type: ignore[assignment]
    ) -> _GraphT:
        if graph is None:
            graph = graph_type()
        if self.format == "python":
            relative_path = self.path.relative_to(PROJECT_ROOT)
            module_name = ".".join([*relative_path.parts[:-1], relative_path.stem])
            logging.debug(
                "relative_path = %s, module_name = %s", relative_path, module_name
            )
            module = importlib.import_module(module_name)
            module.populate_graph(graph)
        else:
            graph.parse(
                source=self.path,
                format=self.format,
                publicID=self.public_id if public_id is None else public_id,
            )
        return graph


def load_sources(
    *sources: GraphSourceType,
    graph: Optional[_GraphT] = None,
    public_id: Optional[str] = None,
    # type error: Incompatible default for argument "graph_type" (default has type "Type[Graph]", argument has type "Type[_GraphT]")
    # see https://github.com/python/mypy/issues/3737
    graph_type: Type[_GraphT] = Graph,  # type: ignore[assignment]
) -> _GraphT:
    if graph is None:
        graph = graph_type()
    for source in sources:
        GraphSource.from_source(source).load(graph, public_id)
    return graph


@lru_cache(maxsize=None)
def cached_graph(
    sources: Tuple[Union[GraphSource, Path], ...], public_id: Optional[str] = None
) -> Graph:
    return load_sources(*sources, public_id=public_id)


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
    def info_dict(cls) -> GraphFormatInfoDict:
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
    def info(self) -> GraphFormatInfo:
        return self.info_dict()[self]

    @classmethod
    def set(cls) -> Set[GraphFormat]:
        return set(cls)


@dataclass(unsafe_hash=True)
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
    def serializer(self) -> str:
        if not self.serializers:
            raise RuntimeError("no serializers for {self.name}")
        return self.serializers[0]

    @property
    def deserializer(self) -> str:
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


GRAPH_FORMAT_DICT = GraphFormat.info_dict()
GRAPH_FORMATS = GraphFormat.set()
# GRAPH_FORMAT_INFO_SET = set(GRAPH_FORMAT_DICT.values())
# GRAPH_SERIALIZERS, GRAPH_DESERIALIZERS = GRAPH_FORMAT_DICT.serdes_dict()
