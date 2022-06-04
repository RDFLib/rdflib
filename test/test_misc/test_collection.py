import logging

import pytest

from rdflib import BNode, Graph, Literal
from rdflib.collection import Collection


def test_scenario() -> None:
    # Taken from https://github.com/RDFLib/rdflib/blob/8a92d3565bf2e502a7c4cadb34b29db72c89d623/rdflib/collection.py#L272-L304
    g = Graph()

    c = Collection(g, BNode())

    assert len(c) == 0

    c = Collection(g, BNode(), [Literal("1"), Literal("2"), Literal("3"), Literal("4")])

    assert len(c) == 4

    assert c[1] == Literal("2"), c[1]

    del c[1]

    assert list(c) == [Literal("1"), Literal("3"), Literal("4")], list(c)

    with pytest.raises(IndexError):
        del c[500]

    c.append(Literal("5"))

    logging.debug("list(c) = %s", list(c))

    for i in c:
        logging.debug("i = %s", i)

    del c[3]

    c.clear()

    assert len(c) == 0
