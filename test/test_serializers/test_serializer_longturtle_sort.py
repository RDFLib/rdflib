#!/usr/bin/env python3

# Portions of this file contributed by NIST are governed by the
# following statement:
#
# This software was developed at the National Institute of Standards
# and Technology by employees of the Federal Government in the course
# of their official duties. Pursuant to Title 17 Section 105 of the
# United States Code, this software is not subject to copyright
# protection within the United States. NIST assumes no responsibility
# whatsoever for its use by other parties, and makes no guarantees,
# expressed or implied, about its quality, reliability, or any other
# characteristic.
#
# We would appreciate acknowledgement if the software is used.

from __future__ import annotations

import random
from collections import defaultdict
from typing import DefaultDict, List

from rdflib import RDFS, BNode, Graph, Literal, Namespace, URIRef

EX = Namespace("http://example.org/ex/")


def test_sort_semiblank_graph() -> None:
    """
    This test reviews whether the output of the Turtle form is
    consistent when involving repeated generates with blank nodes.
    """

    serialization_counter: DefaultDict[str, int] = defaultdict(int)

    first_graph_text: str = ""

    # Use a fixed sequence of once-but-no-longer random values for more
    # consistent test results.
    nonrandom_shuffler = random.Random(1234)
    for x in range(1, 10):
        graph = Graph()
        graph.bind("ex", EX)
        graph.bind("rdfs", RDFS)

        graph.add((EX.A, RDFS.comment, Literal("Thing A")))
        graph.add((EX.B, RDFS.comment, Literal("Thing B")))
        graph.add((EX.C, RDFS.comment, Literal("Thing C")))

        nodes: List[URIRef] = [EX.A, EX.B, EX.C, EX.B]
        nonrandom_shuffler.shuffle(nodes)
        for node in nodes:
            # Instantiate one bnode per URIRef node.
            graph.add((BNode(), RDFS.seeAlso, node))

        nesteds: List[URIRef] = [EX.A, EX.B, EX.C]
        nonrandom_shuffler.shuffle(nesteds)
        for nested in nesteds:
            # Instantiate a nested node reference.
            outer_node = BNode()
            inner_node = BNode()
            graph.add((outer_node, EX.has, inner_node))
            graph.add((inner_node, RDFS.seeAlso, nested))

        graph_text = graph.serialize(format="longturtle", sort=True)
        if first_graph_text == "":
            first_graph_text = graph_text

        serialization_counter[graph_text] += 1

    expected_serialization = """\
PREFIX ns1: <http://example.org/ex/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

ns1:A
    rdfs:comment "Thing A" ;
.

ns1:C
    rdfs:comment "Thing C" ;
.

ns1:B
    rdfs:comment "Thing B" ;
.

[]    ns1:has
        [
            rdfs:seeAlso ns1:A ;
        ] ;
.

[]    rdfs:seeAlso ns1:B ;
.

[]    ns1:has
        [
            rdfs:seeAlso ns1:C ;
        ] ;
.

[]    rdfs:seeAlso ns1:A ;
.

[]    rdfs:seeAlso ns1:C ;
.

[]    rdfs:seeAlso ns1:B ;
.

[]    ns1:has
        [
            rdfs:seeAlso ns1:B ;
        ] ;
.

"""

    assert expected_serialization.strip() == first_graph_text.strip()
    assert 1 == len(serialization_counter)
