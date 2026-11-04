# Upgrading from version 7 to 8

!!! warning "In Development"
    This page is in development and will only be completed with the release of RDFLib v8.

## Python version

RDFLib 8 requires Python 3.11 or later. Python 3.10 reached end of life on
1 October 2026. Users who need Python 3.10 must remain on RDFLib 7.x.

The optional `lxml` dependency now requires version 4.9.1 or later for
Python 3.11 compatibility.

## Dataset length

`len(dataset)` now counts quads: identical triples in different graphs count
separately, including occurrences in the default graph. Empty named graphs
and the contents of quoted N3 formulas do not contribute to the count.
`Graph.__len__()` and `ConjunctiveGraph.__len__()` retain their existing behavior.

Counting delegates to
[`Store.quad_count()`][rdflib.store.Store.quad_count], which stores can override
with an equivalent native operation. The Memory store scans asserted graph
memberships. RDF4JStore uses a single repository-wide size request for RDF4J
and GraphDB. Other stores may enumerate graphs and count each graph separately,
potentially issuing multiple remote requests.

`bool(dataset)` and `if dataset:` perform the same count as `len(dataset)`.
Results are not cached, so repeated checks repeat the work. Avoid assuming
these operations are constant-time, especially in loops over large or remote
datasets. A dataset containing only empty named graphs has length zero and is
false, even though those graph names remain present.

## SPARQL multiplication and division

SPARQL `*` and `/` now give the result the promoted type of their operands, as
XPath's `op:numeric-multiply` and `op:numeric-divide` define it and as `+` and
`-` already did:

- An integer times an integer is an `xsd:integer`, and exact for large values.
  It was an `xsd:decimal`, rounded to 28 digits.
- A product or quotient with an `xsd:float` or `xsd:double` operand is a float
  or double, also when that operand comes first, so `toPython()` gives a
  Python `float` where it gave a `Decimal`.
- A float or double divided by zero is `INF`, `-INF` or `NaN` instead of an
  error. Integer and decimal division by zero are still errors.
- An ill-typed operand, such as `"abc"^^xsd:integer`, is an error.

`DATATYPE()`, `sameTerm()`, `DISTINCT` and joins on such computed values change
accordingly.
