.. _upgrade4to5: Upgrading from RDFLib version 4.2.2 to 5.0.0

============================================
Upgrading 4.2.2 to 5.0.0
============================================

RDFLib version 5.0.0 appeared over 3 years after the previous release, 4.2.2 and contains a large number of both enhancements and bug fixes. Fundamentally though, 5.0.0 is compatible with 4.2.2.


Major Changes
-------------
Paragraphs of explanation

Minor heading
^^^^^^^^^^^^^
Paragraphs of explanation


Minor Changes 
--------------
Minor Changes


This list has been assembled from Pull Request and commit information.

General Bugs Fixed:
^^^^^^^^^^^^^^^^^^^
* Pr 451 redux
  [#978](https://github.com/RDFLib/rdflib/pull/978)
* Issue 920 fixes as per Issue desc + test
  [#974](https://github.com/RDFLib/rdflib/pull/974)
* Remove colons from test result files. Fix #901.
  [#971](https://github.com/RDFLib/rdflib/pull/971)
* Add requirement for requests to setup.py
  [#969](https://github.com/RDFLib/rdflib/pull/969)
* fixed URIRef including native unicode characters
  [#961](https://github.com/RDFLib/rdflib/pull/961)
* DCTERMS.format not working
  [#932](https://github.com/RDFLib/rdflib/issues/932)
* NTriples fails to parse URIs with only a scheme
  [#920](https://github.com/RDFLib/rdflib/issues/920)
* infixowl.manchesterSyntax do not encode strings
  [#906](https://github.com/RDFLib/rdflib/pull/906)
* cannot clone it on windows
  [#901](https://github.com/RDFLib/rdflib/issues/901)
* Fix blank node label to not contain '_:' during parsing
  [#886](https://github.com/RDFLib/rdflib/pull/886)
* rename new SPARQLWrapper to SPARQLConnector
  [#872](https://github.com/RDFLib/rdflib/pull/872)
* Fix #859. Unquote and Uriquote Literal Datatype.
  [#860](https://github.com/RDFLib/rdflib/pull/860)
* Parsing nquads
  [#786](https://github.com/RDFLib/rdflib/issues/786)
* ntriples spec allows for upper-cased lang tag, fixes #782
  [#784](https://github.com/RDFLib/rdflib/pull/784)
* Error parsing N-Triple file using RDFlib
  [#782](https://github.com/RDFLib/rdflib/issues/782)
* Adds escaped single quote to literal parser
  [#736](https://github.com/RDFLib/rdflib/pull/736)
* N3 parse error on single quote within single quotes
  [#732](https://github.com/RDFLib/rdflib/issues/732)
* Fixed #725
  [#730](https://github.com/RDFLib/rdflib/pull/730)
* test for issue #725: canonicalization collapses BNodes
  [#726](https://github.com/RDFLib/rdflib/pull/726)
* RGDA1 graph canonicalization sometimes still collapses distinct BNodes
  [#725](https://github.com/RDFLib/rdflib/issues/725)
* Accept header should use a q parameter
  [#720](https://github.com/RDFLib/rdflib/pull/720)
* Added test for Issue #682 and fixed.
  [#718](https://github.com/RDFLib/rdflib/pull/718)
* Incompatibility with Python3: unichr
  [#687](https://github.com/RDFLib/rdflib/issues/687)
* namespace.py include colon in ALLOWED_NAME_CHARS
  [#663](https://github.com/RDFLib/rdflib/pull/663)
* Parse implicit string
  [#657](https://github.com/RDFLib/rdflib/pull/657)
* namespace.py fix compute_qname missing namespaces
  [#649](https://github.com/RDFLib/rdflib/pull/649)
* RDFa parsing Error! `__init__()` got an unexpected keyword argument 'encoding'
  [#639](https://github.com/RDFLib/rdflib/issues/639)
* Bugfix: `term.Literal.__add__`
  [#451](https://github.com/RDFLib/rdflib/pull/451)
* fixup of #443
  [#445](https://github.com/RDFLib/rdflib/pull/445)
* Microdata to rdf second edition bak
  [#444](https://github.com/RDFLib/rdflib/pull/444)

Enhanced Features:
^^^^^^^^^^^^^^^^^^
* Register additional serializer plugins for SPARQL mime types.
  [#987](https://github.com/RDFLib/rdflib/pull/987)
* Pr 388 redux
  [#979](https://github.com/RDFLib/rdflib/pull/979)
* Allows RDF terms introduced by JSON-LD 1.1
  [#970](https://github.com/RDFLib/rdflib/pull/970)
* make SPARQLConnector work with DBpedia
  [#941](https://github.com/RDFLib/rdflib/pull/941)
* ClosedNamespace returns right exception for way of access
  [#866](https://github.com/RDFLib/rdflib/pull/866)
* Not adding all namespaces for n3 serializer
  [#832](https://github.com/RDFLib/rdflib/pull/832)
* Adds basic support of xsd:duration
  [#808](https://github.com/RDFLib/rdflib/pull/808)
* Add possibility to set authority and basepath to skolemize graph
  [#807](https://github.com/RDFLib/rdflib/pull/807)
* Change notation3 list realization to non-recursive function.
  [#805](https://github.com/RDFLib/rdflib/pull/805)
* Suppress warning for not using custom encoding.
  [#800](https://github.com/RDFLib/rdflib/pull/800)
* Add support to parsing large xml inputs (https://github.com/RDFLib/rdflib/issues/749)
  [#750](https://github.com/RDFLib/rdflib/pull/750)
* improve hash efficiency by directly using str/unicode hash
  [#746](https://github.com/RDFLib/rdflib/pull/746)
* Added the csvw prefix to the RDFa initial context.
  [#594](https://github.com/RDFLib/rdflib/pull/594)
* syncing changes from pyMicrodata
  [#587](https://github.com/RDFLib/rdflib/pull/587)
* Microdata parser: updated the parser to the latest version of the microdata->rdf note (published in December 2014)
  [#443](https://github.com/RDFLib/rdflib/pull/443)
* Literal.toPython() support for xsd:hexBinary
  [#388](https://github.com/RDFLib/rdflib/pull/388)

SPARQL Fixes:
^^^^^^^^^^^^^
* Total order patch patch
  [#862](https://github.com/RDFLib/rdflib/pull/862)
* use <<= instead of deprecated <<
  [#861](https://github.com/RDFLib/rdflib/pull/861)
* Fix #847
  [#856](https://github.com/RDFLib/rdflib/pull/856)
* RDF Literal "1"^^xsd:boolean should _not_ coerce to True
  [#847](https://github.com/RDFLib/rdflib/issues/847)
* Makes NOW() return an UTC date
  [#844](https://github.com/RDFLib/rdflib/pull/844)
* NOW() SPARQL should return an xsd:dateTime with a timezone
  [#843](https://github.com/RDFLib/rdflib/issues/843)
* fix property paths bug: issue #715
  [#822](https://github.com/RDFLib/rdflib/pull/822)
  [#715](https://github.com/RDFLib/rdflib/issues/715)
* MulPath: correct behaviour of n3()
  [#820](https://github.com/RDFLib/rdflib/pull/820)
* Literal total ordering
  [#793](https://github.com/RDFLib/rdflib/pull/793)
* Remove SPARQLWrapper dependency
  [#744](https://github.com/RDFLib/rdflib/pull/744)
* made UNION faster by not preventing duplicates
  [#741](https://github.com/RDFLib/rdflib/pull/741)
* added a hook to add custom functions to SPARQL
  [#723](https://github.com/RDFLib/rdflib/pull/723)
* Issue714
  [#717](https://github.com/RDFLib/rdflib/pull/717)
* Use <<= instead of deprecated << in SPARQL parser
  [#417](https://github.com/RDFLib/rdflib/pull/417)
* Custom FILTER function for SPARQL engine
  [#274](https://github.com/RDFLib/rdflib/issues/274)

Code Quality and Cleanups:
^^^^^^^^^^^^^^^^^^^^^^^^^^
* a slightly opinionated autopep8 run
  [#870](https://github.com/RDFLib/rdflib/pull/870)
* remove rdfa and microdata parsers from core RDFLib
  [#828](https://github.com/RDFLib/rdflib/pull/828)
* ClosedNamespace KeyError -> AttributeError
  [#827](https://github.com/RDFLib/rdflib/pull/827)
* typo in rdflib/plugins/sparql/update.py
  [#760](https://github.com/RDFLib/rdflib/issues/760)
* Fix logging in interactive mode
  [#731](https://github.com/RDFLib/rdflib/pull/731)
* make namespace module flake8-compliant, change exceptions in that mod…
  [#711](https://github.com/RDFLib/rdflib/pull/711)
* delete ez_setup.py?
  [#669](https://github.com/RDFLib/rdflib/issues/669)
* code duplication issue between rdflib and pymicrodata
  [#582](https://github.com/RDFLib/rdflib/issues/582)
* Transition from 2to3 to use of six.py to be merged in 5.0.0-dev
  [#519](https://github.com/RDFLib/rdflib/pull/519)
* sparqlstore drop deprecated methods and args
  [#516](https://github.com/RDFLib/rdflib/pull/516)
* python3 code seems shockingly inefficient
  [#440](https://github.com/RDFLib/rdflib/issues/440)
* removed md5_term_hash, fixes #240
  [#439](https://github.com/RDFLib/rdflib/pull/439)
  [#240](https://github.com/RDFLib/rdflib/issues/240)

Testing:
^^^^^^^^
* 3.7 for travis
  [#864](https://github.com/RDFLib/rdflib/pull/864)
* Added trig unit tests to highlight some current parsing/serializing issues
  [#431](https://github.com/RDFLib/rdflib/pull/431)

Documentation Fixes:
^^^^^^^^^^^^^^^^^^^^
* Fix a doc string in the query module
  [#976](https://github.com/RDFLib/rdflib/pull/976)
* setup.py: Make the license field use an SPDX identifier
  [#789](https://github.com/RDFLib/rdflib/pull/789)
* Update README.md
  [#764](https://github.com/RDFLib/rdflib/pull/764)
* Update namespaces_and_bindings.rst
  [#757](https://github.com/RDFLib/rdflib/pull/757)
* DOC: README.md: rdflib-jsonld, https uris
  [#712](https://github.com/RDFLib/rdflib/pull/712)
* make doctest support py2/py3
  [#707](https://github.com/RDFLib/rdflib/issues/707)
* `pip install rdflib` (as per README.md) gets OSError on Mint 18.1
  [#704](https://github.com/RDFLib/rdflib/issues/704)
