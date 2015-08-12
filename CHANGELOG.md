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

  Sleepycat Store broken with create=False

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

Aligned with how Sleepycat is generating events (remove events
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

Removed Sleepycat level journaling.

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
Sleepycat.py by adding missing import.

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

Sleepycat implementation has been revamped in the process of
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

Fixed Sleepycat backend to commit after an add and
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
