import pytest

from rdflib.compare import graph_diff
from rdflib.graph import Dataset, Graph

jsonld_a = """[
  {
    "@id": "_:N4cd2c0228715435aa65e5046b11e4746",
    "http://www.w3.org/ns/prov#entity": [
      {
        "@id": "http://example.org/e1"
      }
    ]
  },
  {
    "@id": "_:Nf115bd3e6d9a476795daff61e26ffee8",
    "@type": [
      "http://www.w3.org/ns/prov#Derivation"
    ]
  },
  {
    "@id": "_:N7acd074b6795446ea8d8f8a248379abc",
    "http://www.w3.org/ns/prov#hadActivity": [
      {
        "@id": "http://example.org/a"
      }
    ]
  },
  {
    "@id": "_:Na7aa648c02434ee09ff4f456e14b74f9",
    "http://www.w3.org/ns/prov#hadGeneration": [
      {
        "@id": "http://example.org/g"
      }
    ]
  },
  {
    "@id": "http://example.org/e2",
    "http://www.w3.org/ns/prov#qualifiedDerivation": [
      {
        "@id": "_:N5ffbac84c4a74b9bbfa8f2cd5ccaab9a"
      }
    ]
  },
  {
    "@id": "_:N5ffbac84c4a74b9bbfa8f2cd5ccaab9a"
  },
  {
    "@id": "_:Nbc06ed3b41f44a9fb8e4efcd47df0a62",
    "http://www.w3.org/ns/prov#hadUsage": [
      {
        "@id": "http://example.org/u"
      }
    ]
  }
]"""

jsonld_b = """[
  {
    "@id": "_:N8b1785088f964f23beb556dfffdc2963",
    "http://www.w3.org/ns/prov#entity": [
      {
        "@id": "http://example.org/e1"
      }
    ]
  },
  {
    "@id": "_:N971d5a0e2f9d44bb88a29c30aae74d37",
    "http://www.w3.org/ns/prov#hadGeneration": [
      {
        "@id": "http://example.org/g"
      }
    ]
  },
  {
    "@id": "_:N92f811dd984e40cb83034c2aceecf71a",
    "http://www.w3.org/ns/prov#hadActivity": [
      {
        "@id": "http://example.org/a"
      }
    ]
  },
  {
    "@id": "_:N6d1a17f44bea46659ce669a5ce0cfda8",
    "@type": [
      "http://www.w3.org/ns/prov#Derivation"
    ]
  },
  {
    "@id": "http://example.org/e2",
    "http://www.w3.org/ns/prov#qualifiedDerivation": [
      {
        "@id": "_:Nadcc6322a0db46c5b1619abb7cee8595"
      }
    ]
  },
  {
    "@id": "_:Nadcc6322a0db46c5b1619abb7cee8595"
  },
  {
    "@id": "_:Nf51434bd0b05445b90525d8f40c19f90",
    "http://www.w3.org/ns/prov#hadUsage": [
      {
        "@id": "http://example.org/u"
      }
    ]
  }
]"""

nquads_a = """
<http://example.org/vocab#test> <http://example.org/vocab#A> _:b0 .
<http://example.org/vocab#test> <http://example.org/vocab#B> _:b1 .
_:b0 <http://example.org/vocab#next> _:b2 .
_:b1 <http://example.org/vocab#next> _:b2 .
"""

nquads_b = """
<http://example.org/vocab#test> <http://example.org/vocab#A> _:c14n2 .
<http://example.org/vocab#test> <http://example.org/vocab#B> _:c14n0 .
_:c14n0 <http://example.org/vocab#next> _:c14n1 .
_:c14n2 <http://example.org/vocab#next> _:c14n1 .
"""


@pytest.mark.xfail(reason="incorrect graph_diff with JSON-LD")
def test_graph_diff_ds_jsonld():
    ds1 = Dataset().parse(data=jsonld_a, format="json-ld")
    ds2 = Dataset().parse(data=jsonld_b, format="json-ld")
    in_both, in_first, in_second = graph_diff(ds1, ds2)
    assert len(list(in_both)) == 6


@pytest.mark.xfail(reason="incorrect graph_diff with N-Quads")
def test_graph_diff_nquads():
    ds1 = Dataset(default_union=True).parse(data=nquads_a, format="nquads")
    ds2 = Dataset(default_union=True).parse(data=nquads_b, format="nquads")
    in_both, in_first, in_second = graph_diff(ds1, ds2)
    assert len(list(in_both)) == 4

@pytest.mark.xfail(reason="incorrect graph_diff with N-Triples")
def test_graph_diff_nquads_actually_ntriples():
    g1 = Graph().parse(data=nquads_a, format="nt")
    g2 = Graph().parse(data=nquads_b, format="nt")
    in_both, in_first, in_second = graph_diff(g1, g2)
    assert len(list(in_both)) == 4
