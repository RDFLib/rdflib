import json
from os import chdir, environ, getcwd
from os import path as p
from typing import Tuple

import pytest

import rdflib
from rdflib.term import URIRef

from . import runner

unsupported_tests: Tuple[str, ...] = ("frame", "normalize")
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


def get_test_suite_cases(skip_known_bugs=True):
    skiptests = unsupported_tests
    if skip_known_bugs:
        skiptests += known_bugs
    for cat, num, inputpath, expectedpath, context, options in read_manifest(skiptests):
        if inputpath.endswith(".jsonld"):  # toRdf
            if expectedpath.endswith(".jsonld"):  # compact/expand/flatten
                func = runner.do_test_json
            else:  # toRdf
                func = runner.do_test_parser
        else:  # fromRdf
            func = runner.do_test_serializer
        # func.description = "%s-%s-%s" % (group, case)
        rdf_test_uri = URIRef("{0}{1}-manifest.jsonld#t{2}".format(TC_BASE, cat, num))
        yield rdf_test_uri, func, TC_BASE, cat, num, inputpath, expectedpath, context, options


@pytest.fixture(scope="module", autouse=True)
def global_state():
    old_version = runner.DEFAULT_PARSER_VERSION
    runner.DEFAULT_PARSER_VERSION = 1.0
    default_allow = rdflib.plugins.parsers.jsonld.ALLOW_LISTS_OF_LISTS
    rdflib.plugins.parsers.jsonld.ALLOW_LISTS_OF_LISTS = allow_lists_of_lists
    old_cwd = getcwd()
    chdir(test_dir)
    yield
    rdflib.plugins.parsers.jsonld.ALLOW_LISTS_OF_LISTS = default_allow
    runner.DEFAULT_PARSER_VERSION = old_version
    chdir(old_cwd)


@pytest.mark.parametrize(
    "rdf_test_uri, func, suite_base, cat, num, inputpath, expectedpath, context, options",
    get_test_suite_cases(),
)
def test_suite(
    rdf_test_uri: URIRef,
    func,
    suite_base,
    cat,
    num,
    inputpath,
    expectedpath,
    context,
    options,
):
    func(suite_base, cat, num, inputpath, expectedpath, context, options)
