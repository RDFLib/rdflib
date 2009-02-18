import unittest

from rdflib.Graph import ConjunctiveGraph as Graph
from rdflib.Namespace import Namespace as NS

from StringIO import StringIO

class TestCase(unittest.TestCase):
    def setUp(self):
        self.graph = Graph()

        io = StringIO("""
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix : <http://goonmill.org/2007/skill.n3#> .

:Foo a rdfs:Class .

:bar a :Foo .
""")

        
        self.graph.load(io, format='n3')


    def test_ask_true(self):
        """
        Ask for a triple that exists, assert that the response is True.
        """
        res = self.graph.query('ASK { <http://goonmill.org/2007/skill.n3#bar> a <http://goonmill.org/2007/skill.n3#Foo> } ')
        self.assertEquals(res.askAnswer, [True], "The answer should have been that the triple was found")
 
    def test_ask_false(self):
        """
        Ask for a triple that does not exist, assert that the response is False.
        """
        res = self.graph.query('ASK { <http://goonmill.org/2007/skill.n3#baz> a <http://goonmill.org/2007/skill.n3#Foo> } ')
        self.assertEquals(res.askAnswer, [False], "The answer should have been that the triple was not found")

if __name__ == "__main__":
    unittest.main()

