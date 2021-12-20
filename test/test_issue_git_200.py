import rdflib
import pytest


def test_broken_add():

    g = rdflib.Graph()
    with pytest.raises(AssertionError):
        g.add((1, 2, 3))


@pytest.mark.skip
def test_broken_addN():

    g = rdflib.Graph()
    with pytest.raises(AssertionError):
        g.addN([(1, 2, 3, g)])
