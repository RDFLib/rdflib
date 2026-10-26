import tempfile
from io import BytesIO

import pytest

import rdflib
from rdflib.plugins.serializers.xmlwriter import XMLWriter

EXNS = rdflib.Namespace("https://example.org/ns/")
TRIXNS = rdflib.Namespace("http://www.w3.org/2004/03/trix/trix-1/")


def test_xmlwriter_namespaces():
    g = rdflib.Graph(bind_namespaces="core")

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
    g = rdflib.Graph(bind_namespaces="core")

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


@pytest.mark.parametrize(
    "prefix, namespace",
    [("rdf", rdflib.Namespace(str(rdflib.RDF))), ("", TRIXNS), ("ex", EXNS)],
)
@pytest.mark.parametrize("suffix", ["nested/value", "123value"])
def test_xmlwriter_extra_namespace_invalid_local_name(prefix, namespace, suffix):
    graph = rdflib.Graph(bind_namespaces="none")
    graph.bind(prefix, namespace)
    writer = XMLWriter(BytesIO(), graph.namespace_manager, extra_ns={prefix: namespace})

    assert writer.qname(namespace[suffix]) == "ns1:value"


@pytest.mark.parametrize(
    "suffix, expected",
    [
        ("lang", "xml:lang"),
        ("/value", "ns1:value"),
        ("123value", "ns1:namespace123value"),
    ],
)
def test_xmlwriter_xml_namespace_local_name(suffix, expected):
    graph = rdflib.Graph(bind_namespaces="none")
    writer = XMLWriter(BytesIO(), graph.namespace_manager)

    assert writer.qname(rdflib.namespace.XMLNS + suffix) == expected


@pytest.mark.parametrize(
    "prefix, namespace",
    [
        ("rdf", rdflib.Namespace(str(rdflib.RDF))),
        ("", TRIXNS),
        ("ex", EXNS),
        ("xml", rdflib.Namespace(rdflib.namespace.XMLNS)),
    ],
)
@pytest.mark.parametrize(
    "subnamespace", ["foo%20", "foo(", "foo)", "fooª", "fooµ", "fooº"]
)
def test_xmlwriter_longer_namespace_binding(prefix, namespace, subnamespace):
    graph = rdflib.Graph(bind_namespaces="none")
    graph.bind(prefix, namespace)
    extended = rdflib.Namespace(str(namespace) + subnamespace)
    graph.bind("extended", extended)
    extra_ns = {} if prefix == "xml" else {prefix: namespace}
    writer = XMLWriter(BytesIO(), graph.namespace_manager, extra_ns=extra_ns)

    assert writer.qname(extended.value) == "extended:value"


@pytest.mark.parametrize(
    "namespace, prefix",
    [(str(rdflib.RDF), "rdf"), (rdflib.namespace.XMLNS, "xml")],
)
@pytest.mark.parametrize(
    "local_name", ["À", "Ö", "Ø", "ö", "ø", "Δelta", "名前", "a\u0301"]
)
def test_xmlwriter_valid_unicode_local_name(namespace, prefix, local_name):
    graph = rdflib.Graph(bind_namespaces="none")
    writer = XMLWriter(
        BytesIO(),
        graph.namespace_manager,
        extra_ns={"rdf": rdflib.Namespace(str(rdflib.RDF))},
    )

    assert writer.qname(namespace + local_name) == prefix + ":" + local_name


@pytest.mark.parametrize("namespaces", [[], (), {}.items()])
def test_xmlwriter_explicit_empty_namespaces(namespaces):
    graph = rdflib.Graph()
    stream = BytesIO()
    writer = XMLWriter(stream, graph.namespace_manager, decl=0, extra_ns={"ex": EXNS})

    writer.namespaces(namespaces)

    assert stream.getvalue() == b'\n  xmlns:ex="https://example.org/ns/"\n'
