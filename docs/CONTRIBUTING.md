# RDFLib Contributing Guide

Thank you for considering contributing to RDFLib. This project has no formal
funding or full-time maintainers, and relies entirely on independent
contributors to keep it alive and relevant.

## Ways to contribute

Some ways in which you can contribute to RDFLib are:

- Address open issues:
  [![GitHub issues](https://img.shields.io/github/issues/RDFLib/rdflib)](https://github.com/RDFLib/rdflib/issues)
- Fix
  [expected failure](https://docs.pytest.org/en/latest/how-to/skipping.html#xfail-mark-test-functions-as-expected-to-fail)
  tests: [![GitHub search query](https://img.shields.io/badge/GitHub-search-green)](https://github.com/search?q=xfail+repo%3ARDFLib%2Frdflib+path%3Atest%2F**.py&amp%3Btype=code&type=code)
- Add additional
  [expected failure](https://docs.pytest.org/en/latest/how-to/skipping.html#xfail-mark-test-functions-as-expected-to-fail)
  tests for open issues:
  [![GitHub issues](https://img.shields.io/github/issues/RDFLib/rdflib)](https://github.com/RDFLib/rdflib/issues)
- Add tests for untested code:
  [![Coveralls branch](https://img.shields.io/coveralls/RDFLib/rdflib/main.svg)](https://coveralls.io/r/RDFLib/rdflib?branch=main)
- Review pull requests marked with the
  [![review wanted](https://img.shields.io/badge/-review%20wanted-28ead2)](https://github.com/RDFLib/rdflib/labels/review%20wanted)
  label.
- Answer questions on Stack Overflow:
  [![Stack Exchange questions](https://img.shields.io/stackexchange/stackoverflow/t/rdflib)](https://stackoverflow.com/questions/tagged/rdflib)
- Convert
  [`unittest`](https://docs.python.org/3/library/unittest.html)
  based tests to
  [`pytest`](https://docs.pytest.org/en/latest/)
  based tests:
  [![GitHub search query](https://img.shields.io/badge/GitHub-search-green)](https://github.com/search?q=unittest+repo%3ARDFLib%2Frdflib+path%3Atest%2F**.py&type=code)
- Add, correct or improve docstrings:
  [![rtd latest](https://img.shields.io/badge/docs-latest-informational)](https://rdflib.readthedocs.io/en/latest/)
- Update the RDFLib Wikipedia entry:
  [![Wikipedia: RDFLib](https://img.shields.io/badge/Wikipedia-RDFLib-informational)](https://en.wikipedia.org/wiki/RDFLib)
- Update the RDFLib Wikidata entry:
  [![Wikidata: Q7276224](https://img.shields.io/badge/Wikidata-Q7276224-informational)](https://www.wikidata.org/wiki/Q7276224)
- Participate on Gitter/Matrix chat:
  [![Gitter](https://badges.gitter.im/RDFLib/rdflib.svg)](https://gitter.im/RDFLib/rdflib?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge) [![Matrix](https://img.shields.io/matrix/rdflib:matrix.org?label=matrix.org%20chat)](https://matrix.to/#/#RDFLib_rdflib:gitter.im)
- Participate in GitHub discussions:
  [![GitHub Discussions](https://img.shields.io/github/discussions/RDFLib/rdflib)](https://github.com/RDFLib/rdflib/discussions)
- Fix linting failures (see ruff settings in `pyproject.toml` and `#
  noqa:` directives in the codebase).

## Pull Requests

Contributions that involve changes to the RDFLib repository have to be made with
pull requests and should follow the [RDFLib developers guide](./developers.rst).

For changes that add features or affect the public API of RDFLib, it is
recommended to first open an issue to discuss the change before starting to work
on it. That way you can get feedback on the design of the feature before
spending time on it.

## Code of Conduct

All contributions to the project should be consistent with the [code of
conduct](./CODE_OF_CONDUCT.md) adopted by RDFLib.
