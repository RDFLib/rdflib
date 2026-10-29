from __future__ import annotations

import codecs
import os
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from io import BytesIO
from typing import Any

import pytest

from rdflib import RDF, XSD, BNode, Dataset, Graph, Literal, Namespace, URIRef
from rdflib.compare import isomorphic
from rdflib.term import Identifier, Node

EX = Namespace("https://example.test/")


def rdf_isomorphic(first: Graph, second: Graph) -> bool:
    # The graph digest preserves language-tag case, unlike Literal equality.
    def comparable(graph: Graph) -> Graph:
        result = Graph(bind_namespaces="none")
        for subject, predicate, value in graph:
            if isinstance(value, Literal) and value.language:
                value = Literal(
                    str(value), lang=value.language.lower(), normalize=False
                )
            result.add((subject, predicate, value))
        return result

    return isomorphic(comparable(first), comparable(second))


@pytest.fixture(params=("xml", "pretty-xml"))
def format_name(request):
    return request.param


def equivalent_graph(reverse: bool, labels: tuple[str, str]) -> Graph:
    graph = Graph(bind_namespaces="none")
    graph.bind("ex", EX)
    left, right = map(BNode, labels)
    triples = [
        (EX.root, EX.child, left),
        (EX.root, EX.child, right),
        (left, RDF.type, EX.Node),
        (left, EX.label, Literal("alpha", lang="en")),
        (right, RDF.type, EX.Node),
        (right, EX.label, Literal("beta")),
        (right, EX.link, left),
    ]
    for triple in reversed(triples) if reverse else triples:
        graph.add(triple)
    return graph


def relabeled_graph(graph: Graph) -> Graph:
    copy = Graph(bind_namespaces="none")
    labels: dict[BNode, BNode] = {}

    def relabel(term):
        if isinstance(term, BNode):
            return labels.setdefault(term, BNode("other-" + str(term)))
        return term

    for triple in reversed(list(graph)):
        copy.add(tuple(relabel(term) for term in triple))
    return copy


def test_canon_xml_is_identical_for_isomorphic_graphs(format_name: str) -> None:
    first = equivalent_graph(False, ("left", "right"))
    second = equivalent_graph(True, ("x", "y"))
    canonical = first.serialize(format=format_name, canon=True)
    assert canonical == second.serialize(format=format_name, canon=True)
    ordinary = first.serialize(format=format_name)
    assert ordinary == first.serialize(format=format_name, canon=False)
    legacy = Graph()
    legacy.add((EX.subject, EX.label, Literal("text", lang="EN-gb")))
    serialization_options: tuple[dict[str, Any], ...] = ({}, {"canon": False})
    for options in serialization_options:
        document = legacy.serialize(format=format_name, **options)
        label = ET.fromstring(document).find(".//{https://example.test/}label")
        assert label is not None
        assert label.get("{http://www.w3.org/XML/1998/namespace}lang") == "EN-gb"


@pytest.mark.parametrize("blank_subject", [False, True])
def test_equivalent_language_tags_have_identical_canonical_output(
    format_name: str, blank_subject: bool
) -> None:
    graphs = []
    text = " \t label  <b>value</b>\n "
    for language, label in (("EN-gb", "first"), ("en-GB", "second")):
        graph = Graph(bind_namespaces="none")
        subject = BNode(label) if blank_subject else EX.subject
        graph.add((subject, EX.label, Literal(text, lang=language)))
        if blank_subject:
            graph.add((EX.root, EX.child, subject))
        graphs.append(graph)

    documents = [
        graph.serialize(format=format_name, canon=True, encoding="utf-8")
        for graph in graphs
    ]
    assert documents[0] == documents[1]
    parsed = Graph().parse(data=documents[0], format="xml")
    parsed_subject = parsed.value(EX.root, EX.child) if blank_subject else EX.subject
    assert isinstance(parsed_subject, (BNode, URIRef))
    if blank_subject:
        assert isinstance(parsed_subject, BNode)
    expected: set[tuple[Node, Node, Node]] = {
        (parsed_subject, EX.label, Literal(text, lang="en-gb"))
    }
    if blank_subject:
        expected.add((EX.root, EX.child, parsed_subject))
    assert set(parsed) == expected


def test_canonical_bytes_match_for_symmetric_blank_node_cycle(format_name: str) -> None:
    graphs = []
    for labels, reverse in ((("left", "right"), False), (("x", "y"), True)):
        graph = Graph(bind_namespaces="none")
        first, second = map(BNode, labels)
        triples = [
            (EX.root, EX.member, first),
            (EX.root, EX.member, second),
            (first, EX.next, second),
            (second, EX.next, first),
            (first, EX.label, Literal("same")),
            (second, EX.label, Literal("same")),
        ]
        for triple in reversed(triples) if reverse else triples:
            graph.add(triple)
        graphs.append(graph)
    for graph, label, reverse in (
        (graphs[0], "isolated-a", False),
        (graphs[1], "isolated-b", True),
    ):
        isolated = BNode(label)
        detached = [
            (isolated, EX.label, Literal("bonjour", lang="fr")),
            (isolated, EX.label, Literal("typed", datatype=XSD.string)),
            (isolated, EX.rank, Literal(3)),
            (EX.separate, EX.label, Literal("standalone")),
            (EX.separate, EX.reference, EX.other),
        ]
        for triple in reversed(detached) if reverse else detached:
            graph.add(triple)
    document = graphs[0].serialize(format=format_name, canon=True)
    assert document == graphs[1].serialize(format=format_name, canon=True)
    assert rdf_isomorphic(graphs[0], Graph().parse(data=document, format="xml"))


def test_canonical_xml_round_trip_isomorphically(format_name: str) -> None:
    graph = equivalent_graph(True, ("outside", "inside"))
    whitespace = " \t alpha  <b>value</b>\n "
    graph.add((EX.root, EX.whitespace, Literal(whitespace)))
    head, tail = (BNode("head"), BNode("tail"))
    for triple in (
        (EX.root, EX.items, head),
        (EX.other, EX.items, tail),
        (head, RDF.first, EX.first),
        (head, RDF.rest, tail),
        (tail, RDF.first, EX.second),
        (tail, RDF.rest, RDF.nil),
    ):
        graph.add(triple)
    document = graph.serialize(format=format_name, canon=True)
    assert document == relabeled_graph(graph).serialize(format=format_name, canon=True)
    reparsed = Graph().parse(data=document, format="xml")
    assert str(reparsed.value(EX.root, EX.whitespace)) == whitespace
    assert rdf_isomorphic(graph, reparsed)
    carriage_return = Graph(bind_namespaces="none")
    carriage_return.add((EX.root, EX.label, Literal("<b>\r</b>")))
    document = carriage_return.serialize(format=format_name, canon=True)
    assert rdf_isomorphic(carriage_return, Graph().parse(data=document, format="xml"))
    empty = Graph(bind_namespaces="none")
    empty_document = empty.serialize(format=format_name, canon=True)
    assert rdf_isomorphic(empty, Graph().parse(data=empty_document, format="xml"))
    type_only = Graph(bind_namespaces="none")
    type_only.add((EX.root, RDF.type, URIRef("https://types.example/Thing")))
    type_document = type_only.serialize(format=format_name, canon=True)
    assert rdf_isomorphic(type_only, Graph().parse(data=type_document, format="xml"))
    for default_union in (False, True):
        dataset = Dataset(default_union=default_union)
        default_triple = (EX.root, EX.label, Literal("default"))
        named_triple = (EX.other, EX.label, Literal("named"))
        dataset.default_graph.add(default_triple)
        dataset.graph(EX.named).add(named_triple)
        expected = Graph()
        expected.add(default_triple)
        if default_union:
            expected.add(named_triple)
        document = dataset.serialize(format=format_name, canon=True)
        assert rdf_isomorphic(expected, Graph().parse(data=document, format="xml"))


def test_canonical_namespace_declarations_are_stable(format_name: str) -> None:
    first = Graph(bind_namespaces="none")
    first.bind("z", URIRef("urn:z:"))
    first.bind("a", URIRef("urn:a:"))
    first.add((URIRef("urn:s"), URIRef("urn:z:p"), URIRef("urn:a:o")))
    second = Graph(bind_namespaces="none")
    second.bind("a", URIRef("urn:a:"))
    second.bind("z", URIRef("urn:z:"))
    second.add((URIRef("urn:s"), URIRef("urn:z:p"), URIRef("urn:a:o")))
    assert first.serialize(format=format_name, canon=True) == second.serialize(
        format=format_name, canon=True
    )
    predicate = URIRef("http://example.org/foobar")
    for namespace in (None, "http://example.org/foo", "http://example.org/"):
        graph = Graph(bind_namespaces="none")
        if namespace is not None:
            graph.bind("ex", URIRef(namespace))
        graph.add((EX.root, predicate, Literal("value")))
        document = graph.serialize(format=format_name, canon=True, encoding="utf-8")
        assert rdf_isomorphic(graph, Graph().parse(data=document, format="xml"))

    reserved = Graph(bind_namespaces="none")
    reserved.add(
        (EX.root, URIRef("http://www.w3.org/XML/1998/namespacefoo"), Literal("value"))
    )
    reserved_document = reserved.serialize(format=format_name, canon=True)
    assert rdf_isomorphic(reserved, Graph().parse(data=reserved_document, format="xml"))


def test_generated_prefixes_do_not_depend_on_predicate_insertion_order(
    format_name: str,
) -> None:
    triples = [
        (URIRef("urn:s"), URIRef("https://z.example/property"), Literal("z")),
        (URIRef("urn:s"), URIRef("https://a.example/property"), Literal("a")),
    ]
    first = Graph(bind_namespaces="none")
    second = Graph(bind_namespaces="none")
    for triple in triples:
        first.add(triple)
    for triple in reversed(triples):
        second.add(triple)
    assert first.serialize(format=format_name, canon=True) == second.serialize(
        format=format_name, canon=True
    )


def test_canonical_xml_is_stable_across_hash_seeds() -> None:
    program = (
        "from rdflib import Graph, URIRef, Literal, BNode, RDF\n"
        "g = Graph(bind_namespaces='none')\n"
        "for i in range(8):\n"
        "    g.add((URIRef('urn:s'), URIRef(f'https://n{i}.example/p'), Literal(i)))\n"
        "g.add((URIRef('urn:s'), URIRef('https://example.test/ns/123alpha'), BNode('item')))\n"
        "g.add((BNode('item'), URIRef('https://example.test/ns/456beta'), Literal('value')))\n"
        "g.add((URIRef('urn:t'), URIRef('urn:link'), BNode('item')))\n"
        "for name in ('Alpha', 'Beta', 'Gamma'):\n"
        "    g.add((URIRef('urn:s'), RDF.type, URIRef('https://types.example/' + name)))\n"
        "for fmt in ('xml', 'pretty-xml'):\n"
        "    print(g.serialize(format=fmt, canon=True), end='')\n"
        "strict = Graph(bind_namespaces='none')\n"
        "for value in ('123alpha', '456beta'):\n"
        "    predicate = URIRef('https://example.test/ns/' + value)\n"
        "    strict.add((URIRef('urn:s'), predicate, Literal(value)))\n"
        "for fmt in ('xml', 'pretty-xml'):\n"
        "    print(strict.serialize(format=fmt, canon=True), end='')\n"
    )
    outputs = []
    for seed in ("1", "2", "3", "4"):
        result = subprocess.run(
            [sys.executable, "-c", program],
            check=True,
            capture_output=True,
            env={**os.environ, "PYTHONHASHSEED": seed},
        )
        outputs.append(result.stdout)
    assert len(set(outputs)) == 1


@pytest.mark.parametrize("value", [None, 0, 1, "yes"])
def test_canon_option_requires_a_boolean(format_name: str, value: object) -> None:
    graph = Graph()
    graph.add((EX.root, EX.label, Literal("value")))
    with pytest.raises(Exception):
        graph.serialize(format=format_name, canon=value)


def test_canonical_output_honors_base_and_encoding_options(format_name: str) -> None:
    graph = Graph(bind_namespaces="none")
    base = "https://example.test/base/?first=1&second=2"
    predicate = URIRef("https://example.test/ns?first=1&second=2#property")
    datatype = URIRef("https://example.test/type?first=1&second=2")
    graph.add(
        (
            URIRef("https://example.test/base/s"),
            predicate,
            Literal("café", datatype=datatype),
        )
    )
    item = BNode("item")
    graph.add((EX.root, EX.child, item))
    graph.add((item, EX.label, Literal("child")))
    data = graph.serialize(format=format_name, canon=True, base=base, encoding="utf-8")
    assert isinstance(data, bytes)
    assert data == relabeled_graph(graph).serialize(
        format=format_name, canon=True, base=base, encoding="utf-8"
    )
    text = data.decode("utf-8")
    declaration = re.search(
        "encoding=[\\\"']([^\\\"']+)[\\\"']", text.split("?>", 1)[0]
    )
    assert declaration is not None
    assert codecs.lookup(declaration.group(1)).name == codecs.lookup("utf-8").name
    root = ET.fromstring(text)
    assert root.attrib["{http://www.w3.org/XML/1998/namespace}base"] == base
    assert rdf_isomorphic(graph, Graph().parse(source=BytesIO(data), format="xml"))


def test_canonical_base_prefix_collision_round_trips(format_name: str) -> None:
    graph = Graph()
    base = "https://example.test/base"
    subject = URIRef("https://example.test/basement")
    graph.add((subject, EX.label, Literal("value")))
    graph.add((subject, EX.link, URIRef("https://example.test/baseball")))
    data = graph.serialize(format=format_name, canon=True, base=base, encoding="utf-8")
    assert rdf_isomorphic(graph, Graph().parse(source=BytesIO(data), format="xml"))


def test_canonical_base_fragment_preserves_resource_identity(format_name: str) -> None:
    base = "https://example.test/doc#record"
    subject = URIRef(base)
    graph = Graph(bind_namespaces="none")
    graph.add((subject, EX.label, Literal("value")))
    graph.add((EX.root, EX.link, subject))
    document = graph.serialize(
        format=format_name, canon=True, base=base, encoding="utf-8"
    )
    restored = Graph().parse(data=document, format="xml")
    assert set(restored) == set(graph)


def test_canonical_utf8_preserves_unicode(format_name: str) -> None:
    graph = Graph(bind_namespaces="none")
    subject = URIRef("https://example.test/😀")
    graph.add((subject, EX.label, Literal("outside Latin-1: 😀")))
    graph.add((subject, EX.markup, Literal("<tag>😀 & &#128512;</tag>")))
    graph.add((subject, EX.link, URIRef("https://example.test/名")))
    graph.add((subject, RDF.type, URIRef("https://example.test/名Type")))
    graph.add(
        (
            subject,
            URIRef("https://example.test/😀#value"),
            Literal("😀", datatype=URIRef("https://example.test/名")),
        )
    )
    graph.add((subject, EX.xml, Literal("<名>😀</名>", datatype=RDF.XMLLiteral)))
    for encoding in ("utf-8", "utf8", "UTF_8"):
        document = graph.serialize(format=format_name, canon=True, encoding=encoding)
        document.decode("utf-8")
        assert rdf_isomorphic(
            graph, Graph().parse(source=BytesIO(document), format="xml")
        )
        assert document == relabeled_graph(graph).serialize(
            format=format_name, canon=True, encoding=encoding
        )


def test_canonical_unicode_predicate_is_deterministic_and_round_trips(
    format_name: str,
) -> None:
    def make_graph(label: str) -> Graph:
        graph = Graph()
        node = BNode(label)
        predicate = URIRef("https://example.test/关系")
        graph.add((URIRef("https://example.test/first"), predicate, node))
        graph.add((URIRef("https://example.test/second"), predicate, node))
        graph.add((node, URIRef("https://example.test/value"), Literal("value")))
        return graph

    first, second = make_graph("original"), make_graph("renamed")
    outputs = []
    for graph in (first, second):
        output = graph.serialize(format=format_name, encoding="utf-8", canon=True)
        restored = Graph().parse(data=output, format="xml")
        assert isomorphic(graph, restored)
        outputs.append(output)
    assert outputs[0] == outputs[1]


def test_canonical_output_is_independent_of_graph_base(format_name: str) -> None:
    first = equivalent_graph(False, ("left", "right"))
    second = equivalent_graph(True, ("x", "y"))
    for graph in (first, second):
        graph.bind("rdf", RDF)
        graph.bind("xml", URIRef("http://www.w3.org/XML/1998/namespace"))
    first.base = str(EX)
    second.base = "https://other.example/"
    serialization_options: tuple[dict[str, Any], ...] = ({}, {"base": str(EX)})
    for options in serialization_options:
        document = first.serialize(format=format_name, canon=True, **options)
        assert document == second.serialize(format=format_name, canon=True, **options)
        assert rdf_isomorphic(first, Graph().parse(data=document, format="xml"))
        if options:
            assert (
                ET.fromstring(document).get(
                    "{http://www.w3.org/XML/1998/namespace}base"
                )
                == options["base"]
            )
    assert first.base == str(EX)
    assert second.base == "https://other.example/"
    ordinary = first.serialize(format=format_name, canon=False)
    assert (
        ET.fromstring(ordinary).get("{http://www.w3.org/XML/1998/namespace}base")
        == first.base
    )


def test_canonical_pretty_xml_preserves_list_structure() -> None:
    for shape in (
        "ordinary",
        "shared-tail",
        "annotated",
        "literal",
        "shared-item",
        "repeated-item",
        "cycle",
        "missing-rest",
        "multiple-rest",
        "named",
    ):
        graph = Graph(bind_namespaces="none")
        head = URIRef("urn:list-head") if shape == "named" else BNode("head")
        tail, item = BNode("tail"), BNode("item")
        graph.add((EX.root, EX.items, head))
        graph.add((head, RDF.first, Literal("item") if shape == "literal" else item))
        graph.add((head, RDF.rest, tail))
        graph.add((tail, RDF.first, item if shape == "repeated-item" else EX.second))
        graph.add((tail, RDF.rest, RDF.nil))
        graph.add((item, EX.label, Literal("preserved")))
        if shape == "shared-tail":
            graph.add((EX.other, EX.items, tail))
        elif shape == "annotated":
            graph.add((tail, EX.note, Literal("preserved")))
        elif shape == "shared-item":
            graph.add((EX.other, EX.reference, item))
            graph.add((head, EX.note, Literal("preserved")))
        elif shape == "cycle":
            graph.set((tail, RDF.rest, head))
        elif shape == "missing-rest":
            graph.remove((tail, RDF.rest, None))
        elif shape == "multiple-rest":
            graph.add((head, RDF.rest, RDF.nil))
        for depth in (1, 3):
            document = graph.serialize(format="pretty-xml", canon=True, max_depth=depth)
            assert rdf_isomorphic(graph, Graph().parse(data=document, format="xml")), (
                shape
            )
            assert document == relabeled_graph(graph).serialize(
                format="pretty-xml", canon=True, max_depth=depth
            ), shape


def test_canonical_pretty_xml_honors_depth() -> None:
    observed_depth_change = False

    def nested_subject_depth(subject):
        """Count RDF subject elements, skipping the intervening property elements."""
        return max(
            (1 + nested_subject_depth(child) for prop in subject for child in prop),
            default=1,
        )

    for shared_blank_nodes in (False, True):
        graph = Graph(bind_namespaces="none")
        nodes: list[Identifier] = [EX.root, EX.one, EX.two, EX.three]
        if shared_blank_nodes:
            nodes = [EX.root, BNode("one"), BNode("two"), BNode("three")]
            for node in nodes[1:]:
                graph.add((EX.other, EX.reference, node))
        for subject, child in zip(nodes, nodes[1:]):
            graph.add((subject, EX.child, child))
        graph.add((nodes[-1], EX.label, Literal("value")))
        graph.add((BNode("separate"), EX.label, Literal("separate")))
        depths = []
        for limit in (1, 2, 4):
            document = graph.serialize(format="pretty-xml", canon=True, max_depth=limit)
            assert document == relabeled_graph(graph).serialize(
                format="pretty-xml", canon=True, max_depth=limit
            )
            assert rdf_isomorphic(graph, Graph().parse(data=document, format="xml"))
            depth = max(
                nested_subject_depth(subject) for subject in ET.fromstring(document)
            )
            assert depth <= limit
            depths.append(depth)
        observed_depth_change |= len(set(depths)) > 1
    assert observed_depth_change


def test_canonical_xml_preserves_type_objects(format_name: str) -> None:
    for value in (
        URIRef("urn:123"),
        BNode("type"),
        Literal("type"),
        URIRef(str(RDF) + "Description"),
    ):
        graph = Graph(bind_namespaces="none")
        graph.add((BNode("subject"), RDF.type, value))
        graph.add((BNode("subject"), RDF.type, EX.Class))
        document = graph.serialize(format=format_name, canon=True)
        assert document == relabeled_graph(graph).serialize(
            format=format_name, canon=True
        )
        assert rdf_isomorphic(graph, Graph().parse(data=document, format="xml"))
