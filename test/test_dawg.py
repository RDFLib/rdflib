from __future__ import print_function

import os
from pathlib import PurePath
import sys
from io import TextIOWrapper

# Needed to pass
# http://www.w3.org/2009/sparql/docs/tests/data-sparql11/
#           syntax-update-2/manifest#syntax-update-other-01
from test import TEST_DIR
from test.manifest import UP, MF, RDFTest, ResultType, read_manifest
import pytest

from test.testutils import file_uri_to_path

sys.setrecursionlimit(6000)  # default is 1000


from collections import Counter


import datetime
import isodate
import typing
from typing import Dict, Callable, List, Optional, Tuple, cast


from rdflib import Dataset, Graph, URIRef, BNode
from rdflib.term import Identifier, Node
from rdflib.query import Result
from rdflib.compare import isomorphic

from rdflib.plugins import sparql as rdflib_sparql_module
from rdflib.plugins.sparql.algebra import pprintAlgebra, translateQuery, translateUpdate
from rdflib.plugins.sparql.parser import parseQuery, parseUpdate
from rdflib.plugins.sparql.results.rdfresults import RDFResultParser
from rdflib.plugins.sparql.update import evalUpdate

from rdflib.compat import decodeStringEscape, bopen
from urllib.parse import urljoin
from io import BytesIO


def eq(a, b, msg):
    # return eq_(a, b, msg + ": (%r!=%r)" % (a, b))
    assert a == b, msg + ": (%r!=%r)" % (a, b)


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

fails: typing.Counter[str] = Counter()
errors: typing.Counter[str] = Counter()

failed_tests = []
error_tests = []


def bopen_read_close(fn):
    with bopen(fn) as f:
        return f.read()


try:
    with open("skiptests.list") as skip_tests_f:
        skiptests = dict(
            [
                (URIRef(x.strip().split("\t")[0]), x.strip().split("\t")[1])
                for x in skip_tests_f
            ]
        )
except IOError:
    skiptests = dict()


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
    return (
        "\n["
        + ",\n\t".join(
            "{" + ", ".join("%s:%s" % (x[0], x[1].n3()) for x in bindings.items()) + "}"
            for bindings in solutions
        )
        + "]\n"
    )


def update_test(t: RDFTest):

    # the update-eval tests refer to graphs on http://example.org
    rdflib_sparql_module.SPARQL_LOAD_GRAPHS = False

    uri, name, comment, data, graphdata, query, res, syntax = t
    # These casts are here because the RDFTest type is not sufficently
    # expressive to capture the two different flavors of tests.
    res = cast(Optional[ResultType], res)
    graphdata = cast(Optional[List[Tuple[Identifier, Identifier]]], graphdata)

    query_path: PurePath = file_uri_to_path(query)

    if uri in skiptests:
        pytest.skip()

    try:
        g = Dataset()

        if not res:
            if syntax:
                with bopen(query_path) as f:
                    translateUpdate(parseUpdate(f))
            else:
                try:
                    with bopen(query_path) as f:
                        translateUpdate(parseUpdate(f))
                    raise AssertionError("Query shouldn't have parsed!")
                except:
                    pass  # negative syntax test
            return

        res = cast(ResultType, res)
        resdata: Identifier
        resgraphdata: List[Tuple[Identifier, Identifier]]
        resdata, resgraphdata = res  # type: ignore[assignment]

        # read input graphs
        if data:
            g.default_context.parse(data, format=_fmt(data))

        if graphdata:
            for x, l in graphdata:
                g.parse(x, publicID=URIRef(l), format=_fmt(x))

        with bopen(query_path) as f:
            req = translateUpdate(parseUpdate(f))
        evalUpdate(g, req)

        # read expected results
        resg = Dataset()
        if resdata:
            resg.default_context.parse(resdata, format=_fmt(resdata))

        if resgraphdata:
            for x, l in resgraphdata:
                resg.parse(x, publicID=URIRef(l), format=_fmt(x))

        eq(
            set(ctx.identifier for ctx in g.contexts() if ctx != g.default_context),
            set(
                ctx.identifier for ctx in resg.contexts() if ctx != resg.default_context
            ),
            "named graphs in datasets do not match",
        )
        assert isomorphic(
            g.default_context, resg.default_context
        ), "Default graphs are not isomorphic"

        for ctx in g.contexts():
            if ctx == g.default_context:
                continue
            assert isomorphic(ctx, resg.get_context(ctx.identifier)), (
                "Graphs with ID %s are not isomorphic" % ctx.identifier
            )

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
                data_path: PurePath = file_uri_to_path(data)
                print(bopen_read_close(data_path))
            if graphdata:
                print("----------------- GRAPHDATA --------------------")
                for x, l in graphdata:
                    print(">>>", x, l)
                    x_path: PurePath = file_uri_to_path(x)
                    print(bopen_read_close(x_path))

            print("----------------- Request -------------------")
            print(">>>", query)
            print(bopen_read_close(query_path))

            if res:
                if resdata:
                    print("----------------- RES DATA --------------------")
                    print(">>>", resdata)
                    resdata_path: PurePath = file_uri_to_path(resdata)
                    print(bopen_read_close(resdata_path))
                if resgraphdata:
                    print("----------------- RES GRAPHDATA -------------------")
                    for x, l in resgraphdata:
                        print(">>>", x, l)
                        x_path = file_uri_to_path(x)
                        print(bopen_read_close(x_path))

            print("------------- MY RESULT ----------")
            print(g.serialize(format="trig"))

            try:
                pq = translateUpdate(parseUpdate(bopen_read_close(query_path)))
                print("----------------- Parsed ------------------")
                pprintAlgebra(pq)
                # print pq
            except:
                print("(parser error)")

            print(decodeStringEscape(str(e)))

            import pdb

            pdb.post_mortem(sys.exc_info()[2])
        raise


def query_test(t: RDFTest):
    uri, name, comment, data, graphdata, query, resfile, syntax = t

    # These casts are here because the RDFTest type is not sufficently
    # expressive to capture the two different flavors of tests.
    graphdata = cast(Optional[List[Identifier]], graphdata)
    resfile = cast(Optional[Identifier], resfile)

    # the query-eval tests refer to graphs to load by resolvable filenames
    rdflib_sparql_module.SPARQL_LOAD_GRAPHS = True

    query_path: PurePath = file_uri_to_path(query)

    resfile_path = file_uri_to_path(resfile) if resfile else None

    if uri in skiptests:
        pytest.skip()

    def skip(reason="(none)"):
        print("Skipping %s from now on." % uri)
        with bopen("skiptests.list", "a") as f:
            f.write("%s\t%s\n" % (uri, reason))

    try:
        g = Dataset()
        if data:
            g.default_context.parse(data, format=_fmt(data))

        if graphdata:
            for x in graphdata:
                g.parse(x, format=_fmt(x))

        if not resfile:
            # no result - syntax test

            if syntax:
                translateQuery(
                    parseQuery(bopen_read_close(query_path)), base=urljoin(query, ".")
                )
            else:
                # negative syntax test
                try:
                    translateQuery(
                        parseQuery(bopen_read_close(query_path)),
                        base=urljoin(query, "."),
                    )

                    assert False, "Query should not have parsed!"
                except:
                    pass  # it's fine - the query should not parse
            return

        # eval test - carry out query
        res2 = g.query(bopen_read_close(query_path), base=urljoin(query, "."))

        if resfile.endswith("ttl"):
            resg = Graph()
            resg.parse(resfile, format="turtle", publicID=resfile)
            res = RDFResultParser().parse(resg)
        elif resfile.endswith("rdf"):
            resg = Graph()
            resg.parse(resfile, publicID=resfile)
            res = RDFResultParser().parse(resg)
        else:
            with bopen(resfile_path) as f:
                if resfile.endswith("srj"):
                    res = Result.parse(f, format="json")
                elif resfile.endswith("tsv"):
                    res = Result.parse(TextIOWrapper(f), format="tsv")

                elif resfile.endswith("csv"):
                    res = Result.parse(f, format="csv")

                    # CSV is lossy, round-trip our own resultset to
                    # lose the same info :)

                    # write bytes, read strings...
                    s = BytesIO()
                    res2.serialize(s, format="csv")
                    s.seek(0)
                    res2 = Result.parse(s, format="csv")
                    s.close()

                else:
                    res = Result.parse(f, format="xml")

        if not DETAILEDASSERT:
            eq(res.type, res2.type, "Types do not match")
            if res.type == "SELECT":
                assert res2.vars is not None
                eq(set(res.vars), set(res2.vars), "Vars do not match")
                comp = bindingsCompatible(set(res), set(res2))
                assert comp, "Bindings do not match"
            elif res.type == "ASK":
                eq(res.askAnswer, res2.askAnswer, "Ask answer does not match")
            elif res.type in ("DESCRIBE", "CONSTRUCT"):
                assert isomorphic(res.graph, res2.graph), "graphs are not isomorphic!"
            else:
                raise Exception("Unknown result type: %s" % res.type)
        else:
            eq(
                res.type,
                res2.type,
                "Types do not match: %r != %r" % (res.type, res2.type),
            )
            if res.type == "SELECT":
                assert res2.vars is not None
                eq(
                    set(res.vars),
                    set(res2.vars),
                    "Vars do not match: %r != %r" % (set(res.vars), set(res2.vars)),
                )
                assert bindingsCompatible(
                    set(res), set(res2)
                ), "Bindings do not match: \nexpected:\n%r\n!=\ngot:\n%r" % (
                    res.serialize(format="txt", namespace_manager=g.namespace_manager),
                    res2.serialize(format="txt", namespace_manager=g.namespace_manager),
                )
            elif res.type == "ASK":
                eq(
                    res.askAnswer,
                    res2.askAnswer,
                    "Ask answer does not match: %r != %r"
                    % (res.askAnswer, res2.askAnswer),
                )
            elif res.type in ("DESCRIBE", "CONSTRUCT"):
                assert isomorphic(res.graph, res2.graph), "graphs are not isomorphic!"
            else:
                raise Exception("Unknown result type: %s" % res.type)

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
                data_path: PurePath = file_uri_to_path(data)
                print(bopen_read_close(data_path))
            if graphdata:
                print("----------------- GRAPHDATA --------------------")
                for x in graphdata:
                    print(">>>", x)
                    x_path: PurePath = file_uri_to_path(x)
                    print(bopen_read_close(x_path))

            print("----------------- Query -------------------")
            print(">>>", query)
            print(bopen_read_close(query_path))
            if resfile:
                print("----------------- Res -------------------")
                print(">>>", resfile)
                print(bopen_read_close(resfile_path))

            try:
                pq = parseQuery(bopen_read_close(query_path))
                print("----------------- Parsed ------------------")
                pprintAlgebra(translateQuery(pq, base=urljoin(query, ".")))
            except:
                print("(parser error)")

            print(decodeStringEscape(str(e)))

            import pdb

            pdb.post_mortem(sys.exc_info()[2])
        raise


testers: Dict[Node, Callable[[RDFTest], None]] = {
    UP.UpdateEvaluationTest: update_test,
    MF.UpdateEvaluationTest: update_test,
    MF.PositiveUpdateSyntaxTest11: update_test,
    MF.NegativeUpdateSyntaxTest11: update_test,
    MF.QueryEvaluationTest: query_test,
    MF.NegativeSyntaxTest11: query_test,
    MF.PositiveSyntaxTest11: query_test,
    MF.CSVResultFormatTest: query_test,
}


@pytest.fixture(scope="module", autouse=True)
def handle_flags():
    setFlags()
    yield
    resetFlags()


@pytest.mark.parametrize(
    "rdf_test_uri, type, rdf_test",
    read_manifest("test/DAWG/data-r2/manifest-evaluation.ttl"),
)
def test_dawg_data_sparql10(rdf_test_uri: URIRef, type: Node, rdf_test: RDFTest):
    testers[type](rdf_test)


@pytest.mark.parametrize(
    "rdf_test_uri, type, rdf_test",
    read_manifest("test/DAWG/data-sparql11/manifest-all.ttl"),
)
def test_dawg_data_sparql11(rdf_test_uri: URIRef, type: Node, rdf_test: RDFTest):
    testers[type](rdf_test)


@pytest.mark.parametrize(
    "rdf_test_uri, type, rdf_test", read_manifest("test/DAWG/rdflib/manifest.ttl")
)
def test_dawg_rdflib(rdf_test_uri: URIRef, type: Node, rdf_test: RDFTest):
    testers[type](rdf_test)
