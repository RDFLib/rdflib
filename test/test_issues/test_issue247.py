import unittest

import rdflib

failxml = """\
<rdf:RDF
    xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    xmlns:dc="http://purl.org/dc/elements/1.1/"
>

<rdf:Description rdf:about="http://example.org/">
    <dc:description rdf:parseType="Literal">
        <p xmlns="http://www.w3.org/1999/xhtml" xml:lang="en"></p>
    </dc:description>
</rdf:Description>

</rdf:RDF>"""


class TestXMLLiteralwithLangAttr(unittest.TestCase):
    def test_failing_parse_of_literal_with_xmllang_attr(self):
        """
        Show parse of Literal with xmllang attr fails
        Parsing an RDF/XML document fails with a KeyError when
        it contains a XML Literal with a xml:lang attribute:
        """
        g = rdflib.Graph()
        g.parse(data=failxml, format="xml")


if __name__ == "__main__":
    unittest.main()
