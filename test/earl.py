from datetime import datetime

from rdflib import Graph, URIRef, Literal, BNode, RDF, Namespace
from rdflib.namespace import FOAF, DOAP, DC

from nose.tools import nottest

EARL = Namespace("http://www.w3.org/ns/earl#")

report = Graph()

report.bind('foaf', FOAF)
report.bind('earl', EARL)
report.bind('doap', DOAP)
report.bind('dc', DC)

me = URIRef('http://gromgull.net/me')
report.add((me, RDF.type, FOAF.Person))
report.add((me, FOAF.homepage, URIRef("http://gromgull.net")))
report.add((me, FOAF.name, Literal("Gunnar Aastrand Grimnes")))

rdflib = URIRef('https://github.com/RDFLib/rdflib')

report.add((rdflib, DOAP.homepage, rdflib))
report.add((rdflib, DOAP.name, Literal("rdflib")))
report.add((rdflib, DOAP.developer, me))
report.add((rdflib, RDF.type, DOAP.Project))

now = Literal(datetime.now())

@nottest
def add_test(test, res, info=None):
    a = BNode()
    report.add((a, RDF.type, EARL.Assertion))
    report.add((a, EARL.assertedBy, me))
    report.add((a, EARL.test, test))
    report.add((a, EARL.subject, rdflib))

    report.add((a, DC.date, now))

    r = BNode()
    report.add((a, EARL.result, r))
    report.add((r, RDF.type, EARL.TestResult))

    report.add((r, EARL.outcome, EARL[res]))
    if info:
        report.add((r, EARL.info, Literal(info)))
