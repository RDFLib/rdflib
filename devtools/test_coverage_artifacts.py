"""Regression tests for the Validate workflow's coverage artifact helper."""

from __future__ import annotations

import copy
import importlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr
from pathlib import Path
from unittest.mock import patch

from coverage import CoverageData
from coverage_artifacts import (
    coverage_files,
    expand_matrix,
    expected_artifacts,
    load_workflow,
    main,
)

WORKFLOW = Path(__file__).resolve().parents[1] / ".github/workflows/validate.yaml"


class CoverageArtifactsTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.directory = self.root / "coverage downloads"
        self.workflow = load_workflow(WORKFLOW)
        self.workflow["jobs"]["validate"]["strategy"]["matrix"] = {
            "python-version": ["3.13"],
            "os": ["ubuntu-latest", "windows-latest"],
            "suffix": [""],
        }
        self.names = sorted(expected_artifacts(self.workflow))
        # Include an unrelated artifact and split the response across API pages.
        self.pages = [
            {"artifacts": [{"name": self.names[0], "expired": False}]},
            {
                "artifacts": [
                    {"name": self.names[1], "expired": False},
                    {"name": "pytest-junit-xml", "expired": False},
                ]
            },
        ]
        self.source = self.root / "sample.py"
        self.source.write_text("x = 1\ny = 2\n")

    def write_data(self, directory, lines=(1,)):
        directory.mkdir(parents=True, exist_ok=True)
        path = directory / ".coverage.worker.123"
        data = CoverageData(basename=str(path))
        data.add_lines({str(self.source): set(lines)})
        data.write()
        return path

    def cli_args(self):
        workflow = self.root / "workflow.yaml"
        workflow.write_text(importlib.import_module("yaml").safe_dump(self.workflow))
        artifacts = self.root / "artifacts.json"
        artifacts.write_text(json.dumps(self.pages))
        return [str(artifacts), str(self.directory), "--workflow", str(workflow)]

    def assert_rejected(self, message):
        output = io.StringIO()
        with (
            patch("coverage_artifacts.subprocess.run") as combine,
            redirect_stderr(output),
        ):
            self.assertEqual(main(self.cli_args()), 1)
        combine.assert_not_called()
        self.assertIn(message, output.getvalue())

    def test_complete_paginated_multiple_artifact_layout(self):
        paths = [self.write_data(self.directory / name) for name in self.names]
        self.assertEqual(
            coverage_files(self.workflow, self.pages, self.directory), paths
        )
        with patch("coverage_artifacts.subprocess.run") as combine:
            self.assertEqual(main(self.cli_args()), 0)
        self.assertEqual(combine.call_args.args[0][-2:], list(map(str, paths)))

    def test_single_artifact_flat_and_nested_layouts(self):
        self.workflow["jobs"]["validate"]["strategy"]["matrix"]["os"] = [
            "ubuntu-latest"
        ]
        self.pages = self.pages[:1]
        for nested in (False, True):
            with self.subTest(nested=nested):
                directory = self.directory / str(nested)
                path = self.write_data(
                    directory / self.names[0] if nested else directory
                )
                self.assertEqual(
                    coverage_files(self.workflow, self.pages, directory), [path]
                )

    def test_selective_rerun_missing_artifacts_names_them_and_stops_combine(self):
        self.workflow = load_workflow(WORKFLOW)
        remaining = "coverage-3.10-ubuntu-latest-extensive-min"
        self.pages = [{"artifacts": [{"name": remaining, "expired": False}]}]
        self.write_data(self.directory)
        missing = sorted(expected_artifacts(self.workflow) - {remaining})
        self.assertEqual(len(missing), 17)
        self.assert_rejected("Missing coverage artifacts: " + ", ".join(missing))
        self.assert_rejected("Rerun all jobs")

    def test_no_artifacts(self):
        self.pages = [{"artifacts": []}]
        self.assert_rejected("Missing coverage artifacts: " + ", ".join(self.names))

    def test_expired_artifact_is_missing(self):
        self.pages[1]["artifacts"][0]["expired"] = True
        self.assert_rejected("Missing coverage artifacts: " + self.names[1])

    def test_empty_download(self):
        self.directory.mkdir()
        self.assert_rejected("No coverage data in artifacts: " + ", ".join(self.names))

    def test_one_artifact_has_no_data(self):
        self.write_data(self.directory / self.names[0])
        empty = self.directory / self.names[1]
        empty.mkdir()
        (empty / ".coverage.directory").mkdir()
        self.assert_rejected("No coverage data in artifacts: " + self.names[1])

    def test_zero_byte_file_alongside_valid_data_stops_combine(self):
        for single in (False, True):
            with self.subTest(single=single):
                if single:
                    self.workflow["jobs"]["validate"]["strategy"]["matrix"]["os"] = [
                        "ubuntu-latest"
                    ]
                    self.pages = self.pages[:1]
                    self.directory = self.root / "single download"
                    directory = self.directory
                    self.write_data(directory)
                else:
                    for name in self.names:
                        self.write_data(self.directory / name)
                    directory = self.directory / self.names[0]
                (directory / ".coverage.truncated").touch()
                self.assert_rejected("Empty coverage data in artifact " + self.names[0])
                self.assert_rejected(".coverage.truncated")

    def test_zero_byte_file_without_other_data_stops_combine(self):
        self.write_data(self.directory / self.names[0])
        empty = self.directory / self.names[1]
        empty.mkdir()
        (empty / ".coverage.empty").touch()
        self.assert_rejected("Empty coverage data in artifact " + self.names[1])

    def test_corrupt_data_stops_combine(self):
        for name in self.names:
            self.write_data(self.directory / name)
        (self.directory / self.names[1] / ".coverage.worker.123").write_text("corrupt")
        result = subprocess.run(
            [
                sys.executable,
                str(WORKFLOW.parents[2] / "devtools/coverage_artifacts.py"),
                *self.cli_args(),
            ],
            cwd=self.root,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("Couldn't use data file", result.stderr)
        self.assertFalse((self.root / ".coverage").exists())

    def test_complete_layouts_combine_real_data_without_shell_globbing(self):
        for single in (False, True):
            with self.subTest(single=single):
                if single:
                    self.workflow["jobs"]["validate"]["strategy"]["matrix"]["os"] = [
                        "ubuntu-latest"
                    ]
                    self.pages = self.pages[:1]
                    self.directory = self.root / "single download"
                    paths = [self.write_data(self.directory, (1, 2))]
                else:
                    paths = [
                        self.write_data(self.directory / name, (index + 1,))
                        for index, name in enumerate(self.names)
                    ]
                result = subprocess.run(
                    [
                        sys.executable,
                        str(WORKFLOW.parents[2] / "devtools/coverage_artifacts.py"),
                        *self.cli_args(),
                    ],
                    cwd=self.root,
                    capture_output=True,
                    text=True,
                )
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                combined = CoverageData(basename=str(self.root / ".coverage"))
                combined.read()
                self.assertEqual(set(combined.lines(str(self.source))), {1, 2})
                self.assertTrue(all(path.is_file() for path in paths))  # --keep


class MatrixTest(unittest.TestCase):
    def test_real_matrix_and_upload_template(self):
        workflow = load_workflow(WORKFLOW)
        names = expected_artifacts(workflow)
        self.assertEqual(len(names), 18)
        self.assertIn("coverage-3.10-ubuntu-latest-extensive-min", names)
        self.assertIn("coverage-3.11-ubuntu-latest", names)
        self.assertNotIn("coverage-3.11-ubuntu-latest-docs", names)
        # A changed matrix axis and upload name must affect expectations directly.
        changed = copy.deepcopy(workflow)
        changed["jobs"]["validate"]["strategy"]["matrix"]["python-version"].append(
            "3.15"
        )
        upload = next(
            step
            for step in changed["jobs"]["validate"]["steps"]
            if step.get("name") == "Upload coverage data"
        )
        upload["with"]["name"] += "-new"
        self.assertIn("coverage-3.15-windows-latest-new", expected_artifacts(changed))
        self.assertEqual(len(expected_artifacts(changed)), 21)

    def test_documented_include_semantics(self):
        self.assertEqual(
            expand_matrix(
                {
                    "fruit": ["apple", "pear"],
                    "animal": ["cat", "dog"],
                    "include": [
                        {"color": "green"},
                        {"color": "pink", "animal": "cat"},
                        {"fruit": "apple", "shape": "circle"},
                        {"fruit": "banana"},
                        {"fruit": "banana", "animal": "cat"},
                    ],
                }
            ),
            [
                {"fruit": "apple", "animal": "cat", "color": "pink", "shape": "circle"},
                {
                    "fruit": "apple",
                    "animal": "dog",
                    "color": "green",
                    "shape": "circle",
                },
                {"fruit": "pear", "animal": "cat", "color": "pink"},
                {"fruit": "pear", "animal": "dog", "color": "green"},
                {"fruit": "banana"},
                {"fruit": "banana", "animal": "cat"},
            ],
        )

    def test_exclude_then_include_can_restore_a_combination(self):
        self.assertEqual(
            expand_matrix(
                {
                    "os": ["linux", "windows"],
                    "exclude": [{"os": "windows"}],
                    "include": [{"os": "windows", "extra": True}],
                }
            ),
            [{"os": "linux"}, {"os": "windows", "extra": True}],
        )

    def test_include_only_matrix(self):
        self.assertEqual(
            expand_matrix({"include": [{"os": "linux"}, {"os": "windows"}]}),
            [{"os": "linux"}, {"os": "windows"}],
        )

    def test_dynamic_matrix_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "static matrix"):
            expand_matrix({"os": "${{ fromJSON(needs.setup.outputs.os) }}"})


if __name__ == "__main__":
    unittest.main()
