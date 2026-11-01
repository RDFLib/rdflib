# Agent guide

Conventions are in `docs/developers.md` (branch targets, breaking changes,
deprecation, tests, static checks) and `docs/type_hints.md`. For changes that
touch network, file or remote-endpoint access, also read
`docs/security_considerations.md`.

## Before starting a change

List the open PRs that touch the files you will change, and build on any that
overlap:

```bash
gh pr list --repo RDFLib/rdflib --state open --limit 300 --json number,title,files \
  --jq '.[] | select(any(.files[]; .path | test("PATH_REGEX"))) | "#\(.number) \(.title)"'
```

## Checks

- Run the tests for the area you changed with `uv run pytest <paths>`:
  - `rdflib/plugins/sparql/`: `test/test_sparql`, plus
    `test/test_w3c_spec/test_sparql10_w3c.py`, `test_sparql11_w3c.py` and
    `test_sparql_rdflib.py`.
  - Parsers and serializers: `test/test_parsers`, `test/test_serializers` and
    the matching `test/test_w3c_spec/test_*_w3c.py`.
- Static checks: `task validate:static` (Ruff linting and formatting, and mypy), then
  `uv lock --check`.
- Test runs rewrite the tracked EARL reports in `test_reports/*-HEAD.ttl`, and
  a partial run leaves a partial report. Restore them with
  `git checkout -- test_reports/` before committing, unless your change is
  meant to alter test outcomes.

## Pull requests

- `CHANGELOG.md` is updated in release-prep PRs only.
- `gh pr create --body` skips the template, so fill in
  `.github/PULL_REQUEST_TEMPLATE.md` yourself.
