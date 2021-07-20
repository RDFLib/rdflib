from os import environ, chdir, getcwd, path as p
import json
import rdflib
import rdflib.plugins.parsers.jsonld as parser
from . import runner


unsupported_tests = ("frame", "normalize")
unsupported_tests += (
    "error",
    "remote",
)
unsupported_tests += ("flatten", "compact", "expand")
unsupported_tests += ("html",)

known_bugs = (
    # invalid nquads (bnode as predicate)
    # "toRdf-0078-in", "toRdf-0108-in",
    # TODO: Literal doesn't preserve representations
    "fromRdf-0002-in",
    "toRdf-0035-in",
    "toRdf-0101-in",  # Literal doesn't preserve representations
    "fromRdf-0008-in",  # TODO: needs to disallow outer lists-of-lists
    # # "toRdf-0091-in", # TODO: multiple aliases version?
    # # TODO: check that these are corrected in 1.1 testsuite (1.0-deprecated prefix forms)
    "toRdf-0088-in",
    "toRdf-0118-in",  # RDFLib cannot do generalized graphs
)

TC_BASE = "https://w3c.github.io/json-ld-api/tests/"
allow_lists_of_lists = True


testsuite_dir = environ.get("JSONLD_TESTSUITE") or p.join(
    p.abspath(p.dirname(__file__)), "test-suite"
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


def test_suite(skip_known_bugs=True):
    default_allow = rdflib.plugins.parsers.jsonld.ALLOW_LISTS_OF_LISTS
    rdflib.plugins.parsers.jsonld.ALLOW_LISTS_OF_LISTS = allow_lists_of_lists
    skiptests = unsupported_tests
    if skip_known_bugs:
        skiptests += known_bugs
    old_cwd = getcwd()
    chdir(test_dir)
    runner.DEFAULT_PARSER_VERSION = 1.0
    try:
        for cat, num, inputpath, expectedpath, context, options in read_manifest(
            skiptests
        ):
            if inputpath.endswith(".jsonld"):  # toRdf
                if expectedpath.endswith(".jsonld"):  # compact/expand/flatten
                    func = runner.do_test_json
                else:  # toRdf
                    func = runner.do_test_parser
            else:  # fromRdf
                func = runner.do_test_serializer
            # func.description = "%s-%s-%s" % (group, case)
            yield func, TC_BASE, cat, num, inputpath, expectedpath, context, options
    finally:
        rdflib.plugins.parsers.jsonld.ALLOW_LISTS_OF_LISTS = default_allow
        chdir(old_cwd)


if __name__ == "__main__":
    import sys
    from rdflib import *
    from datetime import datetime

    EARL = Namespace("http://www.w3.org/ns/earl#")
    DC = Namespace("http://purl.org/dc/terms/")
    FOAF = Namespace("http://xmlns.com/foaf/0.1/")
    DOAP = Namespace("http://usefulinc.com/ns/doap#")

    rdflib_jsonld_page = "https://github.com/RDFLib/rdflib-jsonld"
    rdflib_jsonld = URIRef(rdflib_jsonld_page + "#it")

    args = sys.argv[1:]
    asserter = URIRef(args.pop(0)) if args else None
    asserter_name = Literal(args.pop(0)) if args else None

    graph = Graph()

    graph.parse(
        data="""
        @prefix earl: <{EARL}> .
        @prefix dc: <{DC}> .
        @prefix foaf: <{FOAF}> .
        @prefix doap: <{DOAP}> .

        <{rdflib_jsonld}> a doap:Project, earl:TestSubject, earl:Software ;
            doap:homepage <{rdflib_jsonld_page}> ;
            doap:name "RDFLib-JSONLD" ;
            doap:programming-language "Python" ;
            doap:title "RDFLib plugin for JSON-LD " .
    """.format(
            **vars()
        ),
        format="turtle",
    )

    if asserter_name:
        graph.add((asserter, RDF.type, FOAF.Person))
        graph.add((asserter, FOAF.name, asserter_name))
        graph.add((rdflib_jsonld, DOAP.developer, asserter))

    for args in test_suite(skip_known_bugs=False):
        try:
            args[0](*args[1:])
            success = True
        except AssertionError:
            success = False
        assertion = graph.resource(BNode())
        assertion.add(RDF.type, EARL.Assertion)
        assertion.add(EARL.mode, EARL.automatic)
        if asserter:
            assertion.add(EARL.assertedBy, asserter)
        assertion.add(EARL.subject, rdflib_jsonld)
        assertion.add(
            EARL.test,
            URIRef(
                "http://json-ld.org/test-suite/tests/{1}-manifest.jsonld#t{2}".format(
                    *args
                )
            ),
        )
        result = graph.resource(BNode())
        assertion.add(EARL.result, result)
        result.add(RDF.type, EARL.TestResult)
        result.add(DC.date, Literal(datetime.utcnow()))
        result.add(EARL.outcome, EARL.passed if success else EARL.failed)

    graph.serialize(destination=sys.stdout)
