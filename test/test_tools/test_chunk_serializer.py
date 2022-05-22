import os
from pathlib import Path
import tempfile

try:
    from rdflib import Graph
    from rdflib.tools.chunk_serializer import serialize_in_chunks
    from test.data import TEST_DATA_DIR
except:
    px = str(Path(__file__).absolute().parent.parent.parent)
    import sys
    sys.path.insert(0, px)
    from rdflib import Graph
    from rdflib.tools.chunk_serializer import serialize_in_chunks
    from test.data import TEST_DATA_DIR


def test_chunk_by_triples():
    g = Graph().parse(Path(TEST_DATA_DIR) / "suites/w3c/trig/manifest.ttl")
    # this graph has 2,848 triples

    # make a temp dir to work with
    temp_dir_path = Path(tempfile.TemporaryDirectory().name)
    Path(temp_dir_path).mkdir()

    # serialize into chunks file with 100 triples each
    serialize_in_chunks(
        g,
        max_triples=100,
        file_name_stem="chunk_100",
        output_dir=temp_dir_path
    )

    # count the resultant .nt files, should be math.ceil(2848 / 100) = 25
    assert len(list(Path(temp_dir_path).glob("*.nt"))) == 25

    # check, when a graph is made from the chunk files, it's isomorphic with original
    g2 = Graph()
    for f in Path(temp_dir_path).glob("*.nt"):
        g2.parse(f, format="nt")

    assert g.isomorphic(g2), "Reconstructed graph is not isomorphic with original"


def test_chunk_by_size():
    g = Graph().parse(Path(TEST_DATA_DIR) / "suites/w3c/trig/manifest.ttl")
    # as an NT file, this graph is 323kb

    # make a temp dir to work with
    temp_dir_path = Path(tempfile.TemporaryDirectory().name)
    Path(temp_dir_path).mkdir()

    # serialize into chunks file of > 50kb each
    serialize_in_chunks(
        g,
        max_file_size_kb=50,
        file_name_stem="chunk_50k",
        output_dir=temp_dir_path
    )

    # check all files are size < 50kb, with a margin up to 60kb
    for f in Path(temp_dir_path).glob("*.nt"):
        assert os.path.getsize(f) < 60000

    # check, when a graph is made from the chunk files, it's isomorphic with original
    g2 = Graph()
    for f in Path(temp_dir_path).glob("*.nt"):
        g2.parse(f, format="nt")

    assert g.isomorphic(g2), "Reconstructed graph is not isomorphic with original"
