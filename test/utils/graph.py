from __future__ import annotations

import logging
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from runpy import run_path
from typing import Any, Optional, Tuple, Type, Union

import rdflib.util
import test.data
from rdflib.graph import Graph, _GraphT
from rdflib.util import guess_format

GraphSourceType = Union["GraphSource", Path]

SUFFIX_FORMAT_MAP = {**rdflib.util.SUFFIX_FORMAT_MAP, "hext": "hext"}


@dataclass(frozen=True)
class GraphSource:
    path: Path
    format: str
    public_id: Optional[str] = None

    @classmethod
    def guess_format(cls, path: Path) -> Optional[str]:
        format: Optional[str]
        if path.suffix == ".py":
            format = "python"
        else:
            format = guess_format(f"{path}", SUFFIX_FORMAT_MAP)
        return format

    @classmethod
    def from_path(
        cls, path: Path, public_id: Optional[str] = None, format: Optional[str] = None
    ) -> GraphSource:
        if format is None:
            format = cls.guess_format(path)
        if format is None:
            raise ValueError(f"could not guess format for source {path}")
        return cls(path, format, public_id)

    @classmethod
    def from_paths(cls, *paths: Path) -> Tuple[GraphSource, ...]:
        result = []
        for path in paths:
            result.append(cls.from_path(path))
        return tuple(result)

    @classmethod
    def from_source(
        cls, source: GraphSourceType, public_id: Optional[str] = None
    ) -> GraphSource:
        logging.debug("source(%s) = %r", id(source), source)
        if isinstance(source, Path):
            source = GraphSource.from_path(source)
        return source

    def public_id_or_path_uri(self) -> str:
        if self.public_id is not None:
            self.public_id
        return self.path.as_uri()

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
            load_from_python(self.path, graph, graph_type)
        else:
            graph.parse(
                source=self.path,
                format=self.format,
                publicID=self.public_id if public_id is None else public_id,
            )
        return graph

    @classmethod
    def idfn(cls, val: Any) -> Optional[str]:
        """
        ID function for GraphSource objects.

        :param val: The value to try to generate and identifier for.
        :return: A string identifying the given value if the value is a
            `GraphSource`, otherwise return `None`.
        """
        if isinstance(val, cls):
            try:
                path_string = f"{val.path.relative_to(test.data.TEST_DATA_DIR)}"
            except ValueError:
                path_string = f"{val.path}"
            return f"GS({path_string}, {val.format}, {val.public_id})"
        return None


def load_sources(
    *sources: GraphSourceType,
    graph: Optional[_GraphT] = None,
    public_id: Optional[str] = None,
    graph_type: Type[_GraphT] = Graph,  # type: ignore[assignment]
) -> _GraphT:
    if graph is None:
        graph = graph_type()
    for source in sources:
        GraphSource.from_source(source).load(graph, public_id)
    return graph


@lru_cache(maxsize=None)
def cached_graph(
    sources: Tuple[Union[GraphSource, Path], ...],
    public_id: Optional[str] = None,
    graph_type: Type[_GraphT] = Graph,  # type: ignore[assignment]
) -> _GraphT:
    return load_sources(*sources, public_id=public_id, graph_type=graph_type)


def load_from_python(
    path: Path,
    graph: Optional[_GraphT] = None,
    graph_type: Type[_GraphT] = Graph,  # type: ignore[assignment]
) -> _GraphT:
    if graph is None:
        graph = graph_type()

    mod = run_path(f"{path}")
    if "populate_graph" not in mod:
        raise ValueError(f"{path} does not contain a `populate_graph` function")
    mod["populate_graph"](graph)
    return graph
