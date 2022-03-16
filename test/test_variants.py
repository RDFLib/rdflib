import json
import logging
import os
import re
from dataclasses import dataclass, field
from pathlib import Path, PurePath
from test.testutils import GraphHelper
from typing import (
    ClassVar,
    Collection,
    Dict,
    Iterable,
    List,
    Optional,
    Pattern,
    Tuple,
    Union,
    cast,
)

import pytest
from _pytest.mark.structures import Mark, MarkDecorator, ParameterSet

import rdflib.compare
import rdflib.util
from rdflib.graph import ConjunctiveGraph, Graph
from rdflib.namespace import XSD
from rdflib.term import URIRef
from rdflib.util import guess_format

TEST_DIR = Path(__file__).parent.absolute()
VARIANTS_DIR = TEST_DIR / "variants"

# Put files from other directories in here.
EXTRA_FILES: List[Path] = []

SUFFIX_FORMAT_MAP = {**rdflib.util.SUFFIX_FORMAT_MAP, "hext": "hext"}


@dataclass
class GraphAsserts:
    """
    A specification of asserts that must be checked against a graph. This is
    read in from a JSON dict.
    """

    quad_count: Optional[int] = None

    def check(self, graph: ConjunctiveGraph) -> None:
        if self.quad_count is not None:
            assert self.quad_count == len(list(graph.quads()))


@dataclass(order=True)
class GraphVariants:
    """
    Represents a graph with multiple variants in different files.
    """

    key: str
    variants: Dict[str, Path] = field(default_factory=dict)
    asserts: GraphAsserts = field(default_factory=lambda: GraphAsserts())

    _variant_regex: ClassVar[Pattern[str]] = re.compile(
        r"^(.*?)(|[-]variant-[^/]+|[-]asserts)$"
    )

    def pytest_param(
        self,
        marks: Optional[
            Union[MarkDecorator, Collection[Union[MarkDecorator, Mark]]]
        ] = None,
    ) -> ParameterSet:
        if marks is None:
            marks = cast(Tuple[MarkDecorator], tuple())
        logging.debug("self = %s", self)
        return pytest.param(self, id=self.key, marks=marks)

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
    ) -> Dict[str, "GraphVariants"]:
        graph_varaint_dict: Dict[str, GraphVariants] = {}
        for file_path in file_paths:
            logging.debug("file_path = %s", file_path)
            file_key, variant_key = cls._decompose_path(file_path, basedir)
            # file_key = f"{file_path.parent / stem}"
            if file_key not in graph_varaint_dict:
                graph_variant = graph_varaint_dict[file_key] = GraphVariants(file_key)
            else:
                graph_variant = graph_varaint_dict[file_key]
            if variant_key.endswith("-asserts.json"):
                graph_variant.asserts = GraphAsserts(
                    **json.loads(file_path.read_text())
                )
            else:
                graph_variant.variants[variant_key] = file_path
        return graph_varaint_dict

    @classmethod
    def for_directory(
        cls, directory: Path, basedir: Optional[Path] = None
    ) -> Dict[str, "GraphVariants"]:
        file_paths = []
        for file_path in directory.glob("**/*"):
            if not file_path.is_file():
                continue
            if file_path.name.endswith(".md"):
                continue
            file_paths.append(file_path)
        logging.debug("file_paths = %s", file_paths)
        return cls.for_files(file_paths, basedir)


GRAPH_VARIANT_DICT = {
    **GraphVariants.for_directory(VARIANTS_DIR, TEST_DIR),
    **GraphVariants.for_files(EXTRA_FILES, TEST_DIR),
}

EXPECTED_FAILURES = {
    ("variants/schema_only_base"): pytest.mark.xfail(
        reason="Some issue with handling base URI that does not end with a slash",
        raises=ValueError,
    ),
}


def tests_found() -> None:
    logging.debug("VARIANTS_DIR = %s", VARIANTS_DIR)
    logging.debug("EXTRA_FILES = %s", EXTRA_FILES)
    assert len(GRAPH_VARIANT_DICT) >= 1
    logging.debug("ALL_VARIANT_GRAPHS = %s", GRAPH_VARIANT_DICT)
    xml_literal = GRAPH_VARIANT_DICT.get("variants/xml_literal")
    assert xml_literal is not None
    assert len(xml_literal.variants) >= 5
    assert xml_literal.asserts.quad_count == 1


@pytest.mark.parametrize(
    "graph_variant",
    [
        graph_variant.pytest_param(EXPECTED_FAILURES.get(graph_variant.key))
        for graph_variant in GRAPH_VARIANT_DICT.values()
    ],
)
def test_variants(graph_variant: GraphVariants) -> None:
    """
    All variants of a graph are isomorphic with the first variant, and thus
    eachother.
    """
    logging.debug("graph_variant = %s", graph_variant)
    public_id = URIRef(f"example:{graph_variant.key}")
    assert len(graph_variant.variants) > 0
    first_graph: Optional[Graph] = None
    for variant_key, variant_path in graph_variant.variants.items():
        logging.debug("variant_path = %s", variant_path)
        format = guess_format(variant_path.name, fmap=SUFFIX_FORMAT_MAP)
        assert format is not None, f"could not determine format for {variant_path.name}"
        graph = ConjunctiveGraph()
        graph.parse(variant_path, format=format, publicID=public_id)
        # Stripping data types as different parsers (e.g. hext) have different
        # opinions of when a bare string is of datatype XSD.string or not.
        # Probably something that needs more investigation.
        GraphHelper.strip_literal_datatypes(graph, {XSD.string})
        graph_variant.asserts.check(graph)
        if first_graph is None:
            first_graph = graph
        else:
            GraphHelper.assert_isomorphic(first_graph, graph)
