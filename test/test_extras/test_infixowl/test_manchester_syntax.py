from test.data import TEST_DATA_DIR

import pytest

from rdflib import OWL, RDFS, Graph, Literal, Namespace
from rdflib.extras.infixowl import Class, Individual, manchesterSyntax

EXNS = Namespace("http://example.org/vocab/")
PZNS = Namespace(
    "http://www.co-ode.org/ontologies/pizza/2005/10/18/classified/pizza.owl#"
)


@pytest.fixture(scope="function")
def graph():
    g = Graph(identifier=EXNS.context0)
    g.bind("ex", EXNS)
    g.bind("pizza", PZNS)
    Individual.factoryGraph = g

    yield g

    del g


def test_manchester_syntax(graph):
    graph.parse(TEST_DATA_DIR / "owl" / "pizza.owl", format="xml")

    res = manchesterSyntax(
        PZNS.Caprina,
        graph,
        boolean=False,
        transientList=False,
    )
    assert res == Literal("Caprina", lang="pt")

    res = manchesterSyntax(
        PZNS.Caprina,
        graph,
        boolean=False,
        transientList=True,
    )
    assert res == Literal("Caprina", lang="pt")


def test_manchester_syntax_parse_with_transientlist(graph):

    graph.parse(TEST_DATA_DIR / "owl" / "pizza.owl", format="xml")

    res = manchesterSyntax(
        PZNS.Caprina,
        graph,
        boolean=False,
        transientList=False,
    )

    assert res == Literal("Caprina", lang="pt")

    assert (
        PZNS.SloppyGiuseppe,
        RDFS.label,
        Literal("SloppyGiuseppe", lang="pt"),
    ) in graph

    Class(PZNS.Caprina).complementOf = Class(PZNS.SloppyGiuseppe)

    res = manchesterSyntax(
        PZNS.Caprina,
        graph,
        boolean=OWL.complementOf,
        transientList=True,
    )

    assert res == "( NOT SloppyGiuseppe )"
