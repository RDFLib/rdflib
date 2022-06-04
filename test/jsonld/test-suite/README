Introduction
------------

The JSON-LD Test Suite is a set of tests that can
be used to verify JSON-LD Processor conformance to the set of specifications
that constitute JSON-LD. The goal of the suite is to provide an easy and
comprehensive JSON-LD testing solution for developers creating JSON-LD Processors.

Design
------

Tests are defined into _compact_, _expand_, _frame_, _normalize_, and _rdf_ sections:
* _compact_ tests have _input_, _expected_ and _context_ documents. The _expected_ results
  can be compared using JSON object comparison with the processor output.
* _expand_ tests have _input_ and _expected_ documents. The _expected_ results
  can be compared using JSON object comparison with the processor output.
* _frame_ tests have _input_, _frame_ and _expected_ documents. The _expected_ results
  can be compared using JSON object comparison with the processor output.
* _normalize_ tests have _input_ and _expected_ documents. The _expected_ results
  can be compared using string comparison with the processor output.
* _rdf_ tests have _input_ and _sparql_ documents. The results are tested
  by performing the RDF conversion and using this as the default document for an `ASK` query
  contained within the _sparql_ document using a SPARQL endpoint. The end result is a
  yes/no on whether the expected triples were extracted by the JSON-LD processor.


Contributing
------------

If you would like to contribute a new test or a fix to an existing test,
please follow these steps:

1. Notify the JSON-LD mailing list, public-linked-json@w3.org,
   that you will be creating a new test or fix and the purpose of the
   change.
2. Clone the git repository: git://github.com/json-ld/json-ld.org.git
3. Make your changes and submit them via github, or via a 'git format-patch'
   to the [JSON-LD mailing list](mailto:public-linked-json@w3.org).

Optionally, you can ask for direct access to the repository and may make
changes directly to the JSON-LD Test Suite source code. All updates to the test
suite go live on Digital Bazaar's JSON-LD Test Suite site within seconds of
committing changes to github via a WebHook call.

How to Add a Unit Test
----------------------

In order to add a unit test, you must follow these steps:

1. Pick a new unit test number. For example - 250. To be consistent, please use
   the next available unit test number.
2. Create a markup file in the tests/ directory with a .jsonld extension.
   For example: tests/rdf-250.jsonld
3. Create a SPARQL query file in the tests/ directory with a .jsonld or .sparql extension.
   For example: tests/rdf-250.sparql
4. Add your test to manifest.jsonld.

The test suite is designed to empower JSON-LD processor maintainers to create
and add tests as they see fit. This may mean that the test suite may become
unstable from time to time, but this approach has been taken so that the
long-term goal of having a comprehensive test suite for JSON-LD can be achieved
by the JSON-LD community.
