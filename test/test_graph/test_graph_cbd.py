"""Tests the Graph class' cbd() function"""

import pytest

from rdflib import Graph, Namespace
from rdflib.namespace import RDF, RDFS
from rdflib.term import BNode, Literal, URIRef
from test.data import TEST_DATA_DIR
from test.utils import BNodeHandling, GraphHelper

EXAMPLE_GRAPH_FILE_PATH = TEST_DATA_DIR / "spec" / "cbd" / "example_graph.rdf"
EXAMPLE_GRAPH_CBD_FILE_PATH = TEST_DATA_DIR / "spec" / "cbd" / "example_graph_cbd.rdf"


EX = Namespace("http://ex/")


@pytest.fixture
def get_graph():
    g = Graph()
    # adding example data for testing
    g.parse(
        data="""
            PREFIX ex: <http://ex/>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

            ex:R1
              a rdf:Resource ;
              ex:hasChild ex:R2 , ex:R3 .

            ex:R2
              ex:propOne ex:P1 ;
              ex:propTwo ex:P2 .

            ex:R3
                ex:propOne ex:P3 ;
                ex:propTwo ex:P4 ;
                ex:propThree [
                    a rdf:Resource ;
                    ex:propFour "Some Literal" ;
                    ex:propFive ex:P5 ;
                    ex:propSix [
                        ex:propSeven ex:P7 ;
                    ] ;
                ] .
        """,
        format="turtle",
    )

    g.bind("ex", EX)
    yield g
    g.close()


def testCbd(get_graph):  # noqa: N802
    g = get_graph
    assert len(g.cbd(EX.R1)) == 3, "cbd() for R1 should return 3 triples"

    assert len(g.cbd(EX.R2)) == 2, "cbd() for R3 should return 2 triples"

    assert len(g.cbd(EX.R3)) == 8, "cbd() for R3 should return 8 triples"

    assert len(g.cbd(EX.R4)) == 0, "cbd() for R4 should return 0 triples"


def testCbdReified(get_graph):  # noqa: N802
    g = get_graph
    # add some reified triples to the testing graph
    g.parse(
        data="""
            PREFIX ex: <http://ex/>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

            ex:R5
                ex:propOne ex:P1 ;
                ex:propTwo ex:P2 ;
                ex:propRei ex:Pre1 .

            ex:S
                a rdf:Statement ;
                rdf:subject ex:R5 ;
                rdf:predicate ex:propRei ;
                rdf:object ex:Pre1 ;
                ex:otherReiProp ex:Pre2 .
        """,
        format="turtle",
    )

    # this cbd() call should get the 3 basic triples with ex:R5 as subject as well as 5 more from the reified
    # statement
    assert len(g.cbd(EX.R5)) == (3 + 5), "cbd() for R5 should return 8 triples"
    assert len(g.cbd(EX.R5, include_reifications=False)) == (
        3 + 0
    ), "cbd() for R5 with no reifications should return 3 triples"

    # add crazy reified triples to the testing graph
    g.parse(
        data="""
            PREFIX ex: <http://ex/>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

            ex:R6
                ex:propOne ex:P1 ;
                ex:propTwo ex:P2 ;
                ex:propRei ex:Pre1 ;
                ex:propRei2 ex:Pre2 .

            ex:S1
                a rdf:Statement ;
                rdf:subject ex:R6 ;
                rdf:predicate ex:propRei ;
                rdf:object ex:Pre1 ;
                ex:otherReiProp ex:Pre3 .

            ex:S2
                rdf:subject ex:R6 ;
                rdf:predicate ex:propRei2 ;
                rdf:object ex:Pre2 ;
                ex:otherReiProp ex:Pre4 ;
                ex:otherReiProp ex:Pre5 .

            # This one should not be included because the statement this reifies is not in the graph
            ex:S3
                rdf:subject ex:R6 ;
                rdf:predicate ex:propRei3 ;
                rdf:object ex:Pre3 ;
                ex:otherReiProp ex:Pre4 ;
                ex:otherReiProp ex:Pre5 .
        """,
        format="turtle",
    )

    assert len(g.cbd(EX.R6)) == (4 + 5 + 5 + 0), "cbd() for R6 should return 14 triples"
    assert len(g.cbd(EX.R6, include_reifications=False)) == (
        4 + 0 + 0 + 0
    ), "cbd() for R6 with no reifications should return 4 triples"


def test_cbd_example():
    """
    Example from Concise Bounded Description definition at https://www.w3.org/Submission/CBD/#example
    """
    g = Graph()
    g.parse(EXAMPLE_GRAPH_FILE_PATH)

    g_cbd = Graph()
    g_cbd.parse(EXAMPLE_GRAPH_CBD_FILE_PATH)

    query = "http://example.com/aReallyGreatBook"
    GraphHelper.assert_isomorphic(g.cbd(URIRef(query)), g_cbd)
    GraphHelper.assert_sets_equals(g.cbd(URIRef(query)), g_cbd, BNodeHandling.COLLAPSE)
    assert len(g.cbd(URIRef(query))) == (
        21
    ), "cbd() for aReallyGreatBook should return 21 triples"


def test_cbd_target(rdfs_graph: Graph):
    """
    `Graph.cbd` places the Concise Bounded Description in the target graph.
    """

    target = Graph()
    result = rdfs_graph.cbd(RDFS.Literal, target_graph=target)

    expected_result = {
        (RDFS.Literal, RDFS.subClassOf, RDFS.Resource),
        (RDFS.Literal, RDF.type, RDFS.Class),
        (RDFS.Literal, RDFS.label, Literal("Literal")),
        (
            RDFS.Literal,
            RDFS.comment,
            Literal("The class of literal values, eg. textual strings and integers."),
        ),
        (RDFS.Literal, RDFS.isDefinedBy, URIRef(f"{RDFS}")),
    }

    assert result is target
    assert expected_result == set(result.triples((None, None, None)))


def test_cbd_rdf12_reification():
    """CBD Rule 3 includes RDF 1.2 reifiers linked via rdf:reifies."""
    g = Graph()
    g.add((EX.R1, EX.propOne, EX.P1))
    g.add((EX.R1, EX.propTwo, EX.P2))

    # Reify one of R1's triples using RDF 1.2 reification
    reifier = g.reify(EX.R1, EX.propOne, EX.P1, reifier=EX.rei1)
    # Add extra metadata on the reifier
    g.add((reifier, EX.certainty, Literal("0.9")))
    g.add((reifier, EX.source, EX.S1))

    cbd = g.cbd(EX.R1)

    # CBD should include: 2 triples about R1, 1 reifying triple, 2 reifier metadata
    assert (EX.R1, EX.propOne, EX.P1) in cbd
    assert (EX.R1, EX.propTwo, EX.P2) in cbd
    assert (EX.rei1, EX.certainty, Literal("0.9")) in cbd
    assert (EX.rei1, EX.source, EX.S1) in cbd
    # The rdf:reifies triple about the reifier should also be included
    assert len(list(cbd.triples((EX.rei1, RDF.reifies, None)))) == 1
    assert len(cbd) == 5


def test_cbd_rdf12_reification_multiple_reifiers():
    """CBD Rule 3 includes multiple RDF 1.2 reifiers of the same triple."""
    g = Graph()
    g.add((EX.R1, EX.knows, EX.R2))

    g.reify(EX.R1, EX.knows, EX.R2, reifier=EX.rei1)
    g.add((EX.rei1, EX.source, EX.S1))

    g.reify(EX.R1, EX.knows, EX.R2, reifier=EX.rei2)
    g.add((EX.rei2, EX.source, EX.S2))

    cbd = g.cbd(EX.R1)

    # 1 triple about R1 + 2 reifiers * (1 rdf:reifies + 1 metadata) = 5
    assert (EX.rei1, EX.source, EX.S1) in cbd
    assert (EX.rei2, EX.source, EX.S2) in cbd
    assert len(cbd) == 5


def test_cbd_rdf12_reification_with_bnode_reifier():
    """CBD Rule 3 follows BNode reifiers linked via rdf:reifies."""
    g = Graph()
    g.add((EX.R1, EX.propOne, EX.P1))

    # Reify with a blank node reifier
    reifier = g.reify(EX.R1, EX.propOne, EX.P1)
    g.add((reifier, EX.source, EX.S1))

    cbd = g.cbd(EX.R1)

    # 1 triple about R1 + 1 rdf:reifies + 1 metadata on bnode reifier = 3
    assert (EX.R1, EX.propOne, EX.P1) in cbd
    assert (reifier, EX.source, EX.S1) in cbd
    assert len(cbd) == 3


def test_cbd_rdf12_reification_reifier_with_bnode_object():
    """CBD Rule 3 recursively follows BNodes in reifier descriptions."""
    g = Graph()
    g.add((EX.R1, EX.propOne, EX.P1))

    reifier = g.reify(EX.R1, EX.propOne, EX.P1, reifier=EX.rei1)
    bn = BNode()
    g.add((reifier, EX.details, bn))
    g.add((bn, EX.note, Literal("important")))

    cbd = g.cbd(EX.R1)

    # 1 R1 triple + 1 rdf:reifies + 1 reifier->bnode + 1 bnode detail = 4
    assert (EX.R1, EX.propOne, EX.P1) in cbd
    assert (reifier, EX.details, bn) in cbd
    assert (bn, EX.note, Literal("important")) in cbd
    assert len(cbd) == 4


def test_cbd_rdf12_reification_no_false_match():
    """CBD Rule 3 does not include reifiers of triples not in the CBD."""
    g = Graph()
    g.add((EX.R1, EX.propOne, EX.P1))

    # Reify a triple about R2 (not R1)
    g.reify(EX.R2, EX.propOne, EX.P1, reifier=EX.rei1)
    g.add((EX.rei1, EX.source, EX.S1))

    cbd = g.cbd(EX.R1)

    # Only R1's own triple should be present
    assert len(cbd) == 1
    assert (EX.R1, EX.propOne, EX.P1) in cbd
    assert (EX.rei1, EX.source, EX.S1) not in cbd
