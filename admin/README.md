# Admin Tools

Tools to assist with RDFlib releases, like extracting all merged PRs from GitHub since last release and printing them into MArkdown lists.

To make a release of RDFLib, see the [Developer's Guide](https://rdflib.readthedocs.io/en/latest/developers.html).

## PR Changelog Summary

An alternative to the `get_merged_prs.py` script is to use the GitHub CL to get the list of PRs and pipe it into the `pr_markdown.py` script. The following command retrieves the list of PRs merged since the last release (`2025-09-19`) from a particular branch (`7.x`).

```bash
gh api '/search/issues?q=repo:rdflib/rdflib+is:pr+is:merged+base:7.x+merged:>2025-10-24&per_page=100' | jq '{total_count, incomplete_results, items: [.items[] | {number, title, pull_request_merged_at: .pull_request.merged_at, pull_request_url: .pull_request.html_url, username: .user.login}]}' | poetry run python admin/pr_markdown.py
```
