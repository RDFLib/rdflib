import os
import re
import subprocess
import sys
from tempfile import mkstemp
from unittest.mock import mock_open, patch, sentinel

from rdflib.tools import csv2rdf
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
            capture_output=True,
            text=True,
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

    @patch.object(csv2rdf.CSV2RDF, "convert", return_value=None)
    def test_csv2rdf_config_file_opened(self, config_mock):
        """Test that the config file is read when specified."""
        # Pretend there is a file with the section we're looking for.
        # We don't care about the actual path, since it won't really be opened
        # but when we try to open it, we will get back the section header
        # so that the reader doesn't complain.
        config_file = sentinel.file_path
        open_mock = mock_open(read_data="[csv2rdf]")
        # Also pretend that we're passing the arguments from the command line
        cli_args = ["csv2rdf.py", "-f", config_file, str(REALESTATE_FILE_PATH)]
        with patch.object(csv2rdf.sys, "argv", cli_args):
            with patch("builtins.open", open_mock):
                csv2rdf.main()
                # Check that we've "opened" the right file
                open_mock.assert_called_once_with(config_file)
