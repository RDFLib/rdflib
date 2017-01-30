from __future__ import print_function

from collections import namedtuple
from nose.tools import nottest

from rdflib import Graph, RDF, RDFS, Namespace
from six import text_type

MF = Namespace('http://www.w3.org/2001/sw/DataAccess/tests/test-manifest#')
QT = Namespace('http://www.w3.org/2001/sw/DataAccess/tests/test-query#')
UP = Namespace('http://www.w3.org/2009/sparql/tests/test-update#')
RDFT = Namespace('http://www.w3.org/ns/rdftest#')

DAWG = Namespace('http://www.w3.org/2001/sw/DataAccess/tests/test-dawg#')

RDFTest = namedtuple('RDFTest', ['uri', 'name', 'comment', 'data',
                         'graphdata', 'action', 'result', 'syntax'])

def read_manifest(f, base=None, legacy=False):

    def _str(x):
        if x is not None:
            return text_type(x)
        return None

    g = Graph()
    g.load(f, publicID=base, format='turtle')

    for m in g.subjects(RDF.type, MF.Manifest):

        for col in g.objects(m, MF.include):
            for i in g.items(col):
                for x in read_manifest(i):
                    yield x

        for col in g.objects(m, MF.entries):
            for e in g.items(col):

                approved = ((e, DAWG.approval, DAWG.Approved) in g or
                            (e, DAWG.approval, DAWG.NotClassified) in g or
                            (e, RDFT.approval, RDFT.Approved) in g)

                # run proposed tests
                # approved |= (e, RDFT.approval, RDFT.Proposed) in g

                # run legacy tests with no approval set
                if legacy:
                    approved |= ((e, DAWG.approval, None) not in g and
                                 (e, RDFT.approval, None) not in g)

                if not approved:
                    continue

                _type = g.value(e, RDF.type)

                # if _type in (MF.ServiceDescriptionTest, MF.ProtocolTest):
                #     continue  # skip tests we do not know

                name = g.value(e, MF.name)
                comment = g.value(e, RDFS.comment)
                data = None
                graphdata = None
                res = None
                syntax = True


                if _type in (MF.QueryEvaluationTest, MF.CSVResultFormatTest):
                    a = g.value(e, MF.action)
                    query = g.value(a, QT.query)
                    data = g.value(a, QT.data)
                    graphdata = list(g.objects(a, QT.graphData))
                    res = g.value(e, MF.result)
                elif _type in (MF.UpdateEvaluationTest, UP.UpdateEvaluationTest):
                    a = g.value(e, MF.action)
                    query = g.value(a, UP.request)
                    data = g.value(a, UP.data)
                    graphdata = []
                    for gd in g.objects(a, UP.graphData):
                        graphdata.append((g.value(gd, UP.graph),
                                          g.value(gd, RDFS.label)))

                    r = g.value(e, MF.result)
                    resdata = g.value(r, UP.data)
                    resgraphdata = []
                    for gd in g.objects(r, UP.graphData):
                        resgraphdata.append((g.value(gd, UP.graph),
                                             g.value(gd, RDFS.label)))

                    res = resdata, resgraphdata

                elif _type in (MF.NegativeSyntaxTest11, MF.PositiveSyntaxTest11):
                    query = g.value(e, MF.action)
                    syntax = _type == MF.PositiveSyntaxTest11

                elif _type in (MF.PositiveUpdateSyntaxTest11,
                           MF.NegativeUpdateSyntaxTest11):
                    query = g.value(e, MF.action)
                    syntax = _type == MF.PositiveUpdateSyntaxTest11

                elif _type in (RDFT.TestNQuadsPositiveSyntax,
                               RDFT.TestNQuadsNegativeSyntax,
                               RDFT.TestTrigPositiveSyntax,
                               RDFT.TestTrigNegativeSyntax,
                               RDFT.TestNTriplesPositiveSyntax,
                               RDFT.TestNTriplesNegativeSyntax,
                               RDFT.TestTurtlePositiveSyntax,
                               RDFT.TestTurtleNegativeSyntax,
                ):
                    query = g.value(e, MF.action)
                    syntax = _type in (RDFT.TestNQuadsPositiveSyntax,
                                       RDFT.TestNTriplesPositiveSyntax,
                                       RDFT.TestTrigPositiveSyntax,
                                       RDFT.TestTurtlePositiveSyntax)

                elif _type in (RDFT.TestTurtleEval, RDFT.TestTurtleNegativeEval,
                               RDFT.TestTrigEval, RDFT.TestTrigNegativeEval):
                    query = g.value(e, MF.action)
                    res = g.value(e, MF.result)
                    syntax = _type in (RDFT.TestTurtleEval, RDFT.TestTrigEval)

                else:
                    pass
                    print("I dont know DAWG Test Type %s" % _type)
                    continue

                yield _type, RDFTest(e, _str(name), _str(comment),
                               _str(data), graphdata, _str(query),
                               res, syntax)

@nottest
def nose_tests(testers, manifest, base=None, legacy=False):
    for _type, test in read_manifest(manifest, base, legacy):
        if _type in testers:
            yield testers[_type], test
