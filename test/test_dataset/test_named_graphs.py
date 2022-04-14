# -*- coding: UTF-8 -*-
import pytest

from rdflib import *
from rdflib.plugin import Parser, register

register("json-ld", Parser, "rdflib.plugins.parsers.jsonld", "JsonLDParser")
register("application/ld+json", Parser, "rdflib.plugins.parsers.jsonld", "JsonLDParser")

data = """
{
    "@context": {"@vocab": "http://schema.org/"},
    "@graph": [
        { "@id": "http://example.org/data#jdoe",
          "name": "John"
        },
        { "@id": "http://example.org/data#janedoe",
          "name": "Jane"
        },
        { "@id": "http://example.org/data#metadata",
          "@graph": [
              { "@id": "http://example.org/data",
                "creator": "http://example.org/data#janedoe"
              }
          ]
        }
    ]
}
"""

meta_ctx = URIRef("http://example.org/data#metadata")


@pytest.mark.xfail(reason="Reading JSON-LD into a Graph")
def test_graph():
    g = Graph()
    g.parse(data=data, format="application/ld+json")
    assert len(g) == 2


def test_dataset_acting_as_conjunctive_graph():
    cg = Dataset(default_union=True)
    cg.default_graph.parse(data=data, format="application/ld+json")
    assert len(cg) == 3

    print(
        "default graph (%s) contains %s triples (expected 2)"
        % (cg, len(cg.default_graph))
    )
    for g in cg.graphs():
        print("named graph (%s) contains %s triples" % (g.identifier, len(g)))

    assert len(cg.default_graph) == 2
    assert len(list(cg.graphs())) == 1


def test_dataset():
    ds = Dataset()
    ds.default_graph.parse(data=data, format="application/ld+json")

    assert len(ds) == 2
    assert len(ds.default_graph) == 2

    print(
        "default graph (%s) contains %s triples (expected 2)"
        % (ds.identifier, len(ds.default_graph))
    )
    contexts = dict((g.identifier, g) for g in ds.graphs())
    assert len(contexts) == 1
    assert len(contexts.pop(meta_ctx)) == 1
    assert len(ds.default_graph) == 2
