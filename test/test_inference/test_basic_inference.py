from pathlib import Path

from rdflib import Graph, Namespace
from rdflib.namespace import RDF
from rdflib.plugins.inference import DeductiveClosure
from rdflib.plugins.inference.owlrl import OWLRL_Semantics

RELS = Namespace("http://example.org/relatives#")


def test_basic_inference():
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
    DeductiveClosure(OWLRL_Semantics).expand(g)

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


def test_basic_inference_query():
    # create an RDF graph, load a simple OWL ontology and data
    g = Graph().parse(Path(__file__).parent / "relatives.ttl")

    # count no. rels:Person class instances, no inferencing, should find 14 results (one Child)
    assert len(list(g.subjects(predicate=RDF.type, object=RELS.Person))) == 14

    # count no. of hasGrandparent predicates, no inferencing, should find 0 results
    assert len(list(g.subject_objects(predicate=RELS.hasGrandparent))) == 0

    # expand the graph with OWL-RL semantics
    rules = ""
    res = g.query(rules, processor="owlrl")

    g += res.graph

    # count no. rels:Person class instances, after inferencing, should find 15 results
    assert len(list(g.subjects(predicate=RDF.type, object=RELS.Person))) == 15

    # count no. of hasGrandparent predicates, after inferencing, should find 7 results
    assert len(list(g.subject_objects(predicate=RELS.hasGrandparent))) == 7


def test_basic_inference_update():
    # create an RDF graph, load a simple OWL ontology and data
    g = Graph().parse(Path(__file__).parent / "relatives.ttl")

    orig_len = len(g)
    assert orig_len == 59

    # count no. rels:Person class instances, no inferencing, should find 14 results (one Child)
    assert len(list(g.subjects(predicate=RDF.type, object=RELS.Person))) == 14

    # count no. of hasGrandparent predicates, no inferencing, should find 0 results
    assert len(list(g.subject_objects(predicate=RELS.hasGrandparent))) == 0

    # expand the graph with OWL-RL semantics
    rules = ""
    g.update(rules, processor="owlrl")

    expanded_len = len(g)
    assert expanded_len == 250

    n_statements_added = expanded_len - orig_len
    assert n_statements_added == 191

    # count no. rels:Person class instances, after inferencing, should find 15 results
    assert len(list(g.subjects(predicate=RDF.type, object=RELS.Person))) == 15

    # count no. of hasGrandparent predicates, after inferencing, should find 7 results
    assert len(list(g.subject_objects(predicate=RELS.hasGrandparent))) == 7


def test_basic_inference_query_with_augmented_axioms():
    # create an RDF graph, load a simple OWL ontology and data
    g = Graph().parse(Path(__file__).parent / "relatives.ttl")

    # count no. rels:Person class instances, no inferencing, should find 14 results (one Child)
    assert len(list(g.subjects(predicate=RDF.type, object=RELS.Person))) == 14

    # count no. of hasGrandparent predicates, no inferencing, should find 0 results
    assert len(list(g.subject_objects(predicate=RELS.hasGrandparent))) == 0

    # count no. of hasGrandchild predicates, no inferencing, should find 0 results
    assert len(list(g.subject_objects(predicate=RELS.hasGrandchild))) == 0

    # expand the graph with OWL-RL semantics
    rules = """@prefix : <http://example.org/relatives#> .
    @prefix owl: <http://www.w3.org/2002/07/owl#> .

    :hasGrandchild a owl:ObjectProperty ;
        owl:propertyChainAxiom ( :hasChild :hasChild ) .
    """
    res = g.query(rules, processor="owlrl")

    g += res.graph

    # count no. rels:Person class instances, after inferencing, should find 15 results
    assert len(list(g.subjects(predicate=RDF.type, object=RELS.Person))) == 15

    # count no. of hasGrandparent predicates, after inferencing, should find 7 results
    assert len(list(g.subject_objects(predicate=RELS.hasGrandparent))) == 7

    # count no. of hasGrandchild predicates, after inferencing, should find 7 results
    assert len(list(g.subject_objects(predicate=RELS.hasGrandchild))) == 7


def test_basic_inference_update_with_augmented_axioms():
    # create an RDF graph, load a simple OWL ontology and data
    g = Graph().parse(Path(__file__).parent / "relatives.ttl")

    # count no. rels:Person class instances, no inferencing, should find 14 results (one Child)
    assert len(list(g.subjects(predicate=RDF.type, object=RELS.Person))) == 14

    # count no. of hasGrandparent predicates, no inferencing, should find 0 results
    assert len(list(g.subject_objects(predicate=RELS.hasGrandparent))) == 0

    # count no. of hasGrandchild predicates, no inferencing, should find 0 results
    assert len(list(g.subject_objects(predicate=RELS.hasGrandchild))) == 0

    # expand the graph with OWL-RL semantics
    rules = """@prefix : <http://example.org/relatives#> .
    @prefix owl: <http://www.w3.org/2002/07/owl#> .

    :hasGrandchild a owl:ObjectProperty ;
        owl:propertyChainAxiom ( :hasChild :hasChild ) .
    """
    g.update(rules, processor="owlrl")

    # count no. rels:Person class instances, after inferencing, should find 15 results
    assert len(list(g.subjects(predicate=RDF.type, object=RELS.Person))) == 15

    # count no. of hasGrandparent predicates, after inferencing, should find 7 results
    assert len(list(g.subject_objects(predicate=RELS.hasGrandparent))) == 7

    # count no. of hasGrandchild predicates, after inferencing, should find 7 results
    assert len(list(g.subject_objects(predicate=RELS.hasGrandchild))) == 7
