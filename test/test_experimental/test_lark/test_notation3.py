import pytest

from pprint import pformat

import rdflib
from rdflib import FOAF, Namespace
from rdflib.term import BNode, Literal, URIRef, Variable
from rdflib.graph import Dataset, Graph
from rdflib.compare import isomorphic

from test.data import TEST_DATA_DIR, context0

rdflib.plugin.register(
    "larkn3",
    rdflib.parser.Parser,
    "rdflib.plugins.parsers.larknotation3",
    "LarkN3Parser",
)

rdflib.plugin.register(
    "n3",
    rdflib.parser.Parser,
    "rdflib.plugins.parsers.notation3",
    "N3Parser",
)

LOG_NS = Namespace("http://www.w3.org/2000/10/swap/log#")

rulegraph1 = open(TEST_DATA_DIR / "rulegraph1.n3", "r").read()

rulegraph3 = open(TEST_DATA_DIR / "rulegraph3.n3", "r").read()


rulegraph1 = """@prefix : <urn:example:> .
@prefix log: <http://www.w3.org/2000/10/swap/log#> .
:bob :hasmother :alice .
:john :hasmother :alice .

@forAll :x, :y, :z .
{ :x :hasmother :z . :y :hasmother :z } log:implies { :x :issibling :y } .
"""


rulegraph1 = """@prefix : <urn:example:> .
@prefix log: <http://www.w3.org/2000/10/swap/log#> .
:bob :hasmother :alice .
:john :hasmother :alice . 

{ ?x :hasmother ?z . ?y :hasmother ?z } log:implies { ?x :issibling ?y } .
"""

rulegraph1 = """@prefix : <urn:example:> .
@prefix log: <http://www.w3.org/2000/10/swap/log#> .
:bob :hasmother :alice .
:john :hasmother :alice .

{ ?x :hasmother ?z . ?y :hasmother ?z } => { ?x :issibling ?y } .
"""

# testdata1 = """<http://example.org/#spiderman> <http://example.org/#enemyOf> <http://example.org/#green-goblin> .
# <http://example.org/#spiderman> <http://xmlns.com/foaf/0.1/name> "Spiderman" .
# <http://example.org/#green-goblin> <http://xmlns.com/foaf/0.1/name> "Green Goblin" .
# """


# def test_larknotation3():
#     g = Graph()
#     g.parse(
#         data=testdata1,
#         format="larkn3",
#     )
#     gs = sorted(list(g))
#     assert gs == [
#         (
#             rdflib.term.URIRef("http://example.org/#green-goblin"),
#             rdflib.term.URIRef("http://xmlns.com/foaf/0.1/name"),
#             rdflib.term.Literal("Green Goblin"),
#         ),
#         (
#             rdflib.term.URIRef("http://example.org/#spiderman"),
#             rdflib.term.URIRef("http://example.org/#enemyOf"),
#             rdflib.term.URIRef("http://example.org/#green-goblin"),
#         ),
#         (
#             rdflib.term.URIRef("http://example.org/#spiderman"),
#             rdflib.term.URIRef("http://xmlns.com/foaf/0.1/name"),
#             rdflib.term.Literal("Spiderman"),
#         ),
#     ]


# @pytest.mark.xfail(reason="WIP")
# def test_larknotation3_template():
#     d1 = Dataset()
#     d1.parse(
#         data=testdata,
#         format="larkn3",
#     )


def test_formula_extant_n3_parser():
    rulegraph1 = """@prefix : <urn:example:> .
@prefix log: <http://www.w3.org/2000/10/swap/log#> .
:bob :hasmother :alice .
:john :hasmother :alice .

{ ?x :hasmother ?z . ?y :hasmother ?z } => { ?x :issibling ?y } .
"""
    g = Graph()
    g.parse(
        data=rulegraph1,
        format="n3",
    )

    rule_statement = list(g.triples((None, LOG_NS.implies, None)))[0]

    assert (
        repr(rule_statement)
        == "(<Graph identifier=Formula2 (<class 'rdflib.graph.QuotedGraph'>)>, "
        + "rdflib.term.URIRef('http://www.w3.org/2000/10/swap/log#implies'), "
        + "<Graph identifier=Formula3 (<class 'rdflib.graph.QuotedGraph'>)>)"
    )

    quoted_graph_sub_obj = list(g.subject_objects(predicate=LOG_NS.implies))

    assert (
        str(quoted_graph_sub_obj)
        == "[("
        + "<Graph identifier=Formula2 (<class 'rdflib.graph.QuotedGraph'>)>, "
        + "<Graph identifier=Formula3 (<class 'rdflib.graph.QuotedGraph'>)>"
        + ")]"
    )

    formula1, formula2 = quoted_graph_sub_obj[0]

    assert sorted(list(formula1)) == [
        (
            Variable("x"),
            URIRef("urn:example:hasmother"),
            Variable("z"),
        ),
        (
            Variable("y"),
            URIRef("urn:example:hasmother"),
            Variable("z"),
        ),
    ]

    assert sorted(list(formula2)) == [
        (
            Variable("x"),
            URIRef("urn:example:issibling"),
            Variable("y"),
        )
    ]

    hashmotherrule = (Variable("y"), URIRef("urn:example:hasmother"), Variable("z"))

    sortedtriples = sorted(list(g))

    assert hashmotherrule not in sortedtriples


# @pytest.mark.xfail(reason="WIP")
def test_formula_lark_notation3_parser():
    rulegraph1 = """@prefix : <urn:example:> .
@prefix log: <http://www.w3.org/2000/10/swap/log#> .
:bob :hasmother :alice .
:john :hasmother :alice .

{ ?x :hasmother ?z . ?y :hasmother ?z } => { ?x :issibling ?y } .
"""
    g = Graph()
    g.parse(
        data=rulegraph1,
        format="larkn3",
    )

    rule_statement = list(g.triples((None, LOG_NS.implies, None)))[0]

    assert (
        repr(rule_statement)
        == "(<Graph identifier=Formula1 (<class 'rdflib.graph.QuotedGraph'>)>, "
        + "rdflib.term.URIRef('http://www.w3.org/2000/10/swap/log#implies'), "
        + "<Graph identifier=Formula2 (<class 'rdflib.graph.QuotedGraph'>)>)"
    )

    quoted_graph_sub_obj = list(g.subject_objects(predicate=LOG_NS.implies))

    assert (
        str(quoted_graph_sub_obj)
        == "[("
        + "<Graph identifier=Formula1 (<class 'rdflib.graph.QuotedGraph'>)>, "
        + "<Graph identifier=Formula2 (<class 'rdflib.graph.QuotedGraph'>)>"
        + ")]"
    )

    formula1, formula2 = quoted_graph_sub_obj[0]

    assert sorted(list(formula1)) == [
        (
            Variable("x"),
            URIRef("urn:example:hasmother"),
            Variable("z"),
        ),
        (
            Variable("y"),
            URIRef("urn:example:hasmother"),
            Variable("z"),
        ),
    ]

    assert sorted(list(formula2)) == [
        (
            Variable("x"),
            URIRef("urn:example:issibling"),
            Variable("y"),
        )
    ]

    # print(f"G:\n{g.serialize(format='n3')}")

    del formula1, formula2, rule_statement, quoted_graph_sub_obj, rulegraph1

    hashmotherrule = (Variable("y"), URIRef("urn:example:hasmother"), Variable("z"))

    sortedtriples = sorted(list(g))

    assert hashmotherrule not in sortedtriples


# @pytest.mark.skip("WIP")
# def test_larknotation3_with_forall():
#     ds = Dataset()
#     ds.parse(
#         data=rulegraph1,
#         format="larkn3",
#     )


#     # print(list(ds))
#     assert len(ds) == 3


# def test_compare_graphs_with_forall():
#     ds1 = Dataset()

#     ds1.parse(
#         data=rulegraph1,
#         format="n3",
#     )

#     assert len(ds1) == 3

#     ds2 = Dataset()

#     ds2.parse(
#         data=rulegraph1,
#         format="larkn3",
#     )

#     assert len(ds2) == 3

#     assert ds1.serialize(format="n3") == ds2.serialize(format="n3")


# def test_notation3_with_variables():
#     ds = Dataset()
#     ds.parse(
#         data=rulegraph3,
#         format="n3",
#     )

#     # print(list(ds))
#     assert len(ds) == 3


# def test_larknotation3_with_variables():
#     ds = Dataset()
#     ds.parse(
#         data=rulegraph3,
#         format="larkn3",
#     )

#     # print(list(ds))
#     assert len(ds) == 3


# def test_compare_graphs_without_variables():
#     ds1 = Dataset()

#     ds1.parse(
#         data=rulegraph3,
#         format="n3",
#     )

#     assert len(ds1) == 3

#     ds2 = Dataset()

#     ds2.parse(
#         data=rulegraph3,
#         format="larkn3",
#     )

#     assert len(ds2) == 3

#     assert ds1.serialize(format="n3") == ds2.serialize(format="n3")


# @pytest.mark.xfail(reason="WIP")
# def test_cwm_reasoning_parse():
#     data = """@prefix li:  <http://www.w3.org/2000/10/swap/list#> .
# @prefix : <urn:example:> .

# { ?x li:in (3 4 5) } => { ?x a :RESULT1 } .
# { ( :joe :fred :amy ) li:member ?y } => { ?y a :Friend } .

# { ( (3 4 5) (5 12 13) )!li:member li:member ?z } => { ?z a :Pythagorean } .

# # ends
# """
#     g = Graph()
#     g.parse(
#         data=data,
#         base="https://w3c.github.io/N3/tests/N3Tests/list-in.n3",
#         format="larkn3",
#     )
