The `test-suite` directory is a partial *copy* of the official test suite available at <http://www.w3.org/2013/json-ld-tests/>. Do *not* add tests directly there, but follow the instructions provided at the preceding location.

To update this copy, first obtain a local copy of the json-ld-tests test-suite. Then copy the relevants parts of that directory into this test directory.

You can do so by first defining a `$JSONLD_TESTSUITE` environment variable set to the local copy of the test-suite directory. Then run:

    $ cp $JSONLD_TESTSUITE/*.jsonld test/test-suite/
    $ cp $JSONLD_TESTSUITE/tests/{toRdf,fromRdf}-*.* test/test-suite/tests/

