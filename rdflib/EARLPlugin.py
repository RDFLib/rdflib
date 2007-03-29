""" A Nose Plugin for EARL.

See Also: 
  http://nose.python-hosting.com/
  http://www.w3.org/TR/EARL10-Schema/ 

"""

import logging
import sys

from nose.plugins import Plugin
from nose.suite import TestModule

from rdflib import URIRef, BNode, Literal
from rdflib import RDF, RDFS
from rdflib.Graph import Graph
from rdflib.Namespace import NamespaceDict as Namespace

log = logging.getLogger(__name__)

log.info("HELLO")


EARL = Namespace("http://www.w3.org/ns/earl#")


class EARLPlugin(Plugin):
    """
    Activate the EARL plugin to generate a report of the test results
    using EARL.
    """
    name = 'EARL'
    
    def begin(self):
        self.graph = Graph()
        self.graph.bind("earl", EARL.uri)

    def finalize(self, result):
        self.graph.serialize("results.rdf")

    def addDeprecated(self, test):
        print "Deprecated: %s" % test

    def addError(self, test, err, capt):
        print "Error: %s" % test

    def addFailure(self, test, err, capt, tb_info):
        print "Failure: %s" % test

    def addSkip(self, test):
        print "Skip: %s" % test

    def addSuccess(self, test, capt):
        result = BNode() # TODO: coin URIRef
        print repr(test)
        self.graph.add((result, RDFS.label, Literal(test)))
        self.graph.add((result, RDF.type, EARL.TestResult))
        self.graph.add((result, EARL.outcome, EARL["pass"]))
        # etc

"""
<earl:TestResult rdf:about="#result">
  <earl:outcome rdf:resource="http://www.w3.org/ns/earl#fail"/>
  <dc:title xml:lang="en">Invalid Markup (code #353)</dc:title>
  <dc:description rdf:parseType="Literal" xml:lang="en">
    <div xmlns="http://www.w3.org/1999/xhtml">
      <p>The <code>table</code> element is not allowed to appear
        inside a <code>p</code> element</p>
    </div>
  </dc:description>
  <dc:date rdf:datatype="http://www.w3.org/2001/XMLSchema#date">2006-08-13</dc:date>
  <earl:pointer rdf:resource="#xpointer"/>
  <earl:info rdf:parseType="Literal" xml:lang="en">
    <div xmlns="http://www.w3.org/1999/xhtml">
      <p>It seems the <code>p</code> element has not been closed</p>
    </div>
  </earl:info>
</earl:TestResult>
"""


