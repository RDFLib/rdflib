from os import environ, chdir, getcwd, path as p
import json
from . import runner


TC_BASE = "https://w3c.github.io/json-ld-api/tests/toRdf/"


testsuite_dir = p.join(p.abspath(p.dirname(__file__)), "1.1")


unsupported_tests = ("frame", "normalize")
unsupported_tests += (
    "error",
    "remote",
)
unsupported_tests += ("flatten", "compact", "expand")
unsupported_tests += ("html",)
unsupported_tests += ("fromRdf",)  # The JSON-LD 1.1 enhancement applies to parsing only

known_bugs = (
    # TODO: Literal doesn't preserve representations
    "fromRdf/0002-in",
    # RDflib does not print Integer with scientific notation
    "toRdf/0035-in",
    # TODO: "http:g" should serialize to "http:g", not "//g"
    "toRdf/0120-in",
    "toRdf/0121-in",
    "toRdf/0122-in",
    "toRdf/0123-in",
    "toRdf/0124-in",
    "toRdf/0125-in",
    "toRdf/0126-in",
    # TODO: RDFLib collapses http://ab//de to http://ab/de
    "toRdf/0128-in",
    # TODO: RDFLib does not allow arbitrary "urn:ex:s307" as a URI in predicate place
    "toRdf/0130-in",
    "toRdf/0131-in",
    "toRdf/0132-in",
    # TODO: Odd context lookup bug with scoped context (v1.1 bug)
    "toRdf/c013-in",
    # Type with @context of null should fall back to @vocab (I think), not baseuri
    "toRdf/c014-in",
    # <http://example/typed-base#subject-reference-id> != <http://example/base-base#subject-reference-id>
    "toRdf/c015-in",
    # context null clears vocab from parent context?
    "toRdf/c018-in",
    # TODO: Bug with resolving relative context url from top-level context which is not doc_root
    "toRdf/c031-in",
    # TODO: Nested Contexts don't quite work properly yet
    "toRdf/c037-in",
    "toRdf/c038-in",
    # TODO: @direction doesn't quite work properly in this implementation
    "toRdf/di09-in",
    "toRdf/di10-in",
    "toRdf/di11-in",
    "toRdf/di12-in",
    # TODO: empty list inside a list is represented wrong?
    "toRdf/e004-in",
    # Same problem as 0002-in
    "toRdf/e061-in",
    # Trying to use BNode as predicate, RDFLIB doesn't support
    "toRdf/e075-in",
    # @id and @vocab in literal datatype expansion doesn't work
    "toRdf/e088-in",
    # TODO: relative-iri keeps . on end of IRI?
    "toRdf/e076-in",
    "toRdf/e089-in",
    "toRdf/e090-in",
    "toRdf/e091-in",
    "toRdf/e110-in",
    "toRdf/e129-in",
    "toRdf/e130-in",
    # TODO: Just broken expansion...
    "toRdf/e080-in",
    "toRdf/e092-in",
    "toRdf/e093-in",
    "toRdf/e094-in",
    "toRdf/e104-in",
    "toRdf/e108-in",
    # TODO: Odd result in list expansion
    "toRdf/e105-in",
    "toRdf/e107-in",
    # no expandContent option?
    "toRdf/e077-in",
    # TODO: Investigate:
    "toRdf/e111-in",
    "toRdf/e112-in",
    "toRdf/e119-in",
    "toRdf/e120-in",
    "toRdf/e122-in",
    # RDFLib cannot keep a colon on the end of a prefix uri
    "toRdf/e117-in",
    "toRdf/e118-in",
    # <ex:ns/> doesn't expand to <http://example.org/ns/>
    "toRdf/e124-in",
    # Similar to above?
    "toRdf/e125-in",
    # Recursive Inclusion triggered!
    "toRdf/e128-in",
    # JSON-native double representation
    "toRdf/js04-in",
    "toRdf/js10-in",
    # JSON character escaping
    "toRdf/js12-in",
    "toRdf/js13-in",
    # Broken list comprehension
    "toRdf/li05-in",
    "toRdf/li06-in",
    "toRdf/li07-in",
    "toRdf/li08-in",
    "toRdf/li09-in",
    "toRdf/li10-in",
    "toRdf/li11-in",
    "toRdf/li14-in",
    # Bad URI?
    "toRdf/li12-in",
    # cannot use property-index to add property to graph object?
    "toRdf/pi11-in",
    "toRdf/pr25-in",
    # Investigate property issues:
    "toRdf/pr38-in",
    "toRdf/pr39-in",
    "toRdf/pr40-in",
    # Negative zero representation?
    "toRdf/rt01-in",
    # Property scope with @propagate not working
    "toRdf/so06-in",
    # Expand string as value gives wrong number representation
    "toRdf/tn02-in",
    # TODO: Rdflib should silently reject bad predicate URIs
    "toRdf/wf02-in",
)

TC_BASE = "https://w3c.github.io/json-ld-api/tests/"
allow_lists_of_lists = True

SKIP_KNOWN_BUGS = True
SKIP_1_0_TESTS = True

testsuite_dir = environ.get("JSONLD_TESTSUITE") or p.join(
    p.abspath(p.dirname(__file__)), "1.1"
)
test_dir = p.join(testsuite_dir, "tests")
if not p.isdir(test_dir):  # layout of 1.1 testsuite
    test_dir = testsuite_dir
else:
    TC_BASE = "http://json-ld.org/test-suite/tests/"
    allow_lists_of_lists = False


def read_manifest(skiptests):
    f = open(p.join(testsuite_dir, "manifest.jsonld"), "r")
    manifestdata = json.load(f)
    f.close()
    # context = manifestdata.get('context')
    for m in manifestdata.get("sequence"):
        if any(token in m for token in skiptests):
            continue
        f = open(p.join(testsuite_dir, m), "r")
        md = json.load(f)
        f.close()
        for test in md.get("sequence"):
            parts = test.get("input", "").split(".")[0]
            cat_num, direction = parts.rsplit("-", 1)
            category, testnum = (
                cat_num.split("/") if "/" in cat_num else cat_num.split("-")
            )
            if (
                test.get("input", "").split(".")[0] in skiptests
                or category in skiptests
            ):
                pass
            else:
                inputpath = test.get("input")
                expectedpath = test.get("expect")
                expected_error = test.get("expect")  # TODO: verify error
                context = test.get("context", False)
                options = test.get("option") or {}
                if expectedpath:
                    yield category, testnum, inputpath, expectedpath, context, options


def test_suite():
    skiptests = unsupported_tests
    if SKIP_KNOWN_BUGS:
        skiptests += known_bugs
    old_cwd = getcwd()
    chdir(test_dir)
    try:
        for cat, num, inputpath, expectedpath, context, options in read_manifest(
            skiptests
        ):
            if options:
                if (
                    SKIP_1_0_TESTS
                    and "specVersion" in options
                    and str(options["specVersion"]).lower() == "json-ld-1.0"
                ):
                    # Skip the JSON v1.0 tests
                    continue
            if inputpath.endswith(".jsonld"):  # toRdf
                if expectedpath.endswith(".jsonld"):  # compact/expand/flatten
                    func = runner.do_test_json
                else:  # toRdf
                    func = runner.do_test_parser
            else:  # fromRdf
                func = runner.do_test_serializer
            yield func, TC_BASE, cat, num, inputpath, expectedpath, context, options
    finally:
        chdir(old_cwd)
