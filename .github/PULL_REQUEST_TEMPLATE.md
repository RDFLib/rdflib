<!--
Thank you for your contribution to this project. This project has no formal
funding or full-time maintainers, and relies entirely on independent
contributors to keep it alive and relevant.

This pull request template includes some guidelines intended to help
contributors, not to deter contributions. While we prefer that PRs follow our
guidelines, we will not reject PRs solely on the basis that they do not, though
we may take longer to process them as in most cases the remaining work will
have to be done by someone else.

If you have any questions regarding our guidelines, submit the PR as is
and ask.

More detailed guidelines for pull requests are provided in our [developers
guide](https://github.com/RDFLib/rdflib/blob/main/docs/developers.rst).

PRs that are smaller in size and scope will be reviewed and merged quicker, so
please consider if your PR could be split up into more than one independent part
before submitting it, no PR is too small. The maintainers of this project may
also split up larger PRs into smaller, more manageable PRs, if they deem it
necessary.

PRs should be reviewed and approved by at least two people other than the author
using GitHub's review system before being merged. This is less important for bug
fixes and changes that don't impact runtime behaviour, but more important for
changes that expand the RDFLib public API. Reviews are open to anyone, so please
consider reviewing other open pull requests, as this will also free up the
capacity required for your PR to be reviewed.
-->

# Summary of changes

<!--
Briefly explain what changes the pull request is making and why. Ideally, this
should cover all changes in the pull request, as the changes will be reviewed
against this summary to ensure that the PR does not include unintended changes.

Please also explicitly state if the PR makes any changes that are not backwards
compatible.
-->

# Checklist

<!--
If an item on this list doesn't apply to your pull request, just remove it.

If, for some reason, you can't check some items on the checklist, or you are
unsure about them, submit your PR as is and ask for help.
-->

- [ ] Checked that there aren't other open pull requests for
  the same change.
- [ ] Checked that all tests and type checking passes.
- If the change adds new features or changes the RDFLib public API:
  <!-- This can be removed if no new features are added and the RDFLib public API is
  not changed. -->
  - [ ] Created an issue to discuss the change and get in-principle agreement.
  - [ ] Considered adding an example in `./examples`.
- If the change has a potential impact on users of this project:
  <!-- This can be removed if the changed does affect users of this project. -->
  - [ ] Added or updated tests that fail without the change.
  - [ ] Updated relevant documentation to avoid inaccuracies.
  - [ ] Considered adding additional documentation.
- [ ] Considered granting [push permissions to the PR branch](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/allowing-changes-to-a-pull-request-branch-created-from-a-fork),
  so maintainers can fix minor issues and keep your PR up to date.

