from pathlib import Path

from rdflib import Dataset, Namespace, URIRef
from rdflib.namespace import RDF
from rdflib.plugins.inference import DeductiveClosure
from rdflib.plugins.inference.owlrl import OWLRL_Semantics

try:
    from rdflib.graph import ConjunctiveGraph

    # ConjunctiveGraph is going away in rdflib 8.0
except ImportError:
    ConjunctiveGraph = Dataset  # type: ignore[assignment, misc]


RELS = Namespace("http://example.org/relatives#")


def test_dataset():
    # create an RDF graph, load a simple OWL ontology and data
    d = Dataset()
    d.default_union = True
    g = d.default_context

    g.parse(Path(__file__).parent / "relatives.ttl")

    # count no. rels:Person class instances, no inferencing, should find 14 results (one Child)
    cnt = 0
    for _ in d.subjects(predicate=RDF.type, object=RELS.Person):
        cnt += 1

    assert cnt == 14
    dest = d.graph(identifier=URIRef("urn:test:dest"))
    # count no. of hasGrandparent predicates, no inferencing, should find 0 results
    cnt = 0
    for _ in d.subject_objects(predicate=RELS.hasGrandparent):
        cnt += 1
    assert cnt == 0

    # expand the graph with OWL-RL semantics
    DeductiveClosure(OWLRL_Semantics).expand(d, destination=dest)

    # count no. rels:Person class instances, after inferencing, should find 1 result in the Dest graph
    cnt = 0
    for _ in dest.subjects(predicate=RDF.type, object=RELS.Person):
        cnt += 1

    assert cnt == 1

    # count no. rels:Person class instances, after inferencing, should find 15 results in the whole dataset
    cnt = 0
    for _ in d.subjects(predicate=RDF.type, object=RELS.Person):
        cnt += 1

    assert cnt == 15

    # count no. of hasGrandparent predicates, after inferencing, should find 7 results in the Dest graph
    cnt = 0
    for _ in dest.subject_objects(predicate=RELS.hasGrandparent):
        cnt += 1
    assert cnt == 7

    # count no. of hasGrandparent predicates, after inferencing, should find 7 results in the whole dataset
    cnt = 0
    for _ in d.subject_objects(predicate=RELS.hasGrandparent):
        cnt += 1
    assert cnt == 7

    # count no. of hasGrandparent predicates, after inferencing, should find 0 results in the default graph
    cnt = 0
    for _ in g.subject_objects(predicate=RELS.hasGrandparent):
        cnt += 1
    assert cnt == 0


def test_conjunctive_graph():
    # create an RDF graph, load a simple OWL ontology and data
    d = ConjunctiveGraph()
    g = d.default_context

    g.parse(Path(__file__).parent / "relatives.ttl")

    # count no. rels:Person class instances, no inferencing, should find 14 results (one Child)
    cnt = 0
    for _ in d.subjects(predicate=RDF.type, object=RELS.Person):
        cnt += 1

    assert cnt == 14
    dest = d.get_context(URIRef("urn:test:dest"))
    # count no. of hasGrandparent predicates, no inferencing, should find 0 results
    cnt = 0
    for _ in d.subject_objects(predicate=RELS.hasGrandparent):
        cnt += 1
    assert cnt == 0

    # expand the graph with OWL-RL semantics
    DeductiveClosure(OWLRL_Semantics).expand(d, destination=dest)

    # count no. rels:Person class instances, after inferencing, should find 1 result in the Dest graph
    cnt = 0
    for _ in dest.subjects(predicate=RDF.type, object=RELS.Person):
        cnt += 1

    assert cnt == 1

    # count no. rels:Person class instances, after inferencing, should find 15 results in the whole dataset
    cnt = 0
    for _ in d.subjects(predicate=RDF.type, object=RELS.Person):
        cnt += 1

    assert cnt == 15

    # count no. of hasGrandparent predicates, after inferencing, should find 7 results in the Dest graph
    cnt = 0
    for _ in dest.subject_objects(predicate=RELS.hasGrandparent):
        cnt += 1
    assert cnt == 7

    # count no. of hasGrandparent predicates, after inferencing, should find 7 results in the whole dataset
    cnt = 0
    for _ in d.subject_objects(predicate=RELS.hasGrandparent):
        cnt += 1
    assert cnt == 7

    # count no. of hasGrandparent predicates, after inferencing, should find 0 results in the default graph
    cnt = 0
    for _ in g.subject_objects(predicate=RELS.hasGrandparent):
        cnt += 1
    assert cnt == 0
