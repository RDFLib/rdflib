from __future__ import print_function
import sys

# Needed to pass
# http://www.w3.org/2009/sparql/docs/tests/data-sparql11/
#           syntax-update-2/manifest#syntax-update-other-01
sys.setrecursionlimit(6000)  # default is 1000


try:
    from collections import Counter
except:

    # cheap Counter impl for py 2.5
    # not a complete implementation - only good enough for the use here!
    from collections import defaultdict
    from operator import itemgetter

    class Counter(defaultdict):
        def __init__(self):
            defaultdict.__init__(self, int)

        def most_common(self, N):
            return [x[0] for x in sorted(self.items(),
                                         key=itemgetter(1),
                                         reverse=True)[:10]]


import datetime
import isodate


from rdflib import (
    Dataset, Graph, URIRef, BNode)
from rdflib.query import Result
from rdflib.compare import isomorphic

from rdflib.plugins import sparql as rdflib_sparql_module
from rdflib.plugins.sparql.algebra import (
    pprintAlgebra, translateQuery, translateUpdate)
from rdflib.plugins.sparql.parser import parseQuery, parseUpdate
from rdflib.plugins.sparql.results.rdfresults import RDFResultParser
from rdflib.plugins.sparql.update import evalUpdate

from rdflib.compat import decodeStringEscape, bopen
from six.moves.urllib.parse import urljoin
from six import BytesIO

from nose.tools import nottest, eq_
from nose import SkipTest


from .manifest import nose_tests, MF, UP
from .earl import report, add_test

def eq(a,b,msg):
    return eq_(a,b,msg+': (%r!=%r)'%(a,b))

def setFlags():
    import rdflib
    # Several tests rely on lexical form of literals being kept!
    rdflib.NORMALIZE_LITERALS = False

    # we need an explicit default graph
    rdflib_sparql_module.SPARQL_DEFAULT_GRAPH_UNION = False

    # we obviously need this
    rdflib.DAWG_LITERAL_COLLATION = True

def resetFlags():
    import rdflib
    # Several tests rely on lexical form of literals being kept!
    rdflib.NORMALIZE_LITERALS = True

    # we need an explicit default graph
    rdflib_sparql_module.SPARQL_DEFAULT_GRAPH_UNION = True

    # we obviously need this
    rdflib.DAWG_LITERAL_COLLATION = False


DEBUG_FAIL = True
DEBUG_FAIL = False

DEBUG_ERROR = True
DEBUG_ERROR = False

SPARQL10Tests = True
# SPARQL10Tests = False

SPARQL11Tests = True
# SPARQL11Tests=False

RDFLibTests = True

DETAILEDASSERT = True
# DETAILEDASSERT=False



NAME = None

fails = Counter()
errors = Counter()

failed_tests = []
error_tests = []


def bopen_read_close(fn):
    with bopen(fn) as f:
        return f.read()


try:
    with open("skiptests.list") as skip_tests_f:
        skiptests = dict([(URIRef(x.strip().split(
            "\t")[0]), x.strip().split("\t")[1]) for x in skip_tests_f])
except IOError:
    skiptests = set()


def _fmt(f):
    if f.endswith(".rdf"):
        return "xml"
    return "turtle"




def bindingsCompatible(a, b):

    """

    Are two binding-sets compatible.

    From the spec: http://www.w3.org/2009/sparql/docs/tests/#queryevaltests

    A SPARQL implementation passes a query evaluation test if the
    graph produced by evaluating the query against the RDF dataset
    (and encoding in the DAWG result set vocabulary, if necessary) is
    equivalent [RDF-CONCEPTS] to the graph named in the result (after
    encoding in the DAWG result set vocabulary, if necessary). Note
    that, solution order only is considered relevant, if the result is
    expressed in the test suite in the DAWG result set vocabulary,
    with explicit rs:index triples; otherwise solution order is
    considered irrelevant for passing. Equivalence can be tested by
    checking that the graphs are isomorphic and have identical IRI and
    literal nodes. Note that testing whether two result sets are
    isomorphic is simpler than full graph isomorphism. Iterating over
    rows in one set, finding a match with the other set, removing this
    pair, then making sure all rows are accounted for, achieves the
    same effect.
    """

    def rowCompatible(x, y):
        m = {}
        y = y.asdict()
        for v1, b1 in x.asdict().items():
            if v1 not in y:
                return False
            if isinstance(b1, BNode):
                if b1 in m:
                    if y[v1] != m[b1]:
                        return False
                else:
                    m[b1] = y[v1]
            else:
                 # if y[v1]!=b1:
                 #    return False
                try:
                    if y[v1].neq(b1):
                        return False
                except TypeError:
                    return False
        return True

    if not a:
        if b:
            return False
        return True

    x = next(iter(a))

    for y in b:
        if rowCompatible(x, y):
            if bindingsCompatible(a - set((x,)), b - set((y,))):
                return True

    return False


def pp_binding(solutions):
    """
    Pretty print a single binding - for less eye-strain when debugging
    """
    return "\n[" + ",\n\t".join("{" + ", ".join("%s:%s" % (
        x[0], x[1].n3()) for x in bindings.items()) + "}"
        for bindings in solutions) + "]\n"


@nottest
def update_test(t):

    # the update-eval tests refer to graphs on http://example.org
    rdflib_sparql_module.SPARQL_LOAD_GRAPHS = False

    uri, name, comment, data, graphdata, query, res, syntax = t

    if uri in skiptests:
        raise SkipTest()

    try:
        g = Dataset()

        if not res:
            if syntax:
                with bopen(query[7:]) as f:
                    translateUpdate(parseUpdate(f))
            else:
                try:
                    with bopen(query[7:]) as f:
                        translateUpdate(parseUpdate(f))
                    raise AssertionError("Query shouldn't have parsed!")
                except:
                    pass  # negative syntax test
            return

        resdata, resgraphdata = res

        # read input graphs
        if data:
            g.default_context.load(data, format=_fmt(data))

        if graphdata:
            for x, l in graphdata:
                g.load(x, publicID=URIRef(l), format=_fmt(x))

        with bopen(query[7:]) as f:
            req = translateUpdate(parseUpdate(f))
        evalUpdate(g, req)

        # read expected results
        resg = Dataset()
        if resdata:
            resg.default_context.load(resdata, format=_fmt(resdata))

        if resgraphdata:
            for x, l in resgraphdata:
                resg.load(x, publicID=URIRef(l), format=_fmt(x))

        eq(set(x.identifier for x in g.contexts() if x != g.default_context),
           set(x.identifier for x in resg.contexts()
               if x != resg.default_context), 'named graphs in datasets do not match')
        assert isomorphic(g.default_context, resg.default_context), \
            'Default graphs are not isomorphic'

        for x in g.contexts():
            if x == g.default_context:
                continue
            assert isomorphic(x, resg.get_context(x.identifier)), \
                "Graphs with ID %s are not isomorphic" % x.identifier

    except Exception as e:

        if isinstance(e, AssertionError):
            failed_tests.append(uri)
            fails[str(e)] += 1
        else:
            error_tests.append(uri)
            errors[str(e)] += 1

        if DEBUG_ERROR and not isinstance(e, AssertionError) or DEBUG_FAIL:
            print("======================================")
            print(uri)
            print(name)
            print(comment)

            if not res:
                if syntax:
                    print("Positive syntax test")
                else:
                    print("Negative syntax test")

            if data:
                print("----------------- DATA --------------------")
                print(">>>", data)
                print(bopen_read_close(data[7:]))
            if graphdata:
                print("----------------- GRAPHDATA --------------------")
                for x, l in graphdata:
                    print(">>>", x, l)
                    print(bopen_read_close(x[7:]))

            print("----------------- Request -------------------")
            print(">>>", query)
            print(bopen_read_close(query[7:]))

            if res:
                if resdata:
                    print("----------------- RES DATA --------------------")
                    print(">>>", resdata)
                    print(bopen_read_close(resdata[7:]))
                if resgraphdata:
                    print("----------------- RES GRAPHDATA -------------------")
                    for x, l in resgraphdata:
                        print(">>>", x, l)
                        print(bopen_read_close(x[7:]))

            print("------------- MY RESULT ----------")
            print(g.serialize(format='trig'))

            try:
                pq = translateUpdate(parseUpdate(bopen_read_close(query[7:])))
                print("----------------- Parsed ------------------")
                pprintAlgebra(pq)
                # print pq
            except:
                print("(parser error)")

            print(decodeStringEscape(str(e)))

            import pdb
            pdb.post_mortem(sys.exc_info()[2])
        raise


@nottest  # gets called by generator
def query_test(t):
    uri, name, comment, data, graphdata, query, resfile, syntax = t

    # the query-eval tests refer to graphs to load by resolvable filenames
    rdflib_sparql_module.SPARQL_LOAD_GRAPHS = True

    if uri in skiptests:
        raise SkipTest()

    def skip(reason='(none)'):
        print("Skipping %s from now on." % uri)
        with bopen("skiptests.list", "a") as f:
            f.write("%s\t%s\n" % (uri, reason))

    try:
        g = Dataset()
        if data:
            g.default_context.load(data, format=_fmt(data))

        if graphdata:
            for x in graphdata:
                g.load(x, format=_fmt(x))

        if not resfile:
            # no result - syntax test

            if syntax:
                translateQuery(parseQuery(
                    bopen_read_close(query[7:])), base=urljoin(query, '.'))
            else:
                # negative syntax test
                try:
                    translateQuery(parseQuery(
                        bopen_read_close(query[7:])), base=urljoin(query, '.'))

                    assert False, 'Query should not have parsed!'
                except:
                    pass  # it's fine - the query should not parse
            return

        # eval test - carry out query
        res2 = g.query(bopen_read_close(query[7:]), base=urljoin(query, '.'))

        if resfile.endswith('ttl'):
            resg = Graph()
            resg.load(resfile, format='turtle', publicID=resfile)
            res = RDFResultParser().parse(resg)
        elif resfile.endswith('rdf'):
            resg = Graph()
            resg.load(resfile, publicID=resfile)
            res = RDFResultParser().parse(resg)
        else:
            with bopen(resfile[7:]) as f:
                if resfile.endswith('srj'):
                    res = Result.parse(f, format='json')
                elif resfile.endswith('tsv'):
                    res = Result.parse(f, format='tsv')

                elif resfile.endswith('csv'):
                    res = Result.parse(f, format='csv')

                    # CSV is lossy, round-trip our own resultset to
                    # lose the same info :)

                    # write bytes, read strings...
                    s = BytesIO()
                    res2.serialize(s, format='csv')
                    s.seek(0)
                    res2 = Result.parse(s, format='csv')
                    s.close()

                else:
                    res = Result.parse(f, format='xml')

        if not DETAILEDASSERT:
            eq(res.type, res2.type, 'Types do not match')
            if res.type == 'SELECT':
                eq(set(res.vars), set(res2.vars), 'Vars do not match')
                comp = bindingsCompatible(
                    set(res),
                    set(res2)
                )
                assert comp, 'Bindings do not match'
            elif res.type == 'ASK':
                eq(res.askAnswer, res2.askAnswer, 'Ask answer does not match')
            elif res.type in ('DESCRIBE', 'CONSTRUCT'):
                assert isomorphic(
                    res.graph, res2.graph), 'graphs are not isomorphic!'
            else:
                raise Exception('Unknown result type: %s' % res.type)
        else:
            eq(res.type, res2.type,
               'Types do not match: %r != %r' % (res.type, res2.type))
            if res.type == 'SELECT':
                eq(set(res.vars),
                   set(res2.vars), 'Vars do not match: %r != %r' % (
                   set(res.vars), set(res2.vars)))
                assert bindingsCompatible(
                    set(res),
                    set(res2)
                ), 'Bindings do not match: \nexpected:\n%s\n!=\ngot:\n%s' % (
                    res.serialize(format='txt', namespace_manager=g.namespace_manager),
                    res2.serialize(format='txt', namespace_manager=g.namespace_manager))
            elif res.type == 'ASK':
                eq(res.askAnswer,
                   res2.askAnswer, "Ask answer does not match: %r != %r" % (
                   res.askAnswer, res2.askAnswer))
            elif res.type in ('DESCRIBE', 'CONSTRUCT'):
                assert isomorphic(
                    res.graph, res2.graph), 'graphs are not isomorphic!'
            else:
                raise Exception('Unknown result type: %s' % res.type)

    except Exception as e:

        if isinstance(e, AssertionError):
            failed_tests.append(uri)
            fails[str(e)] += 1
        else:
            error_tests.append(uri)
            errors[str(e)] += 1

        if DEBUG_ERROR and not isinstance(e, AssertionError) or DEBUG_FAIL:
            print("======================================")
            print(uri)
            print(name)
            print(comment)

            if not resfile:
                if syntax:
                    print("Positive syntax test")
                else:
                    print("Negative syntax test")

            if data:
                print("----------------- DATA --------------------")
                print(">>>", data)
                print(bopen_read_close(data[7:]))
            if graphdata:
                print("----------------- GRAPHDATA --------------------")
                for x in graphdata:
                    print(">>>", x)
                    print(bopen_read_close(x[7:]))

            print("----------------- Query -------------------")
            print(">>>", query)
            print(bopen_read_close(query[7:]))
            if resfile:
                print("----------------- Res -------------------")
                print(">>>", resfile)
                print(bopen_read_close(resfile[7:]))

            try:
                pq = parseQuery(bopen_read_close(query[7:]))
                print("----------------- Parsed ------------------")
                pprintAlgebra(translateQuery(pq, base=urljoin(query, '.')))
            except:
                print("(parser error)")

            print(decodeStringEscape(str(e)))

            import pdb
            pdb.post_mortem(sys.exc_info()[2])
            # pdb.set_trace()
            # nose.tools.set_trace()
        raise


testers = {
    UP.UpdateEvaluationTest: update_test,
    MF.UpdateEvaluationTest: update_test,
    MF.PositiveUpdateSyntaxTest11: update_test,
    MF.NegativeUpdateSyntaxTest11: update_test,

    MF.QueryEvaluationTest: query_test,
    MF.NegativeSyntaxTest11: query_test,
    MF.PositiveSyntaxTest11: query_test,
    MF.CSVResultFormatTest: query_test,
}


def test_dawg():

    setFlags()

    if SPARQL10Tests:
        for t in nose_tests(testers, "test/DAWG/data-r2/manifest-evaluation.ttl"):
            yield t

    if SPARQL11Tests:
        for t in nose_tests(testers, "test/DAWG/data-sparql11/manifest-all.ttl"):
            yield t

    if RDFLibTests:
        for t in nose_tests(testers, "test/DAWG/rdflib/manifest.ttl"):
            yield t


    resetFlags()



if __name__ == '__main__':

    import sys
    import time
    start = time.time()
    if len(sys.argv) > 1:
        NAME = sys.argv[1]
        DEBUG_FAIL = True
    i = 0
    success = 0

    skip = 0

    for _type, t in test_dawg():


        if NAME and not str(t[0]).startswith(NAME):
            continue
        i += 1
        try:

            _type(t)

            add_test(t[0], "passed")
            success += 1

        except SkipTest as e:
            msg = skiptests.get(t[0], e.args)
            add_test(t[0], "untested", msg)
            print("skipping %s - %s" % (t[0], msg))
            skip += 1

        except KeyboardInterrupt:
            raise
        except AssertionError:
            add_test(t[0], "failed")
        except:
            add_test(t[0], "failed", "error")
            import traceback
            traceback.print_exc()
            sys.stderr.write("%s\n" % t[0])

    print("\n----------------------------------------------------\n")
    print("Failed tests:")
    for failed in failed_tests:
        print(failed)

    print("\n----------------------------------------------------\n")
    print("Error tests:")
    for error in error_tests:
        print(error)

    print("\n----------------------------------------------------\n")

    print("Most common fails:")
    for failed in fails.most_common(10):
        failed = str(failed)
        print(failed[:450] + (failed[450:] and "..."))

    print("\n----------------------------------------------------\n")

    if errors:
        print("Most common errors:")
        for error in errors.most_common(10):
            print(error)
    else:
        print("(no errors!)")

    f_sum = sum(fails.values())
    e_sum = sum(errors.values())

    if success + f_sum + e_sum + skip != i:
        print("(Something is wrong, %d!=%d)" % (
            success + f_sum + e_sum + skip, i))

    print("\n%d tests, %d passed, %d failed, %d errors, \
          %d skipped (%.2f%% success)" % (
        i, success, f_sum, e_sum, skip, 100. * success / i))
    print("Took %.2fs" % (time.time() - start))

    if not NAME:

        now = isodate.datetime_isoformat(datetime.datetime.utcnow())

        with open("testruns.txt", "a") as tf:
            tf.write(
                "%s\n%d tests, %d passed, %d failed, %d errors, %d "
                "skipped (%.2f%% success)\n\n" % (
                    now, i, success, f_sum, e_sum, skip, 100. * success / i)
            )

        earl_report = 'test_reports/rdflib_sparql-%s.ttl' % now

        report.serialize(earl_report, format='n3')
        report.serialize('test_reports/rdflib_sparql-latest.ttl', format='n3')
        print("Wrote EARL-report to '%s'" % earl_report)
