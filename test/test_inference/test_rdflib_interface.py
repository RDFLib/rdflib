from copy import deepcopy
from pathlib import Path
from typing import Any

import pytest

from rdflib import Graph, Namespace
from rdflib.graph import _ConjunctiveGraphT, _TripleOrOptionalQuadType
from rdflib.namespace import RDF, RDFS

RELS = Namespace("http://example.org/relatives#")


class ImmutableWrapper:
    def __init__(self, obj: Any):
        # 1. Take a deep copy so external modifications don't affect this object
        # 2. Use __dict__ directly to bypass our own __setattr__ during setup
        self.__dict__["_frozen_obj"] = deepcopy(obj)

    def __getattr__(self, name: str) -> Any:
        # Forward attribute access to the underlying object
        attr = getattr(self._frozen_obj, name)

        if callable(attr):
            return attr

        # 3. Recursively wrap returned custom objects or callable methods
        if hasattr(attr, "__dict__") or isinstance(attr, (list, dict, set)):
            return freeze(attr)
        return attr

    def __setattr__(self, name: str, value: Any):
        raise AttributeError("This object is immutable. Cannot modify attributes.")

    def __delattr__(self, name: str):
        raise AttributeError("This object is immutable. Cannot delete attributes.")

    def __repr__(self) -> str:
        return f"Immutable({repr(self._frozen_obj)})"

    def __len__(self) -> int:
        return self._frozen_obj.__len__()

    def add(  # type: ignore[misc]
        self: _ConjunctiveGraphT,
        triple_or_quad: _TripleOrOptionalQuadType,
    ):
        raise ValueError("This object is immutable: you cannot add to it.")

    @property  # type: ignore[misc]
    def __class__(self):
        # Override the __class__ attribute to return TargetClass
        return Graph


# Helper function to recursively freeze standard collections too
def freeze(obj: Any) -> Any:
    if callable(obj):
        return obj
    if isinstance(obj, list):
        return tuple(freeze(item) for item in obj)
    if isinstance(obj, dict):
        return {k: freeze(v) for k, v in obj.items()}
    if isinstance(obj, set):
        return frozenset(freeze(item) for item in obj)

    # This check now safely evaluates because ImmutableWrapper is already declared
    if hasattr(obj, "__dict__") and not isinstance(obj, ImmutableWrapper):
        return ImmutableWrapper(obj)
    return obj


def test_basic_inference_rdfs():
    # create an RDF graph, load a simple OWL ontology and data
    g = Graph().parse(Path(__file__).parent / "relatives.ttl")

    # count no. rels:Person class instances, no inferencing, should find 14 results (one Child)
    cnt = 0
    for _ in g.subjects(predicate=RDF.type, object=RELS.Person):
        cnt += 1

    assert cnt == 14

    # count no. of hasGrandparent predicates, no inferencing, should find 0 results
    cnt = 0
    for _ in g.subject_objects(predicate=RELS.hasGrandparent):
        cnt += 1
    assert cnt == 0

    # expand the graph with RDFS semantics
    g.expand("RDFS")

    # check rdfs:Resource has been applied to all :Person instances
    assert (RELS.Jacob, RDF.type, RDFS.Resource) in g

    # count no. rels:Person class instances, after inferencing, should find 15 results
    cnt = 0
    for _ in g.subjects(predicate=RDF.type, object=RELS.Person):
        cnt += 1

    assert cnt == 15

    with pytest.raises(NotImplementedError):
        g.expand("SPARQLRULES")

    g = Graph().parse(Path(__file__).parent / "relatives.ttl")
    x = g.expand("RDFS")
    assert x is None

    g = Graph().parse(Path(__file__).parent / "relatives.ttl")
    x = g.expand("RDFS", in_place=False)
    assert isinstance(x, Graph)

    g = Graph().parse(Path(__file__).parent / "relatives.ttl")
    x = freeze(g)
    x.expand("RDFS")

    assert isinstance(x, Graph)
    assert len(g) == 59  # the original length of g
    assert len(x) == 108  # the length of g expanded


def test_basic_inference_owlrl():
    # create an RDF graph, load a simple OWL ontology and data
    g = Graph().parse(Path(__file__).parent / "relatives.ttl")

    # count no. rels:Person class instances, no inferencing, should find 14 results (one Child)
    cnt = 0
    for _ in g.subjects(predicate=RDF.type, object=RELS.Person):
        cnt += 1

    assert cnt == 14

    # count no. of hasGrandparent predicates, no inferencing, should find 0 results
    cnt = 0
    for _ in g.subject_objects(predicate=RELS.hasGrandparent):
        cnt += 1
    assert cnt == 0

    # expand the graph with OWL-RL semantics
    g.expand("OWLRL")

    # count no. rels:Person class instances, after inferencing, should find 15 results
    cnt = 0
    for _ in g.subjects(predicate=RDF.type, object=RELS.Person):
        cnt += 1

    assert cnt == 15

    # count no. of hasGrandparent predicates, after inferencing, should find 7 results
    cnt = 0
    for _ in g.subject_objects(predicate=RELS.hasGrandparent):
        cnt += 1
    assert cnt == 7
