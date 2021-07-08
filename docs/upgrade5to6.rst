.. _upgrade4to5: Upgrading from RDFLib version 5.0.0 to 6.0.0

============================================
Upgrading 5.0.0 to 6.0.0
============================================

6.0.0 fully adopts Python 3 practices and drops Python 2 support so it is neater, faster and generally more modern than
5.0.0. It also tidies up the ``Graph`` API (removing duplicate functions) so it does include a few breaking changes.
Additionally, there is a long list of PRs merged into 6.0.0 adding a number of small fixes and features which are listed
below.

RDFLib version 5.0.0 was released in 2020, 3 years after the previous version (4.2.2) and is fundamentally 5.0.0
compatible with. If you need very long-term backwards-compatibility or Python 2 support, you need 5.0.0.


Major Changes
-------------

The most notable changes in RDFLib 6.0.0 are:

Python 3.7+
^^^^^^^^^^^
* The oldest version of python you can use to run RDFLib is now 3.7.
* This is a big jump from RDFLib 5.0.0 that worked on python 2.7 and 3.5.
* This change is to allow the library maintainers to adopt more modern development tools,
  newer language features, and avoid the need to support EOL versions of python in he future

JSON-LD integration and JSON-LD 1.1
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
* The json-ld serializer/parser plugin was by far the most commonly used RDFLib addon.
* Last year we brought it under the RDFLib org in Github
* Now for 6.0.0 release the JSON-LD serializer and parser are integrated into RDFLib core
* This includes the experimental support for the JSON-LD v1.1 spec
* You no longer need to install the json-ld dependency separately.


All Changes
-----------

This list has been assembled from Pull Request and commit information.

General Bugs Fixed:
^^^^^^^^^^^^^^^^^^^
* Pr 451 redux
  `PR #978 <https://github.com/RDFLib/rdflib/pull/978>`_


Enhanced Features:
^^^^^^^^^^^^^^^^^^
* Register additional serializer plugins for SPARQL mime types.
  `PR #987 <https://github.com/RDFLib/rdflib/pull/987>`_


SPARQL Fixes:
^^^^^^^^^^^^^
* Total order patch patch
  `PR #862 <https://github.com/RDFLib/rdflib/pull/862>`_


Code Quality and Cleanups:
^^^^^^^^^^^^^^^^^^^^^^^^^^
* a slightly opinionated autopep8 run
  `PR #870 <https://github.com/RDFLib/rdflib/pull/870>`_


Testing:
^^^^^^^^
* 3.7 for travis
  `PR #864 <https://github.com/RDFLib/rdflib/pull/864>`_


Documentation Fixes:
^^^^^^^^^^^^^^^^^^^^
* Fix a doc string in the query module
  `PR #976 <https://github.com/RDFLib/rdflib/pull/976>`_

Integrade JSON-LD into RDFLib:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
`PR #1354 <https://github.com/RDFLib/rdflib/pull//1354>`_
