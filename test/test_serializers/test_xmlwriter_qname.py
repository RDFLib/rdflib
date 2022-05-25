import tempfile

import pytest

import rdflib
from rdflib.plugins.serializers.xmlwriter import XMLWriter

EXNS = rdflib.Namespace("https://example.org/ns/")
TRIXNS = rdflib.Namespace("http://www.w3.org/2004/03/trix/trix-1/")


def test_xmlwriter_namespaces():

    g = rdflib.Graph()

    with tempfile.TemporaryFile() as fp:

        xmlwr = XMLWriter(fp, g.namespace_manager, extra_ns={"": TRIXNS, "ex": EXNS})

        xmlwr.namespaces()

        fp.seek(0)

        assert fp.readlines() == [
            b'<?xml version="1.0" encoding="utf-8"?>\n',
            b'  xmlns:owl="http://www.w3.org/2002/07/owl#"\n',
            b'  xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"\n',
            b'  xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"\n',
            b'  xmlns:xsd="http://www.w3.org/2001/XMLSchema#"\n',
            b'  xmlns:xml="http://www.w3.org/XML/1998/namespace"\n',
            b'  xmlns="http://www.w3.org/2004/03/trix/trix-1/"\n',
            b'  xmlns:ex="https://example.org/ns/"\n',
        ]


def test_xmlwriter_decl():

    g = rdflib.Graph()

    with tempfile.TemporaryFile() as fp:

        xmlwr = XMLWriter(fp, g.namespace_manager, decl=0, extra_ns={"": TRIXNS})

        xmlwr.namespaces()

        fp.seek(0)
        assert fp.readlines() == [
            b"\n",
            b'  xmlns:owl="http://www.w3.org/2002/07/owl#"\n',
            b'  xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"\n',
            b'  xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"\n',
            b'  xmlns:xsd="http://www.w3.org/2001/XMLSchema#"\n',
            b'  xmlns:xml="http://www.w3.org/XML/1998/namespace"\n',
            b'  xmlns="http://www.w3.org/2004/03/trix/trix-1/"\n',
        ]


@pytest.mark.parametrize(
    "uri",
    [
        # NS bound to “ex”, so “ex:foo”
        ["https://example.org/ns/foo", "ex:foo"],
        # NS bound to "", so “graph”
        ["http://www.w3.org/2004/03/trix/trix-1/graph", "graph"],
        # NS not in extra_ns, use ns<int> idiom
        ["https://example.org/foo", "ns1:foo"],
    ],
)
def test_xmlwriter_qname(uri):

    g = rdflib.Graph()
    g.bind("", TRIXNS)
    g.bind("ex", EXNS)

    fp = tempfile.TemporaryFile()

    xmlwr = XMLWriter(fp, g.namespace_manager, extra_ns={"": TRIXNS, "ex": EXNS})

    assert xmlwr.qname(uri[0]) == uri[1]
