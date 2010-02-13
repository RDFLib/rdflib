#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
==========================
W3C RDFa Test Suite Runner
==========================

This test suite generates test functions with ``all_tests`` which runs the
``RDFaParser`` against the official RDFa testsuite (found via
``XHTML_RDFA_TEST_MANIFEST_URL``).

It is intended to be run by Nose (but can also be invoked as a script).

If files in "test/rdfa/w3c_rdfa_suite" are removed, the test module
automatically downloads them (to allow for "manual+automatic" update).
"""
from operator import attrgetter
import re
import os
from urllib2 import urlopen
from urllib import url2pathname

from rdflib.graph import Graph
from rdflib.namespace import Namespace, RDF
from rdflib.parser import create_input_source
from rdflib.plugins.parsers.rdfa import RDFaParser


DC = Namespace("http://purl.org/dc/elements/1.1/")
TEST = Namespace("http://www.w3.org/2006/03/test-description#")

XHTML_RDFA_TEST_MANIFEST_URL = ("http://www.w3.org/2006/07/SWD/RDFa/"
        "testsuite/xhtml1-testcases/rdfa-xhtml1-test-manifest.rdf")


class TestCase(object):
    def __init__(self, graph, tc_uri):
        val = lambda p: graph.value(tc_uri, p)
        self.number = int(re.search(r'/Test(\d+)$', tc_uri).group(1))
        self.title = val(DC.title)
        self.html_url = val(TEST.informationResourceInput)
        self.sparql_url = val(TEST.informationResourceResults)
        self.status = val(TEST.reviewStatus).split("#")[-1]
        self.expected = val(TEST.expectedResults) in (None, 'true')

    @classmethod
    def all(cls, graph):
        for tc_uri in graph.subjects(RDF.type, TEST.TestCase):
            yield cls(graph, tc_uri)


def get_tcs(manifest_url=XHTML_RDFA_TEST_MANIFEST_URL,
        status="approved"):
    graph = Graph().parse(cached_file(manifest_url), publicID=manifest_url)
    return sorted((tc for tc in TestCase.all(graph) if tc.status == status),
            key=attrgetter('number'))

def run_tc(tc):
    parser = RDFaParser()
    graph = Graph()
    source = create_input_source(cached_file(tc.html_url), publicID=tc.html_url)
    parser.parse(source, graph)
    sparql = open(cached_file(tc.sparql_url)).read()
    ok = verify_ask(sparql, graph, tc.expected)
    return ok, sparql, graph


def verify_ask(sparql, graph, expected):
    try:
        result = graph.query(sparql.decode('utf-8'))
        ok = result.serialize('python') == expected
    except: # TODO: parse failures are probably sparql processor bugs
        ok = False
    if ok:
        return ok
    # TODO: sparql bugs cause a bunch to fail (at least bnodes and xmlliterals)
    # .. extract N3 from ASK and compare graphs instead:
    from rdflib.compare import isomorphic
    for ask_graph in _sparql_to_graphs(sparql):
        if isomorphic(graph, ask_graph) == expected:
            return True
        #else: print ask_graph.serialize(format='nt')
    return False

def _sparql_to_graphs(sparql):
    # turn sparql into n3
    # try to turn bnode sparql into bnode n3
    # NOTE: this requires *all* FILTER tests to use isBlank!
    if re.search(r'(?i)isBlank', sparql):
        sparql = re.sub(r'(?im)^\s*FILTER.+ISBLANK.*$', '', sparql)
        sparql = re.sub(r'\?(\w+)', r'_:\1', sparql)
    # remove ASK block
    n3 = re.sub(r'(?s)ASK\s+WHERE\s*{(.*)}', r'\1', sparql)
    # split union into chunks
    n3chunks = [re.sub(r'(?s)\s*{(.*)}\s*', r'\1', block)
                for block in n3.split('UNION')]
    for chunk in n3chunks:
        yield Graph().parse(data=chunk, format='n3')


CACHE_DIR = os.path.join(os.path.dirname(__file__), "w3c_rdfa_testsuite")

def cached_file(url):
    fname = os.path.basename(url2pathname(url.split(':', 1)[1]))
    fpath = os.path.join(CACHE_DIR, fname)
    if not os.path.exists(fpath):
        f = open(fpath, 'w')
        try:
            f.write(urlopen(url).read())
        finally:
            f.close()
    return fpath


KNOWN_ISSUES = set([11, 92, 94, 100, 101, 102, 103, 114, 117])
KNOWN_ISSUES |= set([105, 106])


def all_tests(skip_known_issues=True):
    """
    Generator used to expose test functions. The Nose test runner use this.
    """
    for tc in get_tcs():
        label = "RDFa TC #%(number)s: %(title)s (%(status)s)"%vars(tc)
        urls = "[<%(html_url)s>, <%(sparql_url)s>]"%vars(tc)
        def do_test():
            ok, sparql, graph = run_tc(tc)
            if not ok:
                n3 = graph.serialize(format='nt')
                raise AssertionError(
                        "The SPARQL:\n%(sparql)s\nDid not match:\n%(n3)s"%vars())
        if skip_known_issues and tc.number in KNOWN_ISSUES:
            # NOTE: nose doesn't support attr-filtering on generated test funcs..
            #do_test.known_issue = True
            continue
        do_test.description = label
        do_test._source_urls = urls
        yield do_test,


def manual_run():
    errors, failed, count = 0, 0, 0
    for test, in all_tests(skip_known_issues=False):
        count += 1; print test.description,
        try:
            test(); print "PASSED"
        except AssertionError, e:
            failed += 1; print "****FAILED****", e;
        except Exception, e:
            errors += 1; print "****ERROR**** in %s" % test._source_urls, e
    print "Ran %(count)s tests. Failed: %(failed)s. Errors: %(errors)s."%vars()


if __name__ == '__main__':

    manual_run()


