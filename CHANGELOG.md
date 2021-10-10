2021/09/17 RELEASE 6.0.2
========================
Minor release to add OWL.rational & OWL.real which are needed to allow the OWL-RL pachage to use only rdflib namespaces, not it's own versions.

* Add owl:rational and owl:real to match standard.
  [PR #1428](https://github.com/RDFLib/rdflib/pull/1428)

A few other small things have been added, see the following merged PRs list:

* rename arg LOVE to ns in rdfpipe
  [PR #1426](https://github.com/RDFLib/rdflib/pull/1426)
* Remove Tox reference to Python 3.6
  [PR #1422](https://github.com/RDFLib/rdflib/pull/1422)
* Add Brick DefinedNamespace
  [PR #1419](https://github.com/RDFLib/rdflib/pull/1419)
* Use setName on TokenConverter to set the name property
  [PR #1409](https://github.com/RDFLib/rdflib/pull/1409)
* Add test for adding JSON-LD to guess_format()
  [PR #1408](https://github.com/RDFLib/rdflib/pull/1408)
* Fix mypy type errors and add mypy to .drone.yml
  [PR #1407](https://github.com/RDFLib/rdflib/pull/1407)


2021/09/17 RELEASE 6.0.1
========================
Minor release to fix a few small errors, in particular with JSON-LD parsing & serializing integration from rdflib-jsonld. Also, a few other niceties, such as allowing graph `add()`, `remove()` etc. to be chainable.

* Add test for adding JSON-LD to guess_format()
  [PR #1408](https://github.com/RDFLib/rdflib/pull/1408)
* Add JSON-LD to guess_format()
  [PR #1403](https://github.com/RDFLib/rdflib/pull/1403)
* add dateTimeStamp, fundamental & constraining facets, 7-prop data model
  [PR #1399](https://github.com/RDFLib/rdflib/pull/1399)
* fix: remove log message on import
  [PR #1398](https://github.com/RDFLib/rdflib/pull/1398)
* Make graph and other methods chainable
  [PR #1394](https://github.com/RDFLib/rdflib/pull/1394)
* fix: use correct name for json-ld
  [PR #1388](https://github.com/RDFLib/rdflib/pull/1388)
* Allowing Container Membership Properties in RDF namespace (#873)
  [PR #1386](https://github.com/RDFLib/rdflib/pull/1386)
* Update intro_to_sparql.rst
  [PR #1386](https://github.com/RDFLib/rdflib/pull/1384)
* Iterate over dataset return quads
  [PR #1382](https://github.com/RDFLib/rdflib/pull/1382)

2021/07/20 RELEASE 6.0.0
========================
6.0.0 is a major stable release that drops support for Python 2 and Python 3 < 3.7. Type hinting is now present in much
of the toolkit as a result.

It includes the formerly independent JSON-LD parser/serializer, improvements to Namespaces that allow for IDE namespace
prompting, simplified use of `g.serialize()` (turtle default, no need to `decode()`) and many other updates to 
documentation, store backends and so on.

Performance of the in-memory store has also improved since Python 3.6 dictionary improvements.

There are numerous supplementary improvements to the toolkit too, such as:

* inclusion of Docker files for easier CI/CD
* black config files for standardised code formatting
* improved testing with mock SPARQL stores, rather than a reliance on DBPedia etc

_**All PRs merged since 5.0.0:**_

* Fixes 1190 - pin major version of pyparsing
  [PR #1366](https://github.com/RDFLib/rdflib/pull/1366)
* Add __init__ for shared jsonld module
  [PR #1365](https://github.com/RDFLib/rdflib/pull/1365)
* Update README with chat info
  [PR #1363](https://github.com/RDFLib/rdflib/pull/1363)
* add xsd dayTimeDuration and yearMonthDuration
  [PR #1364](https://github.com/RDFLib/rdflib/pull/1364)
* Updated film.py
  [PR #1359](https://github.com/RDFLib/rdflib/pull/1359)
* Migration from ClosedNamespace to DeclaredNamespace
  [PR #1074](https://github.com/RDFLib/rdflib/pull/1074)
* Add @expectedFailure unit tests for #1294 and type annotations for compare.py
  [PR #1346](https://github.com/RDFLib/rdflib/pull/1346)
* JSON-LD Integration
  [PR #1354](https://github.com/RDFLib/rdflib/pull/1354)
* ENH: Make ClosedNamespace extend Namespace
  [PR #1213](https://github.com/RDFLib/rdflib/pull/1213)
* Add unit test for #919 and more type hints for sparqlconnector and sparqlstore
  [PR #1348](https://github.com/RDFLib/rdflib/pull/1348)
* fix #876 Updated term.py to add xsd:normalizedString and xsd:token support for Literals
  [PR #1102](https://github.com/RDFLib/rdflib/pull/1102)
* Dev stack update
  [PR #1355](https://github.com/RDFLib/rdflib/pull/1355)
* Add make coverage instructions to README
  [PR #1353](https://github.com/RDFLib/rdflib/pull/1353)
* Improve running tests locally
  [PR #1352](https://github.com/RDFLib/rdflib/pull/1352)
* support day, month and year function for date
  [PR #1154](https://github.com/RDFLib/rdflib/pull/1154)
* Prevent `from_n3` from unescaping `\xhh`
  [PR #1343](https://github.com/RDFLib/rdflib/pull/1343)
* Complete clean up of docs for 6.0.0
  [PR #1296](https://github.com/RDFLib/rdflib/pull/1296)
* pathname2url removal
  [PR #1288](https://github.com/RDFLib/rdflib/pull/1288)
* Replace Sleepycat with BerkeleyDB
  [PR #1347](https://github.com/RDFLib/rdflib/pull/1347)
* Replace use of DBPedia with the new SimpleHTTPMock
  [PR #1345](https://github.com/RDFLib/rdflib/pull/1345)
* Update graph operator overloading for subclasses
  [PR #1349](https://github.com/RDFLib/rdflib/pull/1349)
* Speedup Literal.__hash__ and Literal.__eq__ by accessing directly _da…
  [PR #1321](https://github.com/RDFLib/rdflib/pull/1321)
* Implemented function translateAlgebra. This functions takes a SPARQL …
  [PR #1322](https://github.com/RDFLib/rdflib/pull/1322)
* attempt at adding coveralls support to drone runs
  [PR #1337](https://github.com/RDFLib/rdflib/pull/1337)
* Fix SPARQL update parsing to handle arbitrary amounts of triples in inserts
  [PR #1340](https://github.com/RDFLib/rdflib/pull/1340)
* Add pathlib.PurePath support for Graph.serialize and Graph.parse
  [PR #1309](https://github.com/RDFLib/rdflib/pull/1309)
* dataset examples file
  [PR #1289](https://github.com/RDFLib/rdflib/pull/1289)
* Add handling for 308 (Permanent Redirect)
  [PR #1342](https://github.com/RDFLib/rdflib/pull/1342)
* Speedup of __add_triple_context
  [PR #1320](https://github.com/RDFLib/rdflib/pull/1320)
* Fix prov ns
  [PR #1318](https://github.com/RDFLib/rdflib/pull/1318)
* Speedup __ctx_to_str.
  [PR #1319](https://github.com/RDFLib/rdflib/pull/1319)
* Speedup decodeUnicodeEscape by avoiding useless string replace.
  [PR #1324](https://github.com/RDFLib/rdflib/pull/1324)
* Fix errors reported by mypy
  [PR #1330](https://github.com/RDFLib/rdflib/pull/1330)
* Require setuptools, rdflib/plugins/sparql/__init__.py and rdflib/plugin.py import pkg_resources
  [PR #1339](https://github.com/RDFLib/rdflib/pull/1339)
* Fix tox config
  [PR #1313](https://github.com/RDFLib/rdflib/pull/1313)
* Fix formatting of xsd:decimal
  [PR #1335](https://github.com/RDFLib/rdflib/pull/1335)
* Add tests for issue #1299
  [PR #1328](https://github.com/RDFLib/rdflib/pull/1328)
* Add special handling for gYear and gYearMonth
  [PR #1315](https://github.com/RDFLib/rdflib/pull/1315)
* Replace incomplete example in intro_to_sparql.rst
  [PR #1331](https://github.com/RDFLib/rdflib/pull/1331)
* Added unit test for issue #977.
  [PR #1112](https://github.com/RDFLib/rdflib/pull/1112)
* Don't sort variables in TXTResultSerializer
  [PR #1310](https://github.com/RDFLib/rdflib/pull/1310)
* handle encoding of base64Binary Literals
  [PR #1258](https://github.com/RDFLib/rdflib/pull/1258)
* Add tests for Graph.transitive_{subjects,objects}
  [PR #1307](https://github.com/RDFLib/rdflib/pull/1307)
* Changed to support passing fully qualified queries through the graph …
  [PR #1253](https://github.com/RDFLib/rdflib/pull/1253)
* Upgrade to GitHub-native Dependabot
  [PR #1298](https://github.com/RDFLib/rdflib/pull/1298)
* Fix transitive_objects/subjects docstrings and signatures
  [PR #1305](https://github.com/RDFLib/rdflib/pull/1305)
* Fix typo in ClosedNamespace doc string
  [PR #1293](https://github.com/RDFLib/rdflib/pull/1293)
* Allow parentheses in uri
  [PR #1280](https://github.com/RDFLib/rdflib/pull/1280)
* Add notes about how to install from git
  [PR #1286](https://github.com/RDFLib/rdflib/pull/1286)
*  Feature/forward version to 6.0.0-alpha
  [PR #1285](https://github.com/RDFLib/rdflib/pull/1285)
* speedup notation3/turtle parser
  [PR #1272](https://github.com/RDFLib/rdflib/pull/1272)
* Correct behaviour of compute_qname for URNs
  [PR #1274](https://github.com/RDFLib/rdflib/pull/1274)
* Speedup __add_triple_context.
  [PR #1271](https://github.com/RDFLib/rdflib/pull/1271)
* Feature/coverage configuration
  [PR #1267](https://github.com/RDFLib/rdflib/pull/1267)
* optimize sparql.Bindings
  [PR #1192](https://github.com/RDFLib/rdflib/pull/1192)
* issue_771_add_key_error_if_spaces
  [PR #1070](https://github.com/RDFLib/rdflib/pull/1070)
* Typo fix
  [PR #1254](https://github.com/RDFLib/rdflib/pull/1254)
* Adding Namespace.__contains__()
  [PR #1237](https://github.com/RDFLib/rdflib/pull/1237)
* Add a Drone config file.
  [PR #1247](https://github.com/RDFLib/rdflib/pull/1247)
* Add sentence on names not valid as Python IDs.
  [PR #1234](https://github.com/RDFLib/rdflib/pull/1234)
* Add trig mimetype
  [PR #1238](https://github.com/RDFLib/rdflib/pull/1238)
* Move flake8 config
  [PR #1239](https://github.com/RDFLib/rdflib/pull/1239)
* Update SPARQL tests since the DBpedia was updated
  [PR #1240](https://github.com/RDFLib/rdflib/pull/1240)
* fix foaf ClosedNamespace
  [PR #1220](https://github.com/RDFLib/rdflib/pull/1220)
* add GeoSPARQL ClosedNamespace
  [PR #1221](https://github.com/RDFLib/rdflib/pull/1221)
* docs: fix simple typo, yeild -> yield
  [PR #1223](https://github.com/RDFLib/rdflib/pull/1223)
* do not use current time in sparql TIMEZONE
  [PR #1193](https://github.com/RDFLib/rdflib/pull/1193)
* Reset graph on exit from context
  [PR #1206](https://github.com/RDFLib/rdflib/pull/1206)
* Fix usage of default-graph for POST and introduce POST_FORM
  [PR #1185](https://github.com/RDFLib/rdflib/pull/1185)
* Changes to graph.serialize()
  [PR #1183](https://github.com/RDFLib/rdflib/pull/1183)
* rd2dot Escape HTML in node label and URI text
  [PR #1209](https://github.com/RDFLib/rdflib/pull/1209)
* tests: retry on network error (CI)
  [PR #1203](https://github.com/RDFLib/rdflib/pull/1203)
* Add documentation and type hints for rdflib.query.Result and rdflib.graph.Graph
  [PR #1211](https://github.com/RDFLib/rdflib/pull/1211)
* fix typo
  [PR #1218](https://github.com/RDFLib/rdflib/pull/1218)
* Add architecture ppc64le to travis build
  [PR #1212](https://github.com/RDFLib/rdflib/pull/1212)
* small cleanups
  [PR #1191](https://github.com/RDFLib/rdflib/pull/1191)
* Remove the usage of assert in the SPARQLConnector
  [PR #1186](https://github.com/RDFLib/rdflib/pull/1186)
* Remove requests
  [PR #1175](https://github.com/RDFLib/rdflib/pull/1175)
* Support parsing paths specified with pathlib
  [PR #1180](https://github.com/RDFLib/rdflib/pull/1180)
* URI Validation Performance Improvements
  [PR #1177](https://github.com/RDFLib/rdflib/pull/1177)
* Fix serialize with multiple disks on windows
  [PR #1172](https://github.com/RDFLib/rdflib/pull/1172)
* Fix for issue #629 - Arithmetic Operations of DateTime in SPARQL
  [PR #1061](https://github.com/RDFLib/rdflib/pull/1061)
* Fixes #1043.
  [PR #1054](https://github.com/RDFLib/rdflib/pull/1054)
* N3 parser: do not create formulas if the Turtle mode is activated
  [PR #1142](https://github.com/RDFLib/rdflib/pull/1142)
* Move to using graph.parse() rather than deprecated graph.load()
  [PR #1167](https://github.com/RDFLib/rdflib/pull/1167)
* Small improvement to serialize docs
  [PR #1162](https://github.com/RDFLib/rdflib/pull/1162)
* Issue 1160 missing url fragment
  [PR #1163](https://github.com/RDFLib/rdflib/pull/1163)
* remove import side-effects
  [PR #1156](https://github.com/RDFLib/rdflib/pull/1156)
* Docs update
  [PR #1161](https://github.com/RDFLib/rdflib/pull/1161)
* replace cgi by html, fixes issue #1110
  [PR #1152](https://github.com/RDFLib/rdflib/pull/1152)
* Deprecate some more Graph API surface
  [PR #1151](https://github.com/RDFLib/rdflib/pull/1151)
* Add deprecation warning on graph.load()
  [PR #1150](https://github.com/RDFLib/rdflib/pull/1150)
* Remove all remnants of Python2 compatibility
  [PR #1149](https://github.com/RDFLib/rdflib/pull/1149)
* make csv2rdf work in py3
  [PR #1117](https://github.com/RDFLib/rdflib/pull/1117)
* Add a  __dir__ attribute to a closed namespace
  [PR #1134](https://github.com/RDFLib/rdflib/pull/1134)
* improved Graph().parse()
  [PR #1140](https://github.com/RDFLib/rdflib/pull/1140)
* Discussion around new dict-based store implementation
  [PR #1133](https://github.com/RDFLib/rdflib/pull/1133)
* fix 913
  [PR #1139](https://github.com/RDFLib/rdflib/pull/1139)
* Make parsers CharacterStream aware
  [PR #1145](https://github.com/RDFLib/rdflib/pull/1145)
* More Black formatting changes
  [PR #1146](https://github.com/RDFLib/rdflib/pull/1146)
* Fix comment
  [PR #1130](https://github.com/RDFLib/rdflib/pull/1130)
* Updating namespace.py to solve issue #801
  [PR #1044](https://github.com/RDFLib/rdflib/pull/1044)
* Fix namespaces for SOSA and SSN. Fix #1126.
  [PR #1128](https://github.com/RDFLib/rdflib/pull/1128)
* Create pull request template
  [PR #1114](https://github.com/RDFLib/rdflib/pull/1114)
* BNode context dicts for NT and N-Quads parsers
  [PR #1108](https://github.com/RDFLib/rdflib/pull/1108)
* Allow distinct blank node contexts from one NTriples parser to the next (#980)
  [PR #1107](https://github.com/RDFLib/rdflib/pull/1107)
* Autodetect parse() format
  [PR #1046](https://github.com/RDFLib/rdflib/pull/1046)
* fix #910: Updated evaluate.py so that union includes results of both branches, even when identical.
  [PR #1057](https://github.com/RDFLib/rdflib/pull/1057)
* Removal of six & styling
  [PR #1051](https://github.com/RDFLib/rdflib/pull/1051)
* Add SERVICE clause to documentation
  [PR #1041](https://github.com/RDFLib/rdflib/pull/1041)
* add test with ubuntu 20.04
  [PR #1038](https://github.com/RDFLib/rdflib/pull/1038)
* Improved logo
  [PR #1037](https://github.com/RDFLib/rdflib/pull/1037)
* Add requests to the tests_requirements
  [PR #1036](https://github.com/RDFLib/rdflib/pull/1036)
* Set update endpoint similar to query endpoint for sparqlstore if only one is given
  [PR #1033](https://github.com/RDFLib/rdflib/pull/1033)
* fix shebang typo
  [PR #1034](https://github.com/RDFLib/rdflib/pull/1034)
* Add the content type 'application/sparql-update' when preparing a SPARQL update request
  [PR #1022](https://github.com/RDFLib/rdflib/pull/1022)
* Fix typo in README.md
  [PR #1030](https://github.com/RDFLib/rdflib/pull/1030)
* add Python 3.8
  [PR #1023](https://github.com/RDFLib/rdflib/pull/1023)
* Fix n3 parser exponent syntax of floats with leading dot.
  [PR #1012](https://github.com/RDFLib/rdflib/pull/1012)
* DOC: Use sphinxcontrib-apidoc and various cleanups
  [PR #1010](https://github.com/RDFLib/rdflib/pull/1010)
* FIX: Change is comparison to == for tuple
  [PR #1009](https://github.com/RDFLib/rdflib/pull/1009)
* Update copyright year in docs conf.py
  [PR #1006](https://github.com/RDFLib/rdflib/pull/1006)
  
  
2020/04/18 RELEASE 5.0.0
========================
5.0.0 is a major stable release and is the last release to support Python 2 & 3.4. 5.0.0 is mostly backwards-
compatible with 4.2.2 and is intended for long-term, bug fix only support.

5.0.0 comes two weeks after the 5.0.0RC1 and includes a small number of additional bug fixes. Note that 
rdflib-jsonld has released a version 0.5.0 to be compatible with rdflib 5.0.0.

_**All PRs merged since 5.0.0RC1:**_

### General Bugs Fixed:
  * Fix n3 parser exponent syntax of floats with leading dot.
    [PR #1012](https://github.com/RDFLib/rdflib/pull/1012)
  * FIX: Change is comparison to == for tuple
    [PR #1009](https://github.com/RDFLib/rdflib/pull/1009)
  * fix #913 : Added _parseBoolean function to enforce correct Lexical-to-value mapping
    [PR #995](https://github.com/RDFLib/rdflib/pull/995)  
    
### Enhanced Features:
  * Issue 1003
    [PR #1005](https://github.com/RDFLib/rdflib/pull/1005)
    
### SPARQL Fixes:
  * CONSTRUCT resolve with initBindings fixes #1001
    [PR #1002](https://github.com/RDFLib/rdflib/pull/1002)

### Documentation Fixes:
  * DOC: Use sphinxcontrib-apidoc and various cleanups
    [PR #1010](https://github.com/RDFLib/rdflib/pull/1010)
  * Update copyright year in docs conf.py
    [PR #1006](https://github.com/RDFLib/rdflib/pull/1006)
  * slightly improved styling, small index text changes
    [PR #1004](https://github.com/RDFLib/rdflib/pull/1004)
    

2020/04/04 RELEASE 5.0.0RC1
===========================

After more than three years, RDFLib 5.0.0rc1 is finally released.

This is a rollup of all of the bugfixes merged, and features introduced to RDFLib since 
RDFLib 4.2.2 was released in Jan 2017.

While all effort was taken to minimize breaking changes in this release, there are some.

Please see the upgrade4to5 document in the docs directory for more information on some specific differences from 4.2.2 to 5.0.0.

_**All issues closed and PRs merged since 4.2.2:**_

### General Bugs Fixed:
  * Pr 451 redux
    [PR #978](https://github.com/RDFLib/rdflib/pull/978)
  * NTriples fails to parse URIs with only a scheme
    [ISSUE #920](https://github.com/RDFLib/rdflib/issues/920), [PR #974](https://github.com/RDFLib/rdflib/pull/974)
  * Cannot clone on windows - Remove colons from test result files.
    [ISSUE #901](https://github.com/RDFLib/rdflib/issues/901), [PR #971](https://github.com/RDFLib/rdflib/pull/971)  
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
    [PR #784](https://github.com/RDFLib/rdflib/pull/784), [ISSUE #782](https://github.com/RDFLib/rdflib/issues/782)
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

### Enhanced Features:
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
  
### SPARQL Fixes:
  * Total order patch patch
    [PR #862](https://github.com/RDFLib/rdflib/pull/862)
  * use <<= instead of deprecated <<
    [PR #861](https://github.com/RDFLib/rdflib/pull/861)
  * Fix #847
    [PR #856](https://github.com/RDFLib/rdflib/pull/856)
  * RDF Literal `"1"^^xsd:boolean` should _not_ coerce to True
    [ISSUE #847](https://github.com/RDFLib/rdflib/issues/847)
  * Makes NOW() return an UTC date
    [PR #844](https://github.com/RDFLib/rdflib/pull/844)
  * NOW() SPARQL should return an xsd:dateTime with a timezone
    [ISSUE #843](https://github.com/RDFLib/rdflib/issues/843)
  * fix property paths bug: issue #715
    [PR #822](https://github.com/RDFLib/rdflib/pull/822), [ISSUE #715](https://github.com/RDFLib/rdflib/issues/715)
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
  
### Code Quality and Cleanups:
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
    [PR #439](https://github.com/RDFLib/rdflib/pull/439), [ISSUE #240](https://github.com/RDFLib/rdflib/issues/240)
 
### Testing:
  * 3.7 for travis
    [PR #864](https://github.com/RDFLib/rdflib/pull/864)
  * Added trig unit tests to highlight some current parsing/serializing issues
    [PR #431](https://github.com/RDFLib/rdflib/pull/431)

### Documentation Fixes:
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



2017/01/29 RELEASE 4.2.2
========================

This is a bug-fix release, and the last release in the 4.X.X series.

Bug fixes:
----------
* SPARQL bugs fixed:
  * Fix for filters in sub-queries
    [#693](https://github.com/RDFLib/rdflib/pull/693)
  * Fixed bind, initBindings and filter problems
    [#294](https://github.com/RDFLib/rdflib/issues/294)
    [#555](https://github.com/RDFLib/rdflib/pull/555)
    [#580](https://github.com/RDFLib/rdflib/issues/580)
    [#586](https://github.com/RDFLib/rdflib/issues/586)
    [#601](https://github.com/RDFLib/rdflib/pull/601)
    [#615](https://github.com/RDFLib/rdflib/issues/615)
    [#617](https://github.com/RDFLib/rdflib/issues/617)
    [#619](https://github.com/RDFLib/rdflib/issues/619)
    [#630](https://github.com/RDFLib/rdflib/issues/630)
    [#653](https://github.com/RDFLib/rdflib/issues/653)
    [#686](https://github.com/RDFLib/rdflib/issues/686)
    [#688](https://github.com/RDFLib/rdflib/pull/688)
    [#692](https://github.com/RDFLib/rdflib/pull/692)
  * Fixed unexpected None value in SPARQL-update
    [#633](https://github.com/RDFLib/rdflib/issues/633)
    [#634](https://github.com/RDFLib/rdflib/pull/634)
  * Fix sparql, group by and count of null values with `optional`
    [#631](https://github.com/RDFLib/rdflib/issues/631)
  * Fixed sparql sub-query and aggregation bugs
    [#607](https://github.com/RDFLib/rdflib/issues/607)
    [#610](https://github.com/RDFLib/rdflib/pull/610)
    [#628](https://github.com/RDFLib/rdflib/issues/628)
    [#694](https://github.com/RDFLib/rdflib/pull/694)
  * Fixed parsing Complex BGPs as triples
    [#622](https://github.com/RDFLib/rdflib/pull/622)
    [#623](https://github.com/RDFLib/rdflib/issues/623)
  * Fixed DISTINCT being ignored inside aggregate functions
    [#404](https://github.com/RDFLib/rdflib/issues/404)
    [#611](https://github.com/RDFLib/rdflib/pull/611)
    [#678](https://github.com/RDFLib/rdflib/pull/678)
  * Fix unicode encoding errors in sparql processor
    [#446](https://github.com/RDFLib/rdflib/issues/446)
    [#599](https://github.com/RDFLib/rdflib/pull/599)
  * Fixed SPARQL select nothing no longer returning a `None` row
    [#554](https://github.com/RDFLib/rdflib/issues/554)
    [#592](https://github.com/RDFLib/rdflib/pull/592)
  * Fixed aggregate operators COUNT and SAMPLE to ignore unbound / NULL values
    [#564](https://github.com/RDFLib/rdflib/pull/564)
    [#563](https://github.com/RDFLib/rdflib/issues/563)
    [#567](https://github.com/RDFLib/rdflib/pull/567)
    [#568](https://github.com/RDFLib/rdflib/pull/568)
  * Fix sparql relative uris
    [#523](https://github.com/RDFLib/rdflib/issues/523)
    [#524](https://github.com/RDFLib/rdflib/pull/524)
  * SPARQL can now compare xsd:date type as well, fixes #532
    [#532](https://github.com/RDFLib/rdflib/issues/532)
    [#533](https://github.com/RDFLib/rdflib/pull/533)
  * fix sparql path order on python3: "TypeError: unorderable types: SequencePath() < SequencePath()""
    [#492](https://github.com/RDFLib/rdflib/issues/492)
    [#525](https://github.com/RDFLib/rdflib/pull/525)
  * SPARQL parser now robust to spurious semicolon
    [#381](https://github.com/RDFLib/rdflib/issues/381)
    [#528](https://github.com/RDFLib/rdflib/pull/528)
  * Let paths be comparable against all nodes even in py3 (preparedQuery error)
    [#545](https://github.com/RDFLib/rdflib/issues/545)
    [#552](https://github.com/RDFLib/rdflib/pull/552)
  * Made behavior of `initN` in `update` and `query` more consistent
    [#579](https://github.com/RDFLib/rdflib/issues/579)
    [#600](https://github.com/RDFLib/rdflib/pull/600)
* SparqlStore:
  * SparqlStore now closes underlying urllib response body
    [#638](https://github.com/RDFLib/rdflib/pull/638)
    [#683](https://github.com/RDFLib/rdflib/pull/683)
  * SparqlStore injectPrefixes only modifies query if prefixes present and if adds a newline in between
    [#521](https://github.com/RDFLib/rdflib/issues/521)
    [#522](https://github.com/RDFLib/rdflib/pull/522)
* Fixes and tests for AuditableStore
  [#537](https://github.com/RDFLib/rdflib/pull/537)
  [#557](https://github.com/RDFLib/rdflib/pull/557)
* Trig bugs fixed:
  * trig export of multiple graphs assigns wrong prefixes to prefixedNames
    [#679](https://github.com/RDFLib/rdflib/issues/679)
  * Trig serialiser writing empty named graph name for default graph
    [#433](https://github.com/RDFLib/rdflib/issues/433)
  * Trig parser can creating multiple contexts for the default graph
    [#432](https://github.com/RDFLib/rdflib/issues/432)
  * Trig serialisation handling prefixes incorrectly
    [#428](https://github.com/RDFLib/rdflib/issues/428)
    [#699](https://github.com/RDFLib/rdflib/pull/699)
* Fixed Nquads parser handling of triples in default graph
  [#535](https://github.com/RDFLib/rdflib/issues/535)
  [#536](https://github.com/RDFLib/rdflib/pull/536)
* Fixed TypeError in Turtle serializer (unorderable types: DocumentFragment() > DocumentFragment())
  [#613](https://github.com/RDFLib/rdflib/issues/613)
  [#648](https://github.com/RDFLib/rdflib/issues/648)
  [#666](https://github.com/RDFLib/rdflib/pull/666)
  [#676](https://github.com/RDFLib/rdflib/issues/676)
* Fixed serialization and parsing of inf/nan
  [#655](https://github.com/RDFLib/rdflib/pull/655)
  [#658](https://github.com/RDFLib/rdflib/pull/658)
* Fixed RDFa parser from failing on time elements with child nodes
  [#576](https://github.com/RDFLib/rdflib/issues/576)
  [#577](https://github.com/RDFLib/rdflib/pull/577)
* Fix double reduction of \\ escapes in from_n3
  [#546](https://github.com/RDFLib/rdflib/issues/546)
  [#548](https://github.com/RDFLib/rdflib/pull/548)
* Fixed handling of xsd:base64Binary
  [#646](https://github.com/RDFLib/rdflib/issues/646)
  [#674](https://github.com/RDFLib/rdflib/pull/674)
* Fixed Collection.__setitem__ broken
  [#604](https://github.com/RDFLib/rdflib/issues/604)
  [#605](https://github.com/RDFLib/rdflib/pull/605)
* Fix ImportError when __main__ already loaded
  [#616](https://github.com/RDFLib/rdflib/pull/616)
* Fixed broken top_level.txt file in distribution
  [#571](https://github.com/RDFLib/rdflib/issues/571)
  [#572](https://github.com/RDFLib/rdflib/pull/572)
  [#573](https://github.com/RDFLib/rdflib/pull/573)


Enhancements:
-------------
* Added support for Python 3.5+
  [#526](https://github.com/RDFLib/rdflib/pull/526)
* More aliases for common formats (nt, turtle)
  [#701](https://github.com/RDFLib/rdflib/pull/701)
* Improved RDF1.1 ntriples support
  [#695](https://github.com/RDFLib/rdflib/issues/695)
  [#700](https://github.com/RDFLib/rdflib/pull/700)
* Dependencies updated and improved compatibility with pyparsing, html5lib, SPARQLWrapper and elementtree
  [#550](https://github.com/RDFLib/rdflib/pull/550)
  [#589](https://github.com/RDFLib/rdflib/issues/589)
  [#606](https://github.com/RDFLib/rdflib/issues/606)
  [#641](https://github.com/RDFLib/rdflib/pull/641)
  [#642](https://github.com/RDFLib/rdflib/issues/642)
  [#650](https://github.com/RDFLib/rdflib/pull/650)
  [#671](https://github.com/RDFLib/rdflib/issues/671)
  [#675](https://github.com/RDFLib/rdflib/pull/675)
  [#684](https://github.com/RDFLib/rdflib/pull/684)
  [#696](https://github.com/RDFLib/rdflib/pull/696)
* Improved prefix for SPARQL namespace in XML serialization
  [#493](https://github.com/RDFLib/rdflib/issues/493)
  [#588](https://github.com/RDFLib/rdflib/pull/588)
* Performance improvements:
  * SPARQL Aggregation functions don't build up memory for each row
    [#678](https://github.com/RDFLib/rdflib/pull/678)
  * Collections now support += (__iadd__), fixes slow creation of large lists
    [#609](https://github.com/RDFLib/rdflib/issues/609)
    [#612](https://github.com/RDFLib/rdflib/pull/612)
    [#691](https://github.com/RDFLib/rdflib/pull/691)
  * SPARQL Optimisation to expand BGPs in a smarter way
    [#547](https://github.com/RDFLib/rdflib/pull/547)
* SPARQLStore improvements
  * improved SPARQLStore BNode customizability
    [#511](https://github.com/RDFLib/rdflib/issues/511)
    [#512](https://github.com/RDFLib/rdflib/pull/512)
    [#513](https://github.com/RDFLib/rdflib/pull/513)
    [#603](https://github.com/RDFLib/rdflib/pull/603)
  * Adding the option of using POST for long queries in SPARQLStore
    [#672](https://github.com/RDFLib/rdflib/issues/672)
    [#673](https://github.com/RDFLib/rdflib/pull/673)
  * Exposed the timeout of SPARQLWrapper
    [#531](https://github.com/RDFLib/rdflib/pull/531)
* SPARQL prepared query now carries the original (unparsed) parameters
  [#565](https://github.com/RDFLib/rdflib/pull/565)
* added .n3 methods for path objects
  [#553](https://github.com/RDFLib/rdflib/pull/553)
* Added support for xsd:gYear and xsd:gYearMonth
  [#635](https://github.com/RDFLib/rdflib/issues/635)
  [#636](https://github.com/RDFLib/rdflib/pull/636)
* Allow duplicates in rdf:List
  [#223](https://github.com/RDFLib/rdflib/issues/223)
  [#690](https://github.com/RDFLib/rdflib/pull/690)
* Improved slicing of Resource objects
  [#529](https://github.com/RDFLib/rdflib/pull/529)


Cleanups:
---------
* cleanup: SPARQL Prologue and Query new style classes
  [#566](https://github.com/RDFLib/rdflib/pull/566)
* Reduce amount of warnings, especially closing opened file pointers
  [#518](https://github.com/RDFLib/rdflib/pull/518)
  [#651](https://github.com/RDFLib/rdflib/issues/651)
* Improved ntriples parsing exceptions to actually tell you what's wrong
  [#640](https://github.com/RDFLib/rdflib/pull/640)
  [#643](https://github.com/RDFLib/rdflib/pull/643)
* remove ancient and broken 2.3 support code.
  [#680](https://github.com/RDFLib/rdflib/issues/680)
  [#681](https://github.com/RDFLib/rdflib/pull/681)
* Logger output improved
  [#662](https://github.com/RDFLib/rdflib/pull/662)
* properly cite RGDA1
  [#624](https://github.com/RDFLib/rdflib/pull/624)
* Avoid class reference to imported function
  [#574](https://github.com/RDFLib/rdflib/issues/574)
  [#578](https://github.com/RDFLib/rdflib/pull/578)
* Use find_packages for package discovery.
  [#590](https://github.com/RDFLib/rdflib/pull/590)
* Prepared ClosedNamespace (and _RDFNamespace) to inherit from Namespace (5.0.0)
  [#551](https://github.com/RDFLib/rdflib/pull/551)
  [#595](https://github.com/RDFLib/rdflib/pull/595)
* Avoid verbose build logging
  [#534](https://github.com/RDFLib/rdflib/pull/534)
* (ultra petty) Remove an unused import
  [#593](https://github.com/RDFLib/rdflib/pull/593)


Testing improvements:
---------------------
* updating deprecated testing syntax
  [#697](https://github.com/RDFLib/rdflib/pull/697)
* make test 375 more portable (use sys.executable rather than python)
  [#664](https://github.com/RDFLib/rdflib/issues/664)
  [#668](https://github.com/RDFLib/rdflib/pull/668)
* Removed outdated, skipped test for #130 that depended on content from the internet
  [#256](https://github.com/RDFLib/rdflib/issues/256)
* enable all warnings during travis nosetests
  [#517](https://github.com/RDFLib/rdflib/pull/517)
* travis updates
  [#659](https://github.com/RDFLib/rdflib/issues/659)
* travis also builds release branches
  [#598](https://github.com/RDFLib/rdflib/pull/598)


Doc improvements:
-----------------
* Update list of builtin serialisers in docstring
  [#621](https://github.com/RDFLib/rdflib/pull/621)
* Update reference to "Emulating container types"
  [#575](https://github.com/RDFLib/rdflib/issues/575)
  [#581](https://github.com/RDFLib/rdflib/pull/581)
  [#583](https://github.com/RDFLib/rdflib/pull/583)
  [#584](https://github.com/RDFLib/rdflib/pull/584)
* docs: clarify the use of an identifier when persisting a triplestore
  [#654](https://github.com/RDFLib/rdflib/pull/654)
* DOC: unamed -> unnamed, typos
  [#562](https://github.com/RDFLib/rdflib/pull/562)



2015/08/12 RELEASE 4.2.1
========================

This is a bug-fix release.

Minor enhancements:
-------------------
* Added a Networkx connector
  [#471](https://github.com/RDFLib/rdflib/pull/471),
  [#507](https://github.com/RDFLib/rdflib/pull/507)
* Added a graph_tool connector
  [#473](https://github.com/RDFLib/rdflib/pull/473)
* Added a `graphs` method to the Dataset object
  [#504](https://github.com/RDFLib/rdflib/pull/504),
  [#495](https://github.com/RDFLib/rdflib/issues/495)
* Batch commits for `SPARQLUpdateStore`
  [#486](https://github.com/RDFLib/rdflib/pull/486)

Bug fixes:
----------
* Fixed bnode collision bug
  [#506](https://github.com/RDFLib/rdflib/pull/506),
  [#496](https://github.com/RDFLib/rdflib/pull/496),
  [#494](https://github.com/RDFLib/rdflib/issues/494)
* fix `util.from_n3()` parsing Literals with datatypes and Namespace support
  [#503](https://github.com/RDFLib/rdflib/pull/503),
  [#502](https://github.com/RDFLib/rdflib/issues/502)
* make `Identifier.__hash__` stable wrt. multi processes
  [#501](https://github.com/RDFLib/rdflib/pull/501),
  [#500](https://github.com/RDFLib/rdflib/issues/500)
* fix handling `URLInputSource` without content-type
  [#499](https://github.com/RDFLib/rdflib/pull/499),
  [#498](https://github.com/RDFLib/rdflib/pull/498)
* no relative import in `algebra` when run as a script
  [#497](https://github.com/RDFLib/rdflib/pull/497)
* Duplicate option in armstrong `theme.conf` removed
  [#491](https://github.com/RDFLib/rdflib/issues/491)
* `Variable.__repr__` returns a python representation string, not n3
  [#488](https://github.com/RDFLib/rdflib/pull/488)
* fixed broken example
  [#482](https://github.com/RDFLib/rdflib/pull/482)
* trig output fixes
  [#480](https://github.com/RDFLib/rdflib/pull/480)
* set PYTHONPATH to make rdfpipe tests use the right rdflib version
  [#477](https://github.com/RDFLib/rdflib/pull/477)
* fix RDF/XML problem with unqualified use of `rdf:about`
  [#470](https://github.com/RDFLib/rdflib/pull/470),
  [#468](https://github.com/RDFLib/rdflib/issues/468)
* `AuditableStore` improvements
  [#469](https://github.com/RDFLib/rdflib/pull/469),
  [#463](https://github.com/RDFLib/rdflib/pull/463)
* added asserts for `graph.set([s,p,o])` so `s` and `p` aren't `None`
  [#467](https://github.com/RDFLib/rdflib/pull/467)
* `threading.RLock` instances are context managers
  [#465](https://github.com/RDFLib/rdflib/pull/465)
* SPARQLStore does not transform Literal('') into Literal('None') anymore
  [#459](https://github.com/RDFLib/rdflib/pull/459),
  [#457](https://github.com/RDFLib/rdflib/issues/457)
* slight performance increase for graph.all_nodes()
  [#458](https://github.com/RDFLib/rdflib/pull/458)

Testing improvements:
---------------------
* travis: migrate to docker container infrastructure
  [#508](https://github.com/RDFLib/rdflib/pull/508)
* test for narrow python builds (chars > 0xFFFF) (related to
    [#453](https://github.com/RDFLib/rdflib/pull/453),
    [#454](https://github.com/RDFLib/rdflib/pull/454)
  )
  [#456](https://github.com/RDFLib/rdflib/issues/456),
  [#509](https://github.com/RDFLib/rdflib/pull/509)
* dropped testing py3.2
  [#448](https://github.com/RDFLib/rdflib/issues/448)
* Running a local fuseki server on travis and making it failsafe
  [#476](https://github.com/RDFLib/rdflib/pull/476),
  [#475](https://github.com/RDFLib/rdflib/issues/475),
  [#474](https://github.com/RDFLib/rdflib/pull/474),
  [#466](https://github.com/RDFLib/rdflib/pull/466),
  [#460](https://github.com/RDFLib/rdflib/issues/460)
* exclude `def main():` functions from test coverage analysis
  [#472](https://github.com/RDFLib/rdflib/pull/472)


2015/02/19 RELEASE 4.2.0
========================

This is a new minor version of RDFLib including a handful of new features:

* Supporting N-Triples 1.1 syntax using UTF-8 encoding
  [#447](https://github.com/RDFLib/rdflib/pull/447),
  [#449](https://github.com/RDFLib/rdflib/pull/449),
  [#400](https://github.com/RDFLib/rdflib/issues/400)
* Graph comparison now really works using RGDA1 (RDF Graph Digest Algorithm 1)
  [#441](https://github.com/RDFLib/rdflib/pull/441)
  [#385](https://github.com/RDFLib/rdflib/issues/385)
* More graceful degradation than simple crashing for unicode chars > 0xFFFF on
  narrow python builds. Parsing such characters will now work, but issue a
  UnicodeWarning. If you run `python -W all` you will already see a warning on
  `import rdflib` will show a warning (ImportWarning).
  [#453](https://github.com/RDFLib/rdflib/pull/453),
  [#454](https://github.com/RDFLib/rdflib/pull/454)
* URLInputSource now supports json-ld
  [#425](https://github.com/RDFLib/rdflib/pull/425)
* SPARQLStore is now graph aware
  [#401](https://github.com/RDFLib/rdflib/pull/401),
  [#402](https://github.com/RDFLib/rdflib/pull/402)
* SPARQLStore now uses SPARQLWrapper for updates
  [#397](https://github.com/RDFLib/rdflib/pull/397)
* Certain logging output is immediately shown in interactive mode
  [#414](https://github.com/RDFLib/rdflib/pull/414)
* Python 3.4 fully supported
  [#418](https://github.com/RDFLib/rdflib/pull/418)

Minor enhancements & bugs fixed:
--------------------------------

* Fixed double invocation of 2to3
  [#437](https://github.com/RDFLib/rdflib/pull/437)
* PyRDFa parser missing brackets
  [#434](https://github.com/RDFLib/rdflib/pull/434)
* Correctly handle \uXXXX and \UXXXXXXXX escapes in n3 files
  [#426](https://github.com/RDFLib/rdflib/pull/426)
* Logging cleanups and keeping it on stderr
  [#420](https://github.com/RDFLib/rdflib/pull/420)
  [#414](https://github.com/RDFLib/rdflib/pull/414)
  [#413](https://github.com/RDFLib/rdflib/issues/413)
* n3: allow @base URI to have a trailing '#'
  [#407](https://github.com/RDFLib/rdflib/pull/407)
  [#379](https://github.com/RDFLib/rdflib/issues/379)
* microdata: add file:// to base if it's a filename so rdflib can parse its own
  output
  [#406](https://github.com/RDFLib/rdflib/pull/406)
  [#403](https://github.com/RDFLib/rdflib/issues/403)
* TSV Results parse skips empty bindings in result
  [#390](https://github.com/RDFLib/rdflib/pull/390)
* fixed accidental test run due to name
  [#389](https://github.com/RDFLib/rdflib/pull/389)
* Bad boolean list serialization to Turtle & fixed ambiguity between
  Literal(False) and None
  [#387](https://github.com/RDFLib/rdflib/pull/387)
  [#382](https://github.com/RDFLib/rdflib/pull/382)
* Current version number & PyPI link in README.md
  [#383](https://github.com/RDFLib/rdflib/pull/383)


2014/04/15 RELEASE 4.1.2
========================

This is a bug-fix release.

* Fixed unicode/str bug in py3 for rdfpipe
  [#375](https://github.com/RDFLib/rdflib/issues/375)

2014/03/03 RELEASE 4.1.1
========================

This is a bug-fix release.

This will be the last RDFLib release to support python 2.5.

* The RDF/XML Parser was made stricter, now raises exceptions for
  illegal repeated node-elements.
  [#363](https://github.com/RDFLib/rdflib/issues/363)

* The SPARQLUpdateStore now supports non-ascii unicode in update
  statements
  [#356](https://github.com/RDFLib/rdflib/issues/356)

* Fixed a bug in the NTriple/NQuad parser wrt. to unicode escape sequences
  [#352](https://github.com/RDFLib/rdflib/issues/352)

* HTML5Lib is no longer pinned to 0.95
  [#355](https://github.com/RDFLib/rdflib/issues/360)

* RDF/XML Serializer now uses parseType=Literal for well-formed XML literals

* A bug in the manchester OWL syntax was fixed
  [#355](https://github.com/RDFLib/rdflib/issues/355)

2013/12/31 RELEASE 4.1
======================

This is a new minor version RDFLib, which includes a handful of new features:

* A TriG parser was added (we already had a serializer) - it is
  up-to-date wrt. to the newest spec from: http://www.w3.org/TR/trig/

* The Turtle parser was made up to date wrt. to the latest Turtle spec.

* Many more tests have been added - RDFLib now has over 2000
  (passing!) tests. This is mainly thanks to the NT, Turtle, TriG,
  NQuads and SPARQL test-suites from W3C. This also included many
  fixes to the nt and nquad parsers.

* ```ConjunctiveGraph``` and ```Dataset``` now support directly adding/removing
  quads with ```add/addN/remove``` methods.

* ```rdfpipe``` command now supports datasets, and reading/writing context
  sensitive formats.

* Optional graph-tracking was added to the Store interface, allowing
  empty graphs to be tracked for Datasets. The DataSet class also saw
  a general clean-up, see: [#309](https://github.com/RDFLib/rdflib/pull/309)

* After long deprecation, ```BackwardCompatibleGraph``` was removed.

Minor enhancements/bugs fixed:
------------------------------

* Many code samples in the documentation were fixed thanks to @PuckCh

* The new ```IOMemory``` store was optimised a bit

* ```SPARQL(Update)Store``` has been made more generic.

* MD5 sums were never reinitialized in ```rdflib.compare```

* Correct default value for empty prefix in N3
  [#312](https://github.com/RDFLib/rdflib/issues/312)

* Fixed tests when running in a non UTF-8 locale
  [#344](https://github.com/RDFLib/rdflib/issues/344)

* Prefix in the original turtle have an impact on SPARQL query
  resolution
  [#313](https://github.com/RDFLib/rdflib/issues/313)

* Duplicate BNode IDs from N3 Parser
  [#305](https://github.com/RDFLib/rdflib/issues/305)

* Use QNames for TriG graph names
  [#330](https://github.com/RDFLib/rdflib/issues/330)

* \uXXXX escapes in Turtle/N3 were fixed
  [#335](https://github.com/RDFLib/rdflib/issues/335)

* A way to limit the number of triples retrieved from the
  ```SPARQLStore``` was added
  [#346](https://github.com/RDFLib/rdflib/pull/346)

* Dots in localnames in Turtle
  [#345](https://github.com/RDFLib/rdflib/issues/345)
  [#336](https://github.com/RDFLib/rdflib/issues/336)

* ```BNode``` as Graph's public ID
  [#300](https://github.com/RDFLib/rdflib/issues/300)

* Introduced ordering of ```QuotedGraphs```
  [#291](https://github.com/RDFLib/rdflib/issues/291)

2013/05/22 RELEASE 4.0.1
========================

Following RDFLib tradition, some bugs snuck into the 4.0 release.
This is a bug-fixing release:

* the new URI validation caused lots of problems, but is
  nescessary to avoid ''RDF injection'' vulnerabilities. In the
  spirit of ''be liberal in what you accept, but conservative in
  what you produce", we moved validation to serialisation time.

* the   ```rdflib.tools```   package    was   missing   from   the
  ```setup.py```  script, and  was therefore  not included  in the
  PYPI tarballs.

* RDF parser choked on empty namespace URI
  [#288](https://github.com/RDFLib/rdflib/issues/288)

* Parsing from ```sys.stdin``` was broken
  [#285](https://github.com/RDFLib/rdflib/issues/285)

* The new IO store had problems with concurrent modifications if
  several graphs used the same store
  [#286](https://github.com/RDFLib/rdflib/issues/286)

* Moved HTML5Lib dependency to the recently released 1.0b1 which
  support python3

2013/05/16 RELEASE 4.0
======================

This release includes several major changes:

* The new SPARQL 1.1 engine (rdflib-sparql) has been included in
  the core distribution. SPARQL 1.1 queries and updates should
  work out of the box.

  * SPARQL paths are exposed as operators on ```URIRefs```, these can
    then be be used with graph.triples and friends:

    ```py
    # List names of friends of Bob:
    g.triples(( bob, FOAF.knows/FOAF.name , None ))

    # All super-classes:
    g.triples(( cls, RDFS.subClassOf * '+', None ))
    ```

      * a new ```graph.update``` method will apply SPARQL update statements

* Several RDF 1.1 features are available:
  * A new ```DataSet``` class
  * ```XMLLiteral``` and ```HTMLLiterals```
  * ```BNode``` (de)skolemization is supported through ```BNode.skolemize```,
    ```URIRef.de_skolemize```, ```Graph.skolemize``` and ```Graph.de_skolemize```

* Handled of Literal equality was split into lexical comparison
  (for normal ```==``` operator) and value space (using new ```Node.eq```
  methods). This introduces some slight backwards incomaptible
  changes, but was necessary, as the old version had
  inconsisten hash and equality methods that could lead the
  literals not working correctly in dicts/sets.
  The new way is more in line with how SPARQL 1.1 works.
  For the full details, see:

  https://github.com/RDFLib/rdflib/wiki/Literal-reworking

* Iterating over ```QueryResults``` will generate ```ResultRow``` objects,
  these allow access to variable bindings as attributes or as a
  dict. I.e.

  ```py
  for row in graph.query('select ... ') :
     print row.age, row["name"]
  ```

* "Slicing" of Graphs and Resources as syntactic sugar:
  ([#271](https://github.com/RDFLib/rdflib/issues/271))

  ```py
  graph[bob : FOAF.knows/FOAF.name]
            -> generator over the names of Bobs friends
  ```

* The ```SPARQLStore``` and ```SPARQLUpdateStore``` are now included
  in the RDFLib core

* The documentation has been given a major overhaul, and examples
  for most features have been added.


Minor Changes:
--------------

* String operations on URIRefs return new URIRefs: ([#258](https://github.com/RDFLib/rdflib/issues/258))
  ```py
  >>> URIRef('http://example.org/')+'test
  rdflib.term.URIRef('http://example.org/test')
  ```

* Parser/Serializer plugins are also found by mime-type, not just
  by plugin name:  ([#277](https://github.com/RDFLib/rdflib/issues/277))
* ```Namespace``` is no longer a subclass of ```URIRef```
* URIRefs and Literal language tags are validated on construction,
  avoiding some "RDF-injection" issues ([#266](https://github.com/RDFLib/rdflib/issues/266))
* A new memory store needs much less memory when loading large
  graphs ([#268](https://github.com/RDFLib/rdflib/issues/268))
* Turtle/N3 serializer now supports the base keyword correctly ([#248](https://github.com/RDFLib/rdflib/issues/248))
* py2exe support was fixed ([#257](https://github.com/RDFLib/rdflib/issues/257))
* Several bugs in the TriG serializer were fixed
* Several bugs in the NQuads parser were fixed

2013/03/01 RELEASE 3.4
======================

This release introduced new parsers for structured data in HTML.
In particular formats: hturtle, rdfa, mdata and an auto-detecting
html format were added.  Thanks to Ivan Herman for this!

This release includes a lot of admin maintentance - correct
dependencies for different python versions, etc.  Several py3 bugs
were also fixed.

This release drops python 2.4 compatability - it was just getting
too expensive for us to maintain. It should however be compatible
with any cpython from 2.5 through 3.3.

* ```node.md5_term``` is now deprecated, if you use it let us know.

* Literal.datatype/language are now read-only properties ([#226](https://github.com/RDFLib/rdflib/issues/226))
* Serializing to file fails in py3 ([#249](https://github.com/RDFLib/rdflib/issues/249))
* TriX serializer places two xmlns attributes on same element ([#250](https://github.com/RDFLib/rdflib/issues/250))
* RDF/XML parser fails on when XML namespace is not explicitly declared ([#247](https://github.com/RDFLib/rdflib/issues/247))
* Resource class should "unbox" Resource instances on add ([#215](https://github.com/RDFLib/rdflib/issues/215))
* Turtle/N3 does not encode final quote of a string ([#239](https://github.com/RDFLib/rdflib/issues/239))
* float Literal precision lost when serializing graph to turtle or n3 ([#237](https://github.com/RDFLib/rdflib/issues/237))
* plain-literal representation of xsd:decimals fixed
* allow read-only sleepycat stores
* language tag parsing in N3/Turtle fixes to allow several subtags.

2012/10/10 RELEASE 3.2.3
========================

Almost identical to 3.2.2
A stupid bug snuck into 3.2.2, and querying graphs were broken.

* Fixes broken querying ([#234](https://github.com/RDFLib/rdflib/issues/234))
* graph.transitiveClosure now works with loops ([#206](https://github.com/RDFLib/rdflib/issues/206))

2012/09/25 RELEASE 3.2.2
========================

This is mainly a maintenance release.

This release should be compatible with python 2.4 through to 3.

Changes:

* Improved serialization/parsing roundtrip tests led to some fixes
  of obscure parser/serializer bugs. In particular complex string
  Literals in ntriples improved a lot.
* The terms of a triple are now asserted to be RDFLib Node's in graph.add
  This should avoid getting strings and other things in the store. ([#200](https://github.com/RDFLib/rdflib/issues/200))
* Added a specific TurtleParser that does not require the store to be
  non-formula aware. ([#214](https://github.com/RDFLib/rdflib/issues/214))
* A trig-serializer was added, see:
  http://www4.wiwiss.fu-berlin.de/bizer/trig/
* BNode generation was made thread-safe ([#209](https://github.com/RDFLib/rdflib/issues/209))
  (also fixed better by dzinxed)
* Illegal BNode IDs removed from NT output: ([#212](https://github.com/RDFLib/rdflib/issues/212))
* and more minor bug fixes that had no issues

2012/04/24 RELEASE 3.2.1
========================

This is mainly a maintenance release.

Changes:

* New setuptools entry points for query processors and results

* Literals constructed from other literals copy datatype/lang ([#188](https://github.com/RDFLib/rdflib/issues/188))
* Relative URIs are resolved incorrectly after redirects ([#130](https://github.com/RDFLib/rdflib/issues/130))
* Illegal prefixes in turtle output ([#161](https://github.com/RDFLib/rdflib/issues/161))
* Sleepcat store unstable prefixes ([#201](https://github.com/RDFLib/rdflib/issues/201))
* Consistent toPyton() for all node objects ([#174](https://github.com/RDFLib/rdflib/issues/174))
* Better random BNode ID in multi-thread environments ([#185](https://github.com/RDFLib/rdflib/issues/185))

2012/01/19 RELEASE 3.2.0
========================

Major changes:
* Thanks to Thomas Kluyver, rdflib now works under python3,
  the setup.py script automatically runs 2to3.

* Unit tests were updated and cleaned up. Now all tests should pass.
* Documentation was updated and cleaned up.

* A new resource oriented API was added:
  http://code.google.com/p/rdflib/issues/detail?id=166

  Fixed many minor issues:
    * http://code.google.com/p/rdflib/issues/detail?id=177
  http://code.google.com/p/rdflib/issues/detail?id=129
      Restored compatability with Python 2.4
    * http://code.google.com/p/rdflib/issues/detail?id=158
  Reworking of Query result handling
    * http://code.google.com/p/rdflib/issues/detail?id=193
  generating xml:base attribute in RDF/XML output
* http://code.google.com/p/rdflib/issues/detail?id=180
      serialize(format="pretty-xml") fails on cyclic links


2011/03/17 RELEASE 3.1.0
========================

Fixed a range of minor issues:

* http://code.google.com/p/rdflib/issues/detail?id=128

  Literal.__str__ does not behave like unicode

* http://code.google.com/p/rdflib/issues/detail?id=141

  (RDFa Parser) Does not handle application/xhtml+xml

* http://code.google.com/p/rdflib/issues/detail?id=142

  RDFa TC #117: Fragment identifiers stripped from BASE

* http://code.google.com/p/rdflib/issues/detail?id=146

  Malformed literals produced when rdfa contains newlines

* http://code.google.com/p/rdflib/issues/detail?id=152

  Namespaces beginning with _ are invalid

* http://code.google.com/p/rdflib/issues/detail?id=156

  Turtle Files with a UTF-8 BOM fail to parse

* http://code.google.com/p/rdflib/issues/detail?id=154

  ClosedNamespace.__str__ returns URIRef not str

* http://code.google.com/p/rdflib/issues/detail?id=150

  IOMemory does not override open

* http://code.google.com/p/rdflib/issues/detail?id=153

  Timestamps with microseconds *and* "Z" timezone are not parsed

* http://code.google.com/p/rdflib/issues/detail?id=118

  DateTime literals with offsets fail to convert to Python

* http://code.google.com/p/rdflib/issues/detail?id=157

  Timestamps with timezone information are not parsed

* http://code.google.com/p/rdflib/issues/detail?id=151

        problem with unicode literals in rdflib.compare.graph_diff

* http://code.google.com/p/rdflib/issues/detail?id=149

  BerkeleyDB Store broken with create=False

* http://code.google.com/p/rdflib/issues/detail?id=134

  Would be useful if Graph.query could propagate kwargs to a

  plugin processor

* http://code.google.com/p/rdflib/issues/detail?id=133

  Graph.connected exception when passed empty graph

* http://code.google.com/p/rdflib/issues/detail?id=129

  Not compatible with Python 2.4

* http://code.google.com/p/rdflib/issues/detail?id=119

  Support Python's set operations on Graph

* http://code.google.com/p/rdflib/issues/detail?id=130

  NT output encoding to utf-8 broken as it goes through

  _xmlcharrefreplace

* http://code.google.com/p/rdflib/issues/detail?id=121#c1

  Store SPARQL Support


2010/05/13 RELEASE 3.0.0
========================

Working test suite with all tests passing.

Removed dependency on setuptools.

(Issue #43) Updated Package and Module Names to follow
conventions outlined in
http://www.python.org/dev/peps/pep-0008/

Removed SPARQL bits and non core plugins. They are mostly
moving to http://code.google.com/p/rdfextras/ at least until
they are stable.

Fixed datatype for Literal(True).

Fixed Literal to enforce contraint of having either a language
or datatype but not both.

Fixed Literal's repr.

Fixed to Graph Add/Sub/Mul opterators.

Upgraded RDFa parser to pyRdfa.

Upgraded N3 parser to the one from CWM.

Fixed unicode encoding issue involving N3Parser.

N3 serializer improvments.

Fixed HTTP content-negotiation

Fixed Store.namespaces method (which caused a few issues
depending on Store implementation being used.)

Fixed interoperability issue with plugin module.

Fixed use of Deprecated functionality.

2009/03/30 RELEASE 2.4.1
========================

Fixed Literal comparison case involving Literal's with
datatypes of XSD.base64Binary.

Fixed case where XSD.date was matching before XSD.dateTime for
datetime instances.

Fixed jython interoperability issue (issue #53).

Fixed Literal repr to handle apostrophes correctly (issue #28).

Fixed Literal's repr to be consistent with its ```__init__``` (issue #33).


2007/04/04 RELEASE 2.4.0
========================

Improved Literal comparison / equality

Sparql cleanup.

getLiteralValue now returns the Literal object instead of the
result of toPython().  Now that Literals override a good
coverage of comparison operators, they should be passed around
as first class objects in the SPARQL evaluation engine.

Added support for session bnodes re: sparql

Fixed prolog reduce/reduce conflict.  Added Py_None IncRefs
where they were being passed into Python method invokations
(per drewp's patch)

Fixed sparql queries involving empty namespace prefix.

Fixed the selected variables sparql issue

Fixed <BASE> support in SPARQL queries.

Fixed involving multiple unions and queries are nested more
than one level (bug in _getAllVariables causing failure when
parent.top is None)

Fixed test_sparql_equals.py.

Fixed sparql json result comma errors issue.

Fixed test_sparql_json_results.py (SELECT * variables out of
order)

Added a 4Suite-based SPARQL XML Writer implementation.  If
4Suite is not installed, the fallback python saxutils is used
instead

applied patch from
http://rdflib.net/issues/2007/02/23/bugs_in_rdflib.sparql.queryresult/issue

The restriction on GRAPH patterns with variables has been
relieved a bit to allow such usage when the variable is
provided as an initial binding

Fix for OPTIONAL patterns.  P1 OPT P2, where P1 and P2 shared
variables which were bound to BNodes were not unifying on
these BNode variable efficiently / correctly.  The fix was to
add bindings for 'stored' BNodes so they aren't confused for
wildcards




Added support to n3 parser for retaining namespace bindings.

Fixed several RDFaParser bugs.

Added serializer specific argument support.

Fixed a few PrettyXMLSerializer issues and added a max_depth
option.

Fixed some TurtleSerializer issues.

Fixed some N3Serializer issues.



Added support easy_install

added link to long_descriptin for easy_install -U rdflib==dev
to work; added download_url back

added continuous-releases-using-subversion bit



Added rdflib_tools package
  Added rdfpipe
  Added initial EARLPluging



Improved test running... using nose... added tests

Exposed generated test cases for nose to find.
added bit to configure 'setup.py nosetests' to run doc tests

added nose test bits



Added md5_term_hash method to terms.

Added commit_pending_transaction argument to Graph's close
method.

Added DeprecationWarning to rdflib.constants

Added a NamespaceDict class for those who want to avoid the
Namespace as subclass of URIRef issues

Added bind function

Fixed type of Namespace re: URIRef vs. unicode

Improved ValueError message

Changed value method's any argument to default to True

Changed ```__repr__``` to always reflect that it's an rdf.Literal --
as this is the case even though we now have it acting like the
corresponding type in some casses

A DISTINCT was added to the SELECT clause to ensure duplicate
triples are not returned (an RDF graph is a set of triples) -
which can happen for certain join expressions.

Support for ConditionalAndExpressionList and
RelationalExpressionList (|| and && operators in FILTER)

Fixed context column comparison.  The hash integer was being
compared with 'F' causing a warning:Warning: Truncated
incorrect DOUBLE value: 'F'

applied patch in
http://rdflib.net/issues/2006/12/13/typos_in_abstractsqlstore.py/issue

fix for
http://rdflib.net/issues/2006/12/07/problems_with_graph.seq()_when_sequences_contain_more_than_9_items./issue





General code cleanup (removing redundant imports, changing
relative imports to absolute imports etc)

Removed usage of deprecated bits.

Added a number of test cases.

Added DeprecationWarning for save method

refactoring of GraphPattern

ReadOnlyGraphAggregate uses Graph constructor properly to
setup (optionally) a common store


Fixed bug with . (fullstop) in localname parts.

Changed Graph's value method to return None instead of raising
an AssertionError.

Fixed conversion of (exiplicit) MySQL ports to integers.

Fixed MySQL store so it properly calculates ```__len__``` of
individual Graphs

Aligned with how BerkeleyDB is generating events (remove events
are expressed in terms of interned strings)

Added code to catch unpickling related exceptions

Added BerkeleyDB store implementation.

Merged TextIndex from michel-events branch.


2006/10/15 RELEASE 2.3.3
========================

Added TriXParser, N3Serializer and TurtleSerializer.

Added events to store interface: StoreCreated, TripleAdded and
TripleRemoved.

Added Journal Reader and Writer.

Removed BerkeleyDB level journaling.

Added support for triple quoted Literal's.

Fixed some corner cases with Literal comparison.

Fixed PatternResolution for patterns that return contexts only.

Fixed NodePickler not to choke on unhashable objects.

Fixed Namespace's ```__getattr__``` hack to ignore names starting
with __

Added SPARQL != operator.

Fixed query result ```__len__``` (more efficient).

Fixed and improved RDFa parser.

redland patches from
http://rdflib.net/pipermail/dev/2006-September/000069.html

various patches for the testsuite -
http://rdflib.net/pipermail/dev/2006-September/000069.html


2006/08/01 RELEASE 2.3.2
========================

Added SPARQL query support.

Added XSD to/from Python datatype support to Literals.

Fixed ConjunctiveGraph so that it is a proper subclass of Graph.

Added Deprecation Warning when BackwardCompatGraph gets used.

Added RDFa parser.

Added Collection Class for working with RDF Collections.

Added method to Graph for testing connectedness

Fixed bug in N3 parser where identical BNodes were not being combined.

Fixed literal quoting in N3 serializer.

Fixed RDF/XML serializer to skip over N3 bits.

Changed Literal and URIRef instanciation to catch
UnicodeDecodeErrors - which were being thrown when the default
decoding method (ascii) was hitting certain characters.

Changed Graph's bind method to also override the binding in
the case of an existing generated bindings.

Added FOPLRelationalModel - a set of utility classes that
implement a minimal Relational Model of FOPL implemented as a
SQL database (uses identifier/value interning and integer
half-md5-hashes for space and index efficiency).

Changed MySQL store to use FOPLRelationalModel plus fixes and
improvements.

Added more test cases.

Cleaned up source code to follow pep8 / pep257.


2006/02/27 RELEASE 2.3.1
========================

Added save method to BackwardCompatibleGraph so that
example.py etc work again.

Applied patch from Drew Perttula to add local_time_zone
argument to util's date_time method.

Fixed a relativize bug in the rdf/xml serializer.

Fixed NameError: global name 'URIRef' is not defined error in
BerkeleyDB.py by adding missing import.

Applied patch for Seq to sort list by integer, added by Drew
Hess.

Added a preserve_bnode_ids option to rdf/xml parser.

Applied assorted patches for tests (see
http://tracker.asemantics.com/rdflib/ticket/8 )

Applied redland.diff (see
http://tracker.asemantics.com/rdflib/ticket/9 )

Applied changes specified
http://tracker.asemantics.com/rdflib/ticket/7

Added a set method to Graph.

Fixed RDF/XML serializer so that it does not choke on n3 bits
(rather it'll just ignore them)


2005/12/23 RELEASE 2.3.0
========================

See http://rdflib.net/2.3.0/ for most up-to-date release notes

Added N3 support to Graph and Store.

Added Sean's n3p parser, and ntriples parser.

BerkeleyDB implementation has been revamped in the process of
expanding it to support the new requirements n3
requirements. It also now persists a journal -- more to come.

detabified source files.

Literal and parsers now distinguish between datatype of None and datatype of "".

Store-agnostic 'fallback' implementation of REGEX matching
(inefficient but provides the capability to stores that don't
support it natively). Implemented as a 'wrapper' around any
Store which replaces REGEX terms with None (before dispatching
to the store) and whittles out results that don't match the
given REGEX term expression(s).

Store-agnostic 'fallback' implementation of transactional
rollbacks (also inefficient but provides the capablity to
stores that don't support it natively). Implemented as a
wrapper that tracks a 'thread-safe' list of reversal
operations (for every add, track the remove call that reverts
the store, and vice versa). Upon store.rollback(), execute the
reverse operations. However, this doesn't guarantee
durability, since if the system fails before the rollbacks are
all executed, the store will remain in an invalid state, but
it provides Atomicity in the best case scenario.


2005/10/10 RELEASE 2.2.3
========================

Fixed BerkeleyDB backend to commit after an add and
remove. This should help just a bit with those unclean
shutdowns ;)

Fixed use of logging so that it does not mess with the root
logger. Thank you, Arve, for pointing this one out.

Fixed Graph's value method to have default for subject in
addition to predicate and object.

Fixed Fourthought backend to be consistent with interface. It
now supports an empty constructor and an open method that
takes a configuration string.


2005/09/10 RELEASE 2.2.2
========================

Applied patch from inkel to add encoding argument to all
serialization related methods.

Fixed XMLSerializer bug regarding default namespace bindings.

Fixed namespace binding bug involving binding a second default
namespace.

Applied patch from Gunnar AAstrand Grimnes to add context
support to ```__iadd__``` on Graph. (Am considering the lack of
context support a bug. Any users currently using ```__iadd__```, let
me know if this breaks any of your code.)

Added Fourthought backend contributed by Chimezie Ogbuji.

Fixed a RDF/XML parser bug relating to XMLLiteral and
escaping.

Fixed setup.py so that install does not try to uninstall
(rename_old) before installing; there's now an uninstall
command if one needs to uninstall.


2005/08/25 RELEASE 2.2.1
========================

Fixed issue regarding Python2.3 compatibility.

Fixed minor issue with URIRef's absolute method.


2005/08/12 RELEASE 2.1.4
========================

Added optional base argument to URIRef.

Fixed bug where load and parse had inconsistent behavior.

Added a FileInputSource.

Added skeleton sparql parser and test framework.

Included pyparsing (pyparsing.sourceforge.net) for sparql parsing.

Added attribute support to namespaces.


2005/06/28 RELEASE 2.1.3
========================

Added Ivan's sparql-p implementation.

Literal is now picklable.

Added optional base argument to serialize methods about which to relativize.

Applied patch to remove some dependencies on Python 2.4
features.

Fixed BNode's n3 serialization bug (recently introduced).

Fixed a collections related bug.


2005/05/13 RELEASE 2.1.2
========================

Added patch from Sidnei da Silva that adds a sqlobject based backend.

Fixed bug in PrettyXMLSerializer (rdf prefix decl was missing sometimes)

Fixed bug in RDF/XML parser where empty collections where
causing exceptions.


2005/05/01 RELEASE 2.1.1
========================

Fixed a number of bugs relating to 2.0 backward compatibility.

Fixed split_uri to handle URIs with _ in them properly.

Fixed bug in RDF/XML handler's absolutize that would cause some URIRefs to end in ##

Added check_context to Graph.

Added patch the improves IOMemory implementation.


2005/04/12 RELEASE 2.1.0
========================

Merged TripleStore and InformationStore into Graph.

Added plugin support (or at least cleaned up, made consistent the
plugin support that existed).

Added value and seq methods to Graph.

Renamed prefix_mapping to bind.

Added namespaces method that is a generator over all prefix,
namespace bindings.

Added notion of NamespaceManager.

Added couple new backends, IOMemory and ZODB.


2005/03/19 RELEASE 2.0.6
========================

Added pretty-xml serializer (inlines BNodes where possible,
typed nodes, Collections).

Fixed bug in NTParser and n3 methods where not all characters
where being escaped.

Changed label and comment methods to return default passed in
when there is no label or comment. Moved methods to Store
Class. Store no longer inherits from Schema.

Fixed bug involving a case with rdf:about='#'

Changed InMemoryBackend to update third index in the same style it
does the first two.


2005/01/08 RELEASE 2.0.5
========================

Added publicID argument to Store's load method.

Added RDF and RDFS to top level rdflib package.


2004/10/14 RELEASE 2.0.4
========================

Removed unfinished functionality.

Fixed bug where another prefix other than rdf was getting
defined for the rdf namespace (causing an assertion to fail).

Fixed bug in serializer where nodeIDs were not valid NCNames.


2004/04/21 RELEASE 2.0.3
========================

Added missing "from __future__ import generators" statement to
InformationStore.

Simplified RDF/XML serializer fixing a few bugs involving
BNodes.

Added a reset method to RDF/XML parser.

Changed 'if foo' to "if foo is not None" in a few places in
the RDF/XML parser.

Fully qualified imports in rdflib.syntax {parser, serializer}.

Context now goes through InformationStore (was bypassing it
going directly to backend).


2004/03/22 RELEASE 2.0.2
========================

Improved performance of Identifier equality tests.

Added missing "from __future__ import generators" statements
needed to run on Python2.2.

Added alternative to shlib.move() if it isn't present.

Fixed bug that occured when specifying a backend to
InformationStore's constructor.

Fixed bug recently introduced into InformationStore's remove
method.


2004/03/15 RELEASE 2.0.1
========================

Fixed a bug in the SleepyCatBackend multi threaded concurrency
support. (Tested fairly extensively under the following
conditions: multi threaded, multi process, and both).

> NOTE: fix involved change to database format -- so 2.0.1 will not be
> able to open databases created with 2.0.0

Removed the use of the Concurrent wrapper around
InMemoryBackend and modified InMemoryBackend to handle
concurrent requests. (Motivated by Concurrent's poor
performance on bigger TripleStores.)

Improved the speed of len(store) by making backends
responsible for implementing ```__len__```.

Context objects now have a identifier property.


2004/03/10 RELEASE 2.0.0
========================

Fixed a few bugs in the SleepyCatBackend multi process
concurrency support.

Removed rdflib.Resource

Changed remove to now take a triple pattern and removed
remove_triples method.

Added ```__iadd__``` method to Store in support of store +=
another_store.


2004/01/04 RELEASE 1.3.2
========================

Added a serialization dispatcher.

Added format arg to save method.

Store now remembers prefix/namespace bindings.

Backends are now more pluggable

...

2003/10/14 RELEASE 1.3.1
========================

Fixed bug in serializer where triples where only getting
serialized the first time.

Added type checking for contexts.

Fixed bug that caused comparisons with a Literal to fail when
the right hand side was not a string.

Added DB_INIT_CDB flag to SCBacked for supporting multiple
reader/single writer access

Changed rdf:RDF to be optional to conform with latest spec.

Fixed handling of XMLLiterals


2003/04/40 RELEASE 1.3.0
========================

Removed bag_id support and added it to OLD_TERMS.

Added a double hash for keys in SCBacked.

Fixed _HTTPClient so that it no longer removes metadata about
a context right after it adds it.

Added a KDTreeStore and RedlandStore backends.

Added a StoreTester.


2003/02/28 RELEASE 1.2.4
========================

Fixed bug in SCBackend where language and datatype information
where being ignored.

Fixed bug in transitive_subjects.

Updated some of the test cases that where not up to date.

async_load now adds more http header and error information to
the InformationStore.


2003/02/11 RELEASE 1.2.3
========================

Fixed bug in load methods where relative URLs where not being
absolutized correctly on Windows.

Fixed serializer so that it throws an exception when trying to
serialize a graph with a predicate that can not be split.


2003/02/07 RELEASE 1.2.2
========================

Added an exists method to the BackwardCompatibility mixin.

Added versions of remove, remove_triples and triples methods
to the BackwardCompatility mixin for TripleStores that take an
s, p, o as opposed to an (s, p, o).


2003/02/03 RELEASE 1.2.1
========================

Added support for parsing XMLLiterals.

Added support for proper charmod checking (only works in
Python2.3).

Fixed remaining rdfcore test cases that where not passing.

Fixed windows bug in AbstractInformationStore's run method.


2003/01/02 RELEASE 1.2.0
========================

Added systemID, line #, and column # to error messages.

BNode prefix is now composed of ascii_letters instead of letters.

Added a bsddb backed InformationStore.

Added an asyncronous load method, methods for scheduling context
updates, and a run method.


2002/12/16 RELEASE 1.1.5
========================

Introduction of InformationStore, a TripleStore with the
addition of context support.

Resource ```__getitem__``` now returns object (no longer returns a
Resource for the object).

Fixed bug in parser that was introduced in last release
regaurding unqualified names.


2002/12/10 RELEASE 1.1.4
========================

Interface realigned with last stable release.

Serializer now uses more of the abbreviated forms where
possible.

Parser optimized and cleaned up.

Added third index to InMemoryStore.

The load and parse methods now take a single argument.

Added a StringInputSource for to support parsing from strings.

Renamed rdflib.BTreeTripleStore.TripleStore to
rdflib.BTreeTripleStore.BTreeTripleStore.

Minor reorganization of mix-in classes.


2002/12/03 RELEASE 1.1.3
========================

BNodes now created with a more unique identifier so BNodes
from different sessions do not collide.

Added initial support for XML Literals (for now they are
parsed into Literals).

Resource is no longer a special kind of URIRef.

Resource no longer looks at range to determine default return
type for ```__getitem__```. Instead there is now a get(predicate, default)
method.


2002/11/21 RELEASE 1.1.2
========================

Fixed Literal's ```__eq__``` method so that Literal('foo')=='foo' etc.

Fixed Resource's ```__setitem__``` method so that it does not raise
a dictionary changed size while iterating exception.


2002/11/09 RELEASE 1.1.1
========================

Resource is now a special kind of URIRef

Resource's ```__getitem__``` now looks at rdfs:range to determine
return type in default case.



2002/11/05 RELEASE 1.1.0
========================

# A new development branch

Cleaned up interface and promoted it to SIR: Simple Interface
for RDF.

Updated parser to use SAX2 interfaces instead of using expat directly.

Added BTreeTripleStore, a ZODB BTree TripleStore backend. And
a default pre-mixed TripleStore that uses it.

Synced with latest (Editor's draft) RDF/XML spec.

Added datatype support.

Cleaned up interfaces for load/parse: removed generate_path
from loadsave andrenamed parse_URI to parse.


2002/10/08 RELEASE 0.9.6
========================


# The end of a development branch

BNode can now be created with specified value.

Literal now has a language attribute.

Parser now creates Literals with language attribute set
appropriately as determined by xml:lang attributes.


TODO: Serializer-Literals-language attribute

TODO: Change ```__eq__``` so that Literal("foo")=="foo" etc

TripleStores now support "in" operator.
For example: if (s, p, o) in store: print "Found ", s, p, o

Added APIs/object for working at level of a Resource. NOTE:
This functionality is still experimental

Consecutive Collections now parse correctly.

2002/08/06 RELEASE 0.9.5
========================


Added support for rdf:parseType="Collection"

Added items generator for getting items in a Collection

Renamed rdflib.triple_store to rdflib.TripleStore to better follow
python style conventions.

Added an Identifier Class

Moved each node into its own Python module.

Added rdflib.util with a first and uniq function.

Added a little more to example.py

Removed generate_uri since we have BNodes now.


2002/07/29 RELEASE 0.9.4
========================


Added support for proposed rdf:nodeID to both the parser and
serializer.

Reimplemented serializer which now nests things where
possible.

Added partial support for XML Literal parseTypes.


2002/07/16 RELEASE 0.9.3
========================


Fixed bug where bNodes where being created for nested property
elements when they where not supposed to be.

Added lax mode that will convert rdf/xml files that contain bare
IDs etc. Also, lax mode will only report parse errors instead of
raising exceptions.

Added missing check for valid attribute names in the case of
production 5.18 of latest WD spec.


2002/07/05 RELEASE 0.9.2
========================


Added missing constants for SUBPROPERTYOF, ISDEFINEDBY.

Added test case for running all of the rdf/xml test cases.

Reimplemented rdf/xml parser to conform to latest WD.


2002/06/10 RELEASE 0.9.1
========================


There is now a remove and a remove_triples (no more overloaded
remove).

Layer 2 has been merged with layer 1 since there is no longer a
need for them to be separate layers.

The generate_uri method has moved to LoadSave since triple stores
do not have a notion of a uri. [Also, with proper bNode support on
its way the need for a generate_uri might not be as high.]

Fixed bug in node's n3 function: URI -> URIRef.

Replaced string based exceptions with class based exceptions.

Added PyUnit TestCase for parser.py

Added N-Triples parser.

Added ```__len__``` and ```__eq__``` methods to store interface.


2002/06/04 RELEASE 0.9.0
========================

Initial release after being split from redfootlib.
