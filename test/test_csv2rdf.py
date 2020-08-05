import subprocess
import unittest

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
