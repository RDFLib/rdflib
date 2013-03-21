import unittest
import os
import tempfile
from rdflib import Graph
from rdflib import Literal
from rdflib import URIRef
from rdflib.namespace import XSD, RDFS
from rdflib.py3compat import b


class CoreSQLiteStoreTestCase(unittest.TestCase):
    """
    Test case for SQLite core.
    """
    store = "SQLite"
    path = None
    storetest = True

    def setUp(self):
        self.graph = Graph(store=self.store)
        fp, self.path = tempfile.mkstemp(
            prefix='test', dir='/tmp', suffix='.sqlite')
        self.graph.open(self.path, create=True)

    def tearDown(self):
        # TODO: delete a_tmp_dir
        self.graph.close()
        del self.graph
        os.unlink(self.path)

    def test_escape_quoting(self):
        test_string = "This un's a Literal!!"
        self.graph.add(
            (URIRef("http://example.org/foo"),
             RDFS.label,
             Literal(test_string, datatype=XSD.string)))
        self.graph.commit()
        assert b("This un's a Literal!!") in self.graph.serialize(format="xml")

if __name__ == '__main__':
    unittest.main()
