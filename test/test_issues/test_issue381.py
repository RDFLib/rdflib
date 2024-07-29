from rdflib import BNode, Graph
from rdflib.compare import isomorphic
from test.utils.namespace import EGDO


def test_no_spurious_semicolon():
    sparql = """
      PREFIX : <http://example.org/>
      CONSTRUCT {
        :a :b :c ; :d :e .
      } WHERE {}
    """
    expected = Graph()
    expected.addN(
        t + (expected,)
        for t in [
            (EGDO.a, EGDO.b, EGDO.c),
            (EGDO.a, EGDO.d, EGDO.e),
        ]
    )
    got = Graph().query(sparql).graph
    assert isomorphic(got, expected), got.serialize(format="turtle")


def test_one_spurious_semicolon():
    sparql = """
      PREFIX : <http://example.org/>
      CONSTRUCT {
        :a :b :c ; :d :e ; .
      } WHERE {}
    """
    expected = Graph()
    expected.addN(
        t + (expected,)
        for t in [
            (EGDO.a, EGDO.b, EGDO.c),
            (EGDO.a, EGDO.d, EGDO.e),
        ]
    )
    got = Graph().query(sparql).graph
    assert isomorphic(got, expected), got.serialize(format="turtle")


def test_one_spurious_semicolon_no_perdiod():
    sparql = """
      PREFIX : <http://example.org/>
      CONSTRUCT {
        :a :b :c ; :d :e ;
      } WHERE {}
    """
    expected = Graph()
    expected.addN(
        t + (expected,)
        for t in [
            (EGDO.a, EGDO.b, EGDO.c),
            (EGDO.a, EGDO.d, EGDO.e),
        ]
    )
    got = Graph().query(sparql).graph
    assert isomorphic(got, expected), got.serialize(format="turtle")


def test_two_spurious_semicolons_no_period():
    sparql = """
      PREFIX : <http://example.org/>
      CONSTRUCT {
        :a :b :c ; :d :e ; ;
      } WHERE {}
    """
    expected = Graph()
    expected.addN(
        t + (expected,)
        for t in [
            (EGDO.a, EGDO.b, EGDO.c),
            (EGDO.a, EGDO.d, EGDO.e),
        ]
    )
    got = Graph().query(sparql).graph
    assert isomorphic(got, expected), got.serialize(format="turtle")


def test_one_spurious_semicolons_bnode():
    sparql = """
      PREFIX : <http://example.org/>
      CONSTRUCT {
        [ :b :c ; :d :e ; ]
      } WHERE {}
    """
    expected = Graph()
    expected.addN(
        t + (expected,)
        for t in [
            (BNode("a"), EGDO.b, EGDO.c),
            (BNode("a"), EGDO.d, EGDO.e),
        ]
    )
    got = Graph().query(sparql).graph
    assert isomorphic(got, expected), got.serialize(format="turtle")


def test_pathological():
    """
    This test did not raise an exception,
    but generated a graph completely different from the expected one.
    """
    sparql = """
      PREFIX : <http://example.org/>
      CONSTRUCT {
        :a :b :c ; ;
           :d :e ; ;
           :f :g ;
      } WHERE {}
    """
    expected = Graph()
    expected.addN(
        t + (expected,)
        for t in [
            (EGDO.a, EGDO.b, EGDO.c),
            (EGDO.a, EGDO.d, EGDO.e),
            (EGDO.a, EGDO.f, EGDO.g),
        ]
    )
    got = Graph().query(sparql).graph
    assert isomorphic(got, expected), got.serialize(format="turtle")


def test_mixing_spurious_semicolons_and_commas():
    sparql = """
      PREFIX : <http://example.org/>
      CONSTRUCT {
        :a :b :c ; ;
           :d :e, :f
      } WHERE {}
    """
    expected = Graph()
    expected.addN(
        t + (expected,)
        for t in [
            (EGDO.a, EGDO.b, EGDO.c),
            (EGDO.a, EGDO.d, EGDO.e),
            (EGDO.a, EGDO.d, EGDO.f),
        ]
    )
    got = Graph().query(sparql).graph
    assert isomorphic(got, expected), got.serialize(format="turtle")
