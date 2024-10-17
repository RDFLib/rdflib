## 2024-10-17 RELEASE 7.1.0

This minor release incorporates just over 100 substantive PRs - interesting 
things submitted by people - and around 140 auto-generated update PRs from 
dependabot and similar. 

There are no major changes in this release over 7.0.0 and this release can
be used in place of 7.0.0 without much worry about altered behaviour.

Since the previous release, we have updated the way auto-generated PRs are
handled to ease the job of maintainers.

Due to the large numbers of PRs contained in this release, an abbreviated 
listing of them only is provided here:

Merged human-made PRs:

* 2024-10-16 - Bovlb patch 1
  [PR #2931](https://github.com/RDFLib/rdflib/pull/2931)
* 2024-10-16 - Redo XSD Datetime, Date, Time, Duration parser and serializers
  [PR #2929](https://github.com/RDFLib/rdflib/pull/2929)
* 2024-10-15 - Don't export hashes to requirements.txt from poetry, in readthedocs g…
  [PR #2930](https://github.com/RDFLib/rdflib/pull/2930)
* 2024-10-10 - Use pytest in one more test and update contributing guide
  [PR #2919](https://github.com/RDFLib/rdflib/pull/2919)
* 2024-10-10 - Fix for reassigned term aliases
  [PR #2925](https://github.com/RDFLib/rdflib/pull/2925)
* 2024-10-01 - Replace html5lib with html5lib-modern
  [PR #2911](https://github.com/RDFLib/rdflib/pull/2911)
* 2024-09-29 - Issue #2812: Reflect explicitly XSD-typed Literals in JSON-LD serialization
  [PR #2889](https://github.com/RDFLib/rdflib/pull/2889)
* 2024-09-01 - Replace deprecated method in csv2rdf
  [PR #2901](https://github.com/RDFLib/rdflib/pull/2901)
* 2024-08-31 - Fix test logic for datetime
  [PR #2900](https://github.com/RDFLib/rdflib/pull/2900)
* 2024-08-31 - Format docstring for `Graph.value` to match others
  [PR #2899](https://github.com/RDFLib/rdflib/pull/2899)
* 2024-08-27 - In .patch serializer, default to "add" operation if no operation
  [PR #2898](https://github.com/RDFLib/rdflib/pull/2898)
* 2024-08-26 - Implement RDF Patch serializer
  [PR #2877](https://github.com/RDFLib/rdflib/pull/2877)
* 2024-08-26 - Add initial implementation of RDF Patch parser.
  [PR #2863](https://github.com/RDFLib/rdflib/pull/2863)
* 2024-08-26 - jsonld - Improve handling of URNs in norm_url
  [PR #2892](https://github.com/RDFLib/rdflib/pull/2892)
* 2024-08-10 - chore: fix mypy and test failure
  [PR #2879](https://github.com/RDFLib/rdflib/pull/2879)
* 2024-08-06 - feat: update DOAP namespace
  [PR #2869](https://github.com/RDFLib/rdflib/pull/2869)
* 2024-08-06 - fix: typo in PR template
  [PR #2870](https://github.com/RDFLib/rdflib/pull/2870)
* 2024-08-01 - Change some more internal usages of ConjunctiveGraph to Dataset to silence warnings
  [PR #2867](https://github.com/RDFLib/rdflib/pull/2867)
* 2024-08-01 - Fix missing features of IdentifiedNode
  [PR #2868](https://github.com/RDFLib/rdflib/pull/2868)
* 2024-07-31 - Fix explicit dataset (`FROM` and `FROM NAMED` clauses)
  [PR #2794](https://github.com/RDFLib/rdflib/pull/2794)
* 2024-07-30 - Marks some doctstrings as raw, to silence a SyntaxWarning about invalid escape sequences.
  [PR #2756](https://github.com/RDFLib/rdflib/pull/2756)
* 2024-07-30 - Convert old string substitutions to f-strings in term.py
  [PR #2864](https://github.com/RDFLib/rdflib/pull/2864)
* 2024-07-30 - Prevent Collection from adding 'rdf:nil rdf:rest rdf:nil.' triples
  [PR #2818](https://github.com/RDFLib/rdflib/pull/2818)
* 2024-07-29 - Dependabot ignore newer updates to setuptools.
  [PR #2860](https://github.com/RDFLib/rdflib/pull/2860)
* 2024-07-29 - Add optional orjson support for faster json reading and writing
  [PR #2854](https://github.com/RDFLib/rdflib/pull/2854)
* 2024-07-28 - Fix and extend implementation of `BytesIOWrapper`
  [PR #2853](https://github.com/RDFLib/rdflib/pull/2853)
* 2024-07-28 - Add skolemization support for ntriples, nquads, hextuples and json-ld support at parse time
  [PR #2816](https://github.com/RDFLib/rdflib/pull/2816)
* 2024-07-26 - Add JSON-LD extraction from HTML
  [PR #2804](https://github.com/RDFLib/rdflib/pull/2804)
* 2024-07-25 - New sphinx docs fix
  [PR #2852](https://github.com/RDFLib/rdflib/pull/2852)
* 2024-07-24 - More typing fixes for mypy update
  [PR #2851](https://github.com/RDFLib/rdflib/pull/2851)
* 2024-07-24 - Fix typo, "ConjunctionGraph" -> "ConjunctiveGraph"
  [PR #2850](https://github.com/RDFLib/rdflib/pull/2850)
* 2024-07-24 - feat: hextuple parser and serializer now supports anonymous graph names
  [PR #2815](https://github.com/RDFLib/rdflib/pull/2815)
* 2024-07-24 - Change dependabot strategy back to "auto"
  [PR #2844](https://github.com/RDFLib/rdflib/pull/2844)
* 2024-07-24 - test: Add test for Graph.items
  [PR #2819](https://github.com/RDFLib/rdflib/pull/2819)
* 2024-07-24 - Pin black
  [PR #2843](https://github.com/RDFLib/rdflib/pull/2843)
* 2024-07-24 - Fix bug preventing nested FILTER statements from working (#709)
  [PR #2822](https://github.com/RDFLib/rdflib/pull/2822)
* 2024-07-24 - Ruff fixes
  [PR #2842](https://github.com/RDFLib/rdflib/pull/2842)
* 2024-07-24 - Fix typing issues that appeared after latest mypy update
  [PR #2841](https://github.com/RDFLib/rdflib/pull/2841)
* 2024-07-24 - Reconcile debpendabot
  [PR #2840](https://github.com/RDFLib/rdflib/pull/2840)
* 2024-07-24 - Update dependabot.yml
  [PR #2838](https://github.com/RDFLib/rdflib/pull/2838)
* 2024-07-10 - Fix testing for warnings with pytest 8 (#2748)
  [PR #2817](https://github.com/RDFLib/rdflib/pull/2817)
* 2024-06-17 - Deprecate ConjunctiveGraph (#2405)
  [PR #2786](https://github.com/RDFLib/rdflib/pull/2786)
* 2024-06-17 - fix: task expected type string, got bool
  [PR #2791](https://github.com/RDFLib/rdflib/pull/2791)
* 2024-06-17 - fix: lint
  [PR #2792](https://github.com/RDFLib/rdflib/pull/2792)
* 2024-06-17 - Reformat code, execute task black
  [PR #2798](https://github.com/RDFLib/rdflib/pull/2798)
* 2024-06-17 - Fix for gha:validation error in Github actions
  [PR #2799](https://github.com/RDFLib/rdflib/pull/2799)
* 2024-06-12 - Remove test/data/suites/w3c/dawg-data-r2/sort/.manifest.ttl.swp since…
  [PR #2797](https://github.com/RDFLib/rdflib/pull/2797)
* 2024-05-17 - docs: fix "Build docs" command in developers.rst
  [PR #2783](https://github.com/RDFLib/rdflib/pull/2783)
* 2024-05-17 - Update .mailmap for Nicholas Car
  [PR #2776](https://github.com/RDFLib/rdflib/pull/2776)
* 2024-05-17 - Update _GEO.py to include GeoSPARQL 1.1 vocabularies
  [PR #2771](https://github.com/RDFLib/rdflib/pull/2771)
* 2024-04-27 - set default jsonld version to 1.1. autoformat for corresponding files.
  [PR #2751](https://github.com/RDFLib/rdflib/pull/2751)
* 2024-04-27 - removed unused #ignore comments in algebra.py
  [PR #2746](https://github.com/RDFLib/rdflib/pull/2746)
* 2024-04-18 - Let jsonld handle value nodes/Literal for context search
  [PR #2750](https://github.com/RDFLib/rdflib/pull/2750)
* 2024-03-20 - Cleanup literal comparison ops (#863)
  [PR #2745](https://github.com/RDFLib/rdflib/pull/2745)
* 2024-03-20 - fix: use guess_format when plugin for format not found
  [PR #2735](https://github.com/RDFLib/rdflib/pull/2735)
* 2024-03-20 - Remove unused open method in SPARQLUpdateStore
  [PR #2693](https://github.com/RDFLib/rdflib/pull/2693)
* 2024-03-20 - fix: readthedocs failure with poetry 1.8
  [PR #2744](https://github.com/RDFLib/rdflib/pull/2744)
* 2024-03-20 - fix: typo in Container method name: type_of_conatiner --> type_of_container
  [PR #2733](https://github.com/RDFLib/rdflib/pull/2733)
* 2024-03-13 - fix: gh actions on PR
  [PR #2731](https://github.com/RDFLib/rdflib/pull/2731)
* 2024-03-12 - Fix LongTurtle multi-BN object serialization bug
  [PR #2700](https://github.com/RDFLib/rdflib/pull/2700)
* 2024-03-12 - JSON-LD Docco & Examples
  [PR #2529](https://github.com/RDFLib/rdflib/pull/2529)
* 2024-02-27 - Add SHACL path to RDFLib Path utility and corresponding tests
  [PR #2699](https://github.com/RDFLib/rdflib/pull/2699)
* 2024-02-18 - Add documentation for optional dependencies
  [PR #2701](https://github.com/RDFLib/rdflib/pull/2701)
* 2023-11-30 - Update _SOSA.py with ssn-ex IRIs
  [PR #2654](https://github.com/RDFLib/rdflib/pull/2654)
* 2023-10-29 - fix typo in SPARQLConnector init docstring
  [PR #2619](https://github.com/RDFLib/rdflib/pull/2619)
* 2023-10-24 - Add changelog to sphinx docs
  [PR #2617](https://github.com/RDFLib/rdflib/pull/2617)
* 2023-09-26 - Issue 2378 goal: Get CI to pass without ALLOW_UNICODE on doctests
  [PR #2383](https://github.com/RDFLib/rdflib/pull/2383)
* 2023-09-25 - docs: remove Unicode literals from docstrings
  [PR #2604](https://github.com/RDFLib/rdflib/pull/2604)
* 2023-09-10 - feat: enable `check_untyped_defs` for Mypy
  [PR #2580](https://github.com/RDFLib/rdflib/pull/2580)
* 2023-09-07 - style: Enable most remaining pyupgrade rules for ruff
  [PR #2579](https://github.com/RDFLib/rdflib/pull/2579)
* 2023-09-07 - style: Eliminate quotes from type hints
  [PR #2578](https://github.com/RDFLib/rdflib/pull/2578)
* 2023-09-07 - build: fix minimum version testing
  [PR #2577](https://github.com/RDFLib/rdflib/pull/2577)
* 2023-09-05 - style: add `from __future__ import annotations`
  [PR #2576](https://github.com/RDFLib/rdflib/pull/2576)
* 2023-09-05 - style: homogenize docstrings
  [PR #2575](https://github.com/RDFLib/rdflib/pull/2575)
* 2023-09-04 - style: remove unnecessary shebangs `#!...`
  [PR #2574](https://github.com/RDFLib/rdflib/pull/2574)
* 2023-09-04 - style: remove modelines
  [PR #2573](https://github.com/RDFLib/rdflib/pull/2573)
* 2023-09-04 - style: disable global ignore for E402 in ruff
  [PR #2572](https://github.com/RDFLib/rdflib/pull/2572)
* 2023-09-04 - build: remove unneeded override for PyParsing
  [PR #2571](https://github.com/RDFLib/rdflib/pull/2571)
* 2023-09-03 - style: eliminate unused `noqa` statements
  [PR #2566](https://github.com/RDFLib/rdflib/pull/2566)
* 2023-09-02 - style: fix more linting/ruff issues in tests
  [PR #2565](https://github.com/RDFLib/rdflib/pull/2565)
* 2023-09-02 - test: convert more unittest based tests to pytest
  [PR #2564](https://github.com/RDFLib/rdflib/pull/2564)
* 2023-08-31 - style: fix the naming of test data constants
  [PR #2561](https://github.com/RDFLib/rdflib/pull/2561)
* 2023-08-31 - test: migrate some tests from unittest to pytest
  [PR #2562](https://github.com/RDFLib/rdflib/pull/2562)
* 2023-08-31 - style: Fix linting errors in serializer tests
  [PR #2559](https://github.com/RDFLib/rdflib/pull/2559)
* 2023-08-30 - Add test case for CG operator return type
  [PR #2557](https://github.com/RDFLib/rdflib/pull/2557)
* 2023-08-30 - style: add noqa to allow camelCase for mock function
  [PR #2558](https://github.com/RDFLib/rdflib/pull/2558)
* 2023-08-30 - style: fix linting errors in `test/test_graph`
  [PR #2556](https://github.com/RDFLib/rdflib/pull/2556)
* 2023-08-30 - fix: SPARQL `LOAD ... INTO GRAPH` handling
  [PR #2554](https://github.com/RDFLib/rdflib/pull/2554)
* 2023-08-29 - fix: `queryGraph` selection for `query` and `update`
  [PR #2546](https://github.com/RDFLib/rdflib/pull/2546)
* 2023-08-29 - build: replace Flake8, FlakeHeaven and isort with ruff
  [PR #2548](https://github.com/RDFLib/rdflib/pull/2548)
* 2023-08-28 - fix: remove `print()` calls from SPARQL algebra code
  [PR #2553](https://github.com/RDFLib/rdflib/pull/2553)
* 2023-08-28 - build: remove unused setuptools setting
  [PR #2547](https://github.com/RDFLib/rdflib/pull/2547)
* 2023-08-26 - test: add python variants to variant based tests
  [PR #2544](https://github.com/RDFLib/rdflib/pull/2544)
* 2023-08-25 - test: add more accommodation for DBpedia issues
  [PR #2543](https://github.com/RDFLib/rdflib/pull/2543)
* 2023-08-25 - test: make graph variant tests more granular
  [PR #2540](https://github.com/RDFLib/rdflib/pull/2540)
* 2023-08-24 - test: add skips to accommodate a DBpedia outage
  [PR #2539](https://github.com/RDFLib/rdflib/pull/2539)
* 2023-08-15 - fix: make rdflib.term.Node abstract (fixes #2518)
  [PR #2520](https://github.com/RDFLib/rdflib/pull/2520)
* 2023-08-15 - Fix nested list expansion in JSON-LD
  [PR #2517](https://github.com/RDFLib/rdflib/pull/2517)
* 2023-08-10 - refactor: don't use the same variable name for different types
  [PR #2523](https://github.com/RDFLib/rdflib/pull/2523)
* 2023-08-06 - fix a tiny typo
  [PR #2519](https://github.com/RDFLib/rdflib/pull/2519)
* 2023-08-02 - Introduce abstract base class
  [PR #2516](https://github.com/RDFLib/rdflib/pull/2516)

Auto-generated PRs:

* 2024-10-16 - Revert "build(deps): bump library/python from 3.12.7-slim to 3.13.0-slim in /docker/unstable"
  [PR #2932](https://github.com/RDFLib/rdflib/pull/2932)
* 2024-10-16 - build(deps): bump library/python from 3.12.7-slim to 3.13.0-slim in /docker/unstable
  [PR #2926](https://github.com/RDFLib/rdflib/pull/2926)
* 2024-10-10 - build(deps): bump library/python from 3.12.6-slim to 3.12.7-slim in /docker/latest
  [PR #2920](https://github.com/RDFLib/rdflib/pull/2920)
* 2024-10-10 - build(deps-dev): bump ruff from 0.6.8 to 0.6.9
  [PR #2921](https://github.com/RDFLib/rdflib/pull/2921)
* 2024-10-10 - build(deps): bump library/python from 3.12.6-slim to 3.12.7-slim in /docker/unstable
  [PR #2922](https://github.com/RDFLib/rdflib/pull/2922)
* 2024-09-30 - build(deps-dev): bump ruff from 0.6.5 to 0.6.8
  [PR #2917](https://github.com/RDFLib/rdflib/pull/2917)
* 2024-09-30 - build(deps): bump library/python from `15bad98` to `ad48727` in /docker/unstable
  [PR #2915](https://github.com/RDFLib/rdflib/pull/2915)
* 2024-09-29 - build(deps-dev): bump ruff from 0.6.2 to 0.6.5
  [PR #2908](https://github.com/RDFLib/rdflib/pull/2908)
* 2024-09-21 - build(deps): bump library/python from 3.12.5-slim to 3.12.6-slim in /docker/unstable
  [PR #2910](https://github.com/RDFLib/rdflib/pull/2910)
* 2024-09-21 - build(deps): bump library/python from 3.12.5-slim to 3.12.6-slim in /docker/latest
  [PR #2909](https://github.com/RDFLib/rdflib/pull/2909)
* 2024-09-21 - build(deps-dev): bump pytest from 8.3.2 to 8.3.3
  [PR #2907](https://github.com/RDFLib/rdflib/pull/2907)
* 2024-08-26 - build(deps): bump lxml from 5.2.2 to 5.3.0
  [PR #2882](https://github.com/RDFLib/rdflib/pull/2882)
* 2024-08-26 - build(deps): bump library/python from 3.12.4-slim to 3.12.5-slim in /docker/latest
  [PR #2886](https://github.com/RDFLib/rdflib/pull/2886)
* 2024-08-26 - build(deps): bump library/python from 3.12.4-slim to 3.12.5-slim in /docker/unstable
  [PR #2885](https://github.com/RDFLib/rdflib/pull/2885)
* 2024-08-26 - build(deps): bump orjson from 3.10.6 to 3.10.7
  [PR #2883](https://github.com/RDFLib/rdflib/pull/2883)
* 2024-08-26 - build(deps-dev): bump mypy from 1.11.1 to 1.11.2
  [PR #2896](https://github.com/RDFLib/rdflib/pull/2896)
* 2024-08-26 - build(deps): bump pyparsing from 3.1.2 to 3.1.4
  [PR #2895](https://github.com/RDFLib/rdflib/pull/2895)
* 2024-08-26 - build(deps-dev): bump ruff from 0.5.6 to 0.6.2
  [PR #2894](https://github.com/RDFLib/rdflib/pull/2894)
* 2024-08-11 - build(deps-dev): bump wheel from 0.43.0 to 0.44.0
  [PR #2874](https://github.com/RDFLib/rdflib/pull/2874)
* 2024-08-10 - build(deps-dev): bump ruff from 0.5.5 to 0.5.6
  [PR #2873](https://github.com/RDFLib/rdflib/pull/2873)
* 2024-08-10 - build(deps-dev): bump coverage from 7.6.0 to 7.6.1
  [PR #2872](https://github.com/RDFLib/rdflib/pull/2872)
* 2024-08-10 - build(deps-dev): bump mypy from 1.11.0 to 1.11.1
  [PR #2871](https://github.com/RDFLib/rdflib/pull/2871)
* 2024-08-10 - build(deps): bump library/python from `740d94a` to `a3e58f9` in /docker/unstable
  [PR #2875](https://github.com/RDFLib/rdflib/pull/2875)
* 2024-08-10 - build(deps): bump library/python from `740d94a` to `a3e58f9` in /docker/latest
  [PR #2876](https://github.com/RDFLib/rdflib/pull/2876)
* 2024-07-29 - build(deps-dev): bump pytest from 8.3.1 to 8.3.2
  [PR #2858](https://github.com/RDFLib/rdflib/pull/2858)
* 2024-07-29 - build(deps-dev): bump ruff from 0.5.4 to 0.5.5
  [PR #2859](https://github.com/RDFLib/rdflib/pull/2859)
* 2024-07-29 - build(deps): bump library/python from `52f92c5` to `740d94a` in /docker/latest
  [PR #2856](https://github.com/RDFLib/rdflib/pull/2856)
* 2024-07-29 - build(deps): bump library/python from `52f92c5` to `740d94a` in /docker/unstable
  [PR #2855](https://github.com/RDFLib/rdflib/pull/2855)
* 2024-07-24 - build(deps-dev): bump mypy from 1.8.0 to 1.11.0
  [PR #2848](https://github.com/RDFLib/rdflib/pull/2848)
* 2024-07-24 - build(deps): bump library/python from 3.12.2-slim to 3.12.4-slim in /docker/unstable
  [PR #2845](https://github.com/RDFLib/rdflib/pull/2845)
* 2024-07-24 - build(deps): bump library/python from `f11725a` to `52f92c5` in /docker/latest
  [PR #2846](https://github.com/RDFLib/rdflib/pull/2846)
* 2024-07-24 - build(deps): bump lxml from 4.9.3 to 5.2.2
  [PR #2847](https://github.com/RDFLib/rdflib/pull/2847)
* 2024-07-24 - build(deps-dev): bump types-setuptools from 69.5.0.20240513 to 71.1.0.20240723
  [PR #2834](https://github.com/RDFLib/rdflib/pull/2834)
* 2024-07-24 - build(deps-dev): bump myst-parser from 2.0.0 to 3.0.1
  [PR #2773](https://github.com/RDFLib/rdflib/pull/2773)
* 2024-07-24 - build(deps-dev): bump black from 24.3.0 to 24.4.2
  [PR #2770](https://github.com/RDFLib/rdflib/pull/2770)
* 2024-07-24 - build(deps-dev): bump pytest from 7.4.3 to 8.3.1
  [PR #2837](https://github.com/RDFLib/rdflib/pull/2837)
* 2024-07-24 - build(deps-dev): bump mypy from 1.6.1 to 1.8.0
  [PR #2676](https://github.com/RDFLib/rdflib/pull/2676)
* 2024-07-23 - build(deps): bump library/python from `2fba8e7` to `f11725a` in /docker/latest
  [PR #2827](https://github.com/RDFLib/rdflib/pull/2827)
* 2024-07-23 - build(deps-dev): bump setuptools from 69.5.1 to 71.1.0
  [PR #2832](https://github.com/RDFLib/rdflib/pull/2832)
* 2024-07-23 - build(deps-dev): bump ruff from 0.5.2 to 0.5.4
  [PR #2831](https://github.com/RDFLib/rdflib/pull/2831)
* 2024-07-15 - build(deps-dev): bump types-setuptools from 69.5.0.20240415 to 69.5.0.20240513
  [PR #2789](https://github.com/RDFLib/rdflib/pull/2789)
* 2024-07-15 - build(deps-dev): bump ruff from 0.4.1 to 0.5.2
  [PR #2825](https://github.com/RDFLib/rdflib/pull/2825)
* 2024-07-15 - build(deps-dev): bump coverage from 7.5.4 to 7.6.0
  [PR #2824](https://github.com/RDFLib/rdflib/pull/2824)
* 2024-07-15 - build(deps-dev): bump typing-extensions from 4.11.0 to 4.12.2
  [PR #2826](https://github.com/RDFLib/rdflib/pull/2826)
* 2024-07-15 - build(deps-dev): bump coverage from 7.4.4 to 7.5.4
  [PR #2805](https://github.com/RDFLib/rdflib/pull/2805)
* 2024-07-15 - build(deps): bump library/python from 3.12.2-slim to 3.12.4-slim in /docker/latest
  [PR #2808](https://github.com/RDFLib/rdflib/pull/2808)
* 2024-07-15 - build(deps): bump berkeleydb from 18.1.8 to 18.1.10
  [PR #2813](https://github.com/RDFLib/rdflib/pull/2813)
* 2024-06-19 - [pre-commit.ci] pre-commit autoupdate
  [PR #2777](https://github.com/RDFLib/rdflib/pull/2777)  
* 2024-06-17 - build(deps): bump library/python from `eb53cb9` to `5c73034` in /docker/latest
  [PR #2725](https://github.com/RDFLib/rdflib/pull/2725)
* 2024-05-17 - build(deps): bump poetry from 1.8.2 to 1.8.3 in /devtools
  [PR #2787](https://github.com/RDFLib/rdflib/pull/2787)
* 2024-04-27 - [pre-commit.ci] pre-commit autoupdate
  [PR #2755](https://github.com/RDFLib/rdflib/pull/2755)  
* 2024-05-17 - build(deps): bump networkx from 2.6.3 to 3.1
  [PR #2458](https://github.com/RDFLib/rdflib/pull/2458)
* 2024-04-27 - build(deps-dev): bump black from 24.3.0 to 24.4.0
  [PR #2766](https://github.com/RDFLib/rdflib/pull/2766)
* 2024-04-27 - build(deps-dev): bump ruff from 0.3.4 to 0.4.1
  [PR #2769](https://github.com/RDFLib/rdflib/pull/2769)
* 2024-04-18 - build(deps): bump poetry from 1.7.1 to 1.8.2 in /devtools
  [PR #2743](https://github.com/RDFLib/rdflib/pull/2743)
* 2024-04-18 - build(deps-dev): bump typing-extensions from 4.10.0 to 4.11.0
  [PR #2759](https://github.com/RDFLib/rdflib/pull/2759)
* 2024-04-18 - build(deps-dev): bump setuptools from 69.2.0 to 69.5.1
  [PR #2763](https://github.com/RDFLib/rdflib/pull/2763)
* 2024-04-18 - build(deps-dev): bump types-setuptools from 69.2.0.20240317 to 69.5.0.20240415
  [PR #2765](https://github.com/RDFLib/rdflib/pull/2765)
* 2024-04-03 - build(deps-dev): bump pytest-cov from 4.1.0 to 5.0.0
  [PR #2754](https://github.com/RDFLib/rdflib/pull/2754)
* 2024-04-03 - build(deps-dev): bump ruff from 0.3.2 to 0.3.4
  [PR #2753](https://github.com/RDFLib/rdflib/pull/2753)
* 2024-04-03 - build(deps-dev): bump coverage from 7.4.3 to 7.4.4
  [PR #2752](https://github.com/RDFLib/rdflib/pull/2752)
* 2024-03-20 - build(deps-dev): bump poetry from 1.7.1 to 1.8.2
  [PR #2741](https://github.com/RDFLib/rdflib/pull/2741)
* 2024-03-20 - [pre-commit.ci] pre-commit autoupdate
  [PR #2732](https://github.com/RDFLib/rdflib/pull/2732)  
* 2024-03-20 - build(deps-dev): bump types-setuptools from 69.1.0.20240310 to 69.2.0.20240317
  [PR #2737](https://github.com/RDFLib/rdflib/pull/2737)
* 2024-03-20 - build(deps): bump library/python from `5c73034` to `36d57d7` in /docker/unstable
  [PR #2742](https://github.com/RDFLib/rdflib/pull/2742)
* 2024-03-20 - build(deps-dev): bump wheel from 0.42.0 to 0.43.0
  [PR #2740](https://github.com/RDFLib/rdflib/pull/2740)
* 2024-03-20 - build(deps-dev): bump setuptools from 69.1.1 to 69.2.0
  [PR #2739](https://github.com/RDFLib/rdflib/pull/2739)
* 2024-03-20 - build(deps-dev): bump black from 24.2.0 to 24.3.0
  [PR #2738](https://github.com/RDFLib/rdflib/pull/2738)
* 2024-03-12 - build(deps-dev): bump lxml-stubs from 0.4.0 to 0.5.1
  [PR #2724](https://github.com/RDFLib/rdflib/pull/2724)
* 2024-03-12 - build(deps-dev): bump types-setuptools from 69.1.0.20240302 to 69.1.0.20240310
  [PR #2728](https://github.com/RDFLib/rdflib/pull/2728)
* 2024-03-12 - build(deps-dev): bump ruff from 0.3.0 to 0.3.2
  [PR #2729](https://github.com/RDFLib/rdflib/pull/2729)
* 2024-03-12 - [pre-commit.ci] pre-commit autoupdate
  [PR #2630](https://github.com/RDFLib/rdflib/pull/2630)  
* 2024-03-12 - build(deps): bump pyparsing from 3.1.1 to 3.1.2
  [PR #2730](https://github.com/RDFLib/rdflib/pull/2730)
* 2024-03-05 - build(deps): bump library/python from `eb53cb9` to `5c73034` in /docker/unstable
  [PR #2726](https://github.com/RDFLib/rdflib/pull/2726)
* 2024-03-04 - build(deps-dev): bump sphinxcontrib-apidoc from 0.4.0 to 0.5.0
  [PR #2719](https://github.com/RDFLib/rdflib/pull/2719)
* 2024-03-04 - build(deps-dev): bump types-setuptools from 69.1.0.20240223 to 69.1.0.20240302
  [PR #2722](https://github.com/RDFLib/rdflib/pull/2722)
* 2024-03-04 - build(deps-dev): bump ruff from 0.1.6 to 0.3.0
  [PR #2718](https://github.com/RDFLib/rdflib/pull/2718)
* 2024-03-04 - build(deps-dev): bump poetry from 1.8.0 to 1.8.2
  [PR #2721](https://github.com/RDFLib/rdflib/pull/2721)
* 2024-02-27 - build(deps-dev): bump types-setuptools from 68.2.0.2 to 69.1.0.20240223
  [PR #2716](https://github.com/RDFLib/rdflib/pull/2716)
* 2024-02-27 - build(deps): bump poetry from 1.7.1 to 1.8.0 in /devtools
  [PR #2717](https://github.com/RDFLib/rdflib/pull/2717)
* 2024-02-27 - build(deps): bump library/python from 3.12.0-slim to 3.12.2-slim in /docker/unstable
  [PR #2706](https://github.com/RDFLib/rdflib/pull/2706)
* 2024-02-27 - build(deps-dev): bump typing-extensions from 4.8.0 to 4.10.0
  [PR #2715](https://github.com/RDFLib/rdflib/pull/2715)
* 2024-02-27 - build(deps-dev): bump coverage from 7.3.2 to 7.4.3
  [PR #2714](https://github.com/RDFLib/rdflib/pull/2714)
* 2024-02-27 - build(deps): bump arduino/setup-task from 1 to 2
  [PR #2707](https://github.com/RDFLib/rdflib/pull/2707)
* 2024-02-27 - build(deps-dev): bump setuptools from 69.0.2 to 69.1.1
  [PR #2713](https://github.com/RDFLib/rdflib/pull/2713)
* 2024-02-27 - build(deps): bump library/python from 3.12.0-slim to 3.12.2-slim in /docker/latest
  [PR #2703](https://github.com/RDFLib/rdflib/pull/2703)
* 2024-02-27 - build(deps): bump actions/cache from 3 to 4
  [PR #2690](https://github.com/RDFLib/rdflib/pull/2690)
* 2024-02-27 - build(deps): bump actions/upload-artifact from 3 to 4
  [PR #2669](https://github.com/RDFLib/rdflib/pull/2669)
* 2024-02-27 - build(deps): bump actions/setup-python from 4 to 5
  [PR #2664](https://github.com/RDFLib/rdflib/pull/2664)
* 2024-02-27 - build(deps): bump actions/setup-java from 3 to 4
  [PR #2657](https://github.com/RDFLib/rdflib/pull/2657)
* 2024-02-27 - build(deps-dev): bump black from 23.11.0 to 24.2.0
  [PR #2709](https://github.com/RDFLib/rdflib/pull/2709)
* 2023-12-01 - build(deps): bump library/python from `43a49c9` to `babc0d4` in /docker/latest
  [PR #2627](https://github.com/RDFLib/rdflib/pull/2627)
* 2023-12-01 - build(deps-dev): bump poetry from 1.6.1 to 1.7.1
  [PR #2646](https://github.com/RDFLib/rdflib/pull/2646)
* 2023-11-30 - build(deps-dev): bump setuptools from 68.2.2 to 69.0.2
  [PR #2650](https://github.com/RDFLib/rdflib/pull/2650)
* 2023-11-30 - build(deps-dev): bump ruff from 0.1.1 to 0.1.6
  [PR #2647](https://github.com/RDFLib/rdflib/pull/2647)
* 2023-11-30 - build(deps-dev): bump types-setuptools from 68.2.0.1 to 68.2.0.2
  [PR #2652](https://github.com/RDFLib/rdflib/pull/2652)
* 2023-11-30 - build(deps): bump library/python from `babc0d4` to `32477c7` in /docker/unstable
  [PR #2653](https://github.com/RDFLib/rdflib/pull/2653)
* 2023-11-21 - build(deps-dev): bump types-setuptools from 68.2.0.0 to 68.2.0.1
  [PR #2640](https://github.com/RDFLib/rdflib/pull/2640)
* 2023-11-21 - build(deps-dev): bump black from 23.10.1 to 23.11.0
  [PR #2641](https://github.com/RDFLib/rdflib/pull/2641)
* 2023-11-21 - build(deps-dev): bump sphinx-autodoc-typehints from 1.24.0 to 1.25.2
  [PR #2639](https://github.com/RDFLib/rdflib/pull/2639)
* 2023-11-21 - build(deps-dev): bump pytest from 7.4.2 to 7.4.3
  [PR #2629](https://github.com/RDFLib/rdflib/pull/2629)
* 2023-11-21 - build(deps): bump library/python from `43a49c9` to `babc0d4` in /docker/unstable
  [PR #2626](https://github.com/RDFLib/rdflib/pull/2626)
* 2023-10-29 - build(deps-dev): bump mypy from 1.5.1 to 1.6.1
  [PR #2624](https://github.com/RDFLib/rdflib/pull/2624)
* 2023-10-29 - build(deps): bump berkeleydb from 18.1.6 to 18.1.8
  [PR #2615](https://github.com/RDFLib/rdflib/pull/2615)
* 2023-10-29 - build(deps-dev): bump black from 23.9.1 to 23.10.1
  [PR #2625](https://github.com/RDFLib/rdflib/pull/2625)
* 2023-10-24 - [pre-commit.ci] pre-commit autoupdate
  [PR #2605](https://github.com/RDFLib/rdflib/pull/2605)   
* 2023-10-24 - build(deps-dev): bump ruff from 0.0.291 to 0.1.1
  [PR #2622](https://github.com/RDFLib/rdflib/pull/2622)
* 2023-10-24 - build(deps-dev): bump coverage from 7.3.1 to 7.3.2
  [PR #2614](https://github.com/RDFLib/rdflib/pull/2614)
* 2023-10-24 - build(deps): bump library/python from 3.11.5-slim to 3.12.0-slim in /docker/latest
  [PR #2612](https://github.com/RDFLib/rdflib/pull/2612)
* 2023-09-24 - [pre-commit.ci] pre-commit autoupdate
  [PR #2495](https://github.com/RDFLib/rdflib/pull/2495)  
* 2023-10-24 - build(deps): bump library/python from 3.11.5-slim to 3.12.0-slim in /docker/unstable
  [PR #2611](https://github.com/RDFLib/rdflib/pull/2611)
* 2023-09-25 - build(deps): bump library/python from `9bd704d` to `edaf703` in /docker/latest
  [PR #2600](https://github.com/RDFLib/rdflib/pull/2600)
* 2023-09-25 - build(deps): bump library/python from `9bd704d` to `edaf703` in /docker/unstable
  [PR #2601](https://github.com/RDFLib/rdflib/pull/2601)
* 2023-09-25 - build(deps-dev): bump ruff from 0.0.290 to 0.0.291
  [PR #2602](https://github.com/RDFLib/rdflib/pull/2602)
* 2023-09-24 - build(deps): bump docker/login-action from 2 to 3
  [PR #2594](https://github.com/RDFLib/rdflib/pull/2594)
* 2023-09-24 - build(deps-dev): bump ruff from 0.0.287 to 0.0.290
  [PR #2596](https://github.com/RDFLib/rdflib/pull/2596)
* 2023-09-24 - build(deps-dev): bump typing-extensions from 4.7.1 to 4.8.0
  [PR #2597](https://github.com/RDFLib/rdflib/pull/2597)
* 2023-09-19 - build(deps-dev): bump setuptools from 68.2.0 to 68.2.2
  [PR #2595](https://github.com/RDFLib/rdflib/pull/2595)
* 2023-09-11 - build(deps-dev): bump sphinxcontrib-apidoc from 0.3.0 to 0.4.0
  [PR #2583](https://github.com/RDFLib/rdflib/pull/2583)
* 2023-09-11 - build(deps-dev): bump black from 23.7.0 to 23.9.1
  [PR #2584](https://github.com/RDFLib/rdflib/pull/2584)
* 2023-09-11 - build(deps): bump actions/checkout from 3 to 4
  [PR #2582](https://github.com/RDFLib/rdflib/pull/2582)
* 2023-09-11 - build(deps-dev): bump coverage from 7.3.0 to 7.3.1
  [PR #2586](https://github.com/RDFLib/rdflib/pull/2586)
* 2023-09-11 - build(deps-dev): bump types-setuptools from 68.1.0.1 to 68.2.0.0
  [PR #2587](https://github.com/RDFLib/rdflib/pull/2587)
* 2023-09-11 - build(deps-dev): bump pytest from 7.4.1 to 7.4.2
  [PR #2588](https://github.com/RDFLib/rdflib/pull/2588)
* 2023-09-11 - build(deps): bump library/python from `c499230` to `9bd704d` in /docker/latest
  [PR #2589](https://github.com/RDFLib/rdflib/pull/2589)
* 2023-09-11 - build(deps-dev): bump setuptools from 68.1.2 to 68.2.0
  [PR #2585](https://github.com/RDFLib/rdflib/pull/2585)
* 2023-09-11 - build(deps): bump library/python from `c499230` to `9bd704d` in /docker/unstable
  [PR #2581](https://github.com/RDFLib/rdflib/pull/2581)
* 2023-09-04 - build(deps-dev): bump types-setuptools from 68.1.0.0 to 68.1.0.1
  [PR #2569](https://github.com/RDFLib/rdflib/pull/2569)
* 2023-09-04 - build(deps-dev): bump ruff from 0.0.286 to 0.0.287
  [PR #2567](https://github.com/RDFLib/rdflib/pull/2567)
* 2023-09-04 - build(deps-dev): bump pytest from 7.4.0 to 7.4.1
  [PR #2568](https://github.com/RDFLib/rdflib/pull/2568)
* 2023-08-28 - build(deps): bump library/python from 3.11.4-slim to 3.11.5-slim in /docker/latest
  [PR #2551](https://github.com/RDFLib/rdflib/pull/2551)
* 2023-08-28 - build(deps): bump library/python from 3.11.4-slim to 3.11.5-slim in /docker/unstable
  [PR #2550](https://github.com/RDFLib/rdflib/pull/2550)
* 2023-08-28 - build(deps-dev): bump poetry from 1.5.1 to 1.6.1
  [PR #2549](https://github.com/RDFLib/rdflib/pull/2549)
* 2023-08-23 - build(deps-dev): bump types-setuptools from 68.0.0.3 to 68.1.0.0
  [PR #2532](https://github.com/RDFLib/rdflib/pull/2532)
* 2023-08-23 - build(deps): bump library/python from `58ae46e` to `17d62d6` in /docker/unstable
  [PR #2531](https://github.com/RDFLib/rdflib/pull/2531)
* 2023-08-23 - build(deps-dev): bump setuptools from 68.0.0 to 68.1.2
  [PR #2535](https://github.com/RDFLib/rdflib/pull/2535)
* 2023-08-22 - build(deps-dev): bump mypy from 1.5.0 to 1.5.1
  [PR #2534](https://github.com/RDFLib/rdflib/pull/2534)
* 2023-08-15 - build(deps): bump library/python from `36b544b` to `58ae46e` in /docker/latest
  [PR #2527](https://github.com/RDFLib/rdflib/pull/2527)
* 2023-08-15 - build(deps): bump library/python from `36b544b` to `58ae46e` in /docker/unstable
  [PR #2526](https://github.com/RDFLib/rdflib/pull/2526)
* 2023-08-15 - build(deps-dev): bump mypy from 1.4.1 to 1.5.0
  [PR #2525](https://github.com/RDFLib/rdflib/pull/2525)
* 2023-08-15 - build(deps-dev): bump coverage from 7.2.7 to 7.3.0
  [PR #2524](https://github.com/RDFLib/rdflib/pull/2524)
* 2023-08-07 - build(deps-dev): bump sphinx from 7.1.1 to 7.1.2
  [PR #2521](https://github.com/RDFLib/rdflib/pull/2521)

## 2023-08-02 RELEASE 7.0.0

This is a major release with relatively slight breaking changes, new
features and bug fixes.

The most notable breaking change relates to how RDFLib handles the
`publicID` parameter of the `Graph.parse` and `Dataset.parse` methods.
Most users should not be affected by this change.

Instructions on adapting existing code to the breaking changes can be
found in the upgrade guide from Version 6 to Version 7 which should be
available [here](https://rdflib.readthedocs.io/en/stable/).

It is likely that the next couple of RDFLib releases will all be major
versions, mostly because there are some more shortcomings of RDFLib's
public interface that should be addressed.

If you use RDFLib, please consider keeping an eye on
[discussions](https://github.com/RDFLib/rdflib/discussions?discussions_q=label%3A%22feedback+wanted%22),
issues and pull-requests labelled with ["feedback
wanted"](https://github.com/RDFLib/rdflib/labels/feedback%20wanted).

A big thanks to everyone who contributed to this release.

### BREAKING CHANGE: don't use `publicID` as the name for the default graph. (#2406)

Commit [4b96e9d](https://github.com/RDFLib/rdflib/commit/4b96e9d), closes [#2406](https://github.com/RDFLib/rdflib/issues/2406).


When parsing data into a `ConjunctiveGraph` or `Dataset`, the triples in the
default graphs in the sources were loaded into a graph named `publicID`.

This behaviour has been changed, and now the triples from the default graph in
source RDF documents will be loaded into `ConjunctiveGraph.default_context` or
`Dataset.default_context`.

The `publicID` parameter to `ConjunctiveGraph.parse` and `Dataset.parse`
constructors will now only be used as the base URI for relative URI resolution.

- Fixes https://github.com/RDFLib/rdflib/issues/2404
- Fixes https://github.com/RDFLib/rdflib/issues/2375
- Fixes https://github.com/RDFLib/rdflib/issues/436
- Fixes https://github.com/RDFLib/rdflib/issues/1804

### BREAKING CHANGE: drop support for python 3.7 (#2436)

Commit [1e5f56b](https://github.com/RDFLib/rdflib/commit/1e5f56b), closes [#2436](https://github.com/RDFLib/rdflib/issues/2436).


Python 3.7 will be end-of-life on the 27th of June 2023 and the next release of
RDFLib will be a new major version.

This changes the minimum supported version of Python to 3.8.1 as some of the
dependencies we use are not too fond of python 3.8.0. This change also removes
all accommodations for older python versions.

### feat: add `curie` method to `NamespaceManager` (#2365)

Commit [f200722](https://github.com/RDFLib/rdflib/commit/f200722), closes [#2365](https://github.com/RDFLib/rdflib/issues/2365).


Added a `curie` method to `NamespaceManager`, which can be used to generate a
CURIE from a URI.

Other changes:

- Fixed `NamespaceManager.expand_curie` to work with CURIES that have blank
  prefixes (e.g. `:something`), which are valid according to [CURIE Syntax
  1.0](https://www.w3.org/TR/2010/NOTE-curie-20101216/).
- Added a test to confirm <https://github.com/RDFLib/rdflib/issues/2077>.

Fixes <https://github.com/RDFLib/rdflib/issues/2348>.


### feat: add optional `target_graph` argument to `Graph.cbd` and use it  for DESCRIBE queries (#2322)

Commit [81d13d4](https://github.com/RDFLib/rdflib/commit/81d13d4), closes [#2322](https://github.com/RDFLib/rdflib/issues/2322).


Add optional keyword only `target_graph` argument to `rdflib.graph.Graph.cbd` and use this new argument in `evalDescribeQuery`.

This makes it possible to compute a concise bounded description without creating a new graph to hold the result, and also without potentially having to copy it to another final graph.

### feat: Don't generate prefixes for unknown URIs (#2467)

Commit [bd797ac](https://github.com/RDFLib/rdflib/commit/bd797ac).


When serializing RDF graphs, URIs with unknown prefixes were assigned a
namespace like `ns1:`. While the result would be smaller files, it does
result in output that is not as readable.

This change removes this automatic assignment of namespace prefixes.

This is somewhat of an aesthetic choice, eventually we should have more
flexibility in this regard so that users can exercise more control over
how URIs in unknown namespaces are handled.

With this change, users can still manually create namespace prefixes for
URIs in unknown namespaces, but before it there was no way to avoid the
undesired behaviour, so this seems like the better default.


### feat: Longturtle improvements (#2500)

Commit [5ee8bd7](https://github.com/RDFLib/rdflib/commit/5ee8bd7), closes [#2500](https://github.com/RDFLib/rdflib/issues/2500).

Improved the output of the longturtle serializer.

### fix: SPARQL count with optionals (#2448)

Commit [46ff6cf](https://github.com/RDFLib/rdflib/commit/46ff6cf), closes [#2448](https://github.com/RDFLib/rdflib/issues/2448).


Change SPARQL count aggregate to ignore optional that are unbound
instead of raising an exception when they are encountered.

### fix: `GROUP_CONCAT` handling of empty separator (issue) (#2474)

Commit [e94c252](https://github.com/RDFLib/rdflib/commit/e94c252), closes [#2474](https://github.com/RDFLib/rdflib/issues/2474).


`GROUP_CONCAT` was handling an empty separator (i.e. `""`) incorrectly,
it would handle it as if the separator were not set, so essentially it was
treated as a single space (i.e. `" "`).

This change fixes it so that an empty separator with `GROUP_CONCAT`
results in a value with nothing between concatenated values.


Fixes <https://github.com/RDFLib/rdflib/issues/2473>


### fix: add `NORMALIZE_LITERALS` to `rdflib.__all__` (#2489)

Commit [6981c28](https://github.com/RDFLib/rdflib/commit/6981c28), closes [#2489](https://github.com/RDFLib/rdflib/issues/2489).


This gets Sphinx to generate documentation for it, and also clearly
indicates that it can be used from outside the module.

- Fixes <https://github.com/RDFLib/rdflib/issues/2488>


### fix: bugs with `rdflib.extras.infixowl` (#2390)

Commit [cd0b442](https://github.com/RDFLib/rdflib/commit/cd0b442), closes [#2390](https://github.com/RDFLib/rdflib/issues/2390).


Fix the following issues in `rdflib.extras.infixowl`:
- getting and setting of max cardinality only considered identifiers and not other RDF terms.
- The return value of `manchesterSyntax` was wrong for some cases.
- The way that `BooleanClass` was generating its string representation (i.e. `BooleanClass.__repr__`) was wrong for some cases.

Other changes:
- Added an example for using infixowl to create an ontology.
- Updated infixowl tests.
- Updated infixowl documentation.

This code is based on code from:
- <https://github.com/RDFLib/rdflib/pull/2307>


### fix: correct imports and `__all__` (#2340)

Commit [7df77cd](https://github.com/RDFLib/rdflib/commit/7df77cd), closes [#2340](https://github.com/RDFLib/rdflib/issues/2340).


Disable
[`implicit_reexport`](https://mypy.readthedocs.io/en/stable/config_file.html#confval-implicit_reexport)
and eliminate all errors reported by mypy after this.

This helps ensure that import statements import from the right module and that
the `__all__` variable is correct.


### fix: dbpedia URL to use https instead of http (#2444)

Commit [ef25896](https://github.com/RDFLib/rdflib/commit/ef25896), closes [#2444](https://github.com/RDFLib/rdflib/issues/2444).


The URL for the service keyword had the http address for the dbpedia endpoint, which no longer works. Changing it to https as that works.


### fix: eliminate bare `except:` (#2350)

Commit [4ea1436](https://github.com/RDFLib/rdflib/commit/4ea1436), closes [#2350](https://github.com/RDFLib/rdflib/issues/2350).


Replace bare `except:` with `except Exception`, there are some cases where it
can be narrowed further, but this is already an improvement over the current
situation.

This is somewhat pursuant to eliminating
[flakeheaven](https://github.com/flakeheaven/flakeheaven), as it no longer
supports the latest version of flake8
[[ref](https://github.com/flakeheaven/flakeheaven/issues/132)]. But it also is
just the right thing to do as bare exceptions can cause problems.


### fix: eliminate file intermediary in translate algebra (#2267)

Commit [ae6b859](https://github.com/RDFLib/rdflib/commit/ae6b859), closes [#2267](https://github.com/RDFLib/rdflib/issues/2267).


Previously, `rdflib.plugins.sparql.algebra.translateAlgebra()` maintained state via a file, with a fixed filename `query.txt`.  With this change, use of that file is eliminated; state is now maintained in memory so that multiple concurrent `translateAlgebra()` calls, for example, should no longer interfere with each other.

The change is accomplished with no change to the client interface.  Basically, the actual functionality has been moved into a class, which is instantiated and used as needed (once per call to `algrebra.translateAlgebra()`).


### fix: eliminate some mutable default arguments in SPARQL code (#2301)

Commit [89982f8](https://github.com/RDFLib/rdflib/commit/89982f8), closes [#2301](https://github.com/RDFLib/rdflib/issues/2301).


This change eliminates some situations where a mutable object (i.e., a dictionary) was used as the default value for functions in the `rdflib.plugins.sparql.processor` module and related code. It replaces these situations with `typing.Optinal` that defaults to None, and is then handled within the function. Luckily, some of the code that the SPARQL Processor relied on already had this style, meaning not a lot of changes had to be made.

This change also makes a small update to the logic in the SPARQL Processor's query function to simplify the if/else statement. This better mirrors the implementation in the `UpdateProcessor`.


### fix: formatting of SequencePath and AlternativePath (#2504)

Commit [9c73581](https://github.com/RDFLib/rdflib/commit/9c73581), closes [#2504](https://github.com/RDFLib/rdflib/issues/2504).


These path types were formatted without parentheses even if they
contained multiple elements, resulting in string representations that
did not accurately represent the path.

This change fixes the formatting so that the string representations are
enclosed in parentheses when necessary.

- Fixes <https://github.com/RDFLib/rdflib/issues/2503>.


### fix: handling of `rdf:HTML` literals (#2490)

Commit [588286b](https://github.com/RDFLib/rdflib/commit/588286b), closes [#2490](https://github.com/RDFLib/rdflib/issues/2490).


Previously, without `html5lib` installed, literals with`rdf:HTML`
datatypes were treated as
[ill-typed](https://www.w3.org/TR/rdf11-concepts/#section-Graph-Literal),
even if they were not ill-typed.

With this change, if `html5lib` is not installed, literals with the
`rdf:HTML` datatype will not be treated as ill-typed, and will have
`Null` as their `ill_typed` attribute value, which means that it is
unknown whether they are ill-typed or not.

This change also fixes the mapping from `rdf:HTML` literal values to
lexical forms.

Other changes:

- Add tests for `rdflib.NORMALIZE_LITERALS` to ensure it behaves
  correctly.

Related issues:

- Fixes <https://github.com/RDFLib/rdflib/issues/2475>


### fix: HTTP 308 Permanent Redirect status code handling (#2389)

Commit [e0b3152](https://github.com/RDFLib/rdflib/commit/e0b3152), closes [#2389](https://github.com/RDFLib/rdflib/issues/2389) [/docs.python.org/3.11/whatsnew/changelog.html#id128](https://github.com//docs.python.org/3.11/whatsnew/changelog.html/issues/id128).


Change the handling of HTTP status code 308 to behave more like
`urllib.request.HTTPRedirectHandler`, most critically, the new 308 handling will
create a new `urllib.request.Request` object with the new URL, which will
prevent state from being carried over from the original request.

One case where this is important is when the domain name changes, for example,
when the original URL is `http://www.w3.org/ns/adms.ttl` and the redirect URL is
`https://uri.semic.eu/w3c/ns/adms.ttl`. With the previous behaviour, the redirect
would contain a `Host` header with the value `www.w3.org` instead of
`uri.semic.eu` because the `Host` header is placed in
`Request.unredirected_hdrs` and takes precedence over the `Host` header in
`Request.headers`.

Other changes:
- Only handle HTTP status code 308 on Python versions before 3.11 as Python 3.11

  will handle 308 by default [[ref](https://docs.python.org/3.11/whatsnew/changelog.html#id128)].
- Move code which uses `http://www.w3.org/ns/adms.ttl` and
  `http://www.w3.org/ns/adms.rdf` out of `test_guess_format_for_parse` into a
  separate parameterized test, which instead uses the embedded http server.

  This allows the test to fully control the `Content-Type` header in the
  response instead of relying on the value that the server is sending.

  This is needed because the server is sending `Content-Type: text/plain` for
  the `adms.ttl` file, which is not a valid RDF format, and the test is
  expecting `Content-Type: text/turtle`.

Fixes:
- <https://github.com/RDFLib/rdflib/issues/2382>.

### fix: lexical-to-value mapping of rdf:HTML literals (#2483)

Commit [53aaf02](https://github.com/RDFLib/rdflib/commit/53aaf02), closes [#2483](https://github.com/RDFLib/rdflib/issues/2483).


Use strict mode when parsing `rdf:HTML` literals. This ensures that when
[lexical-to-value
mapping](https://www.w3.org/TR/rdf11-concepts/#dfn-lexical-to-value-mapping)
(i.e. parsing) of a literal with `rdf:HTML` data type occurs, a value will
only be assigned if the lexical form is a valid HTML5 fragment.
Otherwise, i.e. for invalid fragments, no value will be associated with
the literal
[[ref](https://www.w3.org/TR/rdf11-concepts/#section-Graph-Literal)] and
the literal will be ill-typed.


### fix: TriG handling of GRAPH keyword without a graph ID (#2469)

Commit [8c9608b](https://github.com/RDFLib/rdflib/commit/8c9608b), closes [#2469](https://github.com/RDFLib/rdflib/issues/2469) [/www.w3.org/2013/TriGTests/#trig-graph-bad-01](https://github.com//www.w3.org/2013/TriGTests//issues/trig-graph-bad-01).


The RDF 1.1 TriG grammar only allows the `GRAPH` keyword if it
is followed by a graph identifier
[[ref](https://www.w3.org/TR/trig/#grammar-production-block)].

This change enforces this rule so that the

<http://www.w3.org/2013/TriGTests/#trig-graph-bad-01> test passes.

### fix: TriG parser error handling for nested graphs (#2468)

Commit [afea615](https://github.com/RDFLib/rdflib/commit/afea615), closes [#2468](https://github.com/RDFLib/rdflib/issues/2468) [/www.w3.org/2013/TriGTests/#trig-graph-bad-07](https://github.com//www.w3.org/2013/TriGTests//issues/trig-graph-bad-07).


Raise an error when nested graphs occur in TriG.

With this change, the <http://www.w3.org/2013/TriGTests/#trig-graph-bad-07> test passes.

### fix: typing errors from dmypy (#2451)

Commit [10f9ebe](https://github.com/RDFLib/rdflib/commit/10f9ebe), closes [#2451](https://github.com/RDFLib/rdflib/issues/2451).


Fix various typing errors that are reported when running with `dmypy`,
the mypy daemon.

Also add a task for running `dmypy` to the Taskfile that can be selected
as the default mypy variant by setting the `MYPY_VARIANT` environment
variable to `dmypy`.


### fix: widen `Graph.__contains__` type-hints to accept `Path` values (#2323)

Commit [1c45ec4](https://github.com/RDFLib/rdflib/commit/1c45ec4), closes [#2323](https://github.com/RDFLib/rdflib/issues/2323).


Change the type-hints for `Graph.__contains__` to also accept `Path`
values as the parameter is passed to the `Graph.triples` function,
which accepts `Path` values.


### docs: Add CITATION.cff file (#2502)

Commit [ad5c0e1](https://github.com/RDFLib/rdflib/commit/ad5c0e1), closes [#2502](https://github.com/RDFLib/rdflib/issues/2502).


The `CITATION.cff` file provides release metadata which is used by
Zenodo and other software and systems.

This file's content is best-effort, and pull requests with improvements
are welcome and will affect future releases.


### docs: add guidelines for breaking changes (#2402)

Commit [cad367e](https://github.com/RDFLib/rdflib/commit/cad367e), closes [#2402](https://github.com/RDFLib/rdflib/issues/2402).


Add guidelines on how breaking changes should be approached.

The guidelines take a very pragmatic approach with known downsides, but this
seems like the best compromise given the current situation.

For prior discussion on this point see:
- https://github.com/RDFLib/rdflib/discussions/2395
- https://github.com/RDFLib/rdflib/pull/2108
- https://github.com/RDFLib/rdflib/discussions/1841


### docs: fix comment that doesn't describe behavior (#2443)

Commit [4e42d10](https://github.com/RDFLib/rdflib/commit/4e42d10), closes [#2443](https://github.com/RDFLib/rdflib/issues/2443).


Comment refers to a person that knows bob and the code would return a name,
but this would only work if the triple `person foaf:name bob .` is part of the dataset

As this is a very uncommon way to model a `foaf:knows` the code was
adjusted to match the description.

### docs: recommend making an issue before making an enhancement (#2391)

Commit [63b082c](https://github.com/RDFLib/rdflib/commit/63b082c), closes [#2391](https://github.com/RDFLib/rdflib/issues/2391).


Suggest that contributors first make an issue to get in principle
agreement for pull requests before making the pull request.

Enhancements can be controversial, and we may reject the enhancement
sometimes, even if the code is good, as it may just not be deemed
important enough to increase the maintenance burden of RDFLib.

Other changes:
- Updated the checklist in the pull request template to be more accurate to
  current practice.
- Improved grammar and writing in the pull request template, contribution guide
  and developers guide.


### docs: remove unicode string form in rdflib/term.py (#2384)

Commit [ddcc4eb](https://github.com/RDFLib/rdflib/commit/ddcc4eb), closes [#2384](https://github.com/RDFLib/rdflib/issues/2384).


The use of Unicode literals is an artefact of Python 2 and is incorrect in Python 3.

Doctests for docstrings using Unicode literals only pass because [ALLOW_UNICODE](https://docs.pytest.org/en/7.1.x/how-to/doctest.html#using-doctest-options)
is set, but this option should be disabled as RDFLib does not support Python 2 any more.

This partially resolves <https://github.com/RDFLib/rdflib/issues/2378>.

## 2023-03-26 RELEASE 6.3.2

### fix: `ROUND`, `ENCODE_FOR_URI` and `SECONDS` SPARQL functions (#2314)

Commit [af17916](https://github.com/RDFLib/rdflib/commit/af17916), closes [#2314](https://github.com/RDFLib/rdflib/issues/2314).


`ROUND` was not correctly rounding negative numbers towards positive infinity,
`ENCODE_FOR_URI` incorrectly treated `/` as safe, and `SECONDS` did not include
fractional seconds.

This change corrects these issues.

- Closes <https://github.com/RDFLib/rdflib/issues/2151>.


### fix: add `__hash__` and `__eq__` back to `rdflib.paths.Path` (#2292)

Commit [fe1a8f8](https://github.com/RDFLib/rdflib/commit/fe1a8f8), closes [#2292](https://github.com/RDFLib/rdflib/issues/2292).


These methods were removed when `@total_ordering` was added, but
`@total_ordering` does not add them, so removing them essentially
removes functionality.

This change adds the methods back and adds tests to ensure they work
correctly.

All path related tests are also moved into one file.

- Closes <https://github.com/RDFLib/rdflib/issues/2281>.
- Closes <https://github.com/RDFLib/rdflib/issues/2242>.


### fix: Add `to_dict` method to the JSON-LD `Context` class. (#2310)

Commit [d7883eb](https://github.com/RDFLib/rdflib/commit/d7883eb), closes [#2310](https://github.com/RDFLib/rdflib/issues/2310).


`Context.to_dict` is used in JSON-LD serialization, but it was not implemented.
This change adds the method.

- Closes <https://github.com/RDFLib/rdflib/issues/2138>.


### fix: add the `wgs` namespace binding back (#2294)

Commit [adf8eb2](https://github.com/RDFLib/rdflib/commit/adf8eb2), closes [#2294](https://github.com/RDFLib/rdflib/issues/2294).


<https://github.com/RDFLib/rdflib/pull/1686> inadvertently removed the `wgs` prefix.
This change adds it back.

- Closes <https://github.com/RDFLib/rdflib/issues/2196>.


### fix: change the prefix for `https://schema.org/` back to `schema` (#2312)

Commit [3faa01b](https://github.com/RDFLib/rdflib/commit/3faa01b), closes [#2312](https://github.com/RDFLib/rdflib/issues/2312).


The default prefix for `https://schema.org/` registered with
`rdflib.namespace.NamespaceManager` was inadvertently changed to `sdo` in 6.2.0,
this however constitutes a breaking change, as code that was using the `schema`
prefix would no longer have the same behaviour. This change changes the prefix
back to `schema`.


### fix: include docs and examples in the sdist tarball (#2289)

Commit [394fb50](https://github.com/RDFLib/rdflib/commit/394fb50), closes [#2289](https://github.com/RDFLib/rdflib/issues/2289).


The sdists generated by setuptools included the `docs` and `examples`
directories, and they are needed for building docs and running tests using the
sdist.

This change includes these directories in the sdist tarball.

A `test:sdist` task is also added to `Taskfile.yml` which uses the sdists to run
pytest and build docs.


### fix: IRI to URI conversion (#2304)

Commit [dfa4054](https://github.com/RDFLib/rdflib/commit/dfa4054), closes [#2304](https://github.com/RDFLib/rdflib/issues/2304).


The URI to IRI conversion was percentage-quoting characters that should not have
been quoted, like equals in the query string. It was also not quoting things
that should have been quoted, like the username and password components of a
URI.

This change improves the conversion by only quoting characters that are not
allowed in specific parts of the URI and quoting previously unquoted components.
The safe characters for each segment are taken from
[RFC3986](https://datatracker.ietf.org/doc/html/rfc3986).

The new behavior is heavily inspired by

[`werkzeug.urls.iri_to_uri`](https://github.com/pallets/werkzeug/blob/92c6380248c7272ee668e1f8bbd80447027ccce2/src/werkzeug/urls.py#L926-L931)
though there are some differences.

- Closes <https://github.com/RDFLib/rdflib/issues/2120>.

### fix: JSON-LD context construction from a `dict` (#2306)

Commit [832e693](https://github.com/RDFLib/rdflib/commit/832e693), closes [#2306](https://github.com/RDFLib/rdflib/issues/2306).


A variable was only being initialized for string-valued inputs, but if a `dict`
input was passed the variable would still be accessed, resulting in a
`UnboundLocalError`.

This change initializes the variable always, instead of only when string-valued
input is used to construct a JSON-LD context.

- Closes <https://github.com/RDFLib/rdflib/issues/2303>.


### fix: reference to global inside `get_target_namespace_elements` (#2311)

Commit [4da67f9](https://github.com/RDFLib/rdflib/commit/4da67f9), closes [#2311](https://github.com/RDFLib/rdflib/issues/2311).


`get_target_namespace_elements` references the `args` global, which is not
defined if the function is called from outside the module. This commit fixes
that instead referencing the argument passed to the function.

- Closes <https://github.com/RDFLib/rdflib/issues/2072>.


### fix: restore the 6.1.1 default bound namespaces (#2313)

Commit [57bb428](https://github.com/RDFLib/rdflib/commit/57bb428), closes [#2313](https://github.com/RDFLib/rdflib/issues/2313).


The namespaces bound by default by `rdflib.graph.Graph` and
`rdflib.namespace.NamespaceManager` was reduced in version 6.2.0 of RDFLib,
however, this also would cause code that worked with 6.1.1 to break, so this
constituted a breaking change. This change restores the previous behaviour,
binding the same namespaces as was bound in 6.1.1.

To bind a reduced set of namespaces, the `bind_namespaces` parameter of
`rdflib.graph.Graph` or `rdflib.namespace.NamespaceManager` can be used.

- Closes <https://github.com/RDFLib/rdflib/issues/2103>.


### test: add `webtest` marker to tests that use the internet (#2295)

Commit [cfe6e37](https://github.com/RDFLib/rdflib/commit/cfe6e37), closes [#2295](https://github.com/RDFLib/rdflib/issues/2295).


This is being done so that it is easier for downstream packagers to run the test
suite without requiring internet access.

To run only tests that does not use the internet, run `pytest -m "not webtest"`.

The validation workflow validates that test run without internet access by
running the tests inside `firejail --net=none`.

- Closes <https://github.com/RDFLib/rdflib/issues/2293>.

### chore: Update CONTRIBUTORS from commit history (#2305)

Commit [1ab4fc0](https://github.com/RDFLib/rdflib/commit/1ab4fc0), closes [#2305](https://github.com/RDFLib/rdflib/issues/2305).


This ensures contributors are credited. Also added .mailmap to fix early misattributed contributions.

### docs: fix typo in NamespaceManager documentation (#2291)

Commit [7a05c15](https://github.com/RDFLib/rdflib/commit/7a05c15), closes [#2291](https://github.com/RDFLib/rdflib/issues/2291).


Changed `cdterms` to `dcterms`, see <https://github.com/RDFLib/rdflib/issues/2196> for more info.

## 2023-03-18 RELEASE 6.3.1

This is a patch release that includes a singular user facing fix, which is the
inclusion of the `test` directory in the `sdist` release artifact.

The following sections describe the changes included in this version.

### build: explicitly specify `packages` in `pyproject.toml` (#2280)

Commit [334787b](https://github.com/RDFLib/rdflib/commit/334787b), closes [#2280](https://github.com/RDFLib/rdflib/issues/2280).


The default behaviour makes it more of a hassle to republish RDFLib to
a separate package, something which I plan to do for testing purposes
and possibly other reasons.

More changes may follow in a similar vein.


### build: include test in sdist (#2282)

Commit [e3884b7](https://github.com/RDFLib/rdflib/commit/e3884b7), closes [#2282](https://github.com/RDFLib/rdflib/issues/2282).


A perhaps minor regression from earlier versions is that the sdist does not include the test folder, which makes it harder for downstreams to use a single source of truth to build and test a reliable package. This restores the test folder for sdists.

### docs: don't use kroki (#2284)

Commit [bea782f](https://github.com/RDFLib/rdflib/commit/bea782f), closes [#2284](https://github.com/RDFLib/rdflib/issues/2284).


The Kroki server is currently experiencing some issues which breaks our
build, this change eliminates the use of Kroki in favour of directly
using the generated SVG images which is checked into git alongside the
PlantUML sources.

I also added a task to the Taskfile to re-generate the SVG images from
the PlantUML sources by calling docker.

## 2023-03-16 RELEASE 6.3.0

This is a minor release that includes bug fixes and features.

### Important Information

- RDFLib will drop support for Python 3.7 when it becomes EOL on 2023-06-27,
  this will not be considered a breaking change, and RDFLib's major version
  number will not be changed solely on the basis of Python 3.7 support being
  dropped.

### User facing changes

This section lists changes that have a potential impact on users of RDFLib,
changes with no user impact are not included in this section.

- Add chunk serializer that facilitates the encoding of a graph into multiple
  N-Triples encoded chunks.
  [PR #1968](https://github.com/RDFLib/rdflib/pull/1968).

 - Fixes passing `NamespaceManager` in `ConjunctiveGraph`'s method `get_context()`. 
   The `get_context()` method will now pass the `NamespaceManager` of `ConjunctiveGraph` to the `namespace_manager` attribute of the newly created context graph, instead of the `ConjunctiveGraph` object itself. This cleans up an old `FIXME` comment.
   [PR #2073](https://github.com/RDFLib/rdflib/pull/2073). 

- InfixOWL fixes and cleanup.
  Closed [issue #2030](https://github.com/RDFLib/rdflib/issues/2030).
  [PR #2024](https://github.com/RDFLib/rdflib/pull/2024),
  and [PR #2033](https://github.com/RDFLib/rdflib/pull/2033).
  - `rdflib.extras.infixowl.Restriction.__init__` will now raise a `ValueError`
    if there is no restriction value instead of an `AssertionError`.
  - Fixed numerous issues with
    `rdflib.extras.infixowl.Restriction.restrictionKind` which was essentially
    not working at all.
  - Fixed how `rdflib.extras.infixowl.Property.__repr__` uses
    `rdflib.namespace.OWL`. 
  - Removed `rdflib.extras.infixowl.Infix.__ror__` and
    `rdflib.extras.infixowl.Infix.__or__` as they were broken.
  - Removed unused `rdflib.extras.infixowl.termDeletionDecorator`.
  - Added `rdflib.extras.infixowl.MalformedClassError` which will replace
    `rdflib.extras.infixowl.MalformedClass` (which is an exception) in the next
    major version.
  - Eliminated the use of mutable data structures in some argument defaults.

- Fixed some cross-referencing issues in RDFLib documentation.
  Closed [issue #1878](https://github.com/RDFLib/rdflib/issues/1878).
  [PR #2036](https://github.com/RDFLib/rdflib/pull/2036).

- Fixed import of `xml.sax.handler` in `rdflib.plugins.parsers.trix` so that it
  no longer tries to import it from `xml.sax.saxutils`.
  [PR #2041](https://github.com/RDFLib/rdflib/pull/2041).

- Removed a pre python 3.5 regex related workaround in the REPLACE SPARQL
  function.
  [PR #2042](https://github.com/RDFLib/rdflib/pull/2042).

- Fixed some issues with SPARQL XML result parsing that caused problems with
  [`lxml`](https://lxml.de/). Closed [issue #2035](https://github.com/RDFLib/rdflib/issues/2035),
  [issue #1847](https://github.com/RDFLib/rdflib/issues/1847).
  [PR #2044](https://github.com/RDFLib/rdflib/pull/2044).
  - Result parsing from
    [`TextIO`](https://docs.python.org/3/library/typing.html#typing.TextIO)
    streams now work correctly with `lxml` installed and with XML documents that
    are not `utf-8` encoded.
  - Elements inside `<results>` that are not `<result>` are now ignored.
  - Elements inside `<result>` that are not `<binding>` are now ignored.
  - Also added type hints to `rdflib.plugins.sparql.results.xmlresults`.

- Added type hints to the following modules:
  - `rdflib.store`.
     [PR #2057](https://github.com/RDFLib/rdflib/pull/2057).
  - `rdflib.graph`.
    [PR #2080](https://github.com/RDFLib/rdflib/pull/2080).
  - `rdflib.plugins.sparql.*`.
    [PR #2094](https://github.com/RDFLib/rdflib/pull/2094),
    [PR #2133](https://github.com/RDFLib/rdflib/pull/2133),
    [PR #2265](https://github.com/RDFLib/rdflib/pull/2265),
    [PR #2097](https://github.com/RDFLib/rdflib/pull/2097),
    [PR #2268](https://github.com/RDFLib/rdflib/pull/2268).
  - `rdflib.query`.
    [PR #2265](https://github.com/RDFLib/rdflib/pull/2265).
  - `rdflib.parser` and `rdflib.plugins.parsers.*`.
    [PR #2232](https://github.com/RDFLib/rdflib/pull/2232).
  - `rdflib.exceptions`.
    [PR #2232](https://github.com/RDFLib/rdflib/pull/2232)
  - `rdflib.shared.jsonld.*`.
    [PR #2232](https://github.com/RDFLib/rdflib/pull/2232).
  - `rdflib.collection`.
    [PR #2263](https://github.com/RDFLib/rdflib/pull/2263).
  - `rdflib.util`.
    [PR #2262](https://github.com/RDFLib/rdflib/pull/2262).
  - `rdflib.path`.
    [PR #2261](https://github.com/RDFLib/rdflib/pull/2261).
    
- Removed pre python 3.7 compatibility code.
  [PR #2066](https://github.com/RDFLib/rdflib/pull/2066).
  - Removed fallback in case the `shutil` module does not have the `move`
    function.

- Improve file-URI and path handling in `Graph.serialize` and `Result.serialize` to
  address problems with windows path handling in `Result.serialize` and to make
  the behavior between `Graph.serialize` and `Result.serialie` more consistent.
  Closed [issue #2067](https://github.com/RDFLib/rdflib/issues/2067).
  [PR #2065](https://github.com/RDFLib/rdflib/pull/2065).
  - String values for the `destination` argument will now only be treated as
    file URIs if `urllib.parse.urlparse` returns their schema as `file`.
  - Simplified file writing to avoid a temporary file.

- Narrow the type of context-identifiers/graph-names from `rdflib.term.Node` to
  `rdflib.term.IdentifiedNode` as no supported abstract syntax allows for other
  types of context-identifiers.
  [PR #2069](https://github.com/RDFLib/rdflib/pull/2069).

- Always parse HexTuple files as utf-8. 
  [PR #2070](https://github.com/RDFLib/rdflib/pull/2070).

- Fixed handling of `Literal` `datatype` to correctly differentiate between
  blank string values and undefined values, also changed the datatype of
  `rdflib.term.Literal.datatype` from `Optional[str]` to `Optional[URIRef]` now
  that all non-`URIRef` `str` values will be converted to `URIRef`.
  [PR #2076](https://github.com/RDFLib/rdflib/pull/2076).

- Fixed the generation of VALUES block for federated queries.
  The values block was including non-variable values like BNodes which resulted
  in invalid queries. Closed [issue #2079](https://github.com/RDFLib/rdflib/issues/2079).
  [PR #2084](https://github.com/RDFLib/rdflib/pull/2084).

- Only register the `rdflib.plugins.stores.berkeleydb.BerkeleyDB` as a store
  plugin if the `berkeleydb` module is present.
  Closed [issue #1816](https://github.com/RDFLib/rdflib/issues/1816).
  [PR #2096](https://github.com/RDFLib/rdflib/pull/2096).

- Fixed serialization of BNodes in TriG.
  The TriG serializer was only considering BNode references inside a single
  graph and not counting the BNodes subjects as references when considering if a
  BNode should be serialized as unlabeled blank nodes (i.e. `[ ]`), and as a
  result it was serializing BNodes as unlabeled if they were in fact referencing
  BNodes in other graphs.
  [PR #2085](https://github.com/RDFLib/rdflib/pull/2085).

- Deprecated `rdflib.path.evalPath` in favor of `rdflib.path.eval_path` which is
  PEP-8 compliant. [PR #2046](https://github.com/RDFLib/rdflib/pull/2046)

- Added `charset=UTF-8` to the `Content-Type` header sent when doing an update
  with `SPARQLConnector`. Closed [issue
  #2095](https://github.com/RDFLib/rdflib/issues/2095). [PR
  #2112](https://github.com/RDFLib/rdflib/pull/2112).

- Removed the `rdflib.plugins.sparql.parserutils.plist` class as it served no
  discernible purpose. [PR #2143](https://github.com/RDFLib/rdflib/pull/2143)

- Changed the TriG serializer to not generate prefixes for empty graph IDs.
  Closed [issue #2154](https://github.com/RDFLib/rdflib/issues/2154).
  [PR #2160](https://github.com/RDFLib/rdflib/pull/2160).

- Fixed handling of relative context files in the JSON-LD parser. 
  Closed [issue #2164](https://github.com/RDFLib/rdflib/issues/2164).
  [PR #2165](https://github.com/RDFLib/rdflib/pull/2165).

- Improved failure handling in when computing QName for an unbound namespace.
  [PR #2169](https://github.com/RDFLib/rdflib/pull/2169).

- Fixed a typo in the default bound namespace for `DCTERMS`.
  [PR #2173](https://github.com/RDFLib/rdflib/pull/2173).

- Add support for supplying a custom namespace manager to `n3()` methods.
  [PR #2174](https://github.com/RDFLib/rdflib/pull/2174).

- Fixed the query string parameters for `SPARQLConnector` when using POST method.
  [PR #2180](https://github.com/RDFLib/rdflib/pull/2180).

- Fixed extra keyword argument and header handling in `SPARQLConnector` that
  resulted in headers from `SPARQLConnector.update` polluting headers from
  `SPARQLConnector.query` vice versa.
  [PR #2183](https://github.com/RDFLib/rdflib/pull/2183)

- Added version restrictions for dependencies.
  [PR #2187](https://github.com/RDFLib/rdflib/pull/2187)

- Switch to using `importlib` for getting the version of RDFLib instead of
  hard-coding it in `__version__`.
  [PR #2187](https://github.com/RDFLib/rdflib/pull/2187).

- Removed non-runtime extras, for building documentation, running tests and
  other development operations the versions and dependencies are now
  managed with Poetry.
  [PR #2187](https://github.com/RDFLib/rdflib/pull/2187).

- Fixed a bug that occurred when `VALUES` was used outside a `GROUP BY` clause.
  [PR #2188](https://github.com/RDFLib/rdflib/pull/2188).

- Fixed a bug that occurred when using `SELECT *` inside another `SELECT *`.
  Closed [issue #1722](https://github.com/RDFLib/rdflib/issues/1722).
  [PR #2190](https://github.com/RDFLib/rdflib/pull/2190).

- Added SPARQL DESCRIBE query implementation.
  Closes [issue #479](https://github.com/RDFLib/rdflib/issues/479).
  [PR #2221](https://github.com/RDFLib/rdflib/pull/2221).

- Fixed a bug in `rdflib.tools.defined_namespace_creator` that occurred when
  multiple `rdfs:comment` were present on one resource.
  [PR #2254](https://github.com/RDFLib/rdflib/pull/2254).

- Fixed `rdflib.util._iri2uri()` to not quote the `netloc` parameter.
  [PR #2255](https://github.com/RDFLib/rdflib/pull/2255).

- Fixed the HexTuple parser's handling of input sources to works for more input sources.
  [PR #2255](https://github.com/RDFLib/rdflib/pull/2255).

- Fixed the creation of input source objects from IO stream sources.
  [PR #2255](https://github.com/RDFLib/rdflib/pull/2255).

- Eliminated the use of the deprecated `rdflib.path.evalPath` function.
  [PR #2266](https://github.com/RDFLib/rdflib/pull/2266)

- Added documentation for security considerations and available mitigations.
  Closed [issue #1844](https://github.com/RDFLib/rdflib/issues/1844).
  [PR #2267](https://github.com/RDFLib/rdflib/pull/2270).

### PRs merged since last release

* fix: validation issues with examples
  [PR #2269](https://github.com/RDFLib/rdflib/pull/2269)
* feat: more type hints for `rdflib.plugins.sparql`
  [PR #2268](https://github.com/RDFLib/rdflib/pull/2268)
* fix: eliminate use of deprecated `rdflib.path.evalPath`
  [PR #2266](https://github.com/RDFLib/rdflib/pull/2266)
* more type-hinting for SPARQL plugin
  [PR #2265](https://github.com/RDFLib/rdflib/pull/2265)
* feat: add diverse type hints
  [PR #2264](https://github.com/RDFLib/rdflib/pull/2264)
* feat: add type hints to `rdflib.collection`
  [PR #2263](https://github.com/RDFLib/rdflib/pull/2263)
* feat: add type hints to `rdflib.util`
  [PR #2262](https://github.com/RDFLib/rdflib/pull/2262)
* feat: add type hints to `rdflib.path`
  [PR #2261](https://github.com/RDFLib/rdflib/pull/2261)
* test: fix deprecation warnings
  [PR #2260](https://github.com/RDFLib/rdflib/pull/2260)
* docs: update test reports
  [PR #2259](https://github.com/RDFLib/rdflib/pull/2259)
* fix: small InputSource related issues
  [PR #2255](https://github.com/RDFLib/rdflib/pull/2255)
* defined_namespace_creator: concatenate several rdfs:comments
  [PR #2254](https://github.com/RDFLib/rdflib/pull/2254)
* feat: add parser type hints
  [PR #2232](https://github.com/RDFLib/rdflib/pull/2232)
* build: bump versions
  [PR #2231](https://github.com/RDFLib/rdflib/pull/2231)
* Add SPARQL DESCRIBE query implementation
  [PR #2221](https://github.com/RDFLib/rdflib/pull/2221)
* build: rename minimum constraints file to evade dependabot
  [PR #2209](https://github.com/RDFLib/rdflib/pull/2209)
* Fix for `SELECT *` inside `SELECT *` bug
  [PR #2190](https://github.com/RDFLib/rdflib/pull/2190)
* Fixing bug applying VALUES outside of a GROUP BY
  [PR #2188](https://github.com/RDFLib/rdflib/pull/2188)
* move to poetry for dependency management; consolidate more settings into pyproject.toml
  [PR #2187](https://github.com/RDFLib/rdflib/pull/2187)
* build: update black to 22.12.0
  [PR #2186](https://github.com/RDFLib/rdflib/pull/2186)
* Issue2179 incorrect headers
  [PR #2183](https://github.com/RDFLib/rdflib/pull/2183)
* Fix missing query string params in sparqlconnector when using POST method 
  [PR #2180](https://github.com/RDFLib/rdflib/pull/2180)
* [pre-commit.ci] pre-commit autoupdate
  [PR #2178](https://github.com/RDFLib/rdflib/pull/2178)
* Add namespace_manager argument for n3 method on Paths
  [PR #2174](https://github.com/RDFLib/rdflib/pull/2174)
* fix DCTERMS prefix typo
  [PR #2173](https://github.com/RDFLib/rdflib/pull/2173)
* compute_qname handle case where name could be unbound
  [PR #2169](https://github.com/RDFLib/rdflib/pull/2169)
* Issue 2164
  [PR #2165](https://github.com/RDFLib/rdflib/pull/2165)
* build: update black to 22.10.0
  [PR #2163](https://github.com/RDFLib/rdflib/pull/2163)
* ci: switch to python 3.11 release
  [PR #2162](https://github.com/RDFLib/rdflib/pull/2162)
* fix: type errors resulting from new mypy
  [PR #2161](https://github.com/RDFLib/rdflib/pull/2161)
* do not write prefix for empty graph id, fix #2154
  [PR #2160](https://github.com/RDFLib/rdflib/pull/2160)
* Remove redundant class
  [PR #2143](https://github.com/RDFLib/rdflib/pull/2143)
* Pass `service_query` to `_buildQueryStringForServiceCall` instead of a `Match`
  [PR #2134](https://github.com/RDFLib/rdflib/pull/2134)
* Add type hint to part in evalServiceQuery
  [PR #2133](https://github.com/RDFLib/rdflib/pull/2133)
* Remove outdated comment
  [PR #2129](https://github.com/RDFLib/rdflib/pull/2129)
* fix: type ignore compatibility with latest mypy
  [PR #2127](https://github.com/RDFLib/rdflib/pull/2127)
* Remove redundant PR template
  [PR #2126](https://github.com/RDFLib/rdflib/pull/2126)
* build: use 3.11.0-rc.2
  [PR #2119](https://github.com/RDFLib/rdflib/pull/2119)
* build: docker images for latest release and main branch
  [PR #2116](https://github.com/RDFLib/rdflib/pull/2116)
* add charset encoding to SPARQLConnector.update() request.
  [PR #2112](https://github.com/RDFLib/rdflib/pull/2112)
* Add test for issue #2011
  [PR #2107](https://github.com/RDFLib/rdflib/pull/2107)
* chore: rename default branch to `main`
  [PR #2101](https://github.com/RDFLib/rdflib/pull/2101)
* Correct a typo in test_roundtrip.py
  [PR #2100](https://github.com/RDFLib/rdflib/pull/2100)
* feat: add type hints to `rdflib.query` and related
  [PR #2097](https://github.com/RDFLib/rdflib/pull/2097)
* fix: Don't register berkelydb as a store if it is not available on the system
  [PR #2096](https://github.com/RDFLib/rdflib/pull/2096)
* feat: add type hints to `rdflib.plugins.sparql.{algebra,operators}`
  [PR #2094](https://github.com/RDFLib/rdflib/pull/2094)
* test: Fix `exclude_lines` for coverage
  [PR #2093](https://github.com/RDFLib/rdflib/pull/2093)
* test: content-type handling with SPARQLStore + CONSTRUCT queries
  [PR #2092](https://github.com/RDFLib/rdflib/pull/2092)
* ci: publish test reports for mypy and pytest
  [PR #2091](https://github.com/RDFLib/rdflib/pull/2091)
* test: convert more test from unittest to pytest
  [PR #2089](https://github.com/RDFLib/rdflib/pull/2089)
* ci: switch from 3.11.0-beta.4 to 3.11.0-rc.1
  [PR #2087](https://github.com/RDFLib/rdflib/pull/2087)
* fix: issue with trig reference counting across graphs
  [PR #2085](https://github.com/RDFLib/rdflib/pull/2085)
* Generate VALUES block for federated queries with variables only
  [PR #2084](https://github.com/RDFLib/rdflib/pull/2084)
* docs: Add a contributing guide
  [PR #2082](https://github.com/RDFLib/rdflib/pull/2082)
* feat: Add type hints to rdflib.graph
  [PR #2080](https://github.com/RDFLib/rdflib/pull/2080)
* fix: handling of Literal datatype
  [PR #2076](https://github.com/RDFLib/rdflib/pull/2076)
* test: convert some `unittest` based tests to `pytest`
  [PR #2075](https://github.com/RDFLib/rdflib/pull/2075)
* test: honour lax cardinality from test manifests
  [PR #2074](https://github.com/RDFLib/rdflib/pull/2074)
* Fix passing ConjunctiveGraph as namespace_manager
  [PR #2073](https://github.com/RDFLib/rdflib/pull/2073)
* fix: always parse HexTuple files as utf-8
  [PR #2070](https://github.com/RDFLib/rdflib/pull/2070)
* fix: narrow the context identifier type from `Node` to `IdentifiedNode`
  [PR #2069](https://github.com/RDFLib/rdflib/pull/2069)
* build: set a minimum version for flakeheaven
  [PR #2068](https://github.com/RDFLib/rdflib/pull/2068)
* chore: remove pre Python 3.7 compatibility code for shutil
  [PR #2066](https://github.com/RDFLib/rdflib/pull/2066)
* fix: issues with string destination handling in `{Graph,Result}.serialize`
  [PR #2065](https://github.com/RDFLib/rdflib/pull/2065)
* build: fix Taskfile.yml for Windows
  [PR #2064](https://github.com/RDFLib/rdflib/pull/2064)
* test: convert `test/test_sparql/test_sparql_parser.py` to pytest
  [PR #2063](https://github.com/RDFLib/rdflib/pull/2063)
* test: convert `test/test_sparql/test_construct_bindings.py` to pytest
  [PR #2062](https://github.com/RDFLib/rdflib/pull/2062)
* test: convert `test/test_parsers/test_nquads.py` to pytest
  [PR #2061](https://github.com/RDFLib/rdflib/pull/2061)
* test: convert `test/test_namespace/test_namespace.py` to pytest
  [PR #2060](https://github.com/RDFLib/rdflib/pull/2060)
* docs: add DOI for RDFLib
  [PR #2058](https://github.com/RDFLib/rdflib/pull/2058)
* feat: add type hints for `rdflib.store` and `rdflib.plugins.stores`
  [PR #2057](https://github.com/RDFLib/rdflib/pull/2057)
* Toplevel n80x
  [PR #2046](https://github.com/RDFLib/rdflib/pull/2046)
* docs: add some additional badges
  [PR #2045](https://github.com/RDFLib/rdflib/pull/2045)
* fix: SPARQL XML result parsing
  [PR #2044](https://github.com/RDFLib/rdflib/pull/2044)
* chore: remove pre python 3.5 regex related workaround
  [PR #2042](https://github.com/RDFLib/rdflib/pull/2042)
* fix: import xml.sax.handler from the right place
  [PR #2041](https://github.com/RDFLib/rdflib/pull/2041)
* test: remove python 2.4 specific behaviour in test
  [PR #2040](https://github.com/RDFLib/rdflib/pull/2040)
* build: remove drone config
  [PR #2037](https://github.com/RDFLib/rdflib/pull/2037)
* docs: fix sphinx nitpicky issues
  [PR #2036](https://github.com/RDFLib/rdflib/pull/2036)
* build: Gitpod integration and Google Cloud Shell Button
  [PR #2034](https://github.com/RDFLib/rdflib/pull/2034)
* Infixowl cleanup iii
  [PR #2033](https://github.com/RDFLib/rdflib/pull/2033)
* build: Taskfile improvements
  [PR #2032](https://github.com/RDFLib/rdflib/pull/2032)
* docs: removed "Other changes" from CHANGELOG.md
  [PR #2031](https://github.com/RDFLib/rdflib/pull/2031)
* Infixowl coverage ii
  [PR #2024](https://github.com/RDFLib/rdflib/pull/2024)
* add chunk serializer & tests
  [PR #1968](https://github.com/RDFLib/rdflib/pull/1968)

## 2022-07-16 RELEASE 6.2.0

This is a minor release that includes bug fixes and features.

### User facing changes

This section lists changes that have a potential impact on users of RDFLib,
changes with no user impact are not included in this section.

- SPARQL: Fixed handing of `HAVING` clause with variable composition. Closed
  [issue #936](https://github.com/RDFLib/rdflib/issues/936) and [issue
  #935](https://github.com/RDFLib/rdflib/pull/935), [PR
  #1093](https://github.com/RDFLib/rdflib/pull/1093).
- JSON-LD parser: better support for content negotiation. Closed [issue
  #1423](https://github.com/RDFLib/rdflib/issues/1423), [PR
  #1436](https://github.com/RDFLib/rdflib/pull/1436).
- Removed the following functions that were marked as deprecated and scheduled
  for removal in version 6.0.0: `Graph.load`, `Graph.seq`, `Graph.comment`,
  `Graph.label`. [PR #1527](https://github.com/RDFLib/rdflib/pull/1527).
- Use `functools.total_ordering` to implement most comparison operations for
  `rdflib.paths.Path`. Closed [issue
  #685](https://github.com/RDFLib/rdflib/issues/685), [PR
  #1528](https://github.com/RDFLib/rdflib/pull/1528).
- Fixed error handling for invalid URIs. Closed [issue
  #821](https://github.com/RDFLib/rdflib/issues/821), [PR
  #1529](https://github.com/RDFLib/rdflib/pull/1529).
- InfixOWL: Fixed handling of cardinality 0. Closed [issue
 #1453](https://github.com/RDFLib/rdflib/issues/1453) and [issue
 #944](https://github.com/RDFLib/rdflib/pull/1530), [PR
 #1530](https://github.com/RDFLib/rdflib/pull/1530).
- Added quad support to handling to `rdflib.graph.ReadOnlyGraphAggregate.quads`.
  Closed [issue #430](https://github.com/RDFLib/rdflib/issues/430), [PR
  #1590](https://github.com/RDFLib/rdflib/pull/1590)
- Fixed base validation used when joining URIs. [PR
  #1607](https://github.com/RDFLib/rdflib/pull/1607).
- Add GEO defined namespace for GeoSPARQL. Closed [issue
  #1371](https://github.com/RDFLib/rdflib/issues/1371), [PR
  #1622](https://github.com/RDFLib/rdflib/pull/1622).
- Explicitly raise exception when
  `rdflib.plugins.stores.sparqlstore.SPARQLStore.update` is called. Closed
  [issue #1032](https://github.com/RDFLib/rdflib/issues/1032), [PR
  #1623](https://github.com/RDFLib/rdflib/pull/1623).
- Added `rdflib.plugins.sparql.processor.prepareUpdate`. Closed [issue
  #272](https://github.com/RDFLib/rdflib/issues/272) and [discussion
  #1581](https://github.com/RDFLib/rdflib/discussions/1581), [PR
  #1624](https://github.com/RDFLib/rdflib/pull/1624).
- Added `rdflib.namespace.DefinedNamespaceMeta.__dir__`. Closed [issue
  #1593](https://github.com/RDFLib/rdflib/issues/1593), [PR
  #1626](https://github.com/RDFLib/rdflib/pull/1626).
- Removed `TypeCheckError`, `SubjectTypeError`, `PredicateTypeError`,
  `ObjectTypeError` and `ContextTypeError` as these exceptions are not raised by
  RDFLib and their existence will only confuse users which may expect them to be
  used. Also remove corresponding `check_context`, `check_subject`,
  `check_predicate`, `check_object`, `check_statement`, `check_pattern` that is
  unused. [PR #1640](https://github.com/RDFLib/rdflib/pull/1640).
- Improved the population of the `Accept` HTTP header so that it is correctly
  populated for all formats. [PR
  #1643](https://github.com/RDFLib/rdflib/pull/1643).
- Fixed some issues with SPARQL Algebra handling/translation. [PR
  #1645](https://github.com/RDFLib/rdflib/pull/1645).
- Add `nquads` to recognized file extensions.
  [PR #1653](https://github.com/RDFLib/rdflib/pull/1653).
- Fixed issues that prevented HexTuples roundtripping.
  [PR #1656](https://github.com/RDFLib/rdflib/pull/1656).
- Make `rdflib.plugins.sparql.operators.unregister_custom_function` idempotent.
  Closed [issue #1492](https://github.com/RDFLib/rdflib/issues/1492),
  [PR #1659](https://github.com/RDFLib/rdflib/pull/1659).
- Fixed the handling of escape sequences in the N-Triples and N-Quads parsers.
  These parsers will now correctly handle strings like `"\\r"`. The time it
  takes for these parsers to parse strings with escape sequences will be
  increased, and the increase will be correlated with the amount of escape
  sequences that occur in a string. For strings with many escape sequences the
  parsing speed seems to be almost 4 times slower. Closed [issue
  #1655](https://github.com/RDFLib/rdflib/issues/1655), [PR
  #1663](https://github.com/RDFLib/rdflib/pull/1663).
  - Also marked `rdflib.compat.decodeStringEscape` as deprecated as this
    function is not used anywhere in RDFLib anymore and the utility that it does
    provide is not implemented correctly. It will be removed in RDFLib 7.0.0
- Added an abstract class `IdentifiedNode` as a superclass of `BNode` and
  `URIRef`. Closed [issue #1526](https://github.com/RDFLib/rdflib/issues/1526),
  [PR #1680](https://github.com/RDFLib/rdflib/pull/1680).
- Fixed turtle serialization of `rdf:type` in subject, object. Closed [issue
  #1649](https://github.com/RDFLib/rdflib/issues/1649), [PR
  #1649](https://github.com/RDFLib/rdflib/pull/1684).
- Fixed turtle serialization of PNames that contain brackets. Closed [issue
  #1661](https://github.com/RDFLib/rdflib/issues/1661), [PR
  #1678](https://github.com/RDFLib/rdflib/pull/1678).
- Added support for selecting which namespace prefixes to bind. Closed [issue
  #1679](https://github.com/RDFLib/rdflib/issues/1679) and [issue #1880](https://github.com/RDFLib/rdflib/pull/1880), [PR
  #1686](https://github.com/RDFLib/rdflib/pull/1686), [PR
  #1845](https://github.com/RDFLib/rdflib/pull/1845) and [PR
    #2018](https://github.com/RDFLib/rdflib/pull/2018).
  - Also added `ConjunctiveGraph.get_graph`.
  - Also added an `override` argument to `Store.bind` which behaves similarly to
    the `override` parameter for `NamespaceManager.bind`.
  - Also fixed handing of support of the `override` parameter to
    `NamespaceManager.bind` by passing.
- Eliminated a `DeprecationWarning` related to plugin loading [issue
  #1631](https://github.com/RDFLib/rdflib/issues/1631), [PR
  #1694](https://github.com/RDFLib/rdflib/pull/1694).
- Removed the `rdflib.graph.ContextNode` and `rdflib.graph.DatasetQuad` type
  aliases. These were not being widely used in RDFLib and were also not correct.
  [PR #1695](https://github.com/RDFLib/rdflib/pull/1695).
- Added `DefinedNamespace.as_jsonld_context`. [PR
  #1706](https://github.com/RDFLib/rdflib/pull/1706).
- Added `rdflib.namespace.WGS` for WGS84. Closed [issue
  #1709](https://github.com/RDFLib/rdflib/issues/1709),  [PR
  #1710](https://github.com/RDFLib/rdflib/pull/1710).
- Improved performance of `DefinedNamespace` by caching attribute values. [PR
  #1718](https://github.com/RDFLib/rdflib/pull/1718).
- Only configure python logging if `sys.stderr` has a `isatty` attribute. Closed
  [issue #1760](https://github.com/RDFLib/rdflib/issues/1760), [PR
  #1761](https://github.com/RDFLib/rdflib/pull/1761).
- Removed unused `rdflib.compat.etree_register_namespace`. [PR
  #1768](https://github.com/RDFLib/rdflib/pull/1768).
- Fixed numeric shortcut handling in `rdflib.util.from_n3`. Closed [issue
  #1769](https://github.com/RDFLib/rdflib/issues/1769), [PR
  #1771](https://github.com/RDFLib/rdflib/pull/1771).
- Add ability to detect and mark ill-typed literals. Closed [issue
  #1757](https://github.com/RDFLib/rdflib/issues/1757) and [issue
  #848](https://github.com/RDFLib/rdflib/issues/848), [PR
  #1773](https://github.com/RDFLib/rdflib/pull/1773) and [PR
  #2003](https://github.com/RDFLib/rdflib/pull/2003).
- Optimized `NamespaceManager.compute_qname` by caching validity. [PR
  #1779](https://github.com/RDFLib/rdflib/pull/1779).
- SPARQL: Fixed the handling of `EXISTS` inside `BIND` for SPARQL. This was
  raising an exception during evaluation before but is now correctly handled.
  Closed [issue #1472](https://github.com/RDFLib/rdflib/issues/1472), [PR
  #1794](https://github.com/RDFLib/rdflib/pull/1794).
- Propagate exceptions from SPARQL TSV result parser. Closed [issue
  #1477](https://github.com/RDFLib/rdflib/issues/1477), [PR
  #1809](https://github.com/RDFLib/rdflib/pull/1809)
- Eliminate usage of `rdflib.term.RDFLibGenid` as a type as this caused issues
  with querying. Closed [issue
  #1808](https://github.com/RDFLib/rdflib/issues/1808), [PR
  #1821](https://github.com/RDFLib/rdflib/pull/1821)
- Fixed handing of `DefinedNamespace` control attributes so that
  `inspect.signature` works correctly on defined namespaces. [PR
  #1825](https://github.com/RDFLib/rdflib/pull/1825).
- Fixed namespace rebinding in `Memory`, `SimpleMemory` and `BerkelyDB` stores.
  Closed [issue #1826](https://github.com/RDFLib/rdflib/issues/1826), [PR
  #1843](https://github.com/RDFLib/rdflib/pull/1843).
- Fixed issues with the N3 serializer. Closed [issue
  #1701](https://github.com/RDFLib/rdflib/issues/1701) and [issue
  #1807](https://github.com/RDFLib/rdflib/issues/1807), [PR
  #1858](https://github.com/RDFLib/rdflib/pull/1858):
  - The N3 serializer was incorrectly considers a subject as seralized if it is serialized in a quoted graph.
  - The N3 serializer does not consider that the predicate of a triple can also
be a graph.
- Added `NamespaceManager.expand_curie`. Closed [issue
  #1868](https://github.com/RDFLib/rdflib/issues/1868), [PR
  #1869](https://github.com/RDFLib/rdflib/pull/1869).
- Added `Literal.__sub__` and support for datetimes to both `Literal.__add__`
  and `Literal.__sub__`. [PR #1870](https://github.com/RDFLib/rdflib/pull/1870).
- SPARQL: Fix `None`/undefined handing in `GROUP_CONCAT`. Closed [issue
  #1467](https://github.com/RDFLib/rdflib/issues/1467), [PR
  #1887](https://github.com/RDFLib/rdflib/pull/1887).
- SPARQL: Fixed result handling for `SERVICE` directive. Closed [issue
  #1278](https://github.com/RDFLib/rdflib/issues/1278),  [PR
  #1894](https://github.com/RDFLib/rdflib/pull/1894).
- Change the skolem default authority for RDFLib from `http://rdlib.net/` to
  `https://rdflib.github.io` and also change other uses of `http://rdlib.net/`
  to `https://rdflib.github.io`. Closed [issue
  #1824](https://github.com/RDFLib/rdflib/issues/1824), [PR
  #1901](https://github.com/RDFLib/rdflib/pull/1901).
- Fixes handling of non-ascii characters in IRIs. Closed [issue
  #1429](https://github.com/RDFLib/rdflib/issues/1429), [PR
  #1902](https://github.com/RDFLib/rdflib/pull/1902).
- Pass `generate` to `NamespaceManager.compute_qname` from
  `NamespaceManager.compute_qname_strict` so it raises an error in the same
  case as the "non-strict" version. [PR
  #1934](https://github.com/RDFLib/rdflib/pull/1934).
- Log warnings when encountering ill-typed literals.
  [PR #1944](https://github.com/RDFLib/rdflib/pull/1944).
- Fixed error handling in TriX serializer. [PR
  #1945](https://github.com/RDFLib/rdflib/pull/1945).
- Fixed QName generation in XML serializer.
  [PR #1951](https://github.com/RDFLib/rdflib/pull/1951)
- Remove unnecessary hex expansion for PN_LOCAL in SPARQL parser. Closed [issue
  #1957](https://github.com/RDFLib/rdflib/issues/1957), 
  [PR #1959](https://github.com/RDFLib/rdflib/pull/1959).
- Changed the TriX parser to support both `trix` and `TriX` as root element. [PR
  #1966](https://github.com/RDFLib/rdflib/pull/1966).
- Fix SPARQL CSV result serialization of blank nodes.
  [PR #1979](https://github.com/RDFLib/rdflib/pull/1979).
- Added a `URIRef.fragment` property.
  [PR #1991](https://github.com/RDFLib/rdflib/pull/1991).
- Remove superfluous newline from N-Triples output. Closed [issue
  #1998](https://github.com/RDFLib/rdflib/issues/1998), [PR
  #1999](https://github.com/RDFLib/rdflib/pull/1999).
- Added a bunch of type hints. The following modules have nearly complete type hints now:
  - `rdflib.namespace`
  - `rdflib.term`
  - `rdflib.parser`

### PRs merged since last release

* Fallback to old `Store.bind` signature on `TypeError`
  [PR #2018](https://github.com/RDFLib/rdflib/pull/2018)
* Fix/ignore flake8 errors in `rdflib/parser.py`
  [PR #2016](https://github.com/RDFLib/rdflib/pull/2016)
* Update black to 22.6.0
  [PR #2015](https://github.com/RDFLib/rdflib/pull/2015)
* Fix for #1873 avoid AttributeError raised ...
  [PR #2013](https://github.com/RDFLib/rdflib/pull/2013)
* Change Literal.ill_formed to Literal.ill_typed
  [PR #2003](https://github.com/RDFLib/rdflib/pull/2003)
* Continuation of infixowl update and coverage improvement
  [PR #2001](https://github.com/RDFLib/rdflib/pull/2001)
* Update test README
  [PR #2000](https://github.com/RDFLib/rdflib/pull/2000)
* Remove extra newline from N-Triples output
  [PR #1999](https://github.com/RDFLib/rdflib/pull/1999)
* Infixowl cleanup
  [PR #1996](https://github.com/RDFLib/rdflib/pull/1996)
* Add line-specific # noqa to `infixowl.py`, remove exclusion from pyproject.toml
  [PR #1994](https://github.com/RDFLib/rdflib/pull/1994)
* Bump actions/setup-python from 3 to 4
  [PR #1992](https://github.com/RDFLib/rdflib/pull/1992)
* Add fragment property to URIRef
  [PR #1991](https://github.com/RDFLib/rdflib/pull/1991)
* test: run tests on python 3.11 also
  [PR #1989](https://github.com/RDFLib/rdflib/pull/1989)
* test: rework SPARQL test suite
  [PR #1988](https://github.com/RDFLib/rdflib/pull/1988)
* test: rework RDF/XML test suite
  [PR #1987](https://github.com/RDFLib/rdflib/pull/1987)
* Rework turtle-like test suites
  [PR #1986](https://github.com/RDFLib/rdflib/pull/1986)
* Improve docstring of `Graph.serialize`f 
  [PR #1984](https://github.com/RDFLib/rdflib/pull/1984)
* Add more tests for graph_diff
  [PR #1983](https://github.com/RDFLib/rdflib/pull/1983)
* Convert some more graph tests to pytest
  [PR #1982](https://github.com/RDFLib/rdflib/pull/1982)
* Fix SPARQL test data
  [PR #1981](https://github.com/RDFLib/rdflib/pull/1981)
* Add more namespaces to test utils
  [PR #1980](https://github.com/RDFLib/rdflib/pull/1980)
* Fix SPARQL CSV result serialization of blank nodes
  [PR #1979](https://github.com/RDFLib/rdflib/pull/1979)
* correct italic markup in plugin stores docs
  [PR #1977](https://github.com/RDFLib/rdflib/pull/1977)
* escape literal * symbol in `rdflib.paths` docs
  [PR #1976](https://github.com/RDFLib/rdflib/pull/1976)
* Update sphinx requirement from <5 to <6
  [PR #1975](https://github.com/RDFLib/rdflib/pull/1975)
* Remove `pytest-subtest`
  [PR #1973](https://github.com/RDFLib/rdflib/pull/1973)
* style: fix/ignore flake8 errors in store related code
  [PR #1971](https://github.com/RDFLib/rdflib/pull/1971)
* build: speed up flake8 by ignoring test data
  [PR #1970](https://github.com/RDFLib/rdflib/pull/1970)
* Fix trix parser
  [PR #1966](https://github.com/RDFLib/rdflib/pull/1966)
* Add more typing for SPARQL
  [PR #1965](https://github.com/RDFLib/rdflib/pull/1965)
* style: fix/ignore flake8 errors in `rdflib/plugins/sparql/`
  [PR #1964](https://github.com/RDFLib/rdflib/pull/1964)
* test: fix `None` comparisons
  [PR #1963](https://github.com/RDFLib/rdflib/pull/1963)
* style: fix/ingore some flake8 errors in `rdflib/graph.py`
  [PR #1962](https://github.com/RDFLib/rdflib/pull/1962)
* test: convert `test/jsonld/test_util.py` to pytest
  [PR #1961](https://github.com/RDFLib/rdflib/pull/1961)
* Fix for issue1957 sparql parser percent encoded reserved chars
  [PR #1959](https://github.com/RDFLib/rdflib/pull/1959)
* test: convert `test_graph_http.py` to pytest
  [PR #1956](https://github.com/RDFLib/rdflib/pull/1956)
* edit tabs to spaces
  [PR #1952](https://github.com/RDFLib/rdflib/pull/1952)
* fix sonarcloud-reported bug in xmlwriter, add test
  [PR #1951](https://github.com/RDFLib/rdflib/pull/1951)
* test: convert test_literal.py to pytest
  [PR #1949](https://github.com/RDFLib/rdflib/pull/1949)
* style: ignore flake8 name errors for existing names
  [PR #1948](https://github.com/RDFLib/rdflib/pull/1948)
* test: remove unused imports in test code
  [PR #1947](https://github.com/RDFLib/rdflib/pull/1947)
* test: fix `GraphHelper.quad_set` handling of Dataset
  [PR #1946](https://github.com/RDFLib/rdflib/pull/1946)
* fix for sonarcloud-reported bug
  [PR #1945](https://github.com/RDFLib/rdflib/pull/1945)
* Logging exceptions from Literal value converters
  [PR #1944](https://github.com/RDFLib/rdflib/pull/1944)
* fix outmoded `x and x or y` idiom in `infixowl.py`
  [PR #1943](https://github.com/RDFLib/rdflib/pull/1943)
* Address lingering instances of deprecated `tempfile.mktemp`
  [PR #1942](https://github.com/RDFLib/rdflib/pull/1942)
* Add CODEOWNERS
  [PR #1941](https://github.com/RDFLib/rdflib/pull/1941)
* Bump actions/setup-python from 2 to 3
  [PR #1940](https://github.com/RDFLib/rdflib/pull/1940)
* Bump actions/checkout from 2 to 3
  [PR #1939](https://github.com/RDFLib/rdflib/pull/1939)
* Bump actions/cache from 2 to 3
  [PR #1938](https://github.com/RDFLib/rdflib/pull/1938)
* Bump actions/setup-java from 2 to 3
  [PR #1937](https://github.com/RDFLib/rdflib/pull/1937)
* test: move rdfs.ttl into `test/data/defined_namespaces`
  [PR #1936](https://github.com/RDFLib/rdflib/pull/1936)
* feat: add tests and typing for `rdflib.utils.{get_tree,find_roots}`
  [PR #1935](https://github.com/RDFLib/rdflib/pull/1935)
* Passing "generate" option through in compute_qname_strict
  [PR #1934](https://github.com/RDFLib/rdflib/pull/1934)
* build: add GitHub Actions to dependabot
  [PR #1933](https://github.com/RDFLib/rdflib/pull/1933)
* test: move `EARL` and `RDFT` namespaces to separate files
  [PR #1931](https://github.com/RDFLib/rdflib/pull/1931)
* Removed old and unused `test/data/suites/DAWG/data-r2`
  [PR #1930](https://github.com/RDFLib/rdflib/pull/1930)
* Added SPARQL unicode numeric codepoint escape tests
  [PR #1929](https://github.com/RDFLib/rdflib/pull/1929)
* style: enable and baseline flakeheaven
  [PR #1928](https://github.com/RDFLib/rdflib/pull/1928)
* feat: add typing for `rdflib/plugins/sparql`
  [PR #1926](https://github.com/RDFLib/rdflib/pull/1926)
* Switch to latest DAWG test suite
  [PR #1925](https://github.com/RDFLib/rdflib/pull/1925)
* Move `test/data/suites/DAWG/rdflib`
  [PR #1924](https://github.com/RDFLib/rdflib/pull/1924)
* style: normalize quoting with black
  [PR #1916](https://github.com/RDFLib/rdflib/pull/1916)
* Added test for example at CBD definition. Fixes #1914.
  [PR #1915](https://github.com/RDFLib/rdflib/pull/1915)
* Rename `test/data/suites/DAWG/data-r2-1.0`
  [PR #1908](https://github.com/RDFLib/rdflib/pull/1908)
* Move `DAWG/data-sparql11` to `w3c/sparql11/data-sparql11`
  [PR #1907](https://github.com/RDFLib/rdflib/pull/1907)
* Add n3 test suite runner
  [PR #1906](https://github.com/RDFLib/rdflib/pull/1906)
* Migrated the various `test_*_w3c.py` test files into `test/test_w3c_spec/`
  [PR #1904](https://github.com/RDFLib/rdflib/pull/1904)
* Fixes #1429, add `iri2uri`
  [PR #1902](https://github.com/RDFLib/rdflib/pull/1902)
* Fix for #1824 `s,http://rdlib.net,http://rdflib.net,g`
  [PR #1901](https://github.com/RDFLib/rdflib/pull/1901)
* test: Add more tests for Graph serialize
  [PR #1898](https://github.com/RDFLib/rdflib/pull/1898)
* test: earlier assert rewrite for test utitlities
  [PR #1897](https://github.com/RDFLib/rdflib/pull/1897)
* test: Add more tests for test utilities
  [PR #1896](https://github.com/RDFLib/rdflib/pull/1896)
* test: add more graph variants highlighting bugs
  [PR #1895](https://github.com/RDFLib/rdflib/pull/1895)
* Fix simple literals returned as NULL using SERVICE (issue #1278)
  [PR #1894](https://github.com/RDFLib/rdflib/pull/1894)
* W3 test reorg
  [PR #1891](https://github.com/RDFLib/rdflib/pull/1891)
* Improved mock HTTP Server
  [PR #1888](https://github.com/RDFLib/rdflib/pull/1888)
* Fix `None`/undefined handing in GROUP_CONCAT
  [PR #1887](https://github.com/RDFLib/rdflib/pull/1887)
* Move test utility modules into `test/utils/`
  [PR #1879](https://github.com/RDFLib/rdflib/pull/1879)
* Move coveralls to GitHub Actions
  [PR #1877](https://github.com/RDFLib/rdflib/pull/1877)
* test: run doctest on rst files in `docs/`
  [PR #1875](https://github.com/RDFLib/rdflib/pull/1875)
* Add tests demonstrating forward-slash behaviors in Turtle, JSON-LD, and SPARQL
  [PR #1872](https://github.com/RDFLib/rdflib/pull/1872)
* Literal datetime sub
  [PR #1870](https://github.com/RDFLib/rdflib/pull/1870)
* resolve issue1868, add a method to expand qname to URI
  [PR #1869](https://github.com/RDFLib/rdflib/pull/1869)
* build: add Taskfile with development tasks
  [PR #1867](https://github.com/RDFLib/rdflib/pull/1867)
* Delete basically-unusable example
  [PR #1866](https://github.com/RDFLib/rdflib/pull/1866)
* Move `test/translate_algebra` into `test/data`
  [PR #1864](https://github.com/RDFLib/rdflib/pull/1864)
* test: move `test/variants` into `test/data`
  [PR #1862](https://github.com/RDFLib/rdflib/pull/1862)
* test: convert `test/test_serializers/test_serializer.py` to pytest
  [PR #1861](https://github.com/RDFLib/rdflib/pull/1861)
* Add remote file fetcher and N3 test suite
  [PR #1860](https://github.com/RDFLib/rdflib/pull/1860)
* fix: two issues with the N3 serializer
  [PR #1858](https://github.com/RDFLib/rdflib/pull/1858)
* Tell coveragepy to ignore type checking code and `...`
  [PR #1855](https://github.com/RDFLib/rdflib/pull/1855)
* docs: switch to sphinx-autodoc-typehints
  [PR #1854](https://github.com/RDFLib/rdflib/pull/1854)
* More type hints for `rdflib.graph` and related
  [PR #1853](https://github.com/RDFLib/rdflib/pull/1853)
* Remove testing and debug code from rdflib
  [PR #1849](https://github.com/RDFLib/rdflib/pull/1849)
* text: fix pytest config
  [PR #1846](https://github.com/RDFLib/rdflib/pull/1846)
* fix: Raise ValueError for unsupported `bind_namespace` values
  [PR #1845](https://github.com/RDFLib/rdflib/pull/1845)
* fix: namespace rebinding in `Memory`, `SimpleMemory` and `BerkelyDB` stores.
  [PR #1843](https://github.com/RDFLib/rdflib/pull/1843)
* test re-org
  [PR #1838](https://github.com/RDFLib/rdflib/pull/1838)
* fix: DefinedNamespace: fixed handling of control attributes.
  [PR #1825](https://github.com/RDFLib/rdflib/pull/1825)
* docs: change term reference to italicized
  [PR #1823](https://github.com/RDFLib/rdflib/pull/1823)
* Fix issue 1808
  [PR #1821](https://github.com/RDFLib/rdflib/pull/1821)
* build: disable building of epub on readthedocs.org
  [PR #1820](https://github.com/RDFLib/rdflib/pull/1820)
* docs: fix sphinx warnings
  [PR #1818](https://github.com/RDFLib/rdflib/pull/1818)
* style: fix isort config
  [PR #1817](https://github.com/RDFLib/rdflib/pull/1817)
* Migrate to pytest, relocate in subfolder
  [PR #1813](https://github.com/RDFLib/rdflib/pull/1813)
* test: add a test for n3 serialization with formula
  [PR #1812](https://github.com/RDFLib/rdflib/pull/1812)
* refactor: convert `test_n3.py` to pytest
  [PR #1811](https://github.com/RDFLib/rdflib/pull/1811)
* test: Add tests for SPARQL parsing and serialization
  [PR #1810](https://github.com/RDFLib/rdflib/pull/1810)
* fix: propagate exceptions from SPARQL TSV result parser
  [PR #1809](https://github.com/RDFLib/rdflib/pull/1809)
* Migrate more tests to pytest
  [PR #1806](https://github.com/RDFLib/rdflib/pull/1806)
* Convert `test_sparql/test_tsvresults.py` to pytest
  [PR #1805](https://github.com/RDFLib/rdflib/pull/1805)
* Ignore pyparsing type hints
  [PR #1802](https://github.com/RDFLib/rdflib/pull/1802)
* Add two xfails related to Example 2 from RDF 1.1 TriG specification
  [PR #1801](https://github.com/RDFLib/rdflib/pull/1801)
* change pytest.skip to pytest.xfail
  [PR #1799](https://github.com/RDFLib/rdflib/pull/1799)
* Black tests
  [PR #1798](https://github.com/RDFLib/rdflib/pull/1798)
* Convert `test/test_util.py` to `pytest`
  [PR #1795](https://github.com/RDFLib/rdflib/pull/1795)
* Fix handling of EXISTS inside BIND
  [PR #1794](https://github.com/RDFLib/rdflib/pull/1794)
* update test_graph_generators to import from test.data
  [PR #1792](https://github.com/RDFLib/rdflib/pull/1792)
* Test reorg (continued)
  [PR #1788](https://github.com/RDFLib/rdflib/pull/1788)
* Edit readme
  [PR #1787](https://github.com/RDFLib/rdflib/pull/1787)
* Add tests for computing qname on invalid URIs
  [PR #1783](https://github.com/RDFLib/rdflib/pull/1783)
* Convert namespace tests to pytest
  [PR #1782](https://github.com/RDFLib/rdflib/pull/1782)
* Update to black 22.3.0 because of issue with click
  [PR #1780](https://github.com/RDFLib/rdflib/pull/1780)
* Isvaliduri optimization
  [PR #1779](https://github.com/RDFLib/rdflib/pull/1779)
* Add tests for the parsing of literals for the turtle family of formats
  [PR #1778](https://github.com/RDFLib/rdflib/pull/1778)
* Migrate some tests to pytest
  [PR #1774](https://github.com/RDFLib/rdflib/pull/1774)
* Add ability to detect and mark ill-typed literals
  [PR #1773](https://github.com/RDFLib/rdflib/pull/1773)
* Fix for issue1769
  [PR #1771](https://github.com/RDFLib/rdflib/pull/1771)
* Remove unused compatability function
  [PR #1768](https://github.com/RDFLib/rdflib/pull/1768)
* Add pull request guidelines and template.
  [PR #1767](https://github.com/RDFLib/rdflib/pull/1767)
* Rename some tests
  [PR #1766](https://github.com/RDFLib/rdflib/pull/1766)
* Add config for readthedocs.org
  [PR #1764](https://github.com/RDFLib/rdflib/pull/1764)
* Fix black
  [PR #1763](https://github.com/RDFLib/rdflib/pull/1763)
* Check if sys.stderr has isatty
  [PR #1761](https://github.com/RDFLib/rdflib/pull/1761)
* Remove redundant type ignores and fix typing errors
  [PR #1759](https://github.com/RDFLib/rdflib/pull/1759)
* Add documentation about type hints
  [PR #1751](https://github.com/RDFLib/rdflib/pull/1751)
* Enable showing typehints in sphinx function/method signature and content
  [PR #1728](https://github.com/RDFLib/rdflib/pull/1728)
* Update reference to black.toml
  [PR #1721](https://github.com/RDFLib/rdflib/pull/1721)
* black formatting for rdflib/store.py
  [PR #1720](https://github.com/RDFLib/rdflib/pull/1720)
* Use the correct warnings module
  [PR #1719](https://github.com/RDFLib/rdflib/pull/1719)
* `DefinedNamespaceMeta.__getitem__` is slow
  [PR #1718](https://github.com/RDFLib/rdflib/pull/1718)
* Introduce WGS84 DefinedNamespace
  [PR #1710](https://github.com/RDFLib/rdflib/pull/1710)
* #1699 Document `Graph` behavior regarding context in constructor docstring
  [PR #1707](https://github.com/RDFLib/rdflib/pull/1707)
* Generate JSON-LD context from a DefinedNamespace
  [PR #1706](https://github.com/RDFLib/rdflib/pull/1706)
* Use the `property` built-in as a decorator
  [PR #1703](https://github.com/RDFLib/rdflib/pull/1703)
* Apply IdentifiedNode to Graph iterators
  [PR #1697](https://github.com/RDFLib/rdflib/pull/1697)
* Remove singly-used alias obviated by IdentifiedNode
  [PR #1695](https://github.com/RDFLib/rdflib/pull/1695)
* Unify plugin loading
  [PR #1694](https://github.com/RDFLib/rdflib/pull/1694)
* Rename black.toml to pyproject.toml
  [PR #1692](https://github.com/RDFLib/rdflib/pull/1692)
* Improved tox config
  [PR #1691](https://github.com/RDFLib/rdflib/pull/1691)
* Add isort
  [PR #1689](https://github.com/RDFLib/rdflib/pull/1689)
* Fix black
  [PR #1688](https://github.com/RDFLib/rdflib/pull/1688)
* Bind prefixes choices
  [PR #1686](https://github.com/RDFLib/rdflib/pull/1686)
* Fix turtle serialization of `rdf:type` in subject, object
  [PR #1684](https://github.com/RDFLib/rdflib/pull/1684)
* Add typing to rdflib.term
  [PR #1683](https://github.com/RDFLib/rdflib/pull/1683)
* Add a class diagram for terms.
  [PR #1682](https://github.com/RDFLib/rdflib/pull/1682)
* Add typing to rdflib.namespace
  [PR #1681](https://github.com/RDFLib/rdflib/pull/1681)
* Add IdentifiedNode abstract intermediary class
  [PR #1680](https://github.com/RDFLib/rdflib/pull/1680)
* Fix turtle serialization of PNames that contain brackets
  [PR #1678](https://github.com/RDFLib/rdflib/pull/1678)
* Add a test case for a prefix followed by dot in Turtle format
  [PR #1677](https://github.com/RDFLib/rdflib/pull/1677)
* Bump sphinx from 4.3.2 to 4.4.0
  [PR #1675](https://github.com/RDFLib/rdflib/pull/1675)
* pre-commit and pre-commit-ci
  [PR #1672](https://github.com/RDFLib/rdflib/pull/1672)
* Eliminate star import
  [PR #1667](https://github.com/RDFLib/rdflib/pull/1667)
* Fixed the handling of escape sequences in the ntriples and nquads parsers
  [PR #1663](https://github.com/RDFLib/rdflib/pull/1663)
* Remove narrow build detection
  [PR #1660](https://github.com/RDFLib/rdflib/pull/1660)
* Make unregister_custom_function idempotent
  [PR #1659](https://github.com/RDFLib/rdflib/pull/1659)
* Allow hext to participate in RDF format roundtripping
  [PR #1656](https://github.com/RDFLib/rdflib/pull/1656)
* change tests to use urn:example
  [PR #1654](https://github.com/RDFLib/rdflib/pull/1654)
* add nquads to recognised file extensions
  [PR #1653](https://github.com/RDFLib/rdflib/pull/1653)
* Don't update `SUFFIX_FORMAT_MAP` in `plugins/parsers/jsonld.py`
  [PR #1652](https://github.com/RDFLib/rdflib/pull/1652)
* Add Contributor Covenant Code of Conduct
  [PR #1651](https://github.com/RDFLib/rdflib/pull/1651)
* add test of ConjunctiveGraph operators
  [PR #1647](https://github.com/RDFLib/rdflib/pull/1647)
* added three tests to cover changes made by the pull request #1361
  [PR #1645](https://github.com/RDFLib/rdflib/pull/1645)
* Fixed and refactored roundtrip, n3_suite and nt_suite tests
  [PR #1644](https://github.com/RDFLib/rdflib/pull/1644)
* Allow parse of RDF from URL with all RDF Media Types
  [PR #1643](https://github.com/RDFLib/rdflib/pull/1643)
* Black rdflib except for rdflib/namespace/_GEO.py
  [PR #1642](https://github.com/RDFLib/rdflib/pull/1642)
* Remove `(TypeCheck|SubjectType|PredicateType|ObjectType)Error` and related
  [PR #1640](https://github.com/RDFLib/rdflib/pull/1640)
* Rename `test/triple_store.py` so pytest picks it up
  [PR #1639](https://github.com/RDFLib/rdflib/pull/1639)
* Convert translate_algebra tests to pytest
  [PR #1636](https://github.com/RDFLib/rdflib/pull/1636)
* Add some type annotations to JSON-LD code
  [PR #1634](https://github.com/RDFLib/rdflib/pull/1634)
* Add some typing for evaluation related functions in the SPARQL plugin.
  [PR #1633](https://github.com/RDFLib/rdflib/pull/1633)
* Add classifier for python 3.10
  [PR #1630](https://github.com/RDFLib/rdflib/pull/1630)
* Add tests for update method on `Graph(store="SPARQLStore")`
  [PR #1629](https://github.com/RDFLib/rdflib/pull/1629)
* Add __dir__ to DefinedNamespaceMeta.
  [PR #1626](https://github.com/RDFLib/rdflib/pull/1626)
* Add `version` to docker-compose config for tests
  [PR #1625](https://github.com/RDFLib/rdflib/pull/1625)
* Feature prepareupdate
  [PR #1624](https://github.com/RDFLib/rdflib/pull/1624)
* Fix issue1032 error on sparqlstore update
  [PR #1623](https://github.com/RDFLib/rdflib/pull/1623)
* Restore geosparql defined namespace
  [PR #1622](https://github.com/RDFLib/rdflib/pull/1622)
* Fix typing errors in tests
  [PR #1621](https://github.com/RDFLib/rdflib/pull/1621)
* Compile docs in GitHub Actions CI
  [PR #1620](https://github.com/RDFLib/rdflib/pull/1620)
* Scale down CI checks
  [PR #1619](https://github.com/RDFLib/rdflib/pull/1619)
* Revert error-raising change, enable Exception to be raised.
  [PR #1607](https://github.com/RDFLib/rdflib/pull/1607)
* Fix for issue430
  [PR #1590](https://github.com/RDFLib/rdflib/pull/1590)
* Fix for infixowl issues 1453 and 944
  [PR #1530](https://github.com/RDFLib/rdflib/pull/1530)
* Fix `self.line` typos in call to BadSyntax.
  [PR #1529](https://github.com/RDFLib/rdflib/pull/1529)
* Overdue restoration of functools total_order decorator.
  [PR #1528](https://github.com/RDFLib/rdflib/pull/1528)
* Remove deprecated
  [PR #1527](https://github.com/RDFLib/rdflib/pull/1527)
* Clean up documentation
  [PR #1525](https://github.com/RDFLib/rdflib/pull/1525)
* TypeErrors from Results do not propagate through list creation
  [PR #1523](https://github.com/RDFLib/rdflib/pull/1523)
* Add typing for parsers
  [PR #1522](https://github.com/RDFLib/rdflib/pull/1522)
* Fix for issue #837. Graph.[subjects|objects|predicates] optionally return uniques.
  [PR #1520](https://github.com/RDFLib/rdflib/pull/1520)
* Bump sphinx from 4.3.1 to 4.3.2
  [PR #1518](https://github.com/RDFLib/rdflib/pull/1518)
* Start support for mypy --strict
  [PR #1515](https://github.com/RDFLib/rdflib/pull/1515)
* Allow URLInputSource to get content-negotiation links from the Link headers
  [PR #1436](https://github.com/RDFLib/rdflib/pull/1436)
* Fix issue #936 HAVING clause with variable comparison not correctly evaluated
  [PR #1093](https://github.com/RDFLib/rdflib/pull/1093)

## 2021-12-20 RELEASE 6.1.1

Better testing and tidier code.

This is a semi-major release that:

* add support for Python 3.10
* updates the test suite to pytest (from nose) 
* tidies up a lot of continuous integration
* gets more tests tested, not skipped
* implements lots of mypy tests
* updates several parsers and serializers
  * supports the new HexTuples format!
* many bug fixes

This release contains many, many hours of updates from Iwan Aucamp, so thank you Iwan!

PRs merged since last release: 

* Update the guidelines for writing tests
  [PR #1517](https://github.com/RDFLib/rdflib/pull/1517)
* Updated tox config to run mypy in default environment
  [PR #1450](https://github.com/RDFLib/rdflib/pull/1450)
* Add type annotations to constructor parameters in Literal
  [PR #1498](https://github.com/RDFLib/rdflib/pull/1498)
* Increase fuseki start timeout from 15 to 30 seconds
  [PR #1516](https://github.com/RDFLib/rdflib/pull/1516)
* Forbid truthy values for lang when initializing Literal
  [PR #1494](https://github.com/RDFLib/rdflib/pull/1494)
* Add Py 3.10 to testing envs
  [PR #1473](https://github.com/RDFLib/rdflib/pull/1473)
* Add mypy to GitHub actions validate workflow
  [PR #1512](https://github.com/RDFLib/rdflib/pull/1512)
* Improve error messages from with-fuseki.sh
  [PR #1510](https://github.com/RDFLib/rdflib/pull/1510)
* Fix pipeline triggers
  [PR #1511](https://github.com/RDFLib/rdflib/pull/1511)
* Change python version used for mypy to 3.7
  [PR #1514](https://github.com/RDFLib/rdflib/pull/1514)
* Quench nt test userwarn
  [PR #1500](https://github.com/RDFLib/rdflib/pull/1500)
* Raise a more specific Exception when lang isn't valid
  [PR #1497](https://github.com/RDFLib/rdflib/pull/1497)
* Fix for issue893
  [PR #1504](https://github.com/RDFLib/rdflib/pull/1504)
* Fix for issue 893
  [PR #1501](https://github.com/RDFLib/rdflib/pull/1501)
* Re-make of nicholascar's “Concise Bounded Description” PR #968 ...
  [PR #1502](https://github.com/RDFLib/rdflib/pull/1502)
* Remove deprecated Statement class
  [PR #1496](https://github.com/RDFLib/rdflib/pull/1496)
* Fix BNode.skolemize() returning a URIRef instead of an RDFLibGenid.
  [PR #1493](https://github.com/RDFLib/rdflib/pull/1493)
* demo 980 resolution
  [PR #1495](https://github.com/RDFLib/rdflib/pull/1495)
* Hextuples Serializer
  [PR #1489](https://github.com/RDFLib/rdflib/pull/1489)
* Add bindings for rdflib namespaces. Import DCAM.
  [PR #1491](https://github.com/RDFLib/rdflib/pull/1491)
* fix for issue 1484 raised and solved by Graham Klyne:
  [PR #1490](https://github.com/RDFLib/rdflib/pull/1490)
* SDO HTTPS and DN creator script
  [PR #1485](https://github.com/RDFLib/rdflib/pull/1485)
* Fix typing of create_input_source
  [PR #1487](https://github.com/RDFLib/rdflib/pull/1487)
* guess_format() cater for JSON-LD files ending .json-ld
  [PR #1486](https://github.com/RDFLib/rdflib/pull/1486)
* Add GitHub actions workflow for validation
  [PR #1461](https://github.com/RDFLib/rdflib/pull/1461)
* Improved script for running with fuseki
  [PR #1476](https://github.com/RDFLib/rdflib/pull/1476)
* RFC: Add PythonInputSource to create py-based graphs
  [PR #1463](https://github.com/RDFLib/rdflib/pull/1463)
* Adapt for pytest and add back import of os in rdflib/parser.py
  [PR #1480](https://github.com/RDFLib/rdflib/pull/1480)
* Make the test pass on windows
  [PR #1478](https://github.com/RDFLib/rdflib/pull/1478)
* Add type hints
  [PR #1449](https://github.com/RDFLib/rdflib/pull/1449)
* Fix shield for CI status
  [PR #1474](https://github.com/RDFLib/rdflib/pull/1474)
* Fix test files with bare code
  [PR #1481](https://github.com/RDFLib/rdflib/pull/1481)
* Remove some remaining nosetest import
  [PR #1482](https://github.com/RDFLib/rdflib/pull/1482)
* Fix JSON-LD data import adds trailing slashes to IRIs (#1443)
  [PR #1456](https://github.com/RDFLib/rdflib/pull/1456)
* Iwana 20211114 t1305 pytestx
  [PR #1460](https://github.com/RDFLib/rdflib/pull/1460)
* Migrate from nosetest to pytest
  [PR #1452](https://github.com/RDFLib/rdflib/pull/1452)
* Add import of os
  [PR #1464](https://github.com/RDFLib/rdflib/pull/1464)
* replace pkg_resources with importlib.metadata
  [PR #1445](https://github.com/RDFLib/rdflib/pull/1445)
* A new Turtle serializer
  [PR #1425](https://github.com/RDFLib/rdflib/pull/1425)
* Fix typos discovered by codespell
  [PR #1446](https://github.com/RDFLib/rdflib/pull/1446)
* Use assertTrue instead of assert_ for python 3.11 compatibility.
  [PR #1448](https://github.com/RDFLib/rdflib/pull/1448)
* Undefined name: tmppath --> self.tmppath
  [PR #1438](https://github.com/RDFLib/rdflib/pull/1438)
* Fix Graph.parse URL handling on windows
  [PR #1441](https://github.com/RDFLib/rdflib/pull/1441)
* Make Store.namespaces an empty generator
  [PR #1432](https://github.com/RDFLib/rdflib/pull/1432)
* Export DCMITYPE
  [PR #1433](https://github.com/RDFLib/rdflib/pull/1433)

## 2021-12-20 RELEASE 6.1.0

A slightly messed-up release of what is now 6.1.1. Do not use!

## 2021-10-10 RELEASE 6.0.2

Minor release to add OWL.rational & OWL.real which are needed to allow the OWL-RL package to use only rdflib namespaces, not it's own versions.

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

## 2021-09-17 RELEASE 6.0.1

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

## 2021-07-20 RELEASE 6.0.0

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
* docs: fix simple typo, -> yield
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

## 2020-04-18 RELEASE 5.0.0

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

## 2020-04-04 RELEASE 5.0.0RC1

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

## 2017-01-29 RELEASE 4.2.2

This is a bug-fix release, and the last release in the 4.X.X series.

### Bug fixes:

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


### Enhancements:

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


### Cleanups:

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


### Testing improvements:

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


### Doc improvements:

* Update list of builtin serialisers in docstring
  [#621](https://github.com/RDFLib/rdflib/pull/621)
* Update reference to "Emulating container types"
  [#575](https://github.com/RDFLib/rdflib/issues/575)
  [#581](https://github.com/RDFLib/rdflib/pull/581)
  [#583](https://github.com/RDFLib/rdflib/pull/583)
  [#584](https://github.com/RDFLib/rdflib/pull/584)
* docs: clarify the use of an identifier when persisting a triplestore
  [#654](https://github.com/RDFLib/rdflib/pull/654)
* DOC: fix simple typo, -> unnamed
  [#562](https://github.com/RDFLib/rdflib/pull/562)

## 2015-08-12 RELEASE 4.2.1

This is a bug-fix release.

### Minor enhancements:

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

### Bug fixes:

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

### Testing improvements:

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

## 2015-02-19 RELEASE 4.2.0

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

### Minor enhancements & bugs fixed:

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

## 2014-04-15 RELEASE 4.1.2

This is a bug-fix release.

* Fixed unicode/str bug in py3 for rdfpipe
  [#375](https://github.com/RDFLib/rdflib/issues/375)

## 2014-03-03 RELEASE 4.1.1

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

## 2013-12-31 RELEASE 4.1

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

### Minor enhancements/bugs fixed:

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

## 2013-05-22 RELEASE 4.0.1

Following RDFLib tradition, some bugs snuck into the 4.0 release.
This is a bug-fixing release:

* the new URI validation caused lots of problems, but is
  necessary to avoid ''RDF injection'' vulnerabilities. In the
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

## 2013-05-16 RELEASE 4.0

This release includes several major changes:

* The new SPARQL 1.1 engine (rdflib-sparql) has been included in
  the core distribution. SPARQL 1.1 queries and updates should
  work out of the box.

  * SPARQL paths are exposed as operators on ```URIRefs```, these can
    then be be used with graph.triples and friends:

    ```python
    from rdflib import Graph, URIRef
    from rdflib.namespace import FOAF, RDFS
    
    g = Graph()
    bob = URIRef("...")
    cls = URIRef("...")
    
    # List names of friends of Bob:
    g.triples((bob, FOAF.knows/FOAF.name , None))

    # All super-classes:
    g.triples((cls, RDFS.subClassOf * '+', None))
    ```

      * a new ```graph.update``` method will apply SPARQL update statements

* Several RDF 1.1 features are available:
  * A new ```DataSet``` class
  * ```XMLLiteral``` and ```HTMLLiterals```
  * ```BNode``` (de)skolemization is supported through ```BNode.skolemize```,
    ```URIRef.de_skolemize```, ```Graph.skolemize``` and ```Graph.de_skolemize```

* Handled of Literal equality was split into lexical comparison
  (for normal ```==``` operator) and value space (using new ```Node.eq```
  methods). This introduces some slight backwards incompatible
  changes, but was necessary, as the old version had
  inconsistent hash and equality methods that could lead the
  literals not working correctly in dicts/sets.
  The new way is more in line with how SPARQL 1.1 works.
  For the full details, see:

  https://github.com/RDFLib/rdflib/wiki/Literal-reworking

* Iterating over ```QueryResults``` will generate ```ResultRow``` objects,
  these allow access to variable bindings as attributes or as a
  dict. I.e.

  ```py
  for row in g.query('select ... ') :
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


### Minor Changes:

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

## 2013-03-01 RELEASE 3.4

This release introduced new parsers for structured data in HTML.
In particular formats: hturtle, rdfa, mdata and an auto-detecting
html format were added.  Thanks to Ivan Herman for this!

This release includes a lot of admin maintentance - correct
dependencies for different python versions, etc.  Several py3 bugs
were also fixed.

This release drops python 2.4 compatibility - it was just getting
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

## 2012-10-10 RELEASE 3.2.3

Almost identical to 3.2.2
A stupid bug snuck into 3.2.2, and querying graphs were broken.

* Fixes broken querying ([#234](https://github.com/RDFLib/rdflib/issues/234))
* graph.transitiveClosure now works with loops ([#206](https://github.com/RDFLib/rdflib/issues/206))

## 2012-09-25 RELEASE 3.2.2

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

## 2012-04-24 RELEASE 3.2.1

This is mainly a maintenance release.

Changes:

* New setuptools entry points for query processors and results

* Literals constructed from other literals copy datatype/lang ([#188](https://github.com/RDFLib/rdflib/issues/188))
* Relative URIs are resolved incorrectly after redirects ([#130](https://github.com/RDFLib/rdflib/issues/130))
* Illegal prefixes in turtle output ([#161](https://github.com/RDFLib/rdflib/issues/161))
* Sleepcat store unstable prefixes ([#201](https://github.com/RDFLib/rdflib/issues/201))
* Consistent toPyton() for all node objects ([#174](https://github.com/RDFLib/rdflib/issues/174))
* Better random BNode ID in multi-thread environments ([#185](https://github.com/RDFLib/rdflib/issues/185))

## 2012-01-19 RELEASE 3.2.0

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
      Restored compatibility with Python 2.4
    * http://code.google.com/p/rdflib/issues/detail?id=158
  Reworking of Query result handling
    * http://code.google.com/p/rdflib/issues/detail?id=193
  generating xml:base attribute in RDF/XML output
* http://code.google.com/p/rdflib/issues/detail?id=180
      serialize(format="pretty-xml") fails on cyclic links

## 2011-03-17 RELEASE 3.1.0

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

## 2010-05-13 RELEASE 3.0.0

Working test suite with all tests passing.

Removed dependency on setuptools.

(Issue #43) Updated Package and Module Names to follow
conventions outlined in
http://www.python.org/dev/peps/pep-0008/

Removed SPARQL bits and non core plugins. They are mostly
moving to http://code.google.com/p/rdfextras/ at least until
they are stable.

Fixed datatype for Literal(True).

Fixed Literal to enforce constraint of having either a language
or datatype but not both.

Fixed Literal's repr.

Fixed to Graph Add/Sub/Mul opterators.

Upgraded RDFa parser to pyRdfa.

Upgraded N3 parser to the one from CWM.

Fixed unicode encoding issue involving N3Parser.

N3 serializer improvements.

Fixed HTTP content-negotiation

Fixed Store.namespaces method (which caused a few issues
depending on Store implementation being used.)

Fixed interoperability issue with plugin module.

Fixed use of Deprecated functionality.

## 2009-03-30 RELEASE 2.4.1

Fixed Literal comparison case involving Literal's with
datatypes of XSD.base64Binary.

Fixed case where XSD.date was matching before XSD.dateTime for
datetime instances.

Fixed jython interoperability issue (issue #53).

Fixed Literal repr to handle apostrophes correctly (issue #28).

Fixed Literal's repr to be consistent with its ```__init__``` (issue #33).

## 2007-04-04 RELEASE 2.4.0

Improved Literal comparison / equality

Sparql cleanup.

getLiteralValue now returns the Literal object instead of the
result of toPython().  Now that Literals override a good
coverage of comparison operators, they should be passed around
as first class objects in the SPARQL evaluation engine.

Added support for session bnodes re: sparql

Fixed prolog reduce/reduce conflict.  Added Py_None IncRefs
where they were being passed into Python method invocations
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

## 2006-10-15 RELEASE 2.3.3

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

## 2006-08-01 RELEASE 2.3.2

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

Changed Literal and URIRef instantiation to catch
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

## 2006-02-27 RELEASE 2.3.1

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

## 2005-12-23 RELEASE 2.3.0

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
rollbacks (also inefficient but provides the capability to
stores that don't support it natively). Implemented as a
wrapper that tracks a 'thread-safe' list of reversal
operations (for every add, track the remove call that reverts
the store, and vice versa). Upon store.rollback(), execute the
reverse operations. However, this doesn't guarantee
durability, since if the system fails before the rollbacks are
all executed, the store will remain in an invalid state, but
it provides Atomicity in the best case scenario.

## 2005-10-10 RELEASE 2.2.3

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

## 2005-09-10 RELEASE 2.2.2

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

## 2005-08-25 RELEASE 2.2.1

Fixed issue regarding Python2.3 compatibility.

Fixed minor issue with URIRef's absolute method.

## 2005-08-12 RELEASE 2.1.4

Added optional base argument to URIRef.

Fixed bug where load and parse had inconsistent behavior.

Added a FileInputSource.

Added skeleton sparql parser and test framework.

Included pyparsing (pyparsing.sourceforge.net) for sparql parsing.

Added attribute support to namespaces.

## 2005-06-28 RELEASE 2.1.3

Added Ivan's sparql-p implementation.

Literal is now picklable.

Added optional base argument to serialize methods about which to relativize.

Applied patch to remove some dependencies on Python 2.4
features.

Fixed BNode's n3 serialization bug (recently introduced).

Fixed a collections related bug.

## 2005-05-13 RELEASE 2.1.2

Added patch from Sidnei da Silva that adds a sqlobject based backend.

Fixed bug in PrettyXMLSerializer (rdf prefix decl was missing sometimes)

Fixed bug in RDF/XML parser where empty collections where
causing exceptions.

## 2005-05-01 RELEASE 2.1.1

Fixed a number of bugs relating to 2.0 backward compatibility.

Fixed split_uri to handle URIs with _ in them properly.

Fixed bug in RDF/XML handler's absolutize that would cause some URIRefs to end in ##

Added check_context to Graph.

Added patch the improves IOMemory implementation.

## 2005-04-12 RELEASE 2.1.0

Merged TripleStore and InformationStore into Graph.

Added plugin support (or at least cleaned up, made consistent the
plugin support that existed).

Added value and seq methods to Graph.

Renamed prefix_mapping to bind.

Added namespaces method that is a generator over all prefix,
namespace bindings.

Added notion of NamespaceManager.

Added couple new backends, IOMemory and ZODB.

## 2005-03-19 RELEASE 2.0.6

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

## 2005-01-08 RELEASE 2.0.5

Added publicID argument to Store's load method.

Added RDF and RDFS to top level rdflib package.

## 2004-10-14 RELEASE 2.0.4

Removed unfinished functionality.

Fixed bug where another prefix other than rdf was getting
defined for the rdf namespace (causing an assertion to fail).

Fixed bug in serializer where nodeIDs were not valid NCNames.

## 2004-04-21 RELEASE 2.0.3

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

## 2004-03-22 RELEASE 2.0.2

Improved performance of Identifier equality tests.

Added missing "from __future__ import generators" statements
needed to run on Python2.2.

Added alternative to shlib.move() if it isn't present.

Fixed bug that occurred when specifying a backend to
InformationStore's constructor.

Fixed bug recently introduced into InformationStore's remove
method.

## 2004-03-15 RELEASE 2.0.1

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

## 2004-03-10 RELEASE 2.0.0

Fixed a few bugs in the SleepyCatBackend multi process
concurrency support.

Removed rdflib.Resource

Changed remove to now take a triple pattern and removed
remove_triples method.

Added ```__iadd__``` method to Store in support of store +=
another_store.

## 2004-01-04 RELEASE 1.3.2

Added a serialization dispatcher.

Added format arg to save method.

Store now remembers prefix/namespace bindings.

Backends are now more pluggable

...

## 2003-10-14 RELEASE 1.3.1

Fixed bug in serializer where triples where only getting
serialized the first time.

Added type checking for contexts.

Fixed bug that caused comparisons with a Literal to fail when
the right hand side was not a string.

Added DB_INIT_CDB flag to SCBacked for supporting multiple
reader/single writer access

Changed rdf:RDF to be optional to conform with latest spec.

Fixed handling of XMLLiterals

## 2003-04-40 RELEASE 1.3.0

Removed bag_id support and added it to OLD_TERMS.

Added a double hash for keys in SCBacked.

Fixed _HTTPClient so that it no longer removes metadata about
a context right after it adds it.

Added a KDTreeStore and RedlandStore backends.

Added a StoreTester.

## 2003-02-28 RELEASE 1.2.4

Fixed bug in SCBackend where language and datatype information
where being ignored.

Fixed bug in transitive_subjects.

Updated some of the test cases that where not up to date.

async_load now adds more http header and error information to
the InformationStore.

## 2003-02-11 RELEASE 1.2.3

Fixed bug in load methods where relative URLs where not being
absolutized correctly on Windows.

Fixed serializer so that it throws an exception when trying to
serialize a graph with a predicate that can not be split.

## 2003-02-07 RELEASE 1.2.2

Added an exists method to the BackwardCompatibility mixin.

Added versions of remove, remove_triples and triples methods
to the BackwardCompatility mixin for TripleStores that take an
s, p, o as opposed to an (s, p, o).

## 2003-02-03 RELEASE 1.2.1

Added support for parsing XMLLiterals.

Added support for proper charmod checking (only works in
Python2.3).

Fixed remaining rdfcore test cases that where not passing.

Fixed windows bug in AbstractInformationStore's run method.

## 2003-01-02 RELEASE 1.2.0

Added systemID, line #, and column # to error messages.

BNode prefix is now composed of ascii_letters instead of letters.

Added a bsddb backed InformationStore.

Added an asynchronous load method, methods for scheduling context
updates, and a run method.

## 2002-12-16 RELEASE 1.1.5

Introduction of InformationStore, a TripleStore with the
addition of context support.

Resource ```__getitem__``` now returns object (no longer returns a
Resource for the object).

Fixed bug in parser that was introduced in last release
regaurding unqualified names.

## 2002-12-10 RELEASE 1.1.4

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

## 2002-12-03 RELEASE 1.1.3

BNodes now created with a more unique identifier so BNodes
from different sessions do not collide.

Added initial support for XML Literals (for now they are
parsed into Literals).

Resource is no longer a special kind of URIRef.

Resource no longer looks at range to determine default return
type for ```__getitem__```. Instead there is now a get(predicate, default)
method.

## 2002-11-21 RELEASE 1.1.2

Fixed Literal's ```__eq__``` method so that Literal('foo')=='foo' etc.

Fixed Resource's ```__setitem__``` method so that it does not raise
a dictionary changed size while iterating exception.

## 2002-11-09 RELEASE 1.1.1

Resource is now a special kind of URIRef

Resource's ```__getitem__``` now looks at rdfs:range to determine
return type in default case.

## 2002-11-05 RELEASE 1.1.0

### A new development branch

Cleaned up interface and promoted it to SIR: Simple Interface
for RDF.

Updated parser to use SAX2 interfaces instead of using expat directly.

Added BTreeTripleStore, a ZODB BTree TripleStore backend. And
a default pre-mixed TripleStore that uses it.

Synced with latest (Editor's draft) RDF/XML spec.

Added datatype support.

Cleaned up interfaces for load/parse: removed generate_path
from loadsave and renamed parse_URI to parse.

## 2002-10-08 RELEASE 0.9.6

### The end of a development branch

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

## 2002-08-06 RELEASE 0.9.5

Added support for rdf:parseType="Collection"

Added items generator for getting items in a Collection

Renamed rdflib.triple_store to rdflib.TripleStore to better follow
python style conventions.

Added an Identifier Class

Moved each node into its own Python module.

Added rdflib.util with a first and uniq function.

Added a little more to example.py

Removed generate_uri since we have BNodes now.

## 2002-07-29 RELEASE 0.9.4

Added support for proposed rdf:nodeID to both the parser and
serializer.

Reimplemented serializer which now nests things where
possible.

Added partial support for XML Literal parseTypes.

## 2002-07-16 RELEASE 0.9.3

Fixed bug where bNodes where being created for nested property
elements when they where not supposed to be.

Added lax mode that will convert rdf/xml files that contain bare
IDs etc. Also, lax mode will only report parse errors instead of
raising exceptions.

Added missing check for valid attribute names in the case of
production 5.18 of latest WD spec.

## 2002-07-05 RELEASE 0.9.2

Added missing constants for SUBPROPERTYOF, ISDEFINEDBY.

Added test case for running all of the rdf/xml test cases.

Reimplemented rdf/xml parser to conform to latest WD.

## 2002-06-10 RELEASE 0.9.1

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

## 2002-06-04 RELEASE 0.9.0

Initial release after being split from redfootlib.
