import os

from rdflib import ConjunctiveGraph, Graph
from test.data import CHEESE, LIKES, MICHEL, PIZZA, TAREK, TEST_DATA_DIR

sportquadstrig = open(os.path.join(TEST_DATA_DIR, "sportquads.trig")).read()


def test_operators_with_conjunctivegraph_and_graph():
    cg = ConjunctiveGraph()
    cg.add((TAREK, LIKES, PIZZA))
    cg.add((TAREK, LIKES, MICHEL))

    g = Graph()
    g.add([TAREK, LIKES, PIZZA])
    g.add([TAREK, LIKES, CHEESE])

    assert len(cg + g) == 3  # adds CHEESE as liking

    assert len(cg - g) == 1  # removes PIZZA

    assert len(cg * g) == 1  # only PIZZA

    assert len(cg ^ g) == 2  # removes PIZZA, adds CHEESE


def test_reversed_operators_with_conjunctivegraph_and_graph():
    cg = ConjunctiveGraph()
    cg.add((TAREK, LIKES, PIZZA))
    cg.add((TAREK, LIKES, MICHEL))

    g = Graph()
    g.add([TAREK, LIKES, PIZZA])
    g.add([TAREK, LIKES, CHEESE])

    assert len(g + cg) == 3  # adds CHEESE as liking

    assert len(g - cg) == 1  # removes PIZZA

    assert len(g * cg) == 1  # only PIZZA

    assert len(g ^ cg) == 2  # removes PIZZA, adds CHEESE


def test_reversed_operators_with_conjunctivegraph_with_contexts_and_graph():
    cg = ConjunctiveGraph()
    cg.add((TAREK, LIKES, PIZZA))
    cg.add((TAREK, LIKES, MICHEL))
    cg.parse(data=sportquadstrig, format="trig")

    g = Graph()
    g.add([TAREK, LIKES, PIZZA])
    g.add([TAREK, LIKES, CHEESE])

    assert len(g + cg) == 10  # adds CHEESE as liking plus sevenquads

    assert len(list((g + cg).triples((None, None, None)))) == 10

    assert len(g - cg) == 1  # removes PIZZA

    assert len(g * cg) == 1  # only PIZZA

    assert len(g ^ cg) == 9  # removes PIZZA, adds CHEESE and sevenquads


def test_operators_with_two_conjunctivegraphs():
    cg1 = ConjunctiveGraph()
    cg1.add([TAREK, LIKES, PIZZA])
    cg1.add([TAREK, LIKES, MICHEL])

    cg2 = ConjunctiveGraph()
    cg2.add([TAREK, LIKES, PIZZA])
    cg2.add([TAREK, LIKES, CHEESE])

    assert len(cg1 + cg2) == 3  # adds CHEESE as liking

    assert len(cg1 - cg2) == 1  # removes PIZZA from cg1

    assert len(cg1 * cg2) == 1  # only PIZZA

    assert len(cg1 + cg2) == 3  # adds CHEESE as liking

    assert len(cg1 ^ cg2) == 2  # removes PIZZA, adds CHEESE


def test_operators_with_two_conjunctivegraphs_one_with_contexts():
    cg1 = ConjunctiveGraph()
    cg1.add([TAREK, LIKES, PIZZA])
    cg1.add([TAREK, LIKES, MICHEL])

    cg2 = ConjunctiveGraph()
    cg2.add([TAREK, LIKES, PIZZA])
    cg2.add([TAREK, LIKES, CHEESE])
    cg2.parse(data=sportquadstrig, format="trig")

    assert len(cg1 + cg2) == 10  # adds CHEESE as liking and all seven quads

    assert len(cg1 - cg2) == 1  # removes PIZZA

    assert len(cg1 * cg2) == 1  # only PIZZA

    assert len(cg1 ^ cg2) == 9  # removes PIZZA


def test_operators_returning_correct_type():
    g1 = ConjunctiveGraph()
    g2 = ConjunctiveGraph()
    assert type(g1 + g2) is ConjunctiveGraph
    assert type(g1 - g2) is ConjunctiveGraph
    assert type(g1 * g2) is ConjunctiveGraph
    assert type(g1 ^ g2) is ConjunctiveGraph
