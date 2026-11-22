from __future__ import annotations

from rdflib import BNode, Graph, Literal, Namespace, URIRef

DATA = """
{
  "@context": {
    "@version": 1.1,
    "ex": "https://example.com/",
    "@base": "https://example.com/res/",
    "id": "@id",
    "test": {
      "@id": "ex:test",
      "@context": {
        "id": "ex:id"
      }
    }
  },
  "id": "parent",
  "test": [
    { "id": "item1" },
    { "id": "item2" }
  ]
}
"""

DATA_OK = """
<https://example.com/res/parent> <https://example.com/test> _:b0 .
<https://example.com/res/parent> <https://example.com/test> _:b1 .
_:b0 <https://example.com/id> "item1" .
_:b1 <https://example.com/id> "item2" .
"""

EX = Namespace("https://example.com/")


def test_reassign_id():
    g = Graph().parse(data=DATA, format="json-ld")
    # g = Graph().parse(data=DATA_OK)

    parent = URIRef("https://example.com/res/parent")
    ex_id = EX.id
    ex_test = EX.test

    objects = list(g.objects(parent, ex_test))

    assert len(g) == 4
    assert len(objects) == 2
    for obj in objects:
        assert isinstance(obj, BNode)
        obj_pred_objects = list(g.predicate_objects(obj))
        assert len(obj_pred_objects) == 1
        assert obj_pred_objects[0][0] == ex_id
        assert isinstance(obj_pred_objects[0][1], Literal)
