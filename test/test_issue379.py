import unittest

import rdflib

prefix_data = """
              @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
              @prefix : <http://www.example.com#> .

              <http://www.example.com#prefix> a rdf:class ."""

base_data = """
            @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
            @base <http://www.example.com#> .

            <http://www.example.com#base> a rdf:class .
            """


class TestCase(unittest.TestCase):
    def assertIsInstance(self, obj, cls, msg=None, *args, **kwargs):
        """Python < v2.7 compatibility.  Assert 'obj' is instance of 'cls'"""
        try:
            f = super(TestCase, self).assertIsInstance
        except AttributeError:
            self.assertTrue(isinstance(obj, cls), *args, **kwargs)
        else:
            f(obj, cls, *args, **kwargs)


class TestBaseAllowsHash(TestCase):
    """
    GitHub Issue 379: https://github.com/RDFLib/rdflib/issues/379
    """
    def setUp(self):
        self.g = rdflib.Graph()

    def test_parse_successful_prefix_with_hash(self):
        """
        Test parse of '@prefix' namespace directive to allow a trailing hash '#', as is
        permitted for an IRIREF:
        http://www.w3.org/TR/2014/REC-turtle-20140225/#grammar-production-prefixID
        """
        self.g.parse(data=prefix_data, format='n3')
        self.assertIsInstance(next(self.g.subjects()), rdflib.URIRef)

    def test_parse_successful_base_with_hash(self):
        """
        Test parse of '@base' namespace directive to allow a trailing hash '#', as is
        permitted for an '@prefix' since both allow an IRIREF:
        http://www.w3.org/TR/2014/REC-turtle-20140225/#grammar-production-base
        """
        self.g.parse(data=base_data, format='n3')
        self.assertIsInstance(next(self.g.subjects()), rdflib.URIRef)

if __name__ == "__main__":
    unittest.main()
