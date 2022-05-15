from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Iterable, Optional, Tuple, Union

from rdflib.graph import Graph
from rdflib.util import guess_format


@dataclass(frozen=True)
class GraphSource:
    path: Path
    format: str

    @classmethod
    def from_path(cls, path: Path) -> "GraphSource":
        format = guess_format(f"{path}")
        if format is None:
            raise ValueError(f"could not guess format for source {path}")

        return cls(path, format)

    @classmethod
    def from_paths(cls, paths: Iterable[Path]) -> Tuple["GraphSource", ...]:
        result = []
        for path in paths:
            result.append(cls.from_path(path))
        return tuple(result)


@lru_cache(maxsize=None)
def cached_graph(
    sources: Tuple[Union[GraphSource, Path], ...], format: Optional[str] = None
) -> Graph:
    graph = Graph()
    for source in sources:
        if isinstance(source, Path):
            source = GraphSource.from_path(source)
        graph.parse(source=source.path, format=source.format)
    return graph
