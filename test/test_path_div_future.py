from __future__ import division
from rdflib import URIRef
from rdflib.paths import Path

uri_tplt = "http://example.org/%s"

def test_path_div_future():
    path = URIRef(uri_tplt % "one") / URIRef(uri_tplt % "other")
    assert isinstance(path, Path)
