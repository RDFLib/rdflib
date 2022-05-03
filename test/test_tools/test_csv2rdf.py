import os
import re
import subprocess
import sys
from tempfile import mkstemp
from test.data import TEST_DATA_DIR

REALESTATE_FILE_PATH = os.path.join(TEST_DATA_DIR, "csv", "realestate.csv")


class TestCSV2RDF:
    def test_csv2rdf_cli(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "rdflib.tools.csv2rdf",
                str(REALESTATE_FILE_PATH),
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
        )
        assert completed.returncode == 0
        assert "Converted 19 rows into 228 triples." in completed.stderr
        assert re.search(r"Took [\d\.]+ seconds\.", completed.stderr)
        assert "<http://example.org/instances/0>" in completed.stdout
        assert "<http://example.org/props/zip>" in completed.stdout

    def test_csv2rdf_cli_fileout(self):
        fh, fname = mkstemp()
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "rdflib.tools.csv2rdf",
                "-o",
                fname,
                str(REALESTATE_FILE_PATH),
            ],
        )
        assert completed.returncode == 0
        with open(fname) as f:
            assert len(f.readlines()) == 228
        os.close(fh)
        os.remove(fname)
