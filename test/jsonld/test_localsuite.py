import os
from os import environ, chdir, getcwd, path as p
import json

import pytest

from rdflib.term import URIRef
from . import runner


TC_BASE = "http://rdflib.net/rdflib-jsonld/local-testsuite/"


testsuite_dir = p.join(p.abspath(p.dirname(__file__)), "local-suite")


def read_manifest():
    f = open(p.join(testsuite_dir, "manifest.jsonld"), "r")
    manifestdata = json.load(f)
    f.close()
    for test in manifestdata.get("sequence"):
        parts = test.get("input", "").split(".")[0].split("-")
        category, name, direction = parts
        inputpath = test.get("input")
        expectedpath = test.get("expect")
        context = test.get("context", False)
        options = test.get("option") or {}
        yield category, name, inputpath, expectedpath, context, options


def get_test_suite_cases():
    for cat, num, inputpath, expectedpath, context, options in read_manifest():
        if inputpath.endswith(".jsonld"):  # toRdf
            if expectedpath.endswith(".jsonld"):  # compact/expand/flatten
                func = runner.do_test_json
            else:  # toRdf
                func = runner.do_test_parser
        else:  # fromRdf
            func = runner.do_test_serializer
        rdf_test_uri = URIRef("{0}{1}-manifest.jsonld#t{2}".format(
            TC_BASE, cat, num
        ))
        yield rdf_test_uri, func, TC_BASE, cat, num, inputpath, expectedpath, context, options


@pytest.fixture(scope="module", autouse=True)
def testsuide_dir():
    old_cwd = getcwd()
    chdir(testsuite_dir)
    yield
    chdir(old_cwd)


@pytest.mark.parametrize(
    "rdf_test_uri, func, suite_base, cat, num, inputpath, expectedpath, context, options",
    get_test_suite_cases(),
)
def test_suite(rdf_test_uri: URIRef, func, suite_base, cat, num, inputpath, expectedpath, context, options):
    func(suite_base, cat, num, inputpath, expectedpath, context, options)
