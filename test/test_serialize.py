import unittest
from rdflib import Graph, URIRef
from tempfile import NamedTemporaryFile, TemporaryDirectory
from pathlib import Path, PurePath


class TestSerialize(unittest.TestCase):
    def setUp(self) -> None:

        graph = Graph()
        subject = URIRef("example:subject")
        predicate = URIRef("example:predicate")
        object = URIRef("example:object")
        self.triple = (
            subject,
            predicate,
            object,
        )
        graph.add(self.triple)
        self.graph = graph
        return super().setUp()

    def test_serialize_to_purepath(self):
        with TemporaryDirectory() as td:
            tfpath = PurePath(td) / "out.nt"
            self.graph.serialize(destination=tfpath, format="nt")
            graph_check = Graph()
            graph_check.parse(source=tfpath, format="nt")

        self.assertEqual(self.triple, next(iter(graph_check)))

    def test_serialize_to_path(self):
        with NamedTemporaryFile() as tf:
            tfpath = Path(tf.name)
            self.graph.serialize(destination=tfpath, format="nt")
            graph_check = Graph()
            graph_check.parse(source=tfpath, format="nt")

        self.assertEqual(self.triple, next(iter(graph_check)))


if __name__ == "__main__":
    unittest.main()
