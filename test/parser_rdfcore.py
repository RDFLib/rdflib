import unittest

from rdflib import URIRef, BNode, Literal
from rdflib.Namespace import Namespace
from rdflib.exceptions import ParserError
from rdflib.constants import TYPE

from rdflib import Graph
from rdflib.util import first


verbose = 0

from encodings.utf_8 import StreamWriter

import sys
sw = StreamWriter(sys.stdout)
def write(msg):
    sw.write(msg+"\n")
    #sys.stdout.write(msg+"\n")

class TestStore(Graph):
    def __init__(self, expected):
        super(TestStore, self).__init__()
        self.expected = expected

    def add(self, (s, p, o)):
        if not isinstance(s, BNode) and not isinstance(o, BNode):
            if not (s, p, o) in self.expected:
                m = u"Triple not in expected result: %s, %s, %s" % (s.n3(), p.n3(), o.n3())
                if verbose: write(m)
                #raise Exception(m)
        super(TestStore, self).add((s, p, o))


TEST = Namespace("http://www.w3.org/2000/10/rdf-tests/rdfcore/testSchema#")

import os
def resolve(rel):
    return "http://www.w3.org/2000/10/rdf-tests/rdfcore/" + rel

def _testPositive(uri, manifest):
    if verbose: write(u"TESTING: %s" % uri)
    result = 0 # 1=failed, 0=passed
    inDoc = first(manifest.objects(uri, TEST["inputDocument"]))
    outDoc = first(manifest.objects(uri, TEST["outputDocument"]))
    expected = Graph()
    if outDoc[-3:]==".nt":
        format = "nt"
    else:
        format = "xml"
    expected.load(outDoc, format=format)
    store = TestStore(expected)
    if inDoc[-3:]==".nt":
        format = "nt"
    else:
        format = "xml"

    try:
        store.load(inDoc, format=format)
    except ParserError, pe:
        write("Failed '")
        write(inDoc)
        write("' failed with")
        raise pe
        try:
            write(type(pe))
        except:
            write("sorry could not dump out error.")
        result = 1
    else:
        if not store.isomorphic(expected):
            write(u"""Failed: '%s'""" % uri)
#             print """  In:\n"""
#             for s, p, o in store:
#                 print "%s %s %s." % (s.n3(), p.n3(), o.n3())
#             print """  Out:\n"""
#             for s, p, o in expected:
#                 print "%s %s %s." % (s.n3(), p.n3(), o.n3())

            result += 1

    if verbose:
        write("""  In:\n""")
        for s, p, o in store:
            msg = u"%s %s %s." % (s.n3(), p.n3(), o.n3())
            write(msg)
        write("""  Out:\n""")
        for s, p, o in expected:
                write(u"%s %s %s." % (s.n3(), p.n3(), o.n3()))

    return result

def _testNegative(uri, manifest):
    if verbose: write(u"TESTING: %s" % uri)
    result = 0 # 1=failed, 0=passed
    inDoc = first(manifest.objects(uri, TEST["inputDocument"]))
    store = Graph()

    test = BNode()
    results.add((test, RESULT["test"], uri))
    results.add((test, RESULT["system"], system))

    try:
        if inDoc[-3:]==".nt":
            format = "nt"
        else:
            format = "xml"
        store.load(inDoc, format=format)
    except ParserError, pe:
        results.add((test, TYPE, RESULT["PassingRun"]))
        #pass
    else:
        write(u"""Failed: '%s'""" % uri)
        results.add((test, TYPE, RESULT["FailingRun"]))
        result = 1
    return result

class ParserTestCase(unittest.TestCase):
    backend = 'default'
    path = 'store'

    def setUp(self):
        self.manifest = manifest = Graph(backend=self.backend)
        manifest.open(self.path)
        manifest.load("http://www.w3.org/2000/10/rdf-tests/rdfcore/Manifest.rdf")

    def tearDown(self):
        self.manifest.close()

    def testNegative(self):
        manifest = self.manifest
        num_failed = total = 0
        negs = list(manifest.subjects(TYPE, TEST["NegativeParserTest"]))
        negs.sort()
        for neg in negs:
            status = first(manifest.objects(neg, TEST["status"]))
            if status==Literal("APPROVED"):
                result = _testNegative(neg, manifest)
                total += 1
                num_failed += result
        self.assertEquals(num_failed, 0, "Failed: %s of %s." % (num_failed, total))

    def testPositive(self):
        manifest = self.manifest
        uris = list(manifest.subjects(TYPE, TEST["PositiveParserTest"]))
        uris.sort()
        num_failed = total = 0
        for uri in uris:
            status = first(manifest.objects(uri, TEST["status"]))
            if status==Literal("APPROVED"):
                result = _testPositive(uri, manifest)
                test = BNode()
                results.add((test, RESULT["test"], uri))
                results.add((test, RESULT["system"], system))
                if not result:
                    results.add((test, TYPE, RESULT["PassingRun"]))
                else:
                   results.add((test, TYPE, RESULT["FailingRun"]))
                total += 1
                num_failed += result
        self.assertEquals(num_failed, 0, "Failed: %s of %s." % (num_failed, total))

RESULT = Namespace("http://www.w3.org/2002/03owlt/resultsOntology#")
FOAF = Namespace("http://xmlns.com/foaf/0.1/")

from rdflib.constants import RDFS_LABEL, RDFS_COMMENT
results = Graph()

system = BNode("system")
results.add((system, FOAF["homepage"], URIRef("http://rdflib.net/")))
results.add((system, RDFS_LABEL, Literal("RDFLib")))
results.add((system, RDFS_COMMENT, Literal("")))


if __name__ == "__main__":
    manifest = Graph()
    manifest.load("http://www.w3.org/2000/10/rdf-tests/rdfcore/Manifest.rdf")
    import sys, getopt
    try:
        optlist, args = getopt.getopt(sys.argv[1:], 'h:', ["help"])
    except getopt.GetoptError, msg:
        write(msg)
        usage()

    try:
        argv = sys.argv
        for arg in sys.argv[1:]:
            verbose = 1
            case = URIRef(arg)
            write(u"Testing: %s" % case)
            if (case, TYPE, TEST["PositiveParserTest"]) in manifest:
                result = _testPositive(case, manifest)
                write(u"Positive test %s" % ["PASSED", "FAILED"][result])
            elif (case, TYPE, TEST["NegativeParserTest"]) in manifest:
                result = _testNegative(case, manifest)
                write(u"Negative test %s" % ["PASSED", "FAILED"][result])
            else:
                write(u"%s not ??" % case)

        if len(argv)<=1:
            unittest.main()
    finally:
        results.save("results.rdf")
