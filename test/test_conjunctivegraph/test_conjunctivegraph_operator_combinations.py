import os
from test.data import TEST_DATA_DIR, cheese, likes, michel, pizza, tarek

from rdflib import ConjunctiveGraph, Graph

sportquadstrig = open(os.path.join(TEST_DATA_DIR, "sportquads.trig")).read()


def test_operators_with_conjunctivegraph_and_graph():

    cg = ConjunctiveGraph()
    cg.add((tarek, likes, pizza))
    cg.add((tarek, likes, michel))

    g = Graph()
    g.add([tarek, likes, pizza])
    g.add([tarek, likes, cheese])

    assert len(cg + g) == 3  # adds cheese as liking

    assert len(cg - g) == 1  # removes pizza

    assert len(cg * g) == 1  # only pizza

    assert len(cg ^ g) == 2  # removes pizza, adds cheese


def test_reversed_operators_with_conjunctivegraph_and_graph():

    cg = ConjunctiveGraph()
    cg.add((tarek, likes, pizza))
    cg.add((tarek, likes, michel))

    g = Graph()
    g.add([tarek, likes, pizza])
    g.add([tarek, likes, cheese])

    assert len(g + cg) == 3  # adds cheese as liking

    assert len(g - cg) == 1  # removes pizza

    assert len(g * cg) == 1  # only pizza

    assert len(g ^ cg) == 2  # removes pizza, adds cheese


def test_reversed_operators_with_conjunctivegraph_with_contexts_and_graph():

    cg = ConjunctiveGraph()
    cg.add((tarek, likes, pizza))
    cg.add((tarek, likes, michel))
    cg.parse(data=sportquadstrig, format="trig")

    g = Graph()
    g.add([tarek, likes, pizza])
    g.add([tarek, likes, cheese])

    assert len(g + cg) == 10  # adds cheese as liking plus sevenquads

    assert len(list((g + cg).triples((None, None, None)))) == 10

    assert len(g - cg) == 1  # removes pizza

    assert len(g * cg) == 1  # only pizza

    assert len(g ^ cg) == 9  # removes pizza, adds cheese and sevenquads


def test_operators_with_two_conjunctivegraphs():

    cg1 = ConjunctiveGraph()
    cg1.add([tarek, likes, pizza])
    cg1.add([tarek, likes, michel])

    cg2 = ConjunctiveGraph()
    cg2.add([tarek, likes, pizza])
    cg2.add([tarek, likes, cheese])

    assert len(cg1 + cg2) == 3  # adds cheese as liking

    assert len(cg1 - cg2) == 1  # removes pizza from cg1

    assert len(cg1 * cg2) == 1  # only pizza

    assert len(cg1 + cg2) == 3  # adds cheese as liking

    assert len(cg1 ^ cg2) == 2  # removes pizza, adds cheese


def test_operators_with_two_conjunctivegraphs_one_with_contexts():

    cg1 = ConjunctiveGraph()
    cg1.add([tarek, likes, pizza])
    cg1.add([tarek, likes, michel])

    cg2 = ConjunctiveGraph()
    cg2.add([tarek, likes, pizza])
    cg2.add([tarek, likes, cheese])
    cg2.parse(data=sportquadstrig, format="trig")

    assert len(cg1 + cg2) == 10  # adds cheese as liking and all seven quads

    assert len(cg1 - cg2) == 1  # removes pizza

    assert len(cg1 * cg2) == 1  # only pizza

    assert len(cg1 ^ cg2) == 9  # removes pizza
