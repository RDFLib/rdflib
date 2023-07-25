from __future__ import annotations

import logging
import os
from contextlib import ExitStack
from pathlib import Path
from test.data import TEST_DATA_DIR
from test.utils import GraphHelper
from test.utils.graph import cached_graph
from test.utils.namespace import MF
from test.utils.path import ctx_chdir
from typing import TYPE_CHECKING, Any, Dict, Optional, Tuple, Union

import pytest

from rdflib import Graph
from rdflib.tools.chunk_serializer import serialize_in_chunks

if TYPE_CHECKING:
    from builtins import ellipsis

logger = logging.getLogger(__name__)


def test_chunk_by_triples(tmp_path: Path):
    g = cached_graph((TEST_DATA_DIR / "suites/w3c/trig/manifest.ttl",))
    # this graph has 2,848 triples

    # serialize into chunks file with 100 triples each
    serialize_in_chunks(
        g, max_triples=100, file_name_stem="chunk_100", output_dir=tmp_path
    )

    # count the resultant .nt files, should be math.ceil(2848 / 100) = 25
    assert len(list(tmp_path.glob("*.nt"))) == 25

    # check, when a graph is made from the chunk files, it's isomorphic with original
    g2 = Graph()
    for f in tmp_path.glob("*.nt"):
        g2.parse(f, format="nt")

    assert g.isomorphic(g2), "Reconstructed graph is not isomorphic with original"


def test_chunk_by_size(tmp_path: Path):
    g = cached_graph((TEST_DATA_DIR / "suites/w3c/trig/manifest.ttl",))
    # as an NT file, this graph is 323kb

    # serialize into chunks file of > 50kb each
    serialize_in_chunks(
        g, max_file_size_kb=50, file_name_stem="chunk_50k", output_dir=tmp_path
    )

    # check all files are size < 50kb, with a margin up to 60kb
    for f in Path(tmp_path).glob("*.nt"):
        assert os.path.getsize(f) < 50000

    # check, when a graph is made from the chunk files, it's isomorphic with original
    g2 = Graph()
    for f in Path(tmp_path).glob("*.nt"):
        g2.parse(f, format="nt")

    assert g.isomorphic(g2), "Reconstructed graph is not isomorphic with original"


@pytest.mark.parametrize(
    [
        "test_graph_path",
        "max_triples",
        "max_file_size_kb",
        "write_prefixes",
        "set_output_dir",
        "expected_file_count",
    ],
    [
        (TEST_DATA_DIR / "defined_namespaces/mf.ttl", ..., ..., False, True, 1),
        (TEST_DATA_DIR / "defined_namespaces/mf.ttl", ..., ..., True, False, 2),
        (TEST_DATA_DIR / "defined_namespaces/mf.ttl", ..., 5, True, False, (3, 7)),
        (TEST_DATA_DIR / "defined_namespaces/mf.ttl", ..., 1, False, True, (15, 25)),
        (TEST_DATA_DIR / "defined_namespaces/mf.ttl", 10000, 1, False, True, (15, 25)),
        (TEST_DATA_DIR / "defined_namespaces/mf.ttl", 20, ..., False, True, 5),
        (TEST_DATA_DIR / "defined_namespaces/mf.ttl", 20, ..., True, True, 6),
        (TEST_DATA_DIR / "defined_namespaces/mf.ttl", 100, ..., True, True, 2),
        (TEST_DATA_DIR / "defined_namespaces/mf.ttl", 100, ..., False, True, 1),
    ],
)
def test_chuking(
    tmp_path: Path,
    test_graph_path: Path,
    max_triples: Union[ellipsis, int],
    max_file_size_kb: Union[ellipsis, int, None],
    write_prefixes: bool,
    set_output_dir: bool,
    expected_file_count: Optional[Union[int, Tuple[Optional[int], Optional[int]]]],
) -> None:
    test_graph = cached_graph((test_graph_path,))
    kwargs: Dict[str, Any] = {"write_prefixes": write_prefixes}
    if max_triples is not ...:
        kwargs["max_triples"] = max_triples
    if max_file_size_kb is not ...:
        kwargs["max_file_size_kb"] = max_file_size_kb
    logger.debug("kwargs = %s", kwargs)
    with ExitStack() as xstack:
        if set_output_dir:
            kwargs["output_dir"] = tmp_path
        else:
            xstack.enter_context(ctx_chdir(tmp_path))
        serialize_in_chunks(test_graph, **kwargs)

    # set the values to defaults if they were elided in test parameters.
    if max_file_size_kb is ...:
        max_file_size_kb = None
    if max_triples is ...:
        max_triples = 10000

    stem = "chunk"

    output_paths = set(item.relative_to(tmp_path) for item in tmp_path.glob("**/*"))
    # output_filenames = set(f"{item}" for item in output_paths)

    if logger.isEnabledFor(logging.DEBUG):
        logger.debug("tmp_path = %s files = %s", tmp_path, output_paths)

    if isinstance(expected_file_count, tuple):
        if expected_file_count[0] is not None:
            assert expected_file_count[0] <= len(output_paths)
        if expected_file_count[1] is not None:
            assert expected_file_count[1] >= len(output_paths)
    elif isinstance(expected_file_count, int):
        assert expected_file_count == len(output_paths)

    recovered_graph = Graph(bind_namespaces="none")

    if write_prefixes is True:
        prefixes_path = Path(f"{stem}_000000.ttl")
        assert prefixes_path in output_paths
        output_paths.remove(prefixes_path)
        recovered_graph.parse(tmp_path / prefixes_path, format="turtle")
        namespaces_data = (tmp_path / prefixes_path).read_text("utf-8")
        assert f"{MF}" in namespaces_data

    if len(output_paths) == 1:
        all_file = Path(f"{stem}_all.nt")
        assert all_file in output_paths
        all_file = tmp_path / all_file
        file_bytes = all_file.read_bytes()
        recovered_graph.parse(all_file, format="nt")
        if isinstance(max_file_size_kb, int):
            assert len(file_bytes) <= (max_file_size_kb * 1000)
        elif isinstance(max_triples, int):
            assert len(recovered_graph) <= max_triples

    elif max_file_size_kb is not None:
        assert isinstance(max_file_size_kb, int)
        for output_path in output_paths:
            output_path = tmp_path / output_path
            file_bytes = output_path.read_bytes()
            assert len(file_bytes) <= (max_file_size_kb * 1000)
            logger.debug("reading %s", output_path)
            recovered_graph.parse(output_path, format="nt")
    else:
        assert isinstance(max_triples, int)
        for output_path in output_paths:
            output_path = tmp_path / output_path
            file_bytes = output_path.read_bytes()
            triple_count = len(recovered_graph)
            logger.debug("reading %s", output_path)
            recovered_graph.parse(output_path, format="nt")
            extra_triples = len(recovered_graph) - triple_count
            assert extra_triples <= max_triples

    logger.debug("checking isomorphism")
    GraphHelper.assert_isomorphic(test_graph, recovered_graph)
