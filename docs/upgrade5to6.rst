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
