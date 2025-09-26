import logging
import subprocess
import sys
from pathlib import Path
from typing import Iterable

import pytest
from _pytest.mark.structures import ParameterSet

FILE_PATH = Path(__file__)

EXAMPLES_DIR = FILE_PATH.parent.parent / "examples"


def generate_example_cases() -> Iterable[ParameterSet]:
    for example_file in EXAMPLES_DIR.glob("*.py"):
        if example_file.name == "__init__.py":
            # this is not an example ...
            continue
        yield pytest.param(example_file, id=f"{example_file.relative_to(EXAMPLES_DIR)}")


@pytest.mark.webtest
@pytest.mark.parametrize(["example_file"], generate_example_cases())
def test_example(example_file: Path) -> None:
    """
    The example runs without errors.
    """
    if example_file.name == "berkeleydb_example.py":
        # this example requires a berkeleydb installation
        pytest.skip("The BerkeleyDB example is not working correctly.")

    result = subprocess.run(
        [sys.executable, f"{example_file}"],
        capture_output=True,
    )

    logging.debug("result = %s", result)

    try:
        result.check_returncode()
    except subprocess.CalledProcessError as process_error:
        if process_error.returncode == 126:
            pytest.skip("This test returned 126 indikating to skip it.")
        raise
