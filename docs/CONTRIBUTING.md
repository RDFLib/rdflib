# RDFLib Contributing Guide

Thank you for considering contributing to RDFLib. This project has no formal
funding or full-time maintainers, and relies entirely on independent
contributors to keep it alive and relevant.

## Which branch should I target?

Most pull requests should target `main`, the current major release branch.
Backwards-compatible bug fixes, documentation updates, dependency updates, and
new features should usually target `main`.

The `next` branch is reserved for work toward the next major release. Target
`next` only for breaking changes or other work that maintainers have identified
as next-major work.

Maintainers periodically merge `main` forward into `next`, so changes accepted
on `main` will be carried into next-major development when `next` catches up.

If you are unsure which branch to use, open the pull request against `main` and
ask for maintainer guidance.

## Charter

### Vision

The RDFLib community wishes to provide a free and open source toolkit for the manipulation
of RDF data.

This provision is for the community and by the community with contributors giving
their time and skills freely and asking for nothing in return, other than acknowledgements
of them as contributors.

The toolkit is released for use under the [BSD 3-Clause License](https://opensource.org/license/bsd-3-clause)
to be as permissible as possibly: users can do what they wish with the toolkit.

### Scope

The community implements what it perceives to be core RDF manipulation functions within the RDFLib main
library. It also implements specifications related to RDF, such as the SPARQL Query Language,
SHACL the Shapes Validation Language, RDFS and OWL reasoning and the parsing and
serialisation of RDF file formats. Some of these related implementations are modules
within RDFLib, others are stand-alone repositories within the RDFLib family. See <https://rdflib.dev>
for a listing.

The community encourages implementers of other RDFLib-related libraries to communicate them to us.

### Membership

There are no restrictions on users of, and contributors to RDFLib, therefore there is no strict
membership category. We ask only that contributors contribute according to the various technical
protocols in the [Developers guide](./developers.md) and the [Documentation guide](./docs.md).

### Governance

RDFLib had been governed by an evolving set of core developers over its 20+ year lifetime. There are
no strict rules as to who is or isn't a core developer and the recent practice for organisation has been
for the most involved developers to contact the mailing list and recent contributors directly to discuss
major releases and other issues.

If you would like to be involved in core development and/or governance, please just create an Issue in
the issue tracker about this, or contact the most active developers and/or the mailing list.


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
pull requests and should follow the [RDFLib developers guide](./developers.md).

For changes that add features or affect the public API of RDFLib, it is
recommended to first open an issue to discuss the change before starting to work
on it. That way you can get feedback on the design of the feature before
spending time on it.

## Code of Conduct

All contributions to the project should be consistent with the
[code of conduct](./CODE_OF_CONDUCT.md) adopted by RDFLib.
