import os

from rdflib.graph import Graph, ConjunctiveGraph
import unittest
from rdflib.term import Literal, URIRef
from rdflib.plugins.parsers.notation3 import BadSyntax, exponent_syntax
import itertools
from urllib.error import URLError

from test import TEST_DIR

test_data = """
#  Definitions of terms describing the n3 model
#

@keywords a.

@prefix n3: <#>.
@prefix log: <log.n3#> .
@prefix rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix : <#> .

@forAll :s, :p, :x, :y, :z.

n3:Statement    a rdf:Class .
n3:StatementSet a rdf:Class .

n3:includes     a rdfs:Property .   # Cf rdf:li

n3:predicate    a rdf:Property; rdfs:domain n3:statement .
n3:subject      a rdf:Property; rdfs:domain n3:statement .
n3:object       a rdf:Property; rdfs:domain n3:statement .

n3:context      a rdf:Property; rdfs:domain n3:statement;
                rdfs:range n3:StatementSet .



########### Rules

{ :x :p :y . } log:means { [
                n3:subject :x;
                n3:predicate :p;
                n3:object :y ] a log:Truth}.

# Needs more thought ... ideally, we have the implcit AND rules of
# juxtaposition (introduction and elimination)

{
    {
        {  :x n3:includes :s. } log:implies { :y n3:includes :s. } .
    } forall :s1 .
} log:implies { :x log:implies :y } .

{
    {
        {  :x n3:includes :s. } log:implies { :y n3:includes :s. } .
    } forall :s1
} log:implies { :x log:implies :y } .

# I think n3:includes has to be axiomatic builtin. - unless you go to syntax description.
# syntax.n3?
"""


class TestN3Case(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testBaseCumulative(self):
        """
        Test that the n3 parser supports base declarations
        This is issue #22
        """

        input = """
@prefix : <http://example.com/> .
# default base
<foo> :name "Foo" .
# change it
@base <http://example.com/doc/> .
<bar> :name "Bar" .
# and change it more - they are cumulative
@base <doc2/> .
<bing> :name "Bing" .
# unless abosulute
@base <http://test.com/> .
<bong> :name "Bong" .

"""
        g = Graph()
        g.parse(data=input, format="n3")
        print(list(g))
        self.assertTrue((None, None, Literal("Foo")) in g)
        self.assertTrue((URIRef("http://example.com/doc/bar"), None, None) in g)
        self.assertTrue((URIRef("http://example.com/doc/doc2/bing"), None, None) in g)
        self.assertTrue((URIRef("http://test.com/bong"), None, None) in g)

    def testBaseExplicit(self):
        """
        Test that the n3 parser supports resolving relative URIs
        and that base will override
        """

        input = """
@prefix : <http://example.com/> .
# default base
<foo> :name "Foo" .
# change it
@base <http://example.com/doc/> .
<bar> :name "Bar" .
"""
        g = Graph()
        g.parse(data=input, publicID="http://blah.com/", format="n3")
        print(list(g))
        self.assertTrue((URIRef("http://blah.com/foo"), None, Literal("Foo")) in g)
        self.assertTrue((URIRef("http://example.com/doc/bar"), None, None) in g)

    def testBaseSerialize(self):
        g = Graph()
        g.add(
            (
                URIRef("http://example.com/people/Bob"),
                URIRef("urn:knows"),
                URIRef("http://example.com/people/Linda"),
            )
        )
        s = g.serialize(base="http://example.com/", format="n3", encoding="latin-1")
        self.assertTrue(b"<people/Bob>" in s)
        g2 = ConjunctiveGraph()
        g2.parse(data=s, publicID="http://example.com/", format="n3")
        self.assertEqual(list(g), list(g2))

    def testIssue23(self):
        input = """<http://example.com/article1> <http://example.com/title> "this word is in \\u201Cquotes\\u201D"."""

        g = Graph()
        g.parse(data=input, format="n3")

        # Note difference in case of hex code, cwm allows lower-case
        input = """<http://example.com/article1> <http://example.com/title> "this word is in \\u201cquotes\\u201d"."""

        g.parse(data=input, format="n3")

    def testIssue29(self):
        input = """@prefix foo-bar: <http://example.org/> .

foo-bar:Ex foo-bar:name "Test" . """

        g = Graph()
        g.parse(data=input, format="n3")

    def testIssue68(self):
        input = """@prefix : <http://some.url/pome#>.\n\n:Brecon a :Place;\n\t:hasLord\n\t\t:Bernard_of_Neufmarch\xc3\xa9 .\n """

        g = Graph()
        g.parse(data=input, format="n3")

    def testIssue156(self):
        """
        Make sure n3 parser does not choke on UTF-8 BOM
        """
        g = Graph()
        n3_path = os.path.relpath(os.path.join(TEST_DIR, "n3/issue156.n3", os.curdir))
        g.parse(n3_path, format="n3")

    def testIssue999(self):
        """
        Make sure the n3 parser does recognize exponent and leading dot in ".171e-11"
        """
        data = """
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

<http://qudt.org/vocab/unit/MilliM-PER-YR>
  a <http://qudt.org/schema/qudt/Unit> ;
  <http://qudt.org/schema/qudt/conversionMultiplier> .171e-11 ;
  <http://qudt.org/schema/qudt/conversionOffset> 0e+00 ;
  <http://qudt.org/schema/qudt/description> "0.001-fold of the SI base unit metre divided by the unit year" ;
  <http://qudt.org/schema/qudt/hasQuantityKind> <http://qudt.org/vocab/quantitykind/Velocity> ;
  <http://qudt.org/schema/qudt/iec61360Code> "0112/2///62720#UAA868" ;
  <http://qudt.org/schema/qudt/uneceCommonCode> "H66" ;
  rdfs:isDefinedBy <http://qudt.org/2.1/vocab/unit> ;
  rdfs:isDefinedBy <http://qudt.org/vocab/unit> ;
  rdfs:label "MilliM PER YR" ;
  <http://www.w3.org/2004/02/skos/core#prefLabel> "millimetre per year" ;
.
        """
        g = Graph()
        g.parse(data=data, format="n3")
        g.parse(data=data, format="turtle")

    def testDotInPrefix(self):
        g = Graph()
        g.parse(
            data="@prefix a.1: <http://example.org/> .\n a.1:cake <urn:x> <urn:y> . \n",
            format="n3",
        )

    def testModel(self):
        g = ConjunctiveGraph()
        g.parse(data=test_data, format="n3")
        i = 0
        for s, p, o in g:
            if isinstance(s, Graph):
                i += 1
        self.assertEqual(i, 3)
        self.assertEqual(len(list(g.contexts())), 13)

        g.close()

    def testQuotedSerialization(self):
        g = ConjunctiveGraph()
        g.parse(data=test_data, format="n3")
        g.serialize(format="n3")

    def testParse(self):
        g = ConjunctiveGraph()
        try:
            g.parse(
                "http://groups.csail.mit.edu/dig/2005/09/rein/examples/troop42-policy.n3",
                format="n3",
            )
        except URLError:
            from nose import SkipTest

            raise SkipTest("No network to retrieve the information, skipping test")

    def testSingleQuotedLiterals(self):
        test_data = [
            """@prefix : <#> . :s :p 'o' .""",
            """@prefix : <#> . :s :p '''o''' .""",
        ]

        for data in test_data:
            # N3 doesn't accept single quotes around string literals
            g = ConjunctiveGraph()
            self.assertRaises(BadSyntax, g.parse, data=data, format="n3")

            g = ConjunctiveGraph()
            g.parse(data=data, format="turtle")
            self.assertEqual(len(g), 1)
            for _, _, o in g:
                self.assertEqual(o, Literal("o"))

    def testEmptyPrefix(self):

        # this is issue https://github.com/RDFLib/rdflib/issues/312
        g1 = Graph()
        g1.parse(data=":a :b :c .", format="n3")

        g2 = Graph()
        g2.parse(data="@prefix : <#> . :a :b :c .", format="n3")

        assert set(g1) == set(
            g2
        ), "Document with declared empty prefix must match default #"


class TestRegularExpressions(unittest.TestCase):
    def testExponents(self):
        signs = ("", "+", "-")
        mantissas = (
            "1",
            "1.",
            ".1",
            "12",
            "12.",
            "1.2",
            ".12",
            "123",
            "123.",
            "12.3",
            "1.23",
            ".123",
        )
        es = "eE"
        exps = ("1", "12", "+1", "-1", "+12", "-12")
        for parts in itertools.product(signs, mantissas, es, exps):
            expstring = "".join(parts)
            self.assertTrue(exponent_syntax.match(expstring))

    def testInvalidExponents(self):
        # Add test cases as needed
        invalid = (".e1",)
        for expstring in invalid:
            self.assertFalse(exponent_syntax.match(expstring))


if __name__ == "__main__":
    unittest.main()
