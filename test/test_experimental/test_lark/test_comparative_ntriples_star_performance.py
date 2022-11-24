import time
from test.data import TEST_DATA_DIR

import rdflib
from rdflib import Graph, logger

rdflib.plugin.register(
    "larkntstar",
    rdflib.parser.Parser,
    "rdflib.experimental.plugins.parsers.larkntriplesstar",
    "LarkNTriplesStarParser",
)

rdflib.plugin.register(
    "altnt",
    rdflib.parser.Parser,
    "rdflib.experimental.plugins.parsers.ntriples-star",
    "NtriplesStarParser",
)

testloc = TEST_DATA_DIR / "sp2b" / "50ktriples.nt"


def test_larkntriples_50k():
    g = Graph()
    t0 = time.time()
    g.parse(
        location=str(testloc),
        format="larkntstar",
    )
    t1 = time.time()
    print(f"Lark NT parser: {t1 - t0:.5f}")


def test_ntriples_50k():
    g = Graph()
    t0 = time.time()
    g.parse(
        location=str(testloc),
        format="nt",
    )
    t1 = time.time()
    logger.info(f"Extant NT parser: {t1 - t0:.5f}")
