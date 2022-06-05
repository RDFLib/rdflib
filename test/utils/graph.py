import logging
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Optional, Tuple, Union

from rdflib.graph import Graph
from rdflib.util import guess_format

GraphSourceType = Union["GraphSource", Path]


@dataclass(frozen=True)
class GraphSource:
    path: Path
    format: str
    public_id: Optional[str] = None

    @classmethod
    def from_path(cls, path: Path, public_id: Optional[str] = None) -> "GraphSource":
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
        self, graph: Optional[Graph] = None, public_id: Optional[str] = None
    ) -> Graph:
        if graph is None:
            graph = Graph()
        graph.parse(
            source=self.path,
            format=self.format,
            publicID=self.public_id if public_id is None else public_id,
        )
        return graph


def load_sources(
    *sources: GraphSourceType,
    graph: Optional[Graph] = None,
    public_id: Optional[str] = None,
) -> Graph:
    if graph is None:
        graph = Graph()
    for source in sources:
        GraphSource.from_source(source).load(graph, public_id)
    return graph


@lru_cache(maxsize=None)
def cached_graph(
    sources: Tuple[Union[GraphSource, Path], ...], public_id: Optional[str] = None
) -> Graph:
    return load_sources(*sources, public_id=public_id)
