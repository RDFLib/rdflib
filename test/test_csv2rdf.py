import subprocess
import unittest
import sys
from os import remove
from tempfile import mkstemp
from pathlib import Path


class CSV2RDFTest(unittest.TestCase):
    def setUp(self):
        self.REALESTATE_FILE_PATH = Path(__file__).parent / "csv" / "realestate.csv"

    def test_csv2rdf_cli(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "rdflib.tools.csv2rdf",
                str(self.REALESTATE_FILE_PATH),
            ],
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
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "rdflib.tools.csv2rdf",
                "-o",
                fname,
                str(self.REALESTATE_FILE_PATH),
            ],
        )
        self.assertEqual(completed.returncode, 0)
        with open(fname) as f:
            self.assertGreater(len(f.readlines()), 0)
        remove(fname)
