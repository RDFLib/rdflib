.. _upgrade4to5: Upgrading from RDFLib version 4.2.2 to 5.0.0

============================================
Upgrading 4.2.2 to 5.0.0
============================================

RDFLib version 5.0.0 appeared over 3 years after the previous release, 4.2.2 and contains a large number of both enhancements and bug fixes. Fundamentally though, 5.0.0 is compatible with 4.2.2.


Major Changes
-------------

Literal Ordering
^^^^^^^^^^^^^^^^
Literal total ordering `PR #793 <https://github.com/RDFLib/rdflib/pull/793>`_ is implemented. That means all literals can now be compared to be greater than or less than any other literal.
This is required for implementing some specific SPARQL features, but it is counter-intuitive to those who are expecting a TypeError when certain normally-incompatible types are compared.
For example, comparing a ``Literal(int(1), datatype=xsd:integer)`` to ``Literal(datetime.date(10,01,2020), datatype=xsd:date)`` using a ``>`` or ``<`` operator in rdflib 4.2.2 and earlier, would normally throw a TypeError,
however in rdflib 5.0.0 this operation now returns a True or False according to the Literal Total Ordering according the rules outlined in `PR #793 <https://github.com/RDFLib/rdflib/pull/793>`_

Removed RDF Parsers
^^^^^^^^^^^^^^^^^^^
The RDFa and Microdata format RDF parsers were removed from rdflib. There are still other python libraries available to implement these parsers.

All Changes
-----------

This list has been assembled from Pull Request and commit information.

General Bugs Fixed:
^^^^^^^^^^^^^^^^^^^
* Pr 451 redux
  `PR #978 <https://github.com/RDFLib/rdflib/pull/978>`_
* NTriples fails to parse URIs with only a scheme
  `ISSUE #920 <https://github.com/RDFLib/rdflib/issues/920>`_
  `PR #974 <https://github.com/RDFLib/rdflib/pull/974>`_
* cannot clone it on windows - Remove colons from test result files. Fix #901.
  `ISSUE #901 <https://github.com/RDFLib/rdflib/issues/901>`_
  `PR #971 <https://github.com/RDFLib/rdflib/pull/971>`_
* Add requirement for requests to setup.py
  `PR #969 <https://github.com/RDFLib/rdflib/pull/969>`_
* fixed URIRef including native unicode characters
  `PR #961 <https://github.com/RDFLib/rdflib/pull/961>`_
* DCTERMS.format not working
  `ISSUE #932 <https://github.com/RDFLib/rdflib/issues/932>`_
* infixowl.manchesterSyntax do not encode strings
  `PR #906 <https://github.com/RDFLib/rdflib/pull/906>`_
* Fix blank node label to not contain '_:' during parsing
  `PR #886 <https://github.com/RDFLib/rdflib/pull/886>`_
* rename new SPARQLWrapper to SPARQLConnector
  `PR #872 <https://github.com/RDFLib/rdflib/pull/872>`_
* Fix #859. Unquote and Uriquote Literal Datatype.
  `PR #860 <https://github.com/RDFLib/rdflib/pull/860>`_
* Parsing nquads
  `ISSUE #786 <https://github.com/RDFLib/rdflib/issues/786>`_
* ntriples spec allows for upper-cased lang tag, fixes #782
  `PR #784 <https://github.com/RDFLib/rdflib/pull/784>`_
* Error parsing N-Triple file using RDFlib
  `ISSUE #782 <https://github.com/RDFLib/rdflib/issues/782>`_
* Adds escaped single quote to literal parser
  `PR #736 <https://github.com/RDFLib/rdflib/pull/736>`_
* N3 parse error on single quote within single quotes
  `ISSUE #732 <https://github.com/RDFLib/rdflib/issues/732>`_
* Fixed #725
  `PR #730 <https://github.com/RDFLib/rdflib/pull/730>`_
* test for issue #725: canonicalization collapses BNodes
  `PR #726 <https://github.com/RDFLib/rdflib/pull/726>`_
* RGDA1 graph canonicalization sometimes still collapses distinct BNodes
  `ISSUE #725 <https://github.com/RDFLib/rdflib/issues/725>`_
* Accept header should use a q parameter
  `PR #720 <https://github.com/RDFLib/rdflib/pull/720>`_
* Added test for Issue #682 and fixed.
  `PR #718 <https://github.com/RDFLib/rdflib/pull/718>`_
* Incompatibility with Python3: unichr
  `ISSUE #687 <https://github.com/RDFLib/rdflib/issues/687>`_
* namespace.py include colon in ALLOWED_NAME_CHARS
  `PR #663 <https://github.com/RDFLib/rdflib/pull/663>`_
* namespace.py fix compute_qname missing namespaces
  `PR #649 <https://github.com/RDFLib/rdflib/pull/649>`_
* RDFa parsing Error! `__init__()` got an unexpected keyword argument 'encoding'
  `ISSUE #639 <https://github.com/RDFLib/rdflib/issues/639>`_
* Bugfix: `term.Literal.__add__`
  `PR #451 <https://github.com/RDFLib/rdflib/pull/451>`_
* fixup of #443
  `PR #445 <https://github.com/RDFLib/rdflib/pull/445>`_
* Microdata to rdf second edition bak
  `PR #444 <https://github.com/RDFLib/rdflib/pull/444>`_

Enhanced Features:
^^^^^^^^^^^^^^^^^^
* Register additional serializer plugins for SPARQL mime types.
  `PR #987 <https://github.com/RDFLib/rdflib/pull/987>`_
* Pr 388 redux
  `PR #979 <https://github.com/RDFLib/rdflib/pull/979>`_
* Allows RDF terms introduced by JSON-LD 1.1
  `PR #970 <https://github.com/RDFLib/rdflib/pull/970>`_
* make SPARQLConnector work with DBpedia
  `PR #941 <https://github.com/RDFLib/rdflib/pull/941>`_
* ClosedNamespace returns right exception for way of access
  `PR #866 <https://github.com/RDFLib/rdflib/pull/866>`_
* Not adding all namespaces for n3 serializer
  `PR #832 <https://github.com/RDFLib/rdflib/pull/832>`_
* Adds basic support of xsd:duration
  `PR #808 <https://github.com/RDFLib/rdflib/pull/808>`_
* Add possibility to set authority and basepath to skolemize graph
  `PR #807 <https://github.com/RDFLib/rdflib/pull/807>`_
* Change notation3 list realization to non-recursive function.
  `PR #805 <https://github.com/RDFLib/rdflib/pull/805>`_
* Suppress warning for not using custom encoding.
  `PR #800 <https://github.com/RDFLib/rdflib/pull/800>`_
* Add support to parsing large xml inputs
  `ISSUE #749 <https://github.com/RDFLib/rdflib/issues/749>`_
  `PR #750 <https://github.com/RDFLib/rdflib/pull/750>`_
* improve hash efficiency by directly using str/unicode hash
  `PR #746 <https://github.com/RDFLib/rdflib/pull/746>`_
* Added the csvw prefix to the RDFa initial context.
  `PR #594 <https://github.com/RDFLib/rdflib/pull/594>`_
* syncing changes from pyMicrodata
  `PR #587 <https://github.com/RDFLib/rdflib/pull/587>`_
* Microdata parser: updated the parser to the latest version of the microdata->rdf note (published in December 2014)
  `PR #443 <https://github.com/RDFLib/rdflib/pull/443>`_
* Literal.toPython() support for xsd:hexBinary
  `PR #388 <https://github.com/RDFLib/rdflib/pull/388>`_

SPARQL Fixes:
^^^^^^^^^^^^^
* Total order patch patch
  `PR #862 <https://github.com/RDFLib/rdflib/pull/862>`_
* use <<= instead of deprecated <<
  `PR #861 <https://github.com/RDFLib/rdflib/pull/861>`_
* Fix #847
  `PR #856 <https://github.com/RDFLib/rdflib/pull/856>`_
* RDF Literal "1"^^xsd:boolean should _not_ coerce to True
  `ISSUE #847 <https://github.com/RDFLib/rdflib/issues/847>`_
* Makes NOW() return an UTC date
  `PR #844 <https://github.com/RDFLib/rdflib/pull/844>`_
* NOW() SPARQL should return an xsd:dateTime with a timezone
  `ISSUE #843 <https://github.com/RDFLib/rdflib/issues/843>`_
* fix property paths bug: issue #715
  `PR #822 <https://github.com/RDFLib/rdflib/pull/822>`_
  `ISSUE #715 <https://github.com/RDFLib/rdflib/issues/715>`_
* MulPath: correct behaviour of n3()
  `PR #820 <https://github.com/RDFLib/rdflib/pull/820>`_
* Literal total ordering
  `PR #793 <https://github.com/RDFLib/rdflib/pull/793>`_
* Remove SPARQLWrapper dependency
  `PR #744 <https://github.com/RDFLib/rdflib/pull/744>`_
* made UNION faster by not preventing duplicates
  `PR #741 <https://github.com/RDFLib/rdflib/pull/741>`_
* added a hook to add custom functions to SPARQL
  `PR #723 <https://github.com/RDFLib/rdflib/pull/723>`_
* Issue714
  `PR #717 <https://github.com/RDFLib/rdflib/pull/717>`_
* Use <<= instead of deprecated << in SPARQL parser
  `PR #417 <https://github.com/RDFLib/rdflib/pull/417>`_
* Custom FILTER function for SPARQL engine
  `ISSUE #274 <https://github.com/RDFLib/rdflib/issues/274>`_

Code Quality and Cleanups:
^^^^^^^^^^^^^^^^^^^^^^^^^^
* a slightly opinionated autopep8 run
  `PR #870 <https://github.com/RDFLib/rdflib/pull/870>`_
* remove rdfa and microdata parsers from core RDFLib
  `PR #828 <https://github.com/RDFLib/rdflib/pull/828>`_
* ClosedNamespace KeyError -> AttributeError
  `PR #827 <https://github.com/RDFLib/rdflib/pull/827>`_
* typo in rdflib/plugins/sparql/update.py
  `ISSUE #760 <https://github.com/RDFLib/rdflib/issues/760>`_
* Fix logging in interactive mode
  `PR #731 <https://github.com/RDFLib/rdflib/pull/731>`_
* make namespace module flake8-compliant, change exceptions in that mod…
  `PR #711 <https://github.com/RDFLib/rdflib/pull/711>`_
* delete ez_setup.py?
  `ISSUE #669 <https://github.com/RDFLib/rdflib/issues/669>`_
* code duplication issue between rdflib and pymicrodata
  `ISSUE #582 <https://github.com/RDFLib/rdflib/issues/582>`_
* Transition from 2to3 to use of six.py to be merged in 5.0.0-dev
  `PR #519 <https://github.com/RDFLib/rdflib/pull/519>`_
* sparqlstore drop deprecated methods and args
  `PR #516 <https://github.com/RDFLib/rdflib/pull/516>`_
* python3 code seems shockingly inefficient
  `ISSUE #440 <https://github.com/RDFLib/rdflib/issues/440>`_
* removed md5_term_hash, fixes #240
  `PR #439 <https://github.com/RDFLib/rdflib/pull/439>`_
  `ISSUE #240 <https://github.com/RDFLib/rdflib/issues/240>`_

Testing:
^^^^^^^^
* 3.7 for travis
  `PR #864 <https://github.com/RDFLib/rdflib/pull/864>`_
* Added trig unit tests to highlight some current parsing/serializing issues
  `PR #431 <https://github.com/RDFLib/rdflib/pull/431>`_

Documentation Fixes:
^^^^^^^^^^^^^^^^^^^^
* Fix a doc string in the query module
  `PR #976 <https://github.com/RDFLib/rdflib/pull/976>`_
* setup.py: Make the license field use an SPDX identifier
  `PR #789 <https://github.com/RDFLib/rdflib/pull/789>`_
* Update README.md
  `PR #764 <https://github.com/RDFLib/rdflib/pull/764>`_
* Update namespaces_and_bindings.rst
  `PR #757 <https://github.com/RDFLib/rdflib/pull/757>`_
* DOC: README.md: rdflib-jsonld, https uris
  `PR #712 <https://github.com/RDFLib/rdflib/pull/712>`_
* make doctest support py2/py3
  `ISSUE #707 <https://github.com/RDFLib/rdflib/issues/707>`_
* `pip install rdflib` (as per README.md) gets OSError on Mint 18.1
  `ISSUE #704 <https://github.com/RDFLib/rdflib/issues/704>`_
  `PR #717 <https://github.com/RDFLib/rdflib/pull/717>`_
* Use <<= instead of deprecated << in SPARQL parser
  `PR #417 <https://github.com/RDFLib/rdflib/pull/417>`_
* Custom FILTER function for SPARQL engine
  `ISSUE #274 <https://github.com/RDFLib/rdflib/issues/274>`_

Code Quality and Cleanups:
^^^^^^^^^^^^^^^^^^^^^^^^^^
* a slightly opinionated autopep8 run
  `PR #870 <https://github.com/RDFLib/rdflib/pull/870>`_
* remove rdfa and microdata parsers from core RDFLib
  `PR #828 <https://github.com/RDFLib/rdflib/pull/828>`_
* ClosedNamespace KeyError -> AttributeError
  `PR #827 <https://github.com/RDFLib/rdflib/pull/827>`_
* typo in rdflib/plugins/sparql/update.py
  `ISSUE #760 <https://github.com/RDFLib/rdflib/issues/760>`_
* Fix logging in interactive mode
  `PR #731 <https://github.com/RDFLib/rdflib/pull/731>`_
* make namespace module flake8-compliant, change exceptions in that mod…
  `PR #711 <https://github.com/RDFLib/rdflib/pull/711>`_
* delete ez_setup.py?
  `ISSUE #669 <https://github.com/RDFLib/rdflib/issues/669>`_
* code duplication issue between rdflib and pymicrodata
  `ISSUE #582 <https://github.com/RDFLib/rdflib/issues/582>`_
* Transition from 2to3 to use of six.py to be merged in 5.0.0-dev
  `PR #519 <https://github.com/RDFLib/rdflib/pull/519>`_
* sparqlstore drop deprecated methods and args
  `PR #516 <https://github.com/RDFLib/rdflib/pull/516>`_
* python3 code seems shockingly inefficient
  `ISSUE #440 <https://github.com/RDFLib/rdflib/issues/440>`_
* removed md5_term_hash, fixes #240
  `PR #439 <https://github.com/RDFLib/rdflib/pull/439>`_
  `ISSUE #240 <https://github.com/RDFLib/rdflib/issues/240>`_

Testing:
^^^^^^^^
* 3.7 for travis
  `PR #864 <https://github.com/RDFLib/rdflib/pull/864>`_
* Added trig unit tests to highlight some current parsing/serializing issues
  `PR #431 <https://github.com/RDFLib/rdflib/pull/431>`_

Documentation Fixes:
^^^^^^^^^^^^^^^^^^^^
* Fix a doc string in the query module
  `PR #976 <https://github.com/RDFLib/rdflib/pull/976>`_
* setup.py: Make the license field use an SPDX identifier
  `PR #789 <https://github.com/RDFLib/rdflib/pull/789>`_
* Update README.md
  `PR #764 <https://github.com/RDFLib/rdflib/pull/764>`_
* Update namespaces_and_bindings.rst
  `PR #757 <https://github.com/RDFLib/rdflib/pull/757>`_
* DOC: README.md: rdflib-jsonld, https uris
  `PR #712 <https://github.com/RDFLib/rdflib/pull/712>`_
* make doctest support py2/py3
  `ISSUE #707 <https://github.com/RDFLib/rdflib/issues/707>`_
* `pip install rdflib` (as per README.md) gets OSError on Mint 18.1
  `ISSUE #704 <https://github.com/RDFLib/rdflib/issues/704>`_

