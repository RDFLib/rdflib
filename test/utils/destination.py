import enum
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path, PurePath
from typing import IO, Callable, Generator, Optional, TextIO, Union

DestParmType = Union[Path, PurePath, str, IO[bytes], TextIO]


@dataclass(frozen=True)
class DestRef:
    param: DestParmType
    path: Path


class DestinationType(str, enum.Enum):
    RETURN = enum.auto()
    PATH = enum.auto()
    PURE_PATH = enum.auto()
    STR_PATH = enum.auto()
    FILE_URI = enum.auto()
    BINARY_IO = enum.auto()
    TEXT_IO = enum.auto()

    @contextmanager
    def make_ref(
        self,
        tmp_path: Path,
        encoding: Optional[str] = None,
        path_factory: Callable[[Path, "DestinationType", Optional[str]], Path] = (
            lambda tmp_path, type, encoding: tmp_path / f"file-{type.name}-{encoding}"
        ),
    ) -> Generator[Optional[DestRef], None, None]:
        path = path_factory(tmp_path, self, encoding)
        # path = tmp_path / f"file-{self.name}"
        if self is DestinationType.RETURN:
            yield None
        elif self is DestinationType.PATH:
            yield DestRef(path, path)
        elif self is DestinationType.PURE_PATH:
            yield DestRef(PurePath(path), path)
        elif self is DestinationType.STR_PATH:
            yield DestRef(f"{path}", path)
        elif self is DestinationType.FILE_URI:
            yield DestRef(path.as_uri(), path)
        elif self is DestinationType.BINARY_IO:
            with path.open("wb") as bfh:
                yield DestRef(bfh, path)
        elif self is DestinationType.TEXT_IO:
            assert encoding is not None
            with path.open("w", encoding=encoding) as fh:
                yield DestRef(fh, path)
        else:
            raise ValueError(f"unsupported type {type!r}")
