from contextlib import ExitStack
from typing import Any, Optional, Type, Union
from warnings import warn

import pytest

from rdflib import DCTERMS
from rdflib.graph import BNode, Graph, Literal
from rdflib.namespace import (
    FOAF,
    OWL,
    RDF,
    RDFS,
    SH,
    ClosedNamespace,
    DefinedNamespaceMeta,
    Namespace,
    URIPattern,
)
from rdflib.term import URIRef


class TestNamespace:
    def setup_method(self, method):
        self.ns_str = "http://example.com/name/space/"
        self.ns = Namespace(self.ns_str)

    def test_repr(self):
        # NOTE: this assumes ns_str has no characthers that need escaping
        assert self.ns_str in f"{self.ns!r}"
        assert self.ns == eval(f"{self.ns!r}")

    def test_str(self):
        assert self.ns_str == f"{self.ns}"

    def test_member(self):
        assert f"{self.ns_str}a" == f"{self.ns.a}"

    def test_dcterms_title(self):
        assert DCTERMS.title == URIRef(DCTERMS + "title")

    def test_iri(self):
        prefix = "http://jörn.loves.encoding.problems/"
        ns = Namespace(prefix)
        assert ns == str(prefix)
        assert ns["jörn"].startswith(ns)


class TestClosedNamespace:
    def setup_method(self, method):
        self.ns_str = "http://example.com/name/space/"
        self.ns = ClosedNamespace(self.ns_str, ["a", "b", "c"])

    def test_repr(self):
        # NOTE: this assumes ns_str has no characthers that need escaping
        assert self.ns_str in f"{self.ns!r}"

    @pytest.mark.xfail
    def test_repr_ef(self):
        """
        This fails because ClosedNamespace repr does not represent the second argument
        """
        assert self.ns == eval(f"{self.ns!r}")

    def test_str(self):
        assert self.ns_str == f"{self.ns}"

    def test_member(self):
        assert f"{self.ns_str}a" == f"{self.ns.a}"

    def test_missing_member(self):
        with pytest.raises(AttributeError) as context:
            f"{self.ns.missing}"
        assert "missing" in f"{context.value}"


class TestURIPattern:
    def setup_method(self, method):
        self.pattern_str = "http://example.org/%s/%d/resource"
        self.pattern = URIPattern(self.pattern_str)

    def test_repr(self):
        # NOTE: this assumes pattern_str has no characthers that need escaping
        assert self.pattern_str in f"{self.pattern!r}"
        assert self.pattern == eval(f"{self.pattern!r}")

    def test_format(self):
        assert "http://example.org/foo/100/resource" == str(self.pattern % ("foo", 100))


class TestNamespacePrefix:
    @pytest.mark.parametrize(
        "invalid_uri",
        [
            ("<123>"),
            ('-"-'),
            ("{}"),
            ("a|b"),
            ("1\\2"),
            ("^"),
        ],
    )
    def test_invalid_uri(self, invalid_uri: str) -> None:
        g = Graph()
        with pytest.raises(ValueError):
            g.namespace_manager.compute_qname(invalid_uri)

    def test_compute_qname(self):
        """Test sequential assignment of unknown prefixes"""
        g = Graph()
        assert g.compute_qname(URIRef("http://foo/bar/baz")) == (
            "ns1",
            URIRef("http://foo/bar/"),
            "baz",
        )

        assert g.compute_qname(URIRef("http://foo/bar#baz")) == (
            "ns2",
            URIRef("http://foo/bar#"),
            "baz",
        )

        # should skip to ns4 when ns3 is already assigned
        g.bind("ns3", URIRef("http://example.org/"))
        assert g.compute_qname(URIRef("http://blip/blop")) == (
            "ns4",
            URIRef("http://blip/"),
            "blop",
        )

        # should return empty qnames correctly
        assert g.compute_qname(URIRef("http://foo/bar/")) == (
            "ns1",
            URIRef("http://foo/bar/"),
            "",
        )

        # should compute qnames of URNs correctly as well
        assert g.compute_qname(URIRef("urn:ISSN:0167-6423")) == (
            "ns5",
            URIRef("urn:ISSN:"),
            "0167-6423",
        )

        assert g.compute_qname(URIRef("urn:ISSN:")) == ("ns5", URIRef("urn:ISSN:"), "")

        # should compute qnames with parenthesis correctly
        assert g.compute_qname(URIRef("http://foo/bar/name_with_(parenthesis)")) == (
            "ns1",
            URIRef("http://foo/bar/"),
            "name_with_(parenthesis)",
        )

    def test_reset(self):
        data = (
            "@prefix a: <http://example.org/a> .\n"
            "a: <http://example.org/b> <http://example.org/c> ."
        )
        graph = Graph().parse(data=data, format="turtle")
        for p, n in tuple(graph.namespaces()):
            graph.store._Memory__namespace.pop(p)
            graph.store._Memory__prefix.pop(n)
        graph.namespace_manager.reset()
        assert not tuple(graph.namespaces())
        u = URIRef("http://example.org/a")
        prefix, namespace, name = graph.namespace_manager.compute_qname(
            u, generate=True
        )
        assert namespace != u

    def test_reset_preserve_prefixes(self):
        data = (
            "@prefix a: <http://example.org/a> .\n"
            "a: <http://example.org/b> <http://example.org/c> ."
        )
        graph = Graph().parse(data=data, format="turtle")
        graph.namespace_manager.reset()
        assert tuple(graph.namespaces())
        u = URIRef("http://example.org/a")
        prefix, namespace, name = graph.namespace_manager.compute_qname(
            u, generate=True
        )
        assert namespace == u

    def test_n3(self):
        g = Graph()
        g.add(
            (
                URIRef("http://example.com/foo"),
                URIRef("http://example.com/bar"),
                URIRef("http://example.com/baz"),
            )
        )
        n3 = g.serialize(format="n3", encoding="latin-1")
        # Gunnar disagrees that this is right:
        # self.assertTrue("<http://example.com/foo> ns1:bar <http://example.com/baz> ." in n3)
        # as this is much prettier, and ns1 is already defined:
        assert b"ns1:foo ns1:bar ns1:baz ." in n3

    def test_n32(self):
        # this test not generating prefixes for subjects/objects
        g = Graph()
        g.add(
            (
                URIRef("http://example1.com/foo"),
                URIRef("http://example2.com/bar"),
                URIRef("http://example3.com/baz"),
            )
        )
        n3 = g.serialize(format="n3", encoding="latin-1")

        assert b"<http://example1.com/foo> ns1:bar <http://example3.com/baz> ." in n3

    def test_closed_namespace(self):
        """Tests terms both in an out of the ClosedNamespace FOAF"""

        def add_not_in_namespace(s):
            with pytest.raises(AttributeError):
                return FOAF[s]

        # a non-existent FOAF property
        add_not_in_namespace("blah")

        # a deprecated FOAF property
        # add_not_in_namespace('firstName')
        assert FOAF["firstName"] == URIRef("http://xmlns.com/foaf/0.1/firstName")

        warn("DefinedNamespace does not address deprecated properties")

        # a property name within the FOAF namespace
        assert FOAF.givenName == URIRef("http://xmlns.com/foaf/0.1/givenName")

        # namescape can be used as str
        assert FOAF.givenName.startswith(FOAF)

    def test_contains_method(self):
        """Tests for Namespace.__contains__() methods."""

        ref = URIRef("http://www.w3.org/ns/shacl#Info")
        assert (
            type(SH) == DefinedNamespaceMeta
        ), f"SH no longer a DefinedNamespaceMeta (instead it is now {type(SH)}, update test."
        assert ref in SH, "sh:Info not in SH"

        ref = URIRef("http://www.w3.org/2000/01/rdf-schema#label")
        assert ref in RDFS, "ClosedNamespace(RDFS) does not include rdfs:label"
        ref = URIRef("http://www.w3.org/2000/01/rdf-schema#example")
        assert (
            ref not in RDFS
        ), "ClosedNamespace(RDFS) includes out-of-ns member rdfs:example"

        ref = URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type")
        assert ref in RDF, "RDF does not include rdf:type"

        ref = URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#_1")
        assert ref in RDF, "RDF does not include rdf:_1"

        ref = URIRef("http://www.w3.org/2002/07/owl#rational")
        assert ref in OWL, "OWL does not include owl:rational"

        ref = URIRef("http://www.w3.org/2002/07/owl#real")
        assert ref in OWL, "OWL does not include owl:real"

    def test_expand_curie_exception_messages(self) -> None:
        g = Graph()

        with pytest.raises(TypeError) as e:
            assert g.namespace_manager.expand_curie(URIRef("urn:example")) is None
        assert str(e.value) == "Argument must be a string, not URIRef."

        with pytest.raises(TypeError) as e:
            assert g.namespace_manager.expand_curie(Literal("rdf:type")) is None
        assert str(e.value) == "Argument must be a string, not Literal."

        with pytest.raises(TypeError) as e:
            assert g.namespace_manager.expand_curie(BNode()) is None
        assert str(e.value) == "Argument must be a string, not BNode."

        with pytest.raises(TypeError) as e:
            assert g.namespace_manager.expand_curie(Graph()) is None  # type: ignore[arg-type]
        assert str(e.value) == "Argument must be a string, not Graph."

    @pytest.mark.parametrize(
        ["curie", "expected_result"],
        [
            ("ex:tarek", URIRef("urn:example:tarek")),
            ("ex:", URIRef(f"urn:example:")),
            ("ex:a", URIRef(f"urn:example:a")),
            ("ex:a:b", URIRef(f"urn:example:a:b")),
            ("ex:a:b:c", URIRef(f"urn:example:a:b:c")),
            ("ex", ValueError),
            ("em:tarek", ValueError),
            ("em:", ValueError),
            ("em", ValueError),
            (":", ValueError),
            (":type", ValueError),
            ("í", ValueError),
            (" :", ValueError),
            ("", ValueError),
            ("\n", ValueError),
            (None, TypeError),
            (3, TypeError),
            (URIRef("urn:example:"), TypeError),
            (BNode(), TypeError),
            (Literal("rdf:type"), TypeError),
        ],
    )
    def test_expand_curie(
        self, curie: Any, expected_result: Union[Type[Exception], URIRef, None]
    ) -> None:
        g = Graph(bind_namespaces="none")
        nsm = g.namespace_manager
        nsm.bind("ex", "urn:example:")
        result: Optional[URIRef] = None
        catcher: Optional[pytest.ExceptionInfo[Exception]] = None
        with ExitStack() as xstack:
            if isinstance(expected_result, type) and issubclass(
                expected_result, Exception
            ):
                catcher = xstack.enter_context(pytest.raises(expected_result))
            result = g.namespace_manager.expand_curie(curie)

        if catcher is not None:
            assert result is None
            assert catcher.value is not None
        else:
            assert expected_result == result
