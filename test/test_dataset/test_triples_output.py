from test.data import *

import pytest

from rdflib import Dataset


def test_dsdu_triples():
    dsdu = Dataset(default_union=True)

    dsdu.add((tarek, likes, pizza))
    dsdu.add((michel, likes, pizza))
    dsdu.add((bob, likes, pizza))
    dsdu.add((michel, likes, cheese))
    dsdu.add((michel, likes, bob, context1))

    assert len(list(dsdu.triples((None, None, None)))) == 5
    assert sorted(list(dsdu.triples((None, None, None)))) == [
        (bob, likes, pizza),
        (michel, likes, bob),
        (michel, likes, cheese),
        (michel, likes, pizza),
        (tarek, likes, pizza),
    ]

    assert dsdu.value(michel, likes, None) == pizza
    assert list(dsdu.objects(michel, likes, None)) == [pizza, cheese, bob]


def test_ds_default_triples():
    ds = Dataset()

    ds.add((tarek, likes, pizza))
    ds.add((michel, likes, pizza))
    ds.add((bob, likes, pizza))
    ds.add((michel, likes, cheese))
    ds.add((michel, likes, bob, context1))

    assert len(list(ds.triples((None, None, None)))) == 4

    assert sorted(list(ds.triples((None, None, None)))) == [
        (bob, likes, pizza),
        (michel, likes, cheese),
        (michel, likes, pizza),
        (tarek, likes, pizza),
    ]

    assert ds.value(michel, likes, None) == pizza
    assert list(ds.objects(michel, likes, None)) == [pizza, cheese]


def test_ds_triples():
    ds = Dataset()

    ds.add((tarek, likes, pizza, context1))
    ds.add((michel, likes, pizza, context1))
    ds.add((bob, likes, pizza, context1))
    ds.add((michel, likes, cheese, context1))

    ds.add((michel, likes, bob))

    assert len(list(ds.triples((None, None, None)))) == 1

    assert sorted(list(ds.triples((None, None, None)))) == [(michel, likes, bob)]

    assert ds.value(michel, likes, None) == bob
    assert list(ds.objects(michel, likes, None)) == [bob]
    assert list(ds.objects()) == [bob]
