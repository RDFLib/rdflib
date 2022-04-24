# Notation3 Tests

Tests exist for [N3 grammar](N3Tests/manifest.ttl), [N3 reasoning](N3Tests/manifest-reasoner.ttl), [extended N3 grammar](N3Tests/manifest-extended.ttl) and appropriate [Turtle](TurtleTests/manifest.ttl) tests.

# Design

In general, tests are described as Positive or Negative Syntax tests, Evaluation Test, and Reason tests. Syntax tests simply check that the data can be parsed properly; negative syntax tests should generate an error.

Evaluation tests check whether the input (`action`) can be parsed into a dataset which is isomorphic to those described in `results`.

Reason tests invoke the Notation3 reasoner, with various options, and check that the results are isomorphic to those described in `results`.

Tests should be run with an assumed base URI of their associated manifest, either `https://w3c.github.io/N3/tests/N3Tests` or `https://w3c.github.io/N3/tests/TurtleTests`.

# Contributing

If you would like to contribute a new test or a fix to an existing test,
please file an [issue](https://github.com/w3c/N3/issues) and/or create a [pull request](https://github.com/w3c/N3/pulls).
