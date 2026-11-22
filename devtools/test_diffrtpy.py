"""Regression tests for normalizing runtime Python with Ruff."""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().with_name("diffrtpy.py")


class DiffRuntimePythonTest(unittest.TestCase):
    def diff(self, lhs: str, rhs: str) -> str:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            left = root / "left.py"
            right = root / "right.py"
            left.write_text(lhs)
            right.write_text(rhs)
            # Formatting must be consistent regardless of the caller's config.
            (root / "pyproject.toml").write_text(
                '[tool.ruff.format]\nquote-style = "single"\n'
            )
            return subprocess.run(
                [sys.executable, str(SCRIPT), str(left), str(right)],
                cwd=root,
                env={**os.environ, "BASE": "sample.py"},
                capture_output=True,
                text=True,
                check=True,
            ).stdout

    def test_ignores_annotations_comments_and_formatting(self) -> None:
        self.assertEqual(
            self.diff(
                "# A comment\ndef add(value: int) -> int:\n    return value+1\n",
                "def add(value): return value + 1\n",
            ),
            "",
        )

    def test_preserves_runtime_changes(self) -> None:
        result = self.diff(
            "def add(value):\n    return value + 1\n",
            "def add(value):\n    return value + 2\n",
        )
        self.assertIn("-    return value + 1\n", result)
        self.assertIn("+    return value + 2\n", result)

    def test_ignores_local_formatter_configuration(self) -> None:
        result = self.diff("value = 'old'\n", "value = 'new'\n")
        self.assertIn('-value = "old"\n', result)
        self.assertIn('+value = "new"\n', result)


if __name__ == "__main__":
    unittest.main()
