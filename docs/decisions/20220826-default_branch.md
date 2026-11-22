# Default Branch Name

!!! success "Status"
    Accepted

## Context

In recent years usage of the word `master` has become somewhat controversial [as noted by SFC][SFC-BNAMING] and consequently default branch name of Git repos has become `main`, both in Git itself [according to SFC][SFC-BNAMING] and in Git hosting solutions such as GitHub [documentation][GH-BRANCHES].

## Decision

RDFLib's default branch will be renamed from `master` to `main`. This is primarily to stay in line with modern conventions and to adhere to the principle of least surprise.

## Consequences

Anticipated negative consequences:

* Some links to old code will be broken.
* Some people's workflow may break unexpectedly and need adjusting.
* Any code and systems reliant on the old default branch name will fail.

Anticipated positive consequences:

* It will become a bit easier to work with RDFLib for developers that are used
  to `main` as the default branch.

## References

[GH-BRANCHES]: https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/about-branches#about-the-default-branch "GitHub: About the default branch"
[SFC-BNAMING]: https://sfconservancy.org/news/2020/jun/23/gitbranchname/ "Regarding Git and Branch Naming"
