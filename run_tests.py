"""
# Testing with pytest

This test runner uses pytest for test discovery and running. It uses the argument
spec of pytest, but with some options pre-set. To begin with, make sure you have
pytest installed, e.g.:

```bash
poetry add pytest
```

To run the tests, use:

```bash
./run_tests.py
```

For more details check https://rdflib.readthedocs.io/en/stable/developers.html.

## Coverage

If `pytest-cov` is placed in $PYTHONPATH, it can be used to create coverage
information if the "--cov" option is supplied.

See https://github.com/pytest-dev/pytest-cov for details.
"""

import json
import sys

if __name__ == "__main__":
    try:
        import pytest
    except ImportError:
        print(
            """\
    Requires pytest. Try:

        $ pip install pytest

    Exiting. """,
            file=sys.stderr,
        )
        exit(1)

    finalArgs = sys.argv[1:]  # noqa: N816
    print("Running pytest with:", json.dumps(finalArgs))
    sys.exit(pytest.main(args=finalArgs))
