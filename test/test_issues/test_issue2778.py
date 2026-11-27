from __future__ import annotations

import json
from pathlib import Path

import pytest

from rdflib import RDF, Graph, Literal, Namespace, URIRef
from rdflib.plugins.shared.jsonld.errors import (
    RECURSIVE_CONTEXT_INCLUSION,
    JSONLDException,
)


def _write_jsonld(path: Path, data: object) -> str:
    path.write_text(json.dumps(data), encoding="utf-8")
    return path.as_uri()


def test_ro_crate_diamond_context_does_not_raise(tmp_path: Path) -> None:
    ex = Namespace("http://example.org/")
    crate_uri = _write_jsonld(
        tmp_path / "crate.jsonld",
        {
            "@context": {
                "@version": 1.1,
                "Dataset": str(ex.Dataset),
                "name": str(ex.name),
            }
        },
    )
    workflow_uri = _write_jsonld(
        tmp_path / "workflow.jsonld",
        {
            "@context": [
                crate_uri,
                {"@version": 1.1, "WorkflowRun": str(ex.WorkflowRun)},
            ]
        },
    )
    doc = {
        "@context": [crate_uri, workflow_uri],
        "@id": str(ex.run1),
        "@type": ["Dataset", "WorkflowRun"],
        "name": "Example Run",
    }

    g = Graph().parse(data=json.dumps(doc), format="json-ld")

    assert (ex.run1, RDF.type, ex.Dataset) in g
    assert (ex.run1, RDF.type, ex.WorkflowRun) in g
    assert (ex.run1, ex.name, Literal("Example Run")) in g


def test_shared_import_diamond_and_property_scoped_context(tmp_path: Path) -> None:
    _write_jsonld(
        tmp_path / "common.jsonld",
        {"@context": {"@version": 1.1, "shared": "http://example.org/shared"}},
    )
    ctx1_uri = _write_jsonld(
        tmp_path / "ctx1.jsonld",
        {
            "@context": {
                "@version": 1.1,
                "@import": "common.jsonld",
                "a": "http://example.org/a",
            }
        },
    )
    ctx2_uri = _write_jsonld(
        tmp_path / "ctx2.jsonld",
        {
            "@context": {
                "@version": 1.1,
                "@import": "common.jsonld",
                "b": "http://example.org/b",
            }
        },
    )
    doc = {
        "@context": [ctx1_uri, ctx2_uri],
        "@id": "http://example.org/s",
        "shared": "ok",
        "a": "va",
        "b": "vb",
    }

    g = Graph().parse(data=json.dumps(doc), format="json-ld")
    assert (
        URIRef("http://example.org/s"),
        URIRef("http://example.org/shared"),
        Literal("ok"),
    ) in g
    assert (
        URIRef("http://example.org/s"),
        URIRef("http://example.org/a"),
        Literal("va"),
    ) in g
    assert (
        URIRef("http://example.org/s"),
        URIRef("http://example.org/b"),
        Literal("vb"),
    ) in g


def test_w3c_e128_diamond_and_scoped_reinclusion(tmp_path: Path) -> None:
    ctx3 = tmp_path / "ctx3.jsonld"
    _write_jsonld(
        ctx3,
        {
            "@context": {
                "@version": 1.1,
                "prop": {
                    "@id": "http://example.org/prop",
                    "@context": "ctx3.jsonld",
                },
                "value": {"@id": "http://example.org/value"},
            }
        },
    )
    _write_jsonld(tmp_path / "ctx1.jsonld", {"@context": "ctx3.jsonld"})
    _write_jsonld(tmp_path / "ctx2.jsonld", {"@context": "ctx3.jsonld"})
    doc_path = tmp_path / "doc.jsonld"
    _write_jsonld(
        doc_path,
        {
            "@context": ["ctx1.jsonld", "ctx2.jsonld"],
            "@id": "http://example.org/id",
            "prop": {"value": "v"},
        },
    )

    g = Graph().parse(doc_path, format="json-ld")
    objs = list(
        g.objects(URIRef("http://example.org/id"), URIRef("http://example.org/prop"))
    )
    assert len(objs) == 1
    assert (objs[0], URIRef("http://example.org/value"), Literal("v")) in g


def test_true_context_cycles_still_raise(tmp_path: Path) -> None:
    self_uri = _write_jsonld(tmp_path / "self.jsonld", {})
    self_uri = _write_jsonld(tmp_path / "self.jsonld", {"@context": self_uri})
    with pytest.raises(JSONLDException, match=str(RECURSIVE_CONTEXT_INCLUSION)):
        Graph().parse(
            data=json.dumps({"@context": self_uri, "@id": "http://example.org/x"}),
            format="json-ld",
        )

    a_path = tmp_path / "a.jsonld"
    b_path = tmp_path / "b.jsonld"
    a_uri = a_path.as_uri()
    b_uri = _write_jsonld(b_path, {"@context": a_uri})
    _write_jsonld(a_path, {"@context": b_uri})
    with pytest.raises(JSONLDException, match=str(RECURSIVE_CONTEXT_INCLUSION)):
        Graph().parse(
            data=json.dumps({"@context": a_uri, "@id": "http://example.org/x"}),
            format="json-ld",
        )

    imp_a = tmp_path / "imp_a.jsonld"
    imp_b = tmp_path / "imp_b.jsonld"
    imp_a_uri = imp_a.as_uri()
    imp_b_uri = _write_jsonld(
        imp_b,
        {"@context": {"@version": 1.1, "@import": imp_a.name}},
    )
    _write_jsonld(
        imp_a,
        {"@context": imp_b_uri},
    )
    with pytest.raises(JSONLDException, match=str(RECURSIVE_CONTEXT_INCLUSION)):
        Graph().parse(
            data=json.dumps({"@context": imp_a_uri, "@id": "http://example.org/x"}),
            format="json-ld",
        )
