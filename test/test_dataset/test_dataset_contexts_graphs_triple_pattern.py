import os
import shutil
import tempfile
from test.data import (
    tarek,
    likes,
    pizza,
    michel,
    hates,
    cheese,
    bob,
    context0,
    context1,
    context2,
)
from urllib.request import urlopen

import pytest

from rdflib import logger
from rdflib.graph import Dataset
from rdflib.store import VALID_STORE
from rdflib.term import URIRef


def test_dataset_graphs_with_triple_pattern():
    ds = Dataset()

    ds.add((tarek, likes, pizza))

    g1 = ds.graph(context1)
    g1.add((tarek, likes, cheese))
    g1.add((michel, likes, tarek))

    g2 = ds.graph(context2)
    g2.add((michel, likes, cheese))
    g2.add((michel, likes, pizza))

    assert len(list(ds.graphs((michel, likes, cheese)))) == 1  # Is only in one graph

    assert (
        str(list(ds.graphs((michel, likes, cheese))))
        == "[<Graph identifier=urn:example:context-2 (<class 'rdflib.graph.Graph'>)>]"
    )

    assert len(list(ds.graphs((michel, likes, None)))) == 2  # Should yield two graphs

    assert len(list(ds.graphs((tarek, None, None)))) == 1  # Should yield one graph

    assert len(list(ds.graphs((None, likes, None)))) == 2  # Should yield two graphs

    assert len(list(ds.graphs((None, None, pizza)))) == 1  # Should yield two graphs

    assert len(list(ds.graphs((None, None, None)))) == 2  # Should yield both graphs


def test_dataset_contexts_with_triple_pattern():
    ds = Dataset()

    ds.add((tarek, likes, pizza))

    g1 = ds.graph(context1)
    g1.add((tarek, likes, cheese))
    g1.add((michel, likes, tarek))

    g2 = ds.graph(context2)
    g2.add((michel, likes, cheese))
    g2.add((michel, likes, pizza))

    assert len(list(ds.contexts((michel, likes, cheese)))) == 1  # Is only in one graph

    assert (
        str(list(ds.contexts((michel, likes, cheese))))
        == "[rdflib.term.URIRef('urn:example:context-2')]"
    )

    assert (
        len(list(ds.contexts((michel, likes, None)))) == 2
    )  # Should yield two contextss

    assert len(list(ds.contexts((tarek, None, None)))) == 1  # Should yield one context

    assert len(list(ds.contexts((None, likes, None)))) == 2  # Should yield two contexts

    assert len(list(ds.contexts((None, None, pizza)))) == 1  # Should yield one context

    assert len(list(ds.contexts((None, None, None)))) == 2  # Should yield both contexts
