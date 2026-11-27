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

## Infinite and NaN doubles

A [`Literal`][rdflib.term.Literal] made from an infinite or NaN float, or
parsed as an infinite or NaN `xsd:double` or `xsd:float`, now has the lexical
form `INF`, `-INF` or `NaN`, the canonical XML Schema forms. RDFLib 7 used
Python's spelling, `inf`, `-inf` and `nan`, which is not a valid `xsd:double`
or `xsd:float`. Turtle and N3 output already used the new forms; `str()`,
N-Triples, N-Quads, RDF/XML, TriX, HexT, Patch and SPARQL results change.

- A literal made with `normalize=False` keeps its lexical form. Only `n3()`,
  and so Turtle, N3, TriG and the SPARQL stores, writes a special value spelled
  as Python does, such as `infinity`, `INFINITY` or `NAN`, in its XSD form, as
  it already did for `inf` and `nan`; a numeral is kept, even when it
  overflows. Comparisons that use `n3()`, such as
  [`isomorphic`][rdflib.compare.isomorphic], treat such a literal as equal to
  the canonical one.
- Such a literal no longer equals one made with `normalize=False` from the old
  spelling, such as `Literal("inf", datatype=XSD.double, normalize=False)`.
  Literals in SPARQL queries aren't normalized, so a query that spells the
  value `"inf"^^xsd:double` no longer matches, and `"INF"^^xsd:double` now does.
- A persistent store that indexes literals by their lexical form, such as the
  BerkeleyDB store, keeps the old spelling for data written by RDFLib 7.
  RDFLib 8 reads such data back as `INF` and `NaN`, but can't find or remove
  it by value. To migrate such a store, export its data with RDFLib 8 and load
  it into a new store.

## Turtle serialization

`format="turtle"`, and its aliases `ttl` and `text/turtle`, now select the
serializer RDFLib 7 called `longturtle`. It writes `PREFIX` rather than
`@prefix`, and prefers new lines to compactness, so that changes to a file
show as small diffs. `longturtle` remains a name for it. The RDFLib 7 layout is
available as `origturtle`. TriG output uses the new layout; N3 output keeps the
previous one.

[`TurtleSerializer`][rdflib.plugins.serializers.turtle.TurtleSerializer] is now
that serializer, and the RDFLib 7 `TurtleSerializer` is
[`OrigTurtleSerializer`][rdflib.plugins.serializers.origturtle.OrigTurtleSerializer].
The module `rdflib.plugins.serializers.longturtle` is removed. A subclass that
relies on the RDFLib 7 layout or its methods should extend
`OrigTurtleSerializer`.

The methods and attributes of `OrigTurtleSerializer`, `N3Serializer`,
`TrigSerializer` and their base `RecursiveSerializer` now have snake_case
names. A subclass that overrides a method or attribute under its old name is
no longer used, and nothing reports it, so rename such overrides:

| RDFLib 7 | RDFLib 8 |
| --- | --- |
| `addNamespace` | `add_namespace` |
| `buildPredicateHash` | `build_predicate_hash` |
| `checkSubject` | `check_subject` |
| `doList` | `do_list` |
| `endDocument` | `end_document` |
| `indentString` | `indent_string` |
| `isDone` | `is_done` |
| `isValidList` | `is_valid_list` |
| `maxDepth` | `max_depth` |
| `objectList` | `object_list` |
| `orderSubjects` | `order_subjects` |
| `predicateList` | `predicate_list` |
| `predicateOrder` | `predicate_order` |
| `preprocessTriple` | `preprocess_triple` |
| `sortProperties` | `sort_properties` |
| `startDocument` | `start_document` |
| `subjectDone` | `subject_done` |
| `topClasses` | `top_classes` |

`getQName` keeps its name. It was already deprecated in RDFLib 7 and still
warns; use `get_pname` instead.
