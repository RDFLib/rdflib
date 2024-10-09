from __future__ import annotations

import logging
import re
from typing import Pattern, Union

import pytest

from rdflib import Graph
from rdflib.term import BNode, Literal, URIRef
from test.utils import GraphHelper
from test.utils.namespace import EGDC

base_triples = {
    (EGDC.subject, EGDC.predicate, EGDC.object0),
    (EGDC.subject, EGDC.predicate, EGDC.object1),
}


@pytest.mark.parametrize(
    ["node", "expected_uri"],
    [
        (URIRef("http://example.com"), None),
        (Literal("some string in here ..."), None),
        (
            BNode("GMeng4V7"),
            "https://rdflib.github.io/.well-known/genid/rdflib/GMeng4V7",
        ),
        (
            BNode(),
            re.compile(
                "^" + re.escape("https://rdflib.github.io/.well-known/genid/rdflib/")
            ),
        ),
    ],
)
def test_skolemization(
    node: Union[BNode, URIRef, Literal], expected_uri: Union[Pattern[str], str, None]
) -> None:
    g = Graph()
    for triple in base_triples:
        g.add(triple)
    g.add((EGDC.scheck, EGDC.pcheck, node))
    assert len(g) == 3
    dsg = g.skolemize()
    if expected_uri is None:
        GraphHelper.assert_sets_equals(g, dsg)
    else:
        assert len(dsg) == len(g)
        iset = GraphHelper.triple_or_quad_set(dsg)
        logging.debug("iset = %s", iset)
        assert iset.issuperset(base_triples)
        check_triples = list(dsg.triples((EGDC.scheck, EGDC.pcheck, None)))
        assert len(check_triples) == 1
        sbnode = check_triples[0][2]
        logging.debug("sbnode = %s, sbnode_value = %s", sbnode, f"{sbnode}")
        assert isinstance(sbnode, URIRef)
        if isinstance(expected_uri, str):
            assert expected_uri == f"{sbnode}"
        else:
            assert expected_uri.match(f"{sbnode}") is not None


@pytest.mark.parametrize(
    ["iri", "expected_bnode_value"],
    [
        ("http://example.com", None),
        ("http://example.com/not/.well-known/genid/1", None),
        ("https://rdflib.github.io/not/.well-known/genid/1", None),
        ("http://example.com/.well-known/genid/1", re.compile("^N")),
        ("https://rdflib.github.io/.well-known/genid/rdflib/GMeng4V7", "GMeng4V7"),
    ],
)
def test_deskolemization(
    iri: str, expected_bnode_value: Union[str, None, Pattern[str]]
) -> None:
    g = Graph()
    for triple in base_triples:
        g.add(triple)
    g.add((EGDC.scheck, EGDC.pcheck, URIRef(iri)))
    assert len(g) == 3
    dsg = g.de_skolemize()
    if expected_bnode_value is None:
        GraphHelper.assert_sets_equals(g, dsg)
    else:
        assert len(dsg) == len(g)
        iset = GraphHelper.triple_or_quad_set(dsg)
        logging.debug("iset = %s", iset)
        assert iset.issuperset(base_triples)
        check_triples = list(dsg.triples((EGDC.scheck, EGDC.pcheck, None)))
        assert len(check_triples) == 1
        bnode = check_triples[0][2]
        logging.debug("bnode = %s, bnode_value = %s", bnode, f"{bnode}")
        assert isinstance(bnode, BNode)
        if isinstance(expected_bnode_value, str):
            assert expected_bnode_value == f"{bnode}"
        else:
            assert expected_bnode_value.match(f"{bnode}") is not None
