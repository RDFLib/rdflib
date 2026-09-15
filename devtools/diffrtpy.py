#!/usr/bin/env python
"""
This is a tool that can be used with git difftool to generate a diff that
ignores type hints and comments.

The name of this script, `diffrtpy` is short for "diff runtime python", as
this will only compare the parts of the python code that has a runtime impact.

This is to make it easier to review PRs that contain type hints.

To use this script

```bash
task run -- python -m pip install --upgrade strip-hints black python-minifier
PYLOGGING_LEVEL=INFO task run -- git difftool -y -x $(readlink -f devtools/diffrtpy.py) upstream/main | tee /var/tmp/compact.diff
```

Then attach `/var/tmp/compact.diff` to the PR.
"""

from __future__ import annotations

import argparse
import logging
import os
import sys
from dataclasses import dataclass, field
from difflib import unified_diff
from pathlib import Path

import black
import python_minifier
from strip_hints import strip_string_to_string


def clean_python(input: Path) -> str:
    code = input.read_text()
    try:
        code = strip_string_to_string(code, to_empty=True, strip_nl=True)
    except Exception:
        logging.warning(
            "failed to strip type hints from %s, falling back to using with type hints",
            input,
        )
        code = code
    code = python_minifier.minify(
        code,
        remove_annotations=True,
        remove_pass=False,
        remove_literal_statements=True,
        combine_imports=False,
        hoist_literals=False,
        rename_locals=False,
        rename_globals=False,
        remove_object_base=False,
        convert_posargs_to_args=False,
        preserve_shebang=True,
    )
    code = black.format_str(code, mode=black.FileMode())
    return code


@dataclass
class Application:
    parser: argparse.ArgumentParser = field(
        default_factory=lambda: argparse.ArgumentParser(add_help=True)
    )

    def __post_init__(self) -> None:
        parser = self.parser
        parser.add_argument(
            "-v",
            "--verbose",
            action="count",
            dest="verbosity",
            help="increase verbosity level",
        )
        parser.add_argument("lhs_file", nargs=1, type=str)
        parser.add_argument("rhs_file", nargs=1, type=str)
        parser.set_defaults(handler=self.handle)

    def run(self, args: list[str]) -> None:
        parse_result = self.parser.parse_args(args)

        verbosity = parse_result.verbosity
        if verbosity is not None:
            root_logger = logging.getLogger("")
            root_logger.propagate = True
            new_level = (
                root_logger.getEffectiveLevel()
                - (min(1, verbosity)) * 10
                - min(max(0, verbosity - 1), 9) * 1
            )
            root_logger.setLevel(new_level)

        logging.debug(
            "sys.executable = %s, args = %s, parse_result = %s, logging.level = %s",
            sys.executable,
            args,
            parse_result,
            logging.getLogger("").getEffectiveLevel(),
        )

        parse_result.handler(parse_result)

    def handle(self, parse_result: argparse.Namespace) -> None:
        logging.debug("entry ...")

        base = os.environ["BASE"]

        lhs_file: Path = Path(parse_result.lhs_file[0])
        rhs_file: Path = Path(parse_result.rhs_file[0])

        logging.debug(
            "base = %s, lhs_file = %s, rhs_file = %s", base, lhs_file, rhs_file
        )

        if lhs_file.name.endswith(".py") and rhs_file.name.endswith(".py"):
            lhs_file_content = clean_python(lhs_file)
            rhs_file_content = clean_python(rhs_file)
        else:
            lhs_file_content = lhs_file.read_text()
            rhs_file_content = rhs_file.read_text()

        lhs_file_lines = lhs_file_content.splitlines(keepends=True)
        rhs_file_lines = rhs_file_content.splitlines(keepends=True)

        sys.stdout.writelines(
            unified_diff(lhs_file_lines, rhs_file_lines, f"a/{base}", f"b/{base}", n=5)
        )


def main() -> None:
    logging.basicConfig(
        level=os.environ.get("PYLOGGING_LEVEL", logging.INFO),
        stream=sys.stderr,
        datefmt="%Y-%m-%dT%H:%M:%S",
        format=(
            "%(asctime)s.%(msecs)03d %(process)d %(thread)d %(levelno)03d:%(levelname)-8s "
            "%(name)-12s %(module)s:%(lineno)s:%(funcName)s %(message)s"
        ),
    )

    Application().run(sys.argv[1:])


if __name__ == "__main__":
    main()
