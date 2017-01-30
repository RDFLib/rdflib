from codecs import getreader
from six import BytesIO, StringIO

from rdflib import URIRef, Literal
from rdflib.graph import Graph

rdf = u"""@prefix skos:
<http://www.w3.org/2004/02/skos/core#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix : <http://www.test.org/#> .

:world rdf:type skos:Concept;
    skos:prefLabel "World"@en.
:africa rdf:type skos:Concept;
    skos:prefLabel "Africa"@en;
    skos:broaderTransitive :world.
:CI rdf:type skos:Concept;
    skos:prefLabel "C\u00f4te d'Ivoire"@fr;
    skos:broaderTransitive :africa.
"""


rdf_utf8 = rdf.encode('utf-8')

rdf_reader = getreader('utf-8')(BytesIO(rdf.encode('utf-8')))




def test_a():
    """Test reading N3 from a unicode objects as data"""
    g = Graph()
    g.parse(data=rdf, format='n3')
    v = g.value(subject=URIRef("http://www.test.org/#CI"), predicate=URIRef("http://www.w3.org/2004/02/skos/core#prefLabel"))
    assert v==Literal(u"C\u00f4te d'Ivoire", lang='fr')

def test_b():
    """Test reading N3 from a utf8 encoded string as data"""
    g = Graph()
    g.parse(data=rdf_utf8, format='n3')
    v = g.value(subject=URIRef("http://www.test.org/#CI"), predicate=URIRef("http://www.w3.org/2004/02/skos/core#prefLabel"))
    assert v==Literal(u"C\u00f4te d'Ivoire", lang='fr')

def test_c():
    """Test reading N3 from a codecs.StreamReader, outputting unicode"""
    g = Graph()
#    rdf_reader.seek(0)
    g.parse(source=rdf_reader, format='n3')
    v = g.value(subject=URIRef("http://www.test.org/#CI"), predicate=URIRef("http://www.w3.org/2004/02/skos/core#prefLabel"))
    assert v==Literal(u"C\u00f4te d'Ivoire", lang='fr')

def test_d():
    """Test reading N3 from a StringIO over the unicode object"""
    g = Graph()
    g.parse(source=StringIO(rdf), format='n3')
    v = g.value(subject=URIRef("http://www.test.org/#CI"), predicate=URIRef("http://www.w3.org/2004/02/skos/core#prefLabel"))
    assert v==Literal(u"C\u00f4te d'Ivoire", lang='fr')

def test_e():
    """Test reading N3 from a BytesIO over the string object"""
    g = Graph()
    g.parse(source=BytesIO(rdf_utf8), format='n3')
    v = g.value(subject=URIRef("http://www.test.org/#CI"), predicate=URIRef("http://www.w3.org/2004/02/skos/core#prefLabel"))
    assert v==Literal(u"C\u00f4te d'Ivoire", lang='fr')


# this is unicode
rdfxml=u"""<?xml version="1.0" encoding="UTF-8"?>
<rdf:RDF
   xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
   xmlns:skos="http://www.w3.org/2004/02/skos/core#"
>
  <rdf:Description rdf:about="http://www.test.org/#CI">
    <rdf:type rdf:resource="http://www.w3.org/2004/02/skos/core#Concept"/>
    <skos:prefLabel xml:lang="fr">C\u00f4te d\'Ivoire</skos:prefLabel>
    <skos:broaderTransitive rdf:resource="http://www.test.org/#africa"/>
  </rdf:Description>
</rdf:RDF>
"""

# this is a str
rdfxml_utf8 = rdfxml.encode('utf-8')

rdfxml_reader = getreader('utf-8')(BytesIO(rdfxml.encode('utf-8')))


def test_xml_a():
    """Test reading XML from a unicode object as data"""
    import platform
    if platform.system() == 'Java':
        from nose import SkipTest
        raise SkipTest('unicode issue for Jython2.5')
    g = Graph()
    g.parse(data=rdfxml, format='xml')
    v = g.value(subject=URIRef("http://www.test.org/#CI"), predicate=URIRef("http://www.w3.org/2004/02/skos/core#prefLabel"))
    assert v==Literal(u"C\u00f4te d'Ivoire", lang='fr')

def test_xml_b():
    """Test reading XML from a utf8 encoded string object as data"""
    import platform
    if platform.system() == 'Java':
        from nose import SkipTest
        raise SkipTest('unicode issue for Jython2.5')
    g = Graph()
    g.parse(data=rdfxml_utf8, format='xml')
    v = g.value(subject=URIRef("http://www.test.org/#CI"), predicate=URIRef("http://www.w3.org/2004/02/skos/core#prefLabel"))
    assert v==Literal(u"C\u00f4te d'Ivoire", lang='fr')

# The following two cases are currently not supported by Graph.parse
# def test_xml_c():
#     """Test reading XML from a codecs.StreamReader, outputting unicode"""
#     g = Graph()
#     g.parse(source=rdfxml_reader, format='xml')
#     v = g.value(subject=URIRef("http://www.test.org/#CI"), predicate=URIRef("http://www.w3.org/2004/02/skos/core#prefLabel"))
#     assert v==Literal(u"C\u00f4te d'Ivoire", lang='fr')

# def test_xml_d():
#     """Test reading XML from a BytesIO created from unicode object"""
#     g = Graph()
#     g.parse(source=BytesIO(rdfxml), format='xml')
#     v = g.value(subject=URIRef("http://www.test.org/#CI"), predicate=URIRef("http://www.w3.org/2004/02/skos/core#prefLabel"))
#     assert v==Literal(u"C\u00f4te d'Ivoire", lang='fr')

def test_xml_e():
    """Test reading XML from a BytesIO created from utf8 encoded string"""
    import platform
    if platform.system() == 'Java':
        from nose import SkipTest
        raise SkipTest('unicode issue for Jython2.5')
    g = Graph()
    g.parse(source=BytesIO(rdfxml_utf8), format='xml')
    v = g.value(subject=URIRef("http://www.test.org/#CI"), predicate=URIRef("http://www.w3.org/2004/02/skos/core#prefLabel"))
    assert v==Literal(u"C\u00f4te d'Ivoire", lang='fr')
