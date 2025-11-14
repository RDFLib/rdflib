from __future__ import annotations

import json
import logging
import os
import subprocess
import sys
import tempfile
from typing import Dict, Iterable, List, Tuple

import pytest

from rdflib import Dataset, Graph
from rdflib.plugins.stores.berkeleydb import has_bsddb
from rdflib.store import VALID_STORE
from test.data import TEST_DATA_DIR
from test.utils.http import MethodName, MockHTTPResponse
from test.utils.httpservermock import ServedBaseHTTPServerMock

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

# Easy triple exists query
# located at test/data/suites/w3c/sparql11/syntax-query/syntax-exists-01.rq
EXAMPLE_SPARQL_EXISTS_QUERY_PATH = os.path.join(
    TEST_DATA_DIR, "suites", "w3c", "sparql11", "syntax-query", "syntax-exists-01.rq"
)


@pytest.fixture
def get_berkeley_graph() -> Iterable[Tuple[str, Dataset]]:
    path = tempfile.NamedTemporaryFile().name
    g = Dataset("BerkeleyDB")
    rt = g.open(path, create=True)
    assert rt == VALID_STORE, "The underlying store is corrupt"
    assert (
        len(g) == 0
    ), "There must be zero triples in the graph just after store (file) creation"

    yield path, g

    g.close()
    g.destroy(path)


class TestSPARQLQUERY:
    """
    Testing for script `rdflib.tools.sparqlquery`
    """

    def test_singletarget(self):
        """
        Testing sparqlquery test/data/suites/w3c/sparql11/add/add-01-pre.ttl
            --queryfile test/data/suites/w3c/sparql/syntax-query/syntax-exists-01.rq
            --format json
        """
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "rdflib.tools.sparqlquery",
                str(EXAMPLE_SPARQL_ADD1_PATH),
                "--queryfile",
                str(EXAMPLE_SPARQL_EXISTS_QUERY_PATH),
                "--format",
                "json",
            ],
            capture_output=True,
            text=True,
        )
        assert completed.returncode == 0, f"Failed with\n{completed.stderr}"
        decoded_result = json.loads(completed.stdout)
        bindings = decoded_result["results"]["bindings"]
        values = {b["s"].get("value") for b in bindings}
        # because in the file only one subject :john is described,
        # therefor 's' will always be bound only with :john
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

    def test_sparql_select(
        self,
        function_httpmock: ServedBaseHTTPServerMock,
    ):
        """
        Testing sparqlquery http://mockserver/
                -q "SELECT ?x WHERE {?x a foaf:Person. }" --format json

        http://mockserver/ works with data
        from test/data/suites/w3c/sparql11/add/add-01-pre.ttl
        """
        url = f"{function_httpmock.url}/query"
        logging.debug("opening %s", url)
        content_type = "json"
        encoding = "utf-8"
        response_headers: Dict[str, List[str]] = {"Content-Type": [content_type]}
        graph = Graph().parse(str(EXAMPLE_SPARQL_ADD1_PATH))
        query = "SELECT ?x WHERE {?x a foaf:Person. }"
        response_body = graph.query(query).serialize(
            format=content_type, encoding=encoding
        )
        assert response_body is not None
        function_httpmock.responses[MethodName.GET].append(
            MockHTTPResponse(
                200,
                "OK",
                response_body,
                response_headers,
            )
        )

        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "rdflib.tools.sparqlquery",
                url,
                "-q",
                query,
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

    @pytest.mark.skipif(
        not has_bsddb, reason="skipping berkeleydb tests, module not available"
    )
    def test_with_berkeleydb(self, get_berkeley_graph):
        """
        Testing sparqlquery path/to/berkeleystore
                -q "SELECT ?x WHERE {?x a foaf:Person. }" --format json

        berkeleystore holds data
        from test/data/suites/w3c/sparql11/add/add-01-pre.ttl
        """
        store_path, berkeley_graph = get_berkeley_graph
        berkeley_graph.parse(str(EXAMPLE_SPARQL_ADD1_PATH))
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "rdflib.tools.sparqlquery",
                store_path,
                "-q",
                "SELECT ?x WHERE {?x a foaf:Person. }",
                "--remote-storetype",
                "BerkeleyDB",
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
