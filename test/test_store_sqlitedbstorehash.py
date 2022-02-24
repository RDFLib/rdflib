import pytest

from rdflib.plugins.stores.sqlitedbstore import (
    ListRepr,
    SQLhash,
    SQLhashItemsView,
    SQLhashKeysView,
    SQLhashValuesView,
)


def test_sqlitedbstore_sqlhash():
    from rdflib.plugins.stores.sqlitedbstore import SQLhash

    d = SQLhash()
    assert list(d) == []

    d["abc"] = "lmno"
    assert (d["abc"]) == "lmno"
    d["abc"] = "rsvp"
    d["xyz"] = "pdq"
    assert type(d.items()) == SQLhashItemsView
    assert list(d.items()) == [('abc', 'rsvp'), ('xyz', 'pdq')]
    assert type(d.values()) == SQLhashValuesView
    assert list(d.values()) == ['rsvp', 'pdq']
    assert type(d.keys()) == SQLhashKeysView
    assert list(d.keys()) == ['abc', 'xyz']
    assert list(d) == ['abc', 'xyz']
    d.update(p="x", q="y", r="z")
    assert list(d.items()) == [
        ('abc', 'rsvp'),
        ('xyz', 'pdq'),
        ('p', 'x'),
        ('q', 'y'),
        ('r', 'z'),
    ]
    del d["abc"]
    with pytest.raises(KeyError):
        d["abc"]
    with pytest.raises(KeyError):
        del d["abc"]

    assert list(d) == ['xyz', 'p', 'q', 'r']
    assert bool(d) == True
    d.clear()
    assert bool(d) == False
    assert list(d) == []
    d.update(p="x", q="y", r="z")
    assert list(d) == ['p', 'q', 'r']
    d["xyz"] = "pdq"
    assert d.close() is None
