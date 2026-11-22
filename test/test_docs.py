import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest


@pytest.mark.parametrize("docstring", ['"""An example with café text."""\n', ""])
@pytest.mark.parametrize("ending", ["\n", ""])
def test_generate_examples_without_importing(
    tmp_path: Path, docstring: str, ending: str
) -> None:
    project = tmp_path / "project"
    docs = project / "docs"
    docs.mkdir(parents=True)
    shutil.copyfile(
        Path(__file__).parents[1] / "docs/gen_ref_pages.py", docs / "gen_ref_pages.py"
    )
    examples = project / "examples"
    examples.mkdir()
    (examples / "__init__.py").write_text('"""Example programs."""', encoding="utf-8")
    code = 'raise RuntimeError("Examples must not be imported while building docs")\n'
    (examples / "tutorial.py").write_text(
        docstring + code.rstrip("\n") + ending, encoding="utf-8"
    )

    # Model the editable installation: rdflib is importable, examples is not.
    installed = tmp_path / "installed"
    (installed / "rdflib").mkdir(parents=True)
    (installed / "rdflib/__init__.py").touch()
    working = tmp_path / "working"
    working.mkdir()
    result = subprocess.run(
        [sys.executable, str(docs / "gen_ref_pages.py")],
        cwd=working,
        env={**os.environ, "PYTHONPATH": str(installed)},
        capture_output=True,
        text=True,
        check=True,
        timeout=10,
    )

    assert "Error processing examples" not in result.stdout
    index = (docs / "apidocs/examples.md").read_text(encoding="utf-8")
    assert "Example programs." in index
    assert "[tutorial](examples.tutorial.md)" in index
    page = (docs / "apidocs/examples.tutorial.md").read_text(encoding="utf-8")
    assert "{ #examples.tutorial }" in page
    assert f"```python\n{code}```" in page
    if docstring:
        assert "An example with café text." in page.split("```python")[0]
