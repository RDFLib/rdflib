import subprocess
import unittest
from os import remove
from tempfile import mkstemp


class CSV2RDFTest(unittest.TestCase):
    def test_csv2rdf_cli(self):
        completed = subprocess.run(
            ["csv2rdf", "test/csv/realestate.csv"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
        )
        self.assertEqual(completed.returncode, 0)
        self.assertRegex(completed.stderr, r"Converted \d+ rows into \d+ triples.")
        self.assertRegex(completed.stderr, r"Took [\d\.]+ seconds.")
        self.assertIn("<http://example.org/instances/0>", completed.stdout)
        self.assertIn("<http://example.org/props/zip>", completed.stdout)

    def test_csv2rdf_cli_fileout(self):
        _, fname = mkstemp()
        completed = subprocess.run(["csv2rdf", "-o", fname, "test/csv/realestate.csv"],)
        self.assertEqual(completed.returncode, 0)
        with open(fname) as f:
            self.assertGreater(len(f.readlines()), 0)
        remove(fname)
