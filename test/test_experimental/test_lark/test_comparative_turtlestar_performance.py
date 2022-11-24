import time
from test.data import TEST_DATA_DIR

import rdflib
from rdflib import Graph

rdflib.plugin.register(
    "larkttl",
    rdflib.parser.Parser,
    "rdflib.experimental.plugins.parsers.larkturtle",
    "LarkTurtleParser",
)

rdflib.plugin.register(
    "larkturtlestar",
    rdflib.parser.Parser,
    "rdflib.experimental.plugins.parsers.larkturtlestar",
    "LarkTurtleStarParser",
)

testloc = TEST_DATA_DIR / "sp2b" / "50ktriples.ttl"


def test_larkturtle():
    g = Graph()
    t0 = time.time()
    g.parse(
        location=str(testloc),
        format="larkttl",
    )
    t1 = time.time()
    print(f"Lark Turtle classic parser: {t1 - t0:.5f}")


def test_larkturtlestar():
    g = Graph()
    t0 = time.time()
    g.parse(
        location=str(testloc),
        format="larkturtlestar",
    )
    t1 = time.time()
    print(f"Lark-Cython Turtle RDF* parser: {t1 - t0:.5f}")


def test_turtle():
    g = Graph()
    t0 = time.time()
    g.parse(
        location=str(testloc),
        format="ttl",
    )
    t1 = time.time()
    print(f"Extant Turtle parser: {t1 - t0:.5f}")
