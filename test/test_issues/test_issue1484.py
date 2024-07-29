import io
import json

from rdflib import RDF, RDFS, Graph
from test.utils.namespace import EGDO


def test_issue_1484_json():
    """
    Test JSON-LD parsing of result from json.dump
    """
    jsondata = {"@id": EGDO.s, "@type": [EGDO.t], EGDO.p: {"@id": EGDO.o}}

    s = io.StringIO()
    json.dump(jsondata, s, indent=2, separators=(",", ": "))
    s.seek(0)

    DEBUG = False  # noqa: N806
    if DEBUG:
        print("S: ", s.read())
        s.seek(0)

    b = EGDO.base
    g = Graph()
    g.bind("rdf", RDF)
    g.bind("rdfs", RDFS)
    g.parse(source=s, publicID=b, format="json-ld")

    assert (EGDO.s, RDF.type, EGDO.t) in g
    assert (EGDO.s, EGDO.p, EGDO.o) in g


def test_issue_1484_str():
    """
    Test JSON-LD parsing of result from string (used by round tripping tests)

    (Previously passes, but broken by earlier fix for above.)
    """
    jsonstr = """
        {
            "@id": "http://example.org/s",
            "@type": [
            "http://example.org/t"
            ],
            "http://example.org/p": {
            "@id": "http://example.org/o"
            }
        }
    """

    b = EGDO.base
    g = Graph()
    g.bind("rdf", RDF)
    g.bind("rdfs", RDFS)
    g.parse(data=jsonstr, publicID=b, format="json-ld")

    assert (EGDO.s, RDF.type, EGDO.t) in g
    assert (EGDO.s, EGDO.p, EGDO.o) in g
