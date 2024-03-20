from rdflib import Graph


def test_a():
    g = Graph()
    q = g.query(
        """
        SELECT * {
        { BIND ("a" AS ?a) }
        UNION
        { BIND ("a" AS ?a) }
        }
        """
    )
    assert len(q) == 2


def test_b():
    g = Graph()
    q = g.query(
        """
        SELECT * {
            { BIND ("a" AS ?a) }
            UNION
            { VALUES ?a { "a" } }
            UNION
            { SELECT ("a" AS ?a) {} }
        }
        """
    )
    assert len(q) == 3


def test_c():
    g = Graph()
    q = g.query(
        """
        SELECT * {
            { BIND ("a" AS ?a) }
            UNION
            { VALUES ?a { "a" } }
            UNION
            { SELECT ("b" AS ?a) {} }
        }
        """
    )
    assert len(q) == 3


def test_d():
    g = Graph()
    q = g.query(
        """SELECT * {
            { BIND ("a" AS ?a) }
            UNION
            { VALUES ?a { "b" } }
            UNION
            { SELECT ("c" AS ?a) {} }
        }
        """
    )
    assert len(q) == 3
