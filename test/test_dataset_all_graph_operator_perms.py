import pytest
import os
from rdflib import (
    Graph,
    ConjunctiveGraph,
    Dataset,
    URIRef,
)


michel = URIRef("urn:michel")
tarek = URIRef("urn:tarek")
bob = URIRef("urn:bob")
likes = URIRef("urn:likes")
hates = URIRef("urn:hates")
pizza = URIRef("urn:pizza")
cheese = URIRef("urn:cheese")

c1 = URIRef("urn:context-1")
c2 = URIRef("urn:context-2")

sportquadstrig = open(
    os.path.join(os.path.dirname(__file__), "consistent_test_data", "sportquads.trig")
).read()


# @pytest.mark.skip
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


# @pytest.mark.skip
def test_reversed_operators_with_conjunctivegraph_and_graph():

    cg = ConjunctiveGraph()
    cg.add((tarek, likes, pizza))
    cg.add((tarek, likes, michel))

    g = Graph()
    g.add([tarek, likes, pizza])
    g.add([tarek, likes, cheese])

    # logger.debug(
    #     "add\n"
    #     f"g:\n{g.serialize(format='json-ld')}\n"
    #     f"cg\n{cg.serialize(format='json-ld')}\n"
    #     f"(g+cg)\n{(g + cg).serialize(format='json-ld')})"
    # )

    assert len(g + cg) == 3  # adds cheese as liking

    # logger.debug(
    #     "add\n"
    #     f"g:\n{g.serialize(format='json-ld')}\n"
    #     f"cg\n{cg.serialize(format='json-ld')}\n"
    #     f"(g-cg)\n{(g - cg).serialize(format='json-ld')})"
    # )

    assert len(g - cg) == 1  # removes pizza

    # logger.debug(
    #     "add\n"
    #     f"g:\n{g.serialize(format='json-ld')}\n"
    #     "cg\n{cg.serialize(format='json-ld')}\n"
    #     f"(g*cg)\n{(g * cg).serialize(format='json-ld')})"
    # )

    assert len(g * cg) == 1  # only pizza

    # logger.debug(
    #     "add\n"
    #     f"g:\n{g.serialize(format='json-ld')}\n"
    #     f"cg\n{cg.serialize(format='json-ld')}\n"
    #     f"(g*cg)\n{(g ^ cg).serialize(format='json-ld')})"
    # )

    assert len(g ^ cg) == 2  # removes pizza, adds cheese


# @pytest.mark.skip
def test_reversed_operators_with_conjunctivegraph_with_contexts_and_graph():

    cg = ConjunctiveGraph()
    cg.add((tarek, likes, pizza))
    cg.add((tarek, likes, michel))
    cg.parse(data=sportquadstrig, format="trig")

    g = Graph()
    g.add([tarek, likes, pizza])
    g.add([tarek, likes, cheese])

    # logger.debug(
    #     "add\n"
    #     # f"g:\n{g.serialize(format='json-ld')}\n"
    #     f"type (g + cg)\n{type((g + cg))}\n"
    #     f"(g+cg) trig\n{(g + cg).serialize(format='trig')})"
    #     f"(g+cg json-ld)\n{(g + cg).serialize(format='json-ld')})"
    # )

    assert len(g + cg) == 10  # adds cheese as liking plus sevenquads

    assert len(list((g + cg).triples((None, None, None)))) == 10

    # logger.debug(
    #     "sub\n"
    #     # f"g:\n{g.serialize(format='json-ld')}\n"
    #     # f"cg\n{cg.serialize(format='json-ld')}\n"
    #     f"(g-cg)\n{(g - cg).serialize(format='json-ld')})"
    # )

    assert len(g - cg) == 1  # removes pizza

    # logger.debug(
    #     "mul\n"
    #     # f"g:\n{g.serialize(format='json-ld')}\n"
    #     # "cg\n{cg.serialize(format='json-ld')}\n"
    #     f"(g*cg)\n{(g * cg).serialize(format='json-ld')})"
    # )

    assert len(g * cg) == 1  # only pizza

    # logger.debug(
    #     "xor\n"
    #     # f"g:\n{g.serialize(format='json-ld')}\n"
    #     # f"cg\n{cg.serialize(format='json-ld')}\n"
    #     f"(g*cg)\n{(g ^ cg).serialize(format='json-ld')})"
    # )

    assert len(g ^ cg) == 9  # removes pizza, adds cheese and sevenquads


# @pytest.mark.skip
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

    # logger.debug(
    #     "add\n"
    #     f"cg1:\n{cg1.serialize(format='json-ld')}\n"
    #     f"cg2\n{cg2.serialize(format='json-ld')}\n"
    #     f"(cg1^cg2)\n{(cg1 ^ cg2).serialize(format='json-ld')})"
    # )

    assert len(cg1 ^ cg2) == 2  # removes pizza, adds cheese


# @pytest.mark.skip
def test_operators_with_two_conjunctivegraphs_one_with_contexts():

    cg1 = ConjunctiveGraph()
    cg1.add([tarek, likes, pizza])
    cg1.add([tarek, likes, michel])

    cg2 = ConjunctiveGraph()
    cg2.add([tarek, likes, pizza])
    cg2.add([tarek, likes, cheese])
    cg2.parse(data=sportquadstrig, format="trig")

    # logger.debug(
    #     "sub\n"
    #     f"cg1:\n{cg1.serialize(format='json-ld')}\n"
    #     f"cg2\n{cg2.serialize(format='json-ld')}\n"
    #     f"(cg1+cg2)\n{(cg1 + cg2).serialize(format='json-ld')})"
    # )

    assert len(cg1 + cg2) == 10  # adds cheese as liking and all seven quads

    # logger.debug(
    #     "sub\n"
    #     f"cg1:\n{cg1.serialize(format='json-ld')}\n"
    #     f"cg2\n{cg2.serialize(format='json-ld')}\n"
    #     f"(cg1-cg2)\n{(cg1 - cg2).serialize(format='json-ld')})"
    # )

    assert len(cg1 - cg2) == 1  # removes pizza

    # logger.debug(
    #     "sub\n"
    #     f"cg1:\n{cg1.serialize(format='json-ld')}\n"
    #     f"cg2\n{cg2.serialize(format='json-ld')}\n"
    #     f"(cg1*cg2)\n{(cg1 * cg2).serialize(format='json-ld')})"
    # )

    assert len(cg1 * cg2) == 1  # only pizza

    # logger.debug(
    #     "xor\n"
    #     f"cg1:\n{cg1.serialize(format='json-ld')}\n"
    #     f"cg2\n{cg2.serialize(format='json-ld')}\n"
    #     f"(cg1^cg2)\n{(cg1 ^ cg2).serialize(format='json-ld')})"
    # )

    assert len(cg1 ^ cg2) == 9  # removes pizza


# if __name__ == "__main__":
#     test_inplace_operators_with_dataset_and_graph()
