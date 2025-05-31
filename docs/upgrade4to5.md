# Upgrading from RDFLib version 4.2.2 to 5.0.0

RDFLib version 5.0.0 appeared over 3 years after the previous release, 4.2.2 and contains a large number of both enhancements and bug fixes. Fundamentally though, 5.0.0 is compatible with 4.2.2.

## Major Changes

### Literal Ordering

Literal total ordering [PR #793](https://github.com/RDFLib/rdflib/pull/793) is implemented. That means all literals can now be compared to be greater than or less than any other literal. This is required for implementing some specific SPARQL features, but it is counter-intuitive to those who are expecting a TypeError when certain normally-incompatible types are compared. For example, comparing a `Literal(int(1), datatype=xsd:integer)` to `Literal(datetime.date(10,01,2020), datatype=xsd:date)` using a `>` or `<` operator in rdflib 4.2.2 and earlier, would normally throw a TypeError, however in rdflib 5.0.0 this operation now returns a True or False according to the Literal Total Ordering according the rules outlined in [PR #793](https://github.com/RDFLib/rdflib/pull/793)

### Removed RDF Parsers

The RDFa and Microdata format RDF parsers were removed from rdflib. There are still other python libraries available to implement these parsers.

## All Changes

This list has been assembled from Pull Request and commit information.

### General Bugs Fixed

* Pr 451 redux
  [PR #978](https://github.com/RDFLib/rdflib/pull/978)
* NTriples fails to parse URIs with only a scheme
  [ISSUE #920](https://github.com/RDFLib/rdflib/issues/920)
  [PR #974](https://github.com/RDFLib/rdflib/pull/974)
* cannot clone it on windows - Remove colons from test result files. Fix #901.
  [ISSUE #901](https://github.com/RDFLib/rdflib/issues/901)
  [PR #971](https://github.com/RDFLib/rdflib/pull/971)
* Add requirement for requests to setup.py
  [PR #969](https://github.com/RDFLib/rdflib/pull/969)
* fixed URIRef including native unicode characters
  [PR #961](https://github.com/RDFLib/rdflib/pull/961)
* DCTERMS.format not working
  [ISSUE #932](https://github.com/RDFLib/rdflib/issues/932)
* infixowl.manchesterSyntax do not encode strings
  [PR #906](https://github.com/RDFLib/rdflib/pull/906)
* Fix blank node label to not contain '_:' during parsing
  [PR #886](https://github.com/RDFLib/rdflib/pull/886)
* rename new SPARQLWrapper to SPARQLConnector
  [PR #872](https://github.com/RDFLib/rdflib/pull/872)
* Fix #859. Unquote and Uriquote Literal Datatype.
  [PR #860](https://github.com/RDFLib/rdflib/pull/860)
* Parsing nquads
  [ISSUE #786](https://github.com/RDFLib/rdflib/issues/786)
* ntriples spec allows for upper-cased lang tag, fixes #782
  [PR #784](https://github.com/RDFLib/rdflib/pull/784)
* Error parsing N-Triple file using RDFlib
  [ISSUE #782](https://github.com/RDFLib/rdflib/issues/782)
* Adds escaped single quote to literal parser
  [PR #736](https://github.com/RDFLib/rdflib/pull/736)
* N3 parse error on single quote within single quotes
  [ISSUE #732](https://github.com/RDFLib/rdflib/issues/732)
* Fixed #725
  [PR #730](https://github.com/RDFLib/rdflib/pull/730)
* test for issue #725: canonicalization collapses BNodes
  [PR #726](https://github.com/RDFLib/rdflib/pull/726)
* RGDA1 graph canonicalization sometimes still collapses distinct BNodes
  [ISSUE #725](https://github.com/RDFLib/rdflib/issues/725)
* Accept header should use a q parameter
  [PR #720](https://github.com/RDFLib/rdflib/pull/720)
* Added test for Issue #682 and fixed.
  [PR #718](https://github.com/RDFLib/rdflib/pull/718)
* Incompatibility with Python3: unichr
  [ISSUE #687](https://github.com/RDFLib/rdflib/issues/687)
* namespace.py include colon in ALLOWED_NAME_CHARS
  [PR #663](https://github.com/RDFLib/rdflib/pull/663)
* namespace.py fix compute_qname missing namespaces
  [PR #649](https://github.com/RDFLib/rdflib/pull/649)
* RDFa parsing Error! `__init__()` got an unexpected keyword argument 'encoding'
  [ISSUE #639](https://github.com/RDFLib/rdflib/issues/639)
* Bugfix: `term.Literal.__add__`
  [PR #451](https://github.com/RDFLib/rdflib/pull/451)
* fixup of #443
  [PR #445](https://github.com/RDFLib/rdflib/pull/445)
* Microdata to rdf second edition bak
  [PR #444](https://github.com/RDFLib/rdflib/pull/444)

### Enhanced Features

* Register additional serializer plugins for SPARQL mime types.
  [PR #987](https://github.com/RDFLib/rdflib/pull/987)
* Pr 388 redux
  [PR #979](https://github.com/RDFLib/rdflib/pull/979)
* Allows RDF terms introduced by JSON-LD 1.1
  [PR #970](https://github.com/RDFLib/rdflib/pull/970)
* make SPARQLConnector work with DBpedia
  [PR #941](https://github.com/RDFLib/rdflib/pull/941)
* ClosedNamespace returns right exception for way of access
  [PR #866](https://github.com/RDFLib/rdflib/pull/866)
* Not adding all namespaces for n3 serializer
  [PR #832](https://github.com/RDFLib/rdflib/pull/832)
* Adds basic support of xsd:duration
  [PR #808](https://github.com/RDFLib/rdflib/pull/808)
* Add possibility to set authority and basepath to skolemize graph
  [PR #807](https://github.com/RDFLib/rdflib/pull/807)
* Change notation3 list realization to non-recursive function.
  [PR #805](https://github.com/RDFLib/rdflib/pull/805)
* Suppress warning for not using custom encoding.
  [PR #800](https://github.com/RDFLib/rdflib/pull/800)
* Add support to parsing large xml inputs
  [ISSUE #749](https://github.com/RDFLib/rdflib/issues/749)
  [PR #750](https://github.com/RDFLib/rdflib/pull/750)
* improve hash efficiency by directly using str/unicode hash
  [PR #746](https://github.com/RDFLib/rdflib/pull/746)
* Added the csvw prefix to the RDFa initial context.
  [PR #594](https://github.com/RDFLib/rdflib/pull/594)
* syncing changes from pyMicrodata
  [PR #587](https://github.com/RDFLib/rdflib/pull/587)
* Microdata parser: updated the parser to the latest version of the microdata->rdf note (published in December 2014)
  [PR #443](https://github.com/RDFLib/rdflib/pull/443)
* Literal.toPython() support for xsd:hexBinary
  [PR #388](https://github.com/RDFLib/rdflib/pull/388)

### SPARQL Fixes

* Total order patch patch
  [PR #862](https://github.com/RDFLib/rdflib/pull/862)
* use <<= instead of deprecated <<
  [PR #861](https://github.com/RDFLib/rdflib/pull/861)
* Fix #847
  [PR #856](https://github.com/RDFLib/rdflib/pull/856)
* RDF Literal "1"^^xsd:boolean should _not_ coerce to True
  [ISSUE #847](https://github.com/RDFLib/rdflib/issues/847)
* Makes NOW() return an UTC date
  [PR #844](https://github.com/RDFLib/rdflib/pull/844)
* NOW() SPARQL should return an xsd:dateTime with a timezone
  [ISSUE #843](https://github.com/RDFLib/rdflib/issues/843)
* fix property paths bug: issue #715
  [PR #822](https://github.com/RDFLib/rdflib/pull/822)
  [ISSUE #715](https://github.com/RDFLib/rdflib/issues/715)
* MulPath: correct behaviour of n3()
  [PR #820](https://github.com/RDFLib/rdflib/pull/820)
* Literal total ordering
  [PR #793](https://github.com/RDFLib/rdflib/pull/793)
* Remove SPARQLWrapper dependency
  [PR #744](https://github.com/RDFLib/rdflib/pull/744)
* made UNION faster by not preventing duplicates
  [PR #741](https://github.com/RDFLib/rdflib/pull/741)
* added a hook to add custom functions to SPARQL
  [PR #723](https://github.com/RDFLib/rdflib/pull/723)
* Issue714
  [PR #717](https://github.com/RDFLib/rdflib/pull/717)
* Use <<= instead of deprecated << in SPARQL parser
  [PR #417](https://github.com/RDFLib/rdflib/pull/417)
* Custom FILTER function for SPARQL engine
  [ISSUE #274](https://github.com/RDFLib/rdflib/issues/274)

### Code Quality and Cleanups

* a slightly opinionated autopep8 run
  [PR #870](https://github.com/RDFLib/rdflib/pull/870)
* remove rdfa and microdata parsers from core RDFLib
  [PR #828](https://github.com/RDFLib/rdflib/pull/828)
* ClosedNamespace KeyError -> AttributeError
  [PR #827](https://github.com/RDFLib/rdflib/pull/827)
* typo in rdflib/plugins/sparql/update.py
  [ISSUE #760](https://github.com/RDFLib/rdflib/issues/760)
* Fix logging in interactive mode
  [PR #731](https://github.com/RDFLib/rdflib/pull/731)
* make namespace module flake8-compliant, change exceptions in that mod…
  [PR #711](https://github.com/RDFLib/rdflib/pull/711)
* delete ez_setup.py?
  [ISSUE #669](https://github.com/RDFLib/rdflib/issues/669)
* code duplication issue between rdflib and pymicrodata
  [ISSUE #582](https://github.com/RDFLib/rdflib/issues/582)
* Transition from 2to3 to use of six.py to be merged in 5.0.0-dev
  [PR #519](https://github.com/RDFLib/rdflib/pull/519)
* sparqlstore drop deprecated methods and args
  [PR #516](https://github.com/RDFLib/rdflib/pull/516)
* python3 code seems shockingly inefficient
  [ISSUE #440](https://github.com/RDFLib/rdflib/issues/440)
* removed md5_term_hash, fixes #240
  [PR #439](https://github.com/RDFLib/rdflib/pull/439)
  [ISSUE #240](https://github.com/RDFLib/rdflib/issues/240)

### Testing

* 3.7 for travis
  [PR #864](https://github.com/RDFLib/rdflib/pull/864)
* Added trig unit tests to highlight some current parsing/serializing issues
  [PR #431](https://github.com/RDFLib/rdflib/pull/431)

### Documentation Fixes

* Fix a doc string in the query module
  [PR #976](https://github.com/RDFLib/rdflib/pull/976)
* setup.py: Make the license field use an SPDX identifier
  [PR #789](https://github.com/RDFLib/rdflib/pull/789)
* Update README.md
  [PR #764](https://github.com/RDFLib/rdflib/pull/764)
* Update namespaces_and_bindings.rst
  [PR #757](https://github.com/RDFLib/rdflib/pull/757)
* DOC: README.md: rdflib-jsonld, https uris
  [PR #712](https://github.com/RDFLib/rdflib/pull/712)
* make doctest support py2/py3
  [ISSUE #707](https://github.com/RDFLib/rdflib/issues/707)
* `pip install rdflib` (as per README.md) gets OSError on Mint 18.1
  [ISSUE #704](https://github.com/RDFLib/rdflib/issues/704)
  [PR #717](https://github.com/RDFLib/rdflib/pull/717)
* Use <<= instead of deprecated << in SPARQL parser
  [PR #417](https://github.com/RDFLib/rdflib/pull/417)
* Custom FILTER function for SPARQL engine
  [ISSUE #274](https://github.com/RDFLib/rdflib/issues/274)
