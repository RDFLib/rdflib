import unittest

from rdflib import Graph, XSD, RDF, RDFS, URIRef, Literal


class TestIssue977(unittest.TestCase):
    def setUp(self):
        self.graph = Graph()
        # Bind prefixes.
        self.graph.bind("isbn", "urn:isbn:")
        self.graph.bind("webn", "http://w3c.org/example/isbn/")
        # Populate graph.
        self.graph.add(
            (URIRef("urn:isbn:1503280780"), RDFS.label, Literal("Moby Dick"))
        )
        self.graph.add(
            (
                URIRef("http://w3c.org/example/isbn/1503280780"),
                RDFS.label,
                Literal("Moby Dick"),
            )
        )

    def test_namespace_manager(self):
        assert "isbn", "urn:isbn:" in tuple(self.graph.namespaces())
        assert "webn", "http://w3c.org/example/isbn/" in tuple(self.graph.namespaces())

    def test_turtle_serialization(self):
        serialization = self.graph.serialize(None, format="turtle")
        print(f"Test Issue 977, serialization output:\n---\n{serialization}---")
        # Test serialization.
        assert (
            "@prefix webn:" in serialization
        ), "Prefix webn not found in serialization!"
        assert (
            "@prefix isbn:" in serialization
        ), "Prefix isbn not found in serialization!"


if __name__ == "__main__":
    unittest.main()
