import unittest
from rdflib.graph import ConjunctiveGraph

class TestTrigSerialize(unittest.TestCase):

    def test_empty_graph(self):
        graph = ConjunctiveGraph()
        text = graph.serialize(format='trig')
        self.assertTrue(text is not None)

if __name__ == "__main__":
    unittest.main()

