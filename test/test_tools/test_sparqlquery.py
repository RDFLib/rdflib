import json
import os
import subprocess
import sys

from rdflib import Graph
from test.data import TEST_DATA_DIR

__all__ = ["TestSPARQLQUERY"]

# Just normal info with foaf:Person
# located at test/data/suites/w3c/sparql11/add/add-01-pre.ttl
EXAMPLE_SPARQL_ADD1_PATH = os.path.join(
    TEST_DATA_DIR, "suites", "w3c", "sparql11", "add", "add-01-pre.ttl"
)

# Just normal info with foaf:Person
# located at test/data/suites/w3c/sparql11/add/add-02-pre.ttl
EXAMPLE_SPARQL_ADD2_PATH = os.path.join(
    TEST_DATA_DIR, "suites", "w3c", "sparql11", "add", "add-02-pre.ttl"
)


class TestSPARQLQUERY:
    """
    Testing for script `rdflib.tools.sparqluery`

    Missing test for internet query like
    sparqlquery http://example.com/sparqlendpoint --query-file query.spl
                --username user --password secret
    """

    def test_singletarget(self):
        """
        Testing sparqlquery test/data/suites/w3c/sparql11/add/add-01-pre.ttl
                -q "SELECT ?x WHERE {?x a foaf:Person. }" --format json
        """
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "rdflib.tools.sparqlquery",
                str(EXAMPLE_SPARQL_ADD1_PATH),
                "-q",
                "SELECT ?x WHERE {?x a foaf:Person. }",
                "--format",
                "json",
            ],
            capture_output=True,
            text=True,
        )
        assert completed.returncode == 0, f"Failed with\n{completed.stderr}"
        decoded_result = json.loads(completed.stdout)
        bindings = decoded_result["results"]["bindings"]
        values = {b["x"].get("value") for b in bindings}
        assert values == {"http://example.org/john"}

    def test_multitarget(self):
        """
        Testing sparqlquery path/add-01-pre.ttl path/add-02-pre.ttl
                -q "SELECT ?x WHERE {?x a foaf:Person. }" --format json
        """
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "rdflib.tools.sparqlquery",
                str(EXAMPLE_SPARQL_ADD1_PATH),
                str(EXAMPLE_SPARQL_ADD2_PATH),
                "-q",
                "SELECT ?x WHERE {?x a foaf:Person. }",
                "--format",
                "json",
            ],
            capture_output=True,
            text=True,
        )
        assert completed.returncode == 0, f"Failed with\n{completed.stderr}"
        decoded_result = json.loads(completed.stdout)
        bindings = decoded_result["results"]["bindings"]
        values = {b["x"].get("value") for b in bindings}
        assert values == {"http://example.org/john", "http://example.org/sue"}

    def test_ask(self):
        """
        Testing sparqlquery test/data/suites/w3c/sparql11/add/add-01-pre.ttl
                -q "ASK {?x a foaf:Person. }"

        Assert that 'true' is contained in stdout and 'false' isnt.
        """
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "rdflib.tools.sparqlquery",
                str(EXAMPLE_SPARQL_ADD1_PATH),
                "-q",
                "ASK {?x a foaf:Person. }",
                "--format",
                "xml",
            ],
            capture_output=True,
            text=True,
        )
        assert completed.returncode == 0, f"Failed with\n{completed.stderr}"
        assert "true" in completed.stdout
        assert "false" not in completed.stdout

    def test_describe(self):
        """
        Testing sparqlquery test/data/suites/w3c/sparql11/add/add-01-pre.ttl
                -q "DESCRIBE <http://example.org/john>"

        tests if simple information like 'mailto:johnny@example.org' is somewhere
        in the response.
        """
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "rdflib.tools.sparqlquery",
                str(EXAMPLE_SPARQL_ADD1_PATH),
                "-q",
                "DESCRIBE <http://example.org/john>",
                "--format",
                "turtle",
            ],
            capture_output=True,
            text=True,
        )
        assert completed.returncode == 0, f"Failed with\n{completed.stderr}"
        # simple information test
        assert "mailto:johnny@example.org" in completed.stdout

    def test_construct(self):
        """
        Testing sparqlquery test/data/suites/w3c/sparql11/add/add-01-pre.ttl
                -q "CONSTRUCT {[] rdf:subject ?x.} WHERE {?x a foaf:Person.}",

        tests if returned graph has exactly one triple.
        """
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "rdflib.tools.sparqlquery",
                str(EXAMPLE_SPARQL_ADD1_PATH),
                "-q",
                "CONSTRUCT {[] rdf:subject ?x.} WHERE {?x a foaf:Person.}",
            ],
            capture_output=True,
            text=True,
        )
        assert completed.returncode == 0, f"Failed with\n{completed.stderr}"
        g = Graph().parse(data=completed.stdout)
        assert len(g) == 1
