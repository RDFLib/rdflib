"""Check matrix coverage artifacts before combining either download layout."""

from __future__ import annotations

import argparse
import fnmatch
import importlib
import itertools
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

from coverage import CoverageData
from coverage.exceptions import CoverageException


def load_workflow(path: Path) -> dict[str, Any]:
    # PyYAML is supplied by the coverage dependency group.
    return importlib.import_module("yaml").safe_load(path.read_text())


def expand_matrix(matrix: dict[str, Any]) -> list[dict[str, Any]]:
    axes = {
        key: values
        for key, values in matrix.items()
        if key not in {"include", "exclude"}
    }
    if any(not isinstance(values, list) for values in axes.values()):
        raise ValueError("Coverage artifact checking requires a static matrix")
    originals = (
        [dict(zip(axes, values)) for values in itertools.product(*axes.values())]
        if axes
        else []
    )
    originals = [
        row
        for row in originals
        if not any(
            all(row.get(key) == value for key, value in exclusion.items())
            for exclusion in matrix.get("exclude", [])
        )
    ]
    rows = [row.copy() for row in originals]
    additions = []
    for inclusion in matrix.get("include", []):
        matched = False
        for original, row in zip(originals, rows):
            # Includes may overwrite earlier additions, but never original axes.
            if all(
                key not in original or original[key] == value
                for key, value in inclusion.items()
            ):
                row.update(inclusion)
                matched = True
        if not matched:
            additions.append(inclusion.copy())
    return rows + additions


def expected_artifacts(workflow: dict[str, Any]) -> set[str]:
    job = workflow["jobs"]["validate"]
    upload = next(
        step for step in job["steps"] if step.get("name") == "Upload coverage data"
    )
    template = upload["with"]["name"]
    names = []
    for row in expand_matrix(job["strategy"]["matrix"]):
        name = re.sub(
            r"\$\{\{\s*matrix\.([\w-]+)\s*\}\}",
            lambda match: str(row.get(match[1], "")),
            template,
        )
        if "${{" in name:
            raise ValueError("Unsupported expression in coverage artifact name")
        names.append(name)
    if not names or len(set(names)) != len(names):
        raise ValueError("Coverage matrix must produce distinct artifact names")
    return set(names)


def coverage_files(
    workflow: dict[str, Any], pages: list[dict[str, Any]], directory: Path
) -> list[Path]:
    expected = expected_artifacts(workflow)
    download = next(
        step
        for step in workflow["jobs"]["coverage"]["steps"]
        if step.get("name") == "Download coverage data"
    )
    available = {
        artifact["name"]
        for page in pages
        for artifact in page["artifacts"]
        if not artifact["expired"]
        and fnmatch.fnmatchcase(artifact["name"], download["with"]["pattern"])
    }
    missing = expected - available
    if missing:
        raise ValueError(
            "Missing coverage artifacts: "
            + ", ".join(sorted(missing))
            + ". Rerun all jobs to regenerate the full coverage set."
        )
    files = []
    empty = []
    for name in sorted(expected):
        root = directory / name
        # download-artifact extracts a sole matching artifact directly to path.
        if len(available) == 1 and not root.is_dir():
            root = directory
        paths = sorted(path for path in root.rglob(".coverage.*") if path.is_file())
        if not paths:
            empty.append(name)
        for path in paths:
            if not path.stat().st_size:
                raise ValueError(
                    f"Empty coverage data in artifact {name}: {path}. "
                    "Rerun all jobs to regenerate the full coverage set."
                )
            data = CoverageData(basename=str(path))
            data.read()  # Fail on corrupt data rather than letting combine skip it.
            if not data.measured_files():
                raise ValueError(
                    f"No measured files in coverage artifact {name}: {path}"
                )
        files.extend(paths)
    if empty:
        raise ValueError(
            "No coverage data in artifacts: "
            + ", ".join(empty)
            + ". Rerun all jobs to regenerate the full coverage set."
        )
    return files


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("artifacts", type=Path, help="paginated gh api --slurp JSON")
    parser.add_argument("directory", type=Path)
    parser.add_argument(
        "--workflow", type=Path, default=Path(".github/workflows/validate.yaml")
    )
    args = parser.parse_args(argv)
    try:
        workflow = load_workflow(args.workflow)
        paths = coverage_files(
            workflow, json.loads(args.artifacts.read_text()), args.directory
        )
    except (ValueError, OSError, CoverageException) as error:
        print(f"::error::{error}", file=sys.stderr)
        return 1
    subprocess.run(
        [sys.executable, "-m", "coverage", "combine", "--keep", *map(str, paths)],
        check=True,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
