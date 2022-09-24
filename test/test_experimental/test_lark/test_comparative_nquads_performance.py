import time
from test.data import TEST_DATA_DIR

import rdflib
from rdflib import Graph, logger

rdflib.plugin.register(
    "larknquads",
    rdflib.parser.Parser,
    "rdflib.experimental.plugins.parsers.larknquads",
    "LarkNQuadsParser",
)

testloc = TEST_DATA_DIR / "sp2b" / "50ktriples.nq"


def test_larknquads_50k():
    g = Graph()
    t0 = time.time()
    g.parse(
        location=str(testloc),
        format="larknquads",
    )
    t1 = time.time()
    print(f"Lark NT parser: {t1 - t0:.5f}")


def test_nquads_50k():
    g = Graph()
    t0 = time.time()
    g.parse(
        location=str(testloc),
        format="nquads",
    )
    t1 = time.time()
    logger.info(f"Extant NT parser: {t1 - t0:.5f}")
