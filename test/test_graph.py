import sys
import os
import unittest

from tempfile import mkdtemp, mkstemp
import shutil
from urllib.error import URLError, HTTPError

from rdflib import URIRef, Graph, plugin
from rdflib.exceptions import ParserError
from rdflib.plugin import PluginException

from nose.exc import SkipTest


class GraphTestCase(unittest.TestCase):
    store = "default"
    tmppath = None

    def setUp(self):
        try:
            self.graph = Graph(store=self.store)
        except ImportError:
            raise SkipTest("Dependencies for store '%s' not available!" % self.store)
        if self.store == "SQLite":
            _, self.tmppath = mkstemp(prefix="test", dir="/tmp", suffix=".sqlite")
        else:
            self.tmppath = mkdtemp()
        self.graph.open(self.tmppath, create=True)

        self.michel = URIRef("michel")
        self.tarek = URIRef("tarek")
        self.bob = URIRef("bob")
        self.likes = URIRef("likes")
        self.hates = URIRef("hates")
        self.pizza = URIRef("pizza")
        self.cheese = URIRef("cheese")

    def tearDown(self):
        self.graph.close()
        if os.path.isdir(self.tmppath):
            shutil.rmtree(self.tmppath)
        else:
            os.remove(self.tmppath)

    def addStuff(self):
        tarek = self.tarek
        michel = self.michel
        bob = self.bob
        likes = self.likes
        hates = self.hates
        pizza = self.pizza
        cheese = self.cheese

        self.graph.add((tarek, likes, pizza))
        self.graph.add((tarek, likes, cheese))
        self.graph.add((michel, likes, pizza))
        self.graph.add((michel, likes, cheese))
        self.graph.add((bob, likes, cheese))
        self.graph.add((bob, hates, pizza))
        self.graph.add((bob, hates, michel))  # gasp!

    def removeStuff(self):
        tarek = self.tarek
        michel = self.michel
        bob = self.bob
        likes = self.likes
        hates = self.hates
        pizza = self.pizza
        cheese = self.cheese

        self.graph.remove((tarek, likes, pizza))
        self.graph.remove((tarek, likes, cheese))
        self.graph.remove((michel, likes, pizza))
        self.graph.remove((michel, likes, cheese))
        self.graph.remove((bob, likes, cheese))
        self.graph.remove((bob, hates, pizza))
        self.graph.remove((bob, hates, michel))  # gasp!

    def testAdd(self):
        self.addStuff()

    def testRemove(self):
        self.addStuff()
        self.removeStuff()

    def testTriples(self):
        tarek = self.tarek
        michel = self.michel
        bob = self.bob
        likes = self.likes
        hates = self.hates
        pizza = self.pizza
        cheese = self.cheese
        asserte = self.assertEqual
        triples = self.graph.triples
        Any = None

        self.addStuff()

        # unbound subjects
        asserte(len(list(triples((Any, likes, pizza)))), 2)
        asserte(len(list(triples((Any, hates, pizza)))), 1)
        asserte(len(list(triples((Any, likes, cheese)))), 3)
        asserte(len(list(triples((Any, hates, cheese)))), 0)

        # unbound objects
        asserte(len(list(triples((michel, likes, Any)))), 2)
        asserte(len(list(triples((tarek, likes, Any)))), 2)
        asserte(len(list(triples((bob, hates, Any)))), 2)
        asserte(len(list(triples((bob, likes, Any)))), 1)

        # unbound predicates
        asserte(len(list(triples((michel, Any, cheese)))), 1)
        asserte(len(list(triples((tarek, Any, cheese)))), 1)
        asserte(len(list(triples((bob, Any, pizza)))), 1)
        asserte(len(list(triples((bob, Any, michel)))), 1)

        # unbound subject, objects
        asserte(len(list(triples((Any, hates, Any)))), 2)
        asserte(len(list(triples((Any, likes, Any)))), 5)

        # unbound predicates, objects
        asserte(len(list(triples((michel, Any, Any)))), 2)
        asserte(len(list(triples((bob, Any, Any)))), 3)
        asserte(len(list(triples((tarek, Any, Any)))), 2)

        # unbound subjects, predicates
        asserte(len(list(triples((Any, Any, pizza)))), 3)
        asserte(len(list(triples((Any, Any, cheese)))), 3)
        asserte(len(list(triples((Any, Any, michel)))), 1)

        # all unbound
        asserte(len(list(triples((Any, Any, Any)))), 7)
        self.removeStuff()
        asserte(len(list(triples((Any, Any, Any)))), 0)

    def testConnected(self):
        graph = self.graph
        self.addStuff()
        self.assertEqual(True, graph.connected())

        jeroen = URIRef("jeroen")
        unconnected = URIRef("unconnected")

        graph.add((jeroen, self.likes, unconnected))

        self.assertEqual(False, graph.connected())

    def testSub(self):
        g1 = self.graph
        g2 = Graph(store=g1.store)

        tarek = self.tarek
        # michel = self.michel
        bob = self.bob
        likes = self.likes
        # hates = self.hates
        pizza = self.pizza
        cheese = self.cheese

        g1.add((tarek, likes, pizza))
        g1.add((bob, likes, cheese))

        g2.add((bob, likes, cheese))

        g3 = g1 - g2

        self.assertEqual(len(g3), 1)
        self.assertEqual((tarek, likes, pizza) in g3, True)
        self.assertEqual((tarek, likes, cheese) in g3, False)

        self.assertEqual((bob, likes, cheese) in g3, False)

        g1 -= g2

        self.assertEqual(len(g1), 1)
        self.assertEqual((tarek, likes, pizza) in g1, True)
        self.assertEqual((tarek, likes, cheese) in g1, False)

        self.assertEqual((bob, likes, cheese) in g1, False)

    def testGraphAdd(self):
        g1 = self.graph
        g2 = Graph(store=g1.store)

        tarek = self.tarek
        # michel = self.michel
        bob = self.bob
        likes = self.likes
        # hates = self.hates
        pizza = self.pizza
        cheese = self.cheese

        g1.add((tarek, likes, pizza))

        g2.add((bob, likes, cheese))

        g3 = g1 + g2

        self.assertEqual(len(g3), 2)
        self.assertEqual((tarek, likes, pizza) in g3, True)
        self.assertEqual((tarek, likes, cheese) in g3, False)

        self.assertEqual((bob, likes, cheese) in g3, True)

        g1 += g2

        self.assertEqual(len(g1), 2)
        self.assertEqual((tarek, likes, pizza) in g1, True)
        self.assertEqual((tarek, likes, cheese) in g1, False)

        self.assertEqual((bob, likes, cheese) in g1, True)

    def testGraphIntersection(self):
        g1 = self.graph
        g2 = Graph(store=g1.store)

        tarek = self.tarek
        michel = self.michel
        bob = self.bob
        likes = self.likes
        # hates = self.hates
        pizza = self.pizza
        cheese = self.cheese

        g1.add((tarek, likes, pizza))
        g1.add((michel, likes, cheese))

        g2.add((bob, likes, cheese))
        g2.add((michel, likes, cheese))

        g3 = g1 * g2

        self.assertEqual(len(g3), 1)
        self.assertEqual((tarek, likes, pizza) in g3, False)
        self.assertEqual((tarek, likes, cheese) in g3, False)

        self.assertEqual((bob, likes, cheese) in g3, False)

        self.assertEqual((michel, likes, cheese) in g3, True)

        g1 *= g2

        self.assertEqual(len(g1), 1)

        self.assertEqual((tarek, likes, pizza) in g1, False)
        self.assertEqual((tarek, likes, cheese) in g1, False)

        self.assertEqual((bob, likes, cheese) in g1, False)

        self.assertEqual((michel, likes, cheese) in g1, True)

    def testGuessFormatForParse(self):
        self.graph = Graph()

        # files
        with self.assertRaises(ParserError):
            self.graph.parse(__file__)  # here we are trying to parse a Python file!!

        # .nt can be parsed by Turtle Parser
        self.graph.parse("test/nt/anons-01.nt")
        # RDF/XML
        self.graph.parse("test/rdf/datatypes/test001.rdf")  # XML
        # bad filename but set format
        self.graph.parse("test/rdf/datatypes/test001.borked", format="xml")

        # strings
        self.graph = Graph()

        with self.assertRaises(ParserError):
            self.graph.parse(data="rubbish")

        # Turtle - default
        self.graph.parse(
            data="<http://example.com/a> <http://example.com/a> <http://example.com/a> ."
        )

        # Turtle - format given
        self.graph.parse(
            data="<http://example.com/a> <http://example.com/a> <http://example.com/a> .",
            format="turtle",
        )

        # RDF/XML - format given
        rdf = """<rdf:RDF
  xmlns:ns1="http://example.org/#"
  xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
>
  <rdf:Description rdf:nodeID="ub63bL2C1">
    <ns1:p rdf:resource="http://example.org/q"/>
    <ns1:r rdf:resource="http://example.org/s"/>
  </rdf:Description>
  <rdf:Description rdf:nodeID="ub63bL5C1">
    <ns1:r>
      <rdf:Description rdf:nodeID="ub63bL6C11">
        <ns1:s rdf:resource="http://example.org/#t"/>
      </rdf:Description>
    </ns1:r>
    <ns1:p rdf:resource="http://example.org/q"/>
  </rdf:Description>
</rdf:RDF>        
        """
        self.graph.parse(data=rdf, format="xml")

        # URI
        self.graph = Graph()

        # only getting HTML
        with self.assertRaises(PluginException):
            self.graph.parse(location="https://www.google.com")

        try:
            self.graph.parse(location="http://www.w3.org/ns/adms.ttl")
            self.graph.parse(location="http://www.w3.org/ns/adms.rdf")
        except (URLError, HTTPError):
            # this endpoint is currently not available, ignore this test.
            pass

        try:
            # persistent Australian Government online RDF resource without a file-like ending
            self.graph.parse(
                location="https://linked.data.gov.au/def/agrif?_format=text/turtle"
            )
        except (URLError, HTTPError):
            # this endpoint is currently not available, ignore this test.
            pass

    def testTransitive(self):
        person = URIRef("ex:person")
        dad = URIRef("ex:dad")
        mom = URIRef("ex:mom")
        mom_of_dad = URIRef("ex:mom_o_dad")
        mom_of_mom = URIRef("ex:mom_o_mom")
        dad_of_dad = URIRef("ex:dad_o_dad")
        dad_of_mom = URIRef("ex:dad_o_mom")

        parent = URIRef("ex:parent")

        g = Graph()
        g.add((person, parent, dad))
        g.add((person, parent, mom))
        g.add((dad, parent, mom_of_dad))
        g.add((dad, parent, dad_of_dad))
        g.add((mom, parent, mom_of_mom))
        g.add((mom, parent, dad_of_mom))

        # transitive parents of person
        self.assertEqual(
            set(g.transitive_objects(subject=person, predicate=parent)),
            {person, dad, mom_of_dad, dad_of_dad, mom, mom_of_mom, dad_of_mom},
        )
        # transitive parents of dad
        self.assertEqual(
            set(g.transitive_objects(dad, parent)), {dad, mom_of_dad, dad_of_dad}
        )
        # transitive parents of dad_of_dad
        self.assertEqual(set(g.transitive_objects(dad_of_dad, parent)), {dad_of_dad})

        # transitive children (inverse of parents) of mom_of_mom
        self.assertEqual(
            set(g.transitive_subjects(predicate=parent, object=mom_of_mom)),
            {mom_of_mom, mom, person},
        )
        # transitive children (inverse of parents) of mom
        self.assertEqual(set(g.transitive_subjects(parent, mom)), {mom, person})
        # transitive children (inverse of parents) of person
        self.assertEqual(set(g.transitive_subjects(parent, person)), {person})


# dynamically create classes for each registered Store

pluginname = None
if __name__ == "__main__":
    if len(sys.argv) > 1:
        pluginname = sys.argv[1]

tests = 0
for s in plugin.plugins(pluginname, plugin.Store):
    if s.name in (
        "default",
        "Memory",
        "Auditable",
        "Concurrent",
        "SPARQLStore",
        "SPARQLUpdateStore",
    ):
        continue  # these are tested by default

    if s.name in ("SimpleMemory",):
        # these (by design) won't pass some of the tests (like Intersection)
        continue

    locals()["t%d" % tests] = type(
        "%sGraphTestCase" % s.name, (GraphTestCase,), {"store": s.name}
    )
    tests += 1


if __name__ == "__main__":
    unittest.main(argv=sys.argv[:1])
