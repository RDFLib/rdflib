from __future__ import annotations

import urllib.request
from contextlib import contextmanager
from typing import Generator, Optional
from urllib.request import OpenerDirector, install_opener


@contextmanager
def context_urlopener(opener: OpenerDirector) -> Generator[OpenerDirector, None, None]:
    old_opener: Optional[OpenerDirector] = urllib.request._opener  # type: ignore[attr-defined]
    try:
        install_opener(opener)
        yield opener
    finally:
        install_opener(old_opener)  # type: ignore[arg-type]
