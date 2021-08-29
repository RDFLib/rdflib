import os
from os import environ, chdir, getcwd, path as p
import json
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


def test_suite():
    old_cwd = getcwd()
    chdir(testsuite_dir)
    try:
        for cat, num, inputpath, expectedpath, context, options in read_manifest():
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
