from __future__ import annotations

import pytest

from rdflib.contrib.graphdb.util import (
    extract_filename_from_content_disposition,
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
