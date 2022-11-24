import time
from test.data import TEST_DATA_DIR

import rdflib
from rdflib import Graph, logger

rdflib.plugin.register(
    "larknquadsstar",
    rdflib.parser.Parser,
    "rdflib.experimental.plugins.parsers.larknquadsstar",
    "LarkNQuadsStarParser",
)

testloc = TEST_DATA_DIR / "sp2b" / "50ktriples.nq"


def test_larknquads_50k():
    g = Graph()
    t0 = time.time()
    g.parse(
        location=str(testloc),
        format="larknquadsstar",
    )
    t1 = time.time()
    print(f"Lark NQuads RDF * parser: {t1 - t0:.5f}")


def test_nquads_50k():
    g = Graph()
    t0 = time.time()
    g.parse(
        location=str(testloc),
        format="nquads",
    )
    t1 = time.time()
    logger.info(f"Extant NQuads parser: {t1 - t0:.5f}")
