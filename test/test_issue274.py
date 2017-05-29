from nose.tools import assert_raises
from nose.tools import eq_
from unittest import TestCase

from rdflib import BNode, Graph, Literal, Namespace, RDFS, XSD
from rdflib.plugins.sparql.operators import register_custom_function, unregister_custom_function

EX = Namespace('http://example.org/')
G = Graph()
G.add((BNode(), RDFS.label, Literal("bnode")))
NS = {
    'ex': EX,
    'rdfs': RDFS,
    'xsd': XSD,
}

def query(querystr, initNs=NS, initBindings=None):
    return G.query(querystr, initNs=initNs, initBindings=initBindings)

def setup():
    pass

def teardown():
    pass


def test_cast_string_to_string():
    res = query('''SELECT (xsd:string("hello") as ?x) {}''')
    eq_(list(res)[0][0], Literal("hello", datatype=XSD.string))

def test_cast_int_to_string():
    res = query('''SELECT (xsd:string(42) as ?x) {}''')
    eq_(list(res)[0][0], Literal("42", datatype=XSD.string))

def test_cast_float_to_string():
    res = query('''SELECT (xsd:string(3.14) as ?x) {}''')
    eq_(list(res)[0][0], Literal("3.14", datatype=XSD.string))

def test_cast_bool_to_string():
    res = query('''SELECT (xsd:string(true) as ?x) {}''')
    eq_(list(res)[0][0], Literal("true", datatype=XSD.string))

def test_cast_iri_to_string():
    res = query('''SELECT (xsd:string(<http://example.org/>) as ?x) {}''')
    eq_(list(res)[0][0], Literal("http://example.org/", datatype=XSD.string))

def test_cast_datetime_to_datetime():
    res = query('''SELECT (xsd:dateTime("1970-01-01T00:00:00Z"^^xsd:dateTime) as ?x) {}''')
    eq_(list(res)[0][0], Literal("1970-01-01T00:00:00Z", datatype=XSD.dateTime))

def test_cast_string_to_datetime():
    res = query('''SELECT (xsd:dateTime("1970-01-01T00:00:00Z"^^xsd:string) as ?x) {}''')
    eq_(list(res)[0][0], Literal("1970-01-01T00:00:00Z", datatype=XSD.dateTime))

def test_cast_string_to_float():
    res = query('''SELECT (xsd:float("0.5") as ?x) {}''')
    eq_(list(res)[0][0], Literal("0.5", datatype=XSD.float))

def test_cast_int_to_float():
    res = query('''SELECT (xsd:float(1) as ?x) {}''')
    eq_(list(res)[0][0], Literal("1", datatype=XSD.float))

def test_cast_float_to_float():
    res = query('''SELECT (xsd:float("0.5"^^xsd:float) as ?x) {}''')
    eq_(list(res)[0][0], Literal("0.5", datatype=XSD.float))

def test_cast_double_to_float():
    res = query('''SELECT (xsd:float("0.5"^^xsd:double) as ?x) {}''')
    eq_(list(res)[0][0], Literal("0.5", datatype=XSD.float))

def test_cast_decimal_to_float():
    res = query('''SELECT (xsd:float("0.5"^^xsd:decimal) as ?x) {}''')
    eq_(list(res)[0][0], Literal("0.5", datatype=XSD.float))

def test_cast_string_to_double():
    res = query('''SELECT (xsd:double("0.5") as ?x) {}''')
    eq_(list(res)[0][0], Literal("0.5", datatype=XSD.double))

def test_cast_int_to_double():
    res = query('''SELECT (xsd:double(1) as ?x) {}''')
    eq_(list(res)[0][0], Literal("1", datatype=XSD.double))

def test_cast_float_to_double():
    res = query('''SELECT (xsd:double("0.5"^^xsd:float) as ?x) {}''')
    eq_(list(res)[0][0], Literal("0.5", datatype=XSD.double))

def test_cast_double_to_double():
    res = query('''SELECT (xsd:double("0.5"^^xsd:double) as ?x) {}''')
    eq_(list(res)[0][0], Literal("0.5", datatype=XSD.double))

def test_cast_decimal_to_double():
    res = query('''SELECT (xsd:double("0.5"^^xsd:decimal) as ?x) {}''')
    eq_(list(res)[0][0], Literal("0.5", datatype=XSD.double))

def test_cast_string_to_decimal():
    res = query('''SELECT (xsd:decimal("0.5") as ?x) {}''')
    eq_(list(res)[0][0], Literal("0.5", datatype=XSD.decimal))

def test_cast_int_to_decimal():
    res = query('''SELECT (xsd:decimal(1) as ?x) {}''')
    eq_(list(res)[0][0], Literal("1", datatype=XSD.decimal))

def test_cast_float_to_decimal():
    res = query('''SELECT (xsd:decimal("0.5"^^xsd:float) as ?x) {}''')
    eq_(list(res)[0][0], Literal("0.5", datatype=XSD.decimal))

def test_cast_double_to_decimal():
    res = query('''SELECT (xsd:decimal("0.5"^^xsd:double) as ?x) {}''')
    eq_(list(res)[0][0], Literal("0.5", datatype=XSD.decimal))

def test_cast_decimal_to_decimal():
    res = query('''SELECT (xsd:decimal("0.5"^^xsd:decimal) as ?x) {}''')
    eq_(list(res)[0][0], Literal("0.5", datatype=XSD.decimal))

def test_cast_string_to_int():
    res = query('''SELECT (xsd:integer("42") as ?x) {}''')
    eq_(list(res)[0][0], Literal("42", datatype=XSD.integer))

def test_cast_int_to_int():
    res = query('''SELECT (xsd:integer(42) as ?x) {}''')
    eq_(list(res)[0][0], Literal("42", datatype=XSD.integer))

def test_cast_string_to_bool():
    res = query('''SELECT (xsd:boolean("TRUE") as ?x) {}''')
    eq_(list(res)[0][0], Literal("true", datatype=XSD.boolean))

def test_cast_bool_to_bool():
    res = query('''SELECT (xsd:boolean(true) as ?x) {}''')
    eq_(list(res)[0][0], Literal("true", datatype=XSD.boolean))

def test_cast_bool_to_bool():
    res = query('''SELECT (ex:f(42, "hello") as ?x) {}''')
    eq_(len(list(res)), 0)

class TestCustom(TestCase):

    @staticmethod
    def f(x, y):
        return Literal("%s %s" % (x, y), datatype=XSD.string)

    def setUp(self):
        register_custom_function(EX.f, self.f)

    def tearDown(self):
        unregister_custom_function(EX.f, self.f)

    def test_register_twice_fail(self):
        with assert_raises(ValueError):
            register_custom_function(EX.f, self.f)

    def test_register_override(self):
        register_custom_function(EX.f, self.f, override=True)

    def test_wrong_unregister_fails(self):
        with assert_raises(ValueError):
            unregister_custom_function(EX.f, lambda x, y: None)

    def test_f(self):
        res = query('''SELECT (ex:f(42, "hello") as ?x) {}''')
        eq_(list(res)[0][0], Literal("42 hello", datatype=XSD.string))

    def test_f_too_few_args(self):
        res = query('''SELECT (ex:f(42) as ?x) {}''')
        eq_(len(list(res)), 0)

    def test_f_too_many_args(self):
        res = query('''SELECT (ex:f(42, "hello", "world") as ?x) {}''')
        eq_(len(list(res)), 0)
