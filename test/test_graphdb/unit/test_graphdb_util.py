from __future__ import annotations

import pytest

from rdflib.contrib.graphdb.util import (
    extract_filename_from_content_disposition,
    infer_filename_from_fileobj,
    sanitize_filename,
)
from rdflib.contrib.rdf4j import has_httpx

pytestmark = pytest.mark.skipif(
    not has_httpx, reason="skipping graphdb tests, httpx not available"
)


@pytest.mark.parametrize(
    "raw, expected",
    [
        ("backup.tar", "backup.tar"),
        ("'backup.tar'", "backup.tar"),
        ('"backup.tar"', "backup.tar"),
        ("path/to/backup.tar", "backup.tar"),
        ("path\\to\\backup.tar", "backup.tar"),
        ("../../evil.tar", "evil.tar"),
        ("..\\..\\evil.tar", "evil.tar"),
        ("", None),
        ("   ", None),
        (".", None),
        ("..", None),
    ],
)
def test_sanitize_filename(raw: str, expected: str | None):
    assert sanitize_filename(raw) == expected


@pytest.mark.parametrize(
    "header, expected",
    [
        ("attachment; filename=backup.tar", "backup.tar"),
        ("attachment; filename='backup.tar'", "backup.tar"),
        ('attachment; filename="backup.tar"', "backup.tar"),
        ("attachment; filename=../../evil.tar", "evil.tar"),
        ("attachment; filename=..", None),
        ("attachment; filename=", None),
        ("", None),
        # Prefer filename*= when present
        (
            "attachment; filename=plain.tar; filename*=UTF-8''preferred.tar",
            "preferred.tar",
        ),
        # RFC 5987 decoding + unquoting
        ("attachment; filename*=UTF-8''backup%20file.tar", "backup file.tar"),
        ("attachment; filename*=UTF-8'en'backup%20file.tar", "backup file.tar"),
        # Invalid charset falls back to utf-8
        ("attachment; filename*=X-UNKNOWN''backup.tar", "backup.tar"),
        # Malformed filename*= falls back to treating value as raw
        ("attachment; filename*=badformat", "badformat"),
    ],
)
def test_extract_filename_from_content_disposition(header: str, expected: str | None):
    assert extract_filename_from_content_disposition(header) == expected


class _FileLike:
    def __init__(self, name):
        self.name = name


@pytest.mark.parametrize(
    "file_obj, fallback, expected",
    [
        (_FileLike("/path/to/backup.tar"), "fallback.tar", "backup.tar"),
        (_FileLike("path\\to\\backup.tar"), "fallback.tar", "backup.tar"),
        (_FileLike("'backup.tar'"), "fallback.tar", "backup.tar"),
        (_FileLike("  backup.tar  "), "fallback.tar", "backup.tar"),
        (_FileLike("../../evil.tar"), "fallback.tar", "evil.tar"),
        (_FileLike(""), "fallback.tar", "fallback.tar"),
        (_FileLike("."), "fallback.tar", "fallback.tar"),
        (_FileLike(".."), "fallback.tar", "fallback.tar"),
        (_FileLike(None), "fallback.tar", "fallback.tar"),
        (_FileLike(123), "fallback.tar", "fallback.tar"),
        (object(), "fallback.tar", "fallback.tar"),
    ],
)
def test_infer_filename_from_fileobj(file_obj, fallback: str, expected: str):
    assert infer_filename_from_fileobj(file_obj, fallback) == expected
