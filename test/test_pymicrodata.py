import os

# import pytest
from rdflib import Graph
from rdflib.compare import to_isomorphic


def test_microdata():

    path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "pymicrodata")

    # tg = Graph()
    # tg.parse(location="https://en.wikipedia.org/wiki/Australian_Labor_Party")

    for test in ["minischema", "schema", "test1", "test2", "test3"]:

        # HTML containing microdata
        htmlfile = os.path.join(path, test + ".html")

        # Expected RDF statements
        turtlefile = os.path.join(path, test + ".ttl")

        rdf_from_html = Graph()
        with open(htmlfile, "r") as df:
            rdf_from_html.parse(data=df.read(), format="microdata")

        expected_rdf = Graph()
        with open(turtlefile, "r") as df:
            expected_rdf.parse(data=df.read())

        assert to_isomorphic(rdf_from_html) == to_isomorphic(expected_rdf)
