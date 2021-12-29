import pytest
from pathlib import Path
import sys


try:
    import pandas  # noqa: F401
    import tabulate  # noqa: F401
except ImportError:
    pytestmark = pytest.mark.skip(
        reason="No os.fork() and/or os.pipe() on this platform, skipping"
    )


def test_external() -> None:
    """
    Run the tests from the custom framework used in ``translate_algebra/``.
    """

    translate_algebra_path = Path(__file__).absolute().parent / "translate_algebra"
    sys.path.append(f"{translate_algebra_path}")

    # this will trigger the algebra tests
    from .translate_algebra import main
    from .translate_algebra.test_base import Test

    test: Test
    for test in main.t.tests:
        assert (
            test.yn_passed
        ), f"test #{test.test_number} {test.test_name} failed: {test.tc_desc}"
