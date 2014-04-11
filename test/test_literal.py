import unittest

import rdflib # needed for eval(repr(...)) below
from rdflib.term import Literal, URIRef, _XSD_DOUBLE, bind
from rdflib.py3compat import format_doctest_out as uformat

# these are actually meant for test_term.py, which is not yet merged into trunk

class TestMd5(unittest.TestCase):
    def testMd5(self):
        self.assertEqual(rdflib.URIRef("http://example.com/").md5_term_hash(),
                         "40f2c9c20cc0c7716fb576031cceafa4")
        self.assertEqual(rdflib.Literal("foo").md5_term_hash(),
                         "da9954ca5f673f8ab9ebd6faf23d1046")
    

class TestLiteral(unittest.TestCase):
    def setUp(self):
        pass

    def test_repr_apostrophe(self):
        a = rdflib.Literal("'")
        b = eval(repr(a))
        self.assertEquals(a, b)

    def test_repr_quote(self):
        a = rdflib.Literal('"')
        b = eval(repr(a))
        self.assertEquals(a, b)

    def test_backslash(self):
        d = r"""
<rdf:RDF
  xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
  xmlns:foo="http://example.org/foo#">
    <rdf:Description>
      <foo:bar>a\b</foo:bar>
    </rdf:Description>
</rdf:RDF>
"""
        g = rdflib.Graph()
        g.parse(data=d)
        a = rdflib.Literal('a\\b')
        b = list(g.objects())[0]
        self.assertEquals(a, b)

    def test_literal_from_bool(self):
        l = rdflib.Literal(True)
        self.assertEquals(l.datatype, rdflib.XSD["boolean"])

class TestNew(unittest.TestCase):
    def testCantPassLangAndDatatype(self):
        self.assertRaises(TypeError,
           Literal, 'foo', lang='en', datatype=URIRef("http://example.com/"))

    def testFromOtherLiteral(self):
        l = Literal(1)
        l2 = Literal(l)
        self.assertTrue(isinstance(l.value, int))
        self.assertTrue(isinstance(l2.value, int))

        # change datatype
        l = Literal("1")
        l2 = Literal(l, datatype=rdflib.XSD.integer)
        self.assertTrue(isinstance(l2.value, long))



    def testDatatypeGetsAutoURIRefConversion(self):
        # drewp disapproves of this behavior, but it should be
        # represented in the tests
        x = Literal("foo", datatype="http://example.com/")
        self.assert_(isinstance(x.datatype, URIRef))

        x = Literal("foo", datatype=Literal("pennies"))
        self.assertEqual(x.datatype, URIRef("pennies"))



class TestRepr(unittest.TestCase):
    def testOmitsMissingDatatypeAndLang(self):
        self.assertEqual(repr(Literal("foo")),
                         uformat("rdflib.term.Literal(%(u)s'foo')"))

    def testOmitsMissingDatatype(self):
        self.assertEqual(repr(Literal("foo", lang='en')),
                         uformat("rdflib.term.Literal(%(u)s'foo', lang='en')"))

    def testOmitsMissingLang(self):
        self.assertEqual(
            repr(Literal("foo", datatype=URIRef('http://example.com/'))),
            uformat("rdflib.term.Literal(%(u)s'foo', datatype=rdflib.term.URIRef(%(u)s'http://example.com/'))"))

    def testSubclassNameAppearsInRepr(self):
        class MyLiteral(Literal):
            pass
        x = MyLiteral(u"foo")
        self.assertEqual(repr(x), uformat("MyLiteral(%(u)s'foo')"))

class TestDoubleOutput(unittest.TestCase):
    def testNoDanglingPoint(self):
        """confirms the fix for https://github.com/RDFLib/rdflib/issues/237"""
        vv = Literal("0.88", datatype=_XSD_DOUBLE)
        out = vv._literal_n3(use_plain=True)
        self.assert_(out in ["8.8e-01", "0.88"], out)

class TestBindings(unittest.TestCase):

    def testBinding(self):

        class a:
            def __init__(self,v):
                self.v=v[3:-3]
            def __str__(self):
                return '<<<%s>>>'%self.v

        dtA=rdflib.URIRef('urn:dt:a')
        bind(dtA,a)

        va=a("<<<2>>>")
        la=Literal(va, normalize=True)
        self.assertEqual(la.value,va)
        self.assertEqual(la.datatype, dtA)

        la2=Literal("<<<2>>>", datatype=dtA)
        self.assertTrue(isinstance(la2.value, a))
        self.assertEqual(la2.value.v,va.v)

        class b:
            def __init__(self,v):
                self.v=v[3:-3]
            def __str__(self):
                return 'B%s'%self.v

        dtB=rdflib.URIRef('urn:dt:b')
        bind(dtB,b,None,lambda x: '<<<%s>>>'%x)

        vb=b("<<<3>>>")
        lb=Literal(vb, normalize=True)
        self.assertEqual(lb.value,vb)
        self.assertEqual(lb.datatype, dtB)





if __name__ == "__main__":
    unittest.main()
