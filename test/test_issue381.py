from rdflib import BNode, Graph, Namespace
from rdflib.compare import isomorphic

NS = Namespace("http://example.org/")

def test_no_spurious_semicolon():
    sparql = """
      PREFIX : <http://example.org/>
      CONSTRUCT {
        :a :b :c ; :d :e .
      } WHERE {}
    """
    expected = Graph()
    expected.addN( t+(expected,) for t in [
        (NS.a, NS.b, NS.c),
        (NS.a, NS.d, NS.e),
    ])
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
    expected.addN( t+(expected,) for t in [
        (NS.a, NS.b, NS.c),
        (NS.a, NS.d, NS.e),
    ])
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
    expected.addN( t+(expected,) for t in [
        (NS.a, NS.b, NS.c),
        (NS.a, NS.d, NS.e),
    ])
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
    expected.addN( t+(expected,) for t in [
        (NS.a, NS.b, NS.c),
        (NS.a, NS.d, NS.e),
    ])
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
    expected.addN( t+(expected,) for t in [
        (BNode("a"), NS.b, NS.c),
        (BNode("a"), NS.d, NS.e),
    ])
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
    expected.addN( t+(expected,) for t in [
        (NS.a, NS.b, NS.c),
        (NS.a, NS.d, NS.e),
        (NS.a, NS.f, NS.g),
    ])
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
    expected.addN( t+(expected,) for t in [
        (NS.a, NS.b, NS.c),
        (NS.a, NS.d, NS.e),
        (NS.a, NS.d, NS.f),
    ])
    got = Graph().query(sparql).graph
    assert isomorphic(got, expected), got.serialize(format="turtle")

