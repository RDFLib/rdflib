# devtools

This directory contains development related scripts and files.

`coverage_artifacts.py` checks the Validate workflow's expected coverage artifacts
and combines the downloaded data. Its regression tests run in Validate's
`extra-tasks` job. Run them locally with:

```sh
uv run --frozen --only-group coverage python -m unittest discover -v -s devtools -p test_coverage_artifacts.py
```
