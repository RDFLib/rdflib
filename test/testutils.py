from __future__ import print_function

import sys
import isodate
import datetime

from traceback import print_exc
from nose import SkipTest
from .earl import add_test, report

from rdflib import BNode, Graph, ConjunctiveGraph


# TODO: make an introspective version (like this one) of
# rdflib.graphutils.isomorphic and use instead.
def crapCompare(g1, g2):
    """A really crappy way to 'check' if two graphs are equal. It ignores blank
    nodes completely and ignores subgraphs."""
    if len(g1) != len(g2):
        raise Exception("Graphs dont have same length")
    for t in g1:
        s = _no_blank(t[0])
        o = _no_blank(t[2])
        if not (s, t[1] ,o) in g2:
            e = "(%s, %s, %s) is not in both graphs!"%(s, t[1], o)
            raise Exception(e)
def _no_blank(node):
    if isinstance(node, BNode): return None
    if isinstance(node, Graph):
        return None #node._Graph__identifier = _SQUASHED_NODE
    return node

def check_serialize_parse(fpath, infmt, testfmt, verbose=False):
    g = ConjunctiveGraph()
    _parse_or_report(verbose, g, fpath, format=infmt)
    if verbose:
        for t in g:
            print(t)
        print("========================================")
        print("Parsed OK!")
    s = g.serialize(format=testfmt)
    if verbose:
        print(s)
    g2 = ConjunctiveGraph()
    _parse_or_report(verbose, g2, data=s, format=testfmt)
    if verbose:
        print(g2.serialize())
    crapCompare(g,g2)


def _parse_or_report(verbose, graph, *args, **kwargs):
    try:
        graph.parse(*args, **kwargs)
    except:
        if verbose:
            print("========================================")
            print("Error in parsing serialization:")
            print(args, kwargs)
        raise


def nose_tst_earl_report(generator, earl_report_name=None):
    from optparse import OptionParser
    p = OptionParser()
    (options, args) = p.parse_args()

    skip = 0
    tests = 0
    success = 0

    for t in generator(args):
        tests += 1
        print('Running ', t[1].uri)
        try:
            t[0](t[1])
            add_test(t[1].uri, "passed")
            success += 1
        except SkipTest as e:
            add_test(t[1].uri, "untested", e.message)
            print("skipping %s - %s" % (t[1].uri, e.message))
            skip += 1

        except KeyboardInterrupt:
            raise
        except AssertionError:
            add_test(t[1].uri, "failed")
        except:
            add_test(t[1].uri, "failed", "error")
            print_exc()
            sys.stderr.write("%s\n" % t[1].uri)

    print("Ran %d tests, %d skipped, %d failed. "%(tests, skip, tests-skip-success))
    if earl_report_name:
        now = isodate.datetime_isoformat(datetime.datetime.utcnow())
        earl_report = 'test_reports/%s-%s.ttl' % (earl_report_name, now)

        report.serialize(earl_report, format='n3')
        report.serialize('test_reports/%s-latest.ttl'%earl_report_name, format='n3')
        print("Wrote EARL-report to '%s'" % earl_report)
