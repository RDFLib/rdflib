import os
from contextlib import contextmanager
from pathlib import PurePath
from typing import Iterator, TypeVar, Union

PathLike = Union[PurePath, str]
PathLikeT = TypeVar("PathLikeT", bound=PathLike)


@contextmanager
def ctx_chdir(newdir: PathLikeT) -> Iterator[PathLikeT]:
    cwd = os.getcwd()
    try:
        os.chdir(f"{newdir}")
        yield newdir
    finally:
        os.chdir(cwd)
