from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from rdflib.tools.graphisomorphism import IsomorphicTestableGraph


def test_isomorphic_testable_graph_parse_and_compare() -> None:
    nt_a = '_:b1 <urn:ex:p> "val" .\n_:b1 <urn:ex:q> <urn:ex:o> .\n'
    nt_b = '_:b2 <urn:ex:q> <urn:ex:o> .\n_:b2 <urn:ex:p> "val" .\n'
    nt_c = '_:b3 <urn:ex:p> "other" .\n_:b3 <urn:ex:q> <urn:ex:o> .\n'

    g1 = IsomorphicTestableGraph().parse(data=nt_a, format="nt")
    g2 = IsomorphicTestableGraph().parse(data=nt_b, format="nt")
    g3 = IsomorphicTestableGraph().parse(data=nt_c, format="nt")

    assert g1 == g2
    assert not (g1 != g2)
    assert g1 != g3
    assert isinstance(hash(g1), int)


def test_graphisomorphism_cli_isomorphic_files(tmp_path: Path) -> None:
    file_a = tmp_path / "a.nt"
    file_b = tmp_path / "b.nt"
    file_a.write_text('_:b1 <urn:ex:p> "val" .\n', encoding="utf-8")
    file_b.write_text('_:b2 <urn:ex:p> "val" .\n', encoding="utf-8")

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "rdflib.tools.graphisomorphism",
            "--format=nt",
            str(file_a),
            str(file_b),
        ],
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, completed.stderr


def test_graphisomorphism_cli_non_isomorphic_files(tmp_path: Path) -> None:
    file_a = tmp_path / "a.nt"
    file_b = tmp_path / "b.nt"
    file_a.write_text('_:b1 <urn:ex:p> "val1" .\n', encoding="utf-8")
    file_b.write_text('_:b2 <urn:ex:p> "val2" .\n', encoding="utf-8")

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "rdflib.tools.graphisomorphism",
            "--format=nt",
            str(file_a),
            str(file_b),
        ],
        capture_output=True,
        text=True,
    )
    assert completed.returncode != 0
    assert f"{file_a} != {file_b}" in completed.stderr


def test_graphisomorphism_cli_stdin(tmp_path: Path) -> None:
    file_a = tmp_path / "a.nt"
    file_a.write_text('_:b1 <urn:ex:p> "val" .\n', encoding="utf-8")

    match_proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "rdflib.tools.graphisomorphism",
            "--stdin",
            "--format=nt",
            str(file_a),
        ],
        input='_:b9 <urn:ex:p> "val" .\n',
        capture_output=True,
        text=True,
    )
    assert match_proc.returncode == 0, match_proc.stderr

    mismatch_proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "rdflib.tools.graphisomorphism",
            "--stdin",
            "--format=nt",
            str(file_a),
        ],
        input='_:b9 <urn:ex:p> "other" .\n',
        capture_output=True,
        text=True,
    )
    assert mismatch_proc.returncode != 0
    assert f"(STDIN) != {file_a}" in mismatch_proc.stderr
