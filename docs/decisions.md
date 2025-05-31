# Decision Records

To ensure that significant changes to RDFLib are made with sufficient consultation, consideration and planning they should be preceded by a decision record that captures the particulars of the decision that lead to the change.

Decision records present the users and maintainers of RDFLib with an opportunity to review decisions before effort is expended to implement the decision in code, and it also makes it possible to review decisions without having to reconstruct them from the code changes that implement them.

Whether a change is significant is hard to measure objectively, but some characteristics that may indicate that a change is significant include:

* It will require changes to code that use RDFLib.
* It cannot be reversed without requiring changes to code that use RDFLib.
* It is onerous to reverse later.
* It increases the maintenance burden of RDFLib.
* It is very large.

Some of these characteristics are not binary but measured in degrees, so some discretion is required when determining if an architectural decision record is appropriate.

Decision records may also be used for changes that do not have any of the listed characteristics if a decision record would be otherwise helpful, for example to capture a decision to change the maintenance process of RDFLib.

Changes not preceded by decision records won't be rejected solely on this basis even if they are deemed significant, and decision records may also be created retrospectively for changes.

Decision records as described here are similar to the concept of [Architectural Decision Records](https://adr.github.io/), though it is slightly broader as it could include decisions which are not classified as architectural.

## Creating a decision record

Decision records should be added to the RDFLib repository in the `./docs/decisions/` directory with a name `{YYYYmmdd}-{title}.md`.

The content of the decision record should succinctly describe the context of the decision, the decision itself, and the status of the decision.

Decision records should preferably follow [Michael Nygard decision record template](https://github.com/joelparkerhenderson/architecture-decision-record/blob/main/templates/decision-record-template-by-michael-nygard/index.md) that he described in a [2011 article](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions.html) on documenting architecture decisions.

For questions about decision records please reach out to the RDFLib maintainers and community using the options given in [further_help_and_contact].

## Decisions list

- [Default branch](decisions/20220826-default_branch.md)
