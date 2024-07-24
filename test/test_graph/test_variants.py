from __future__ import annotations

import dataclasses
import itertools
import json
import logging
import os
import re
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path, PurePath
from typing import (
    ClassVar,
    Collection,
    DefaultDict,
    Dict,
    Iterable,
    List,
    Optional,
    OrderedDict,
    Pattern,
    Tuple,
    Type,
    Union,
    cast,
)

import pytest
from _pytest.mark.structures import Mark, MarkDecorator, ParameterSet

import rdflib.compare
import rdflib.util
from rdflib.graph import Dataset, _GraphT
from rdflib.namespace import XSD
from rdflib.term import URIRef
from test.data import TEST_DATA_DIR
from test.utils import GraphHelper
from test.utils.graph import GraphSource

MODULE_PATH = Path(__file__).parent

TEST_DIR = Path(__file__).parent.parent.absolute()
VARIANTS_DIR = TEST_DATA_DIR / "variants"

# Put files from other directories in here.
EXTRA_FILES: List[Path] = []

SUFFIX_FORMAT_MAP = {**rdflib.util.SUFFIX_FORMAT_MAP, "hext": "hext"}


@dataclass(frozen=True)
class GraphAsserts:
    """
    A specification of asserts that must be checked against a graph.
    """

    quad_count: Optional[int] = None
    has_subject_iris: Optional[List[str]] = None

    def check(self, graph: Dataset) -> None:
        """
        if `first_graph` is `None` then this is the first check before any
        other graphs have been processed.
        """
        if self.quad_count is not None:
            assert self.quad_count == len(list(graph.quads()))
        if self.has_subject_iris is not None:
            subjects_iris = {
                f"{subject}"
                for subject in graph.subjects()
                if isinstance(subject, URIRef)
            }
            assert set(self.has_subject_iris) == subjects_iris

    @classmethod
    def from_path(cls, path: Path):
        with path.open("r") as f:
            keys = dataclasses.fields(cls)
            data = json.load(f)
            return cls(**{key.name: data[key.name] for key in keys if key.name in data})


@dataclass(frozen=True)
class GraphVariantsMeta(GraphAsserts):
    """
    Meta information about a set of variants.
    """

    public_id: Optional[str] = None
    exact_match: bool = False


_VARIANT_PREFERENCE: Dict[str, int] = dict(
    (format, index)
    for index, format in enumerate(
        [
            "python",
            "nquads",
            "nt",
            "ntriples",
            "turtle",
            "ttl",
            "trig",
            "xml",
            "hext",
        ]
    )
)


@dataclass(order=True)
class GraphVariants:
    """
    Represents multiple variants of a single graph in different files.
    """

    key: str
    variants: Dict[str, GraphSource] = field(default_factory=OrderedDict)
    meta: GraphVariantsMeta = field(default_factory=GraphVariantsMeta)

    _variant_regex: ClassVar[Pattern[str]] = re.compile(
        r"^(.*?)(|[-]variant-[^/]+|[-]asserts|[-]meta)$"
    )

    def __post_init__(self) -> None:
        self.ordered_variants = sorted(
            self.variants.items(),
            key=lambda variant: _VARIANT_PREFERENCE.get(variant[1].format, 1000),
        )

    def pytest_param(
        self,
        marks: Optional[
            Union[MarkDecorator, Collection[Union[MarkDecorator, Mark]]]
        ] = None,
    ) -> ParameterSet:
        if marks is None:
            marks = cast(Tuple[MarkDecorator], tuple())
        return pytest.param(self, id=self.key, marks=marks)

    @property
    def public_id(self) -> str:
        return self.meta.public_id or f"example:rdflib:test:data:variant:{self.key}"

    @property
    def preferred_variant(self) -> Tuple[str, GraphSource]:
        return self.ordered_variants[0]

    def load(self, variant_key: str, graph_type: Type[_GraphT]) -> _GraphT:
        variant = self.variants[variant_key]
        return variant.load(public_id=self.public_id, graph_type=graph_type)

    @classmethod
    def _decompose_path(cls, file_path: Path, basedir: Optional[Path]):
        if basedir:
            file_path = file_path.absolute().resolve().relative_to(basedir)
        name_noext, ext = os.path.splitext(file_path)
        name_noext_path = PurePath(name_noext)
        match = cls._variant_regex.match("/".join(name_noext_path.parts))
        if match is None:
            raise RuntimeError(f"{cls._variant_regex!r} did not match {name_noext}")
        file_key = match.group(1)
        variant_key = f"{match.group(2)}{ext}"
        return (file_key, variant_key)

    @classmethod
    def for_files(
        cls, file_paths: Iterable[Path], basedir: Optional[Path] = None
    ) -> Dict[str, GraphVariants]:
        graph_sources: DefaultDict[str, Dict[str, GraphSource]] = defaultdict(dict)
        graph_meta: Dict[str, GraphVariantsMeta] = {}
        for file_path in file_paths:
            file_key, variant_key = cls._decompose_path(file_path, basedir)
            file_graph_sources = graph_sources[file_key]
            if variant_key.endswith("-meta.json"):
                if file_key in graph_meta:
                    raise RuntimeError(f"Duplicate meta for {file_key} in {file_path}")
                graph_meta[file_key] = GraphVariantsMeta.from_path(file_path)
            else:
                if variant_key in file_graph_sources:
                    raise RuntimeError(
                        f"Duplicate variant {variant_key} for {file_key} in {file_path}"
                    )
                file_graph_sources[variant_key] = GraphSource.from_path(file_path)
        graph_variant_dict = {}
        for file_key, variants in graph_sources.items():
            if file_key in graph_meta:
                meta = graph_meta[file_key]
                del graph_meta[file_key]
            else:
                meta = GraphVariantsMeta()
            if len(variants) < 2:
                raise RuntimeError(f"Only one variant for {file_key}")
            graph_variant_dict[file_key] = GraphVariants(file_key, variants, meta)
        if graph_meta:
            raise RuntimeError(f"Unmatched meta {graph_meta}")
        return graph_variant_dict

    @classmethod
    def for_directory(
        cls, directory: Path, basedir: Optional[Path] = None
    ) -> Dict[str, GraphVariants]:
        file_paths = []
        for file_path in directory.glob("*"):
            if not file_path.is_file():
                continue
            if file_path.name.endswith(".md"):
                continue
            file_paths.append(file_path)
        return cls.for_files(file_paths, basedir)


GRAPH_VARIANTS_DICT = {
    **GraphVariants.for_directory(VARIANTS_DIR, TEST_DATA_DIR),
    **GraphVariants.for_files(EXTRA_FILES, TEST_DIR),
}

EXPECTED_FAILURES: Dict[Tuple[str, Optional[str]], MarkDecorator] = {
    ("variants/schema_only_base", ".ttl"): pytest.mark.xfail(
        reason="Some issue with handling base URI that does not end with a slash",
        raises=ValueError,
    ),
    ("variants/schema_only_base", ".n3"): pytest.mark.xfail(
        reason="Some issue with handling base URI that does not end with a slash",
        raises=ValueError,
    ),
    ("variants/rdf11trig_eg2", ".hext"): pytest.mark.xfail(
        reason="""
    This fails randomly, passing less than 10% of the time, and always failing
    with comparing hext against trig. Not clear why, it may be a big with hext
    parsing.

    AssertionError: checking rdf11trig_eg2.hext against rdf11trig_eg2.trig
    in both:
        (rdflib.term.BNode('cb0'), rdflib.term.URIRef('http://xmlns.com/foaf/0.1/mbox'), rdflib.term.URIRef('mailto:bob@oldcorp.example.org'))
        (rdflib.term.BNode('cb0'), rdflib.term.URIRef('http://xmlns.com/foaf/0.1/name'), rdflib.term.Literal('Bob'))
        (rdflib.term.URIRef('http://example.org/bob'), rdflib.term.URIRef('http://purl.org/dc/terms/publisher'), rdflib.term.Literal('Bob'))
        (rdflib.term.URIRef('http://example.org/alice'), rdflib.term.URIRef('http://purl.org/dc/terms/publisher'), rdflib.term.Literal('Alice'))
    only in first:
        (rdflib.term.BNode('cb0'), rdflib.term.URIRef('http://xmlns.com/foaf/0.1/knows'), rdflib.term.BNode('cbb5eb12b5dcf688537b0298cce144c6dd68cf047530d0b4a455a8f31f314244fd'))
        (rdflib.term.BNode('cbb5eb12b5dcf688537b0298cce144c6dd68cf047530d0b4a455a8f31f314244fd'), rdflib.term.URIRef('http://xmlns.com/foaf/0.1/mbox'), rdflib.term.URIRef('mailto:alice@work.example.org'))
        (rdflib.term.BNode('cbb5eb12b5dcf688537b0298cce144c6dd68cf047530d0b4a455a8f31f314244fd'), rdflib.term.URIRef('http://xmlns.com/foaf/0.1/name'), rdflib.term.Literal('Alice'))
    only in second:
        (rdflib.term.BNode('cb0'), rdflib.term.URIRef('http://xmlns.com/foaf/0.1/knows'), rdflib.term.BNode('cbcd41774964510991c01701d8430149bc373e1f23734d9c938c81a40b1429aa33'))
        (rdflib.term.BNode('cbcd41774964510991c01701d8430149bc373e1f23734d9c938c81a40b1429aa33'), rdflib.term.URIRef('http://xmlns.com/foaf/0.1/mbox'), rdflib.term.URIRef('mailto:alice@work.example.org'))
        (rdflib.term.BNode('cbcd41774964510991c01701d8430149bc373e1f23734d9c938c81a40b1429aa33'), rdflib.term.URIRef('http://xmlns.com/foaf/0.1/name'), rdflib.term.Literal('Alice'))
        """,
        raises=AssertionError,
    ),
    ("variants/diverse_quads", ".nq"): pytest.mark.xfail(
        reason="""
        Problems with default/implicit datatype of strings. It should be
        xsd:string, but for some parsers it is not. See
        <https://github.com/RDFLib/rdflib/issues/1326> for more info.
        """,
        raises=AssertionError,
    ),
    ("variants/diverse_quads", ".jsonld"): pytest.mark.xfail(
        reason="""
        Problems with default/implicit datatype of strings. It should be
        xsd:string, but for some parsers it is not. See
        <https://github.com/RDFLib/rdflib/issues/1326> for more info.
        """,
        raises=AssertionError,
    ),
}


def tests_found() -> None:
    logging.debug("VARIANTS_DIR = %s", VARIANTS_DIR)
    logging.debug("EXTRA_FILES = %s", EXTRA_FILES)
    assert len(GRAPH_VARIANTS_DICT) >= 1
    logging.debug("ALL_VARIANT_GRAPHS = %s", GRAPH_VARIANTS_DICT)
    xml_literal = GRAPH_VARIANTS_DICT.get("variants/xml_literal")
    assert xml_literal is not None
    assert len(xml_literal.variants) >= 5
    assert xml_literal.meta.quad_count == 1


_PREFERRED_GRAPHS: Dict[str, Dataset] = {}


def load_preferred(graph_variants: GraphVariants) -> Dataset:
    if graph_variants.key in _PREFERRED_GRAPHS:
        return _PREFERRED_GRAPHS[graph_variants.key]
    preferred_variant = graph_variants.preferred_variant
    preferred_graph = graph_variants.load(preferred_variant[0], Dataset)
    GraphHelper.strip_literal_datatypes(preferred_graph, {XSD.string})
    _PREFERRED_GRAPHS[graph_variants.key] = preferred_graph
    return preferred_graph


def make_variant_source_cases() -> Iterable[ParameterSet]:
    for graph_variants in GRAPH_VARIANTS_DICT.values():
        variants = graph_variants.ordered_variants
        preferred_variant = variants[0]
        preferred_key = preferred_variant[0]

        for variant_key in itertools.chain([None], (i[0] for i in variants[1:])):
            marks = []
            if (graph_variants.key, variant_key) in EXPECTED_FAILURES:
                marks.append(EXPECTED_FAILURES[(graph_variants.key, variant_key)])
            yield pytest.param(
                graph_variants,
                variant_key,
                marks=marks,
                id=f"{graph_variants.key}-{preferred_key}-{variant_key}",
            )


@pytest.mark.parametrize(["graph_variants", "variant_key"], make_variant_source_cases())
def test_variant_source(
    graph_variants: GraphVariants, variant_key: Optional[str]
) -> None:
    """
    All variants of a graph are isomorphic with the preferred variant,
    and thus eachother.
    """
    preferred_path = graph_variants.preferred_variant[1].path
    preferred_graph: Dataset = load_preferred(graph_variants)

    if variant_key is None:
        # Only check asserts against the preferred variant, and only
        # when not comparing variants.
        graph_variants.meta.check(preferred_graph)
    else:
        variant_path = graph_variants.variants[variant_key].path
        variant_graph = graph_variants.load(variant_key, Dataset)
        GraphHelper.strip_literal_datatypes(variant_graph, {XSD.string})

        if graph_variants.meta.exact_match:
            GraphHelper.assert_quad_sets_equals(preferred_graph, variant_graph)
        else:
            GraphHelper.assert_cgraph_isomorphic(
                preferred_graph,
                variant_graph,
                False,
                f"checking {variant_path.relative_to(VARIANTS_DIR)} against {preferred_path.relative_to(VARIANTS_DIR)}",
            )
