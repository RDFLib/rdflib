#!/usr/bin/env python
"""
Testing with Nose
=================

This test runner uses Nose for test discovery and running. It uses the argument
spec of Nose, but with some options pre-set. To begin with, make sure you have
Nose installed, e.g.:

    $ pip install nose

To run the tests, use:

    $ ./run_tests.py
If you supply attributes, the default ones defined in ``DEFAULT_ATTRS`` will be
ignored. So to run e.g. all tests marked ``slowtest`` or ``non_standard_dep``,
do:

    $ ./run_tests.py -a slowtest,non_standard_dep

For more details check <https://rdflib.readthedocs.io/en/stable/developers.html>.

Coverage
========

If ``coverage.py`` is placed in $PYTHONPATH, it can be used to create coverage
information (using the built-in coverage plugin of Nose) if the default
option "--with-coverage" is supplied (which also enables some additional
coverage options).

See <http://nedbatchelder.com/code/modules/coverage.html> for details.

"""

NOSE_ARGS = [
    "--with-doctest",
    "--doctest-extension=.doctest",
    "--doctest-tests",
    # '--with-EARL',
]

COVERAGE_EXTRA_ARGS = [
    "--cover-package=rdflib",
    "--cover-inclusive",
]

DEFAULT_LOCATION = "--where=./"

DEFAULT_ATTRS = []  # ['!known_issue', '!sparql']

DEFAULT_DIRS = ["test", "rdflib"]


if __name__ == "__main__":

    from sys import argv, exit, stderr

    try:
        import nose
    except ImportError:
        print(
            """\
    Requires Nose. Try:

        $ pip install nose

    Exiting. """,
            file=stderr,
        )
        exit(1)

    if "--with-coverage" in argv:
        try:
            import coverage
        except ImportError:
            print("No coverage module found, skipping code coverage.", file=stderr)
            argv.remove("--with-coverage")
        else:
            NOSE_ARGS += COVERAGE_EXTRA_ARGS

    if True not in [a.startswith("-a") or a.startswith("--attr=") for a in argv]:
        argv.append("--attr=" + ",".join(DEFAULT_ATTRS))

    if not [a for a in argv[1:] if not a.startswith("-")]:
        argv += DEFAULT_DIRS  # since nose doesn't look here by default..

    if not [a for a in argv if a.startswith("--where=")]:
        argv += [DEFAULT_LOCATION]

    finalArgs = argv + NOSE_ARGS
    print("Running nose with:", " ".join(finalArgs[1:]))
    nose.run_exit(argv=finalArgs)
