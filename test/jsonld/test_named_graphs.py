# -*- coding: UTF-8 -*-
from rdflib import *
from rdflib.plugin import register, Parser

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


def test_graph():
    g = Graph()
    g.parse(data=data, format="application/ld+json")
    assert len(g) == 2


def test_conjunctive_graph():
    cg = ConjunctiveGraph()
    cg.default_context.parse(data=data, format="application/ld+json")
    assert len(cg) == 3

    print(
        "default graph (%s) contains %s triples (expected 2)"
        % (cg.identifier, len(cg.default_context))
    )
    for ctx in cg.contexts():
        print("named graph (%s) contains %s triples" % (ctx.identifier, len(ctx)))
    assert len(cg.default_context) == 2
    assert len(list(cg.contexts())) == 2


def test_dataset():
    ds = Dataset()
    ds.default_context.parse(data=data, format="application/ld+json")
    assert len(ds) == 3

    assert len(ds.default_context) == 2
    print(
        "default graph (%s) contains %s triples (expected 2)"
        % (ds.identifier, len(ds.default_context))
    )
    contexts = dict((ctx.identifier, ctx) for ctx in ds.contexts())
    assert len(contexts) == 2
    assert len(contexts.pop(meta_ctx)) == 1
    assert len(list(contexts.values())[0]) == 2
