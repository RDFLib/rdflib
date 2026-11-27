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

## Literals always have a datatype

Every RDF 1.1 literal has a datatype ([RDF 1.1 Concepts and Abstract Syntax,
§3.3](https://www.w3.org/TR/rdf11-concepts/#section-Graph-Literal)), and
[`Literal.datatype`][rdflib.term.Literal.datatype] is no longer `None`:

- A literal with a language tag has the datatype `rdf:langString`.
- A literal without a datatype or a language tag has the datatype
  `xsd:string`: a simple literal is syntactic sugar for an `xsd:string`
  literal.

So `Literal("a")` and `Literal("a", datatype=XSD.string)` are now the same
literal: they are equal, have the same hash, and a graph holds one triple for
`"a"` and `"a"^^xsd:string`. In SPARQL, the triple pattern `?s ?p "a"`,
`sameTerm`, `DISTINCT` and `GROUP BY` treat them as one. RDFLib 7 kept them
apart, so data whose JSON-LD context or store typed a string `xsd:string` did
not match a simple literal in a query or in a SHACL `sh:in` list.

What changes for code:

- Code that tests `literal.datatype is None` to find a string must test
  `literal.datatype == XSD.string`, or `literal.language` for a
  language-tagged one. Code that tests `if literal.datatype:` before
  `elif literal.language:` now always takes the first branch; test the
  language first.
- Code that writes literals, such as a serializer plugin, leaves out an
  implied datatype: `rdf:langString` when the literal has a language tag, and
  `xsd:string`.
- `ill_typed` is `False` for simple and language-tagged literals, as for any
  `xsd:string` literal, where it was `None`.
- A language tag together with a datatype other than `rdf:langString` raises
  `TypeError`; `Literal("a", lang="en", datatype=RDF.langString)` is accepted.
- `Literal(literal, datatype=...)` no longer keeps the language tag of
  `literal`, and `Literal(literal, lang=...)` no longer keeps its datatype, as a
  literal has only the datatype its language tag implies. So the SPARQL cast
  `xsd:string("a"@en)` gives `"a"`.
- A simple or language-tagged literal pickles as before, so pickles and
  persistent stores that index literals by their pickle, such as the BerkeleyDB
  store, find it under the same key. A literal stored with an explicit
  `^^xsd:string` by RDFLib 7 has a different key, so RDFLib 8 can't find or
  remove it by value, and a store that holds both `"a"` and `"a"^^xsd:string`
  holds the same triple twice. To migrate such a store, export its data with
  RDFLib 8 and load it into a new store.

Output is unchanged for simple and language-tagged literals, including their
order. A literal given the datatype `xsd:string` explicitly is now written as a
simple literal, `"a"` rather than `"a"^^xsd:string`, by `n3()`, `repr()` and
the N-Triples, N-Quads, Turtle, N3, TriG, RDF/XML, TriX, JSON-LD and SPARQL
results serializers, as canonical N-Triples requires; no `xsd:` prefix is
declared for it. The SPARQL stores send it the same way, so an endpoint that
still keeps `"a"` and `"a"^^xsd:string` apart no longer matches data it holds
as `"a"^^xsd:string`.

The JSON-LD serializer writes an `xsd:string` literal without `@type`, as RDF
to Object Conversion does ([JSON-LD 1.1 Processing Algorithms and API,
§8.5.2](https://www.w3.org/TR/json-ld11-api/#rdf-to-object-conversion)). So it
no longer uses a context term with `"@type": "xsd:string"` for it, and writes
the property's IRI instead, unless the context has a term for it without a
type. JSON-LD compaction, as in pyld, chooses the same.

In SPARQL, `STRLANG` accepts an `xsd:string` literal. The W3C tests
`strlang03-rdf11`, `distinct-2` and `distinct-9`, which were updated for
RDF 1.1, pass.
