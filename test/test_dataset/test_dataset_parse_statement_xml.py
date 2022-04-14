import pytest

from rdflib import Dataset, Literal, URIRef

xmlpatch1 = """<?xml version="1.0"?>
<rdf:RDF
  xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
  xmlns:pstcn="http://burningbird.net/postcon/elements/1.0/">
  <rdf:Description rdf:about="http://burningbird.net/recommendation.htm">
    <rdf:subject rdf:resource="http://www.webreference.com/dhtml/hiermenus" />
    <rdf:predicate rdf:resource="http://burningbird.net/schema/Contains" />
    <rdf:object>Tutorials and source code about creating hierarchical menus in DHTML</rdf:object>
    <rdf:type rdf:resource="http://www.w3.org/1999/02/22-rdf-syntax-ns#Statement" />
    <pstcn:recommendedBy>Shelley Powers</pstcn:recommendedBy>
  </rdf:Description>
</rdf:RDF>
"""

xmlpatch2 = """<?xml version="1.0"?>
<rdf:RDF
  xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
  xmlns:pstcn="http://burningbird.net/postcon/elements/1.0/"
  xml:base="http://burningbird.net/">
  <rdf:Description rdf:about="#s1"> 
    <rdf:subject rdf:resource="http://www.webreference.com/dhtml/hiermenus" />
    <rdf:predicate rdf:resource="http://burningbird.net/schema/Contains" />
    <rdf:object>Tutorials and source code about creating hierarchical menus in DHTML</rdf:object>
    <rdf:type rdf:resource="http://www.w3.org/1999/02/22-rdf-syntax-ns#Statement" />
   </rdf:Description>
  <rdf:Description rdf:about="http://burningbird.net/person/001">
   <pstcn:recommends rdf:resource="#s1" />
  </rdf:Description>     
</rdf:RDF>
"""


def test_xml_statements_1():
    ds1 = Dataset()
    ds1.parse(data=xmlpatch1, format="xml")
    assert len(ds1) == 5
    assert sorted(list(ds1))[0] == (
        URIRef('http://burningbird.net/recommendation.htm'),
        URIRef('http://burningbird.net/postcon/elements/1.0/recommendedBy'),
        Literal('Shelley Powers'),
        None,
    )


def test_xml_statements_2():
    ds1 = Dataset()
    ds1.parse(data=xmlpatch2, format="xml")
    assert len(ds1) == 5
    assert sorted(list(ds1))[0] == (
        URIRef('http://burningbird.net/#s1'),
        URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#object'),
        Literal('Tutorials and source code about creating hierarchical menus in DHTML'),
        None,
    )
