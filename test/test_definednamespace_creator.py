import sys
import subprocess
from pathlib import Path


def test_definednamespace_creator_qb():
    """
    Tests basic use of DefinedNamespace creator script using QB
    """

    definednamespace_script = Path(__file__).parent.parent / "rdflib" / "tools" / "defined_namespace_creator.py"
    qb_data_file = Path(__file__).parent / "defined_namespaces" / "qb.ttl"
    print("\n")
    print(f"Using {definednamespace_script}...")
    print(f"Testing {qb_data_file}...")
    completed = subprocess.run(
        [
            sys.executable,
            str(definednamespace_script),
            str(qb_data_file),
            "http://purl.org/linked-data/cube#",
            "QB",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
    )
    assert completed.returncode == 0, "subprocess exited incorrectly"
    assert Path.is_file(Path("_QB.py")), "_QB.py file not created"
    has_ns = False
    has_test_class = False
    with open(Path("_QB.py")) as f:
        for line in f.readlines():
            if '_NS = Namespace("http://purl.org/linked-data/cube#")' in line:
                has_ns = True
            if 'Attachable: URIRef  # Abstract superclass for everything that can have attributes and dimensions' in line:
                has_test_class = True
    assert has_ns, "_QB.py does not contain _NS"
    assert has_test_class, "_QB.py does not class Attachable"

    # cleanup
    Path.unlink(Path("_QB.py"))


def test_definednamespace_creator_fake():
    """
    Tests incorrect use of DefinedNamespace creator script -
    RDF file of unknonwn type
    """

    definednamespace_script = Path(__file__).parent.parent / "rdflib" / "tools" / "defined_namespace_creator.py"
    qb_data_file = Path(__file__).parent / "defined_namespaces" / "fake.xxx"
    print("\n")
    print(f"Using {definednamespace_script}...")
    print(f"Testing {qb_data_file}...(expected to fail)")
    completed = subprocess.run(
        [
            sys.executable,
            str(definednamespace_script),
            str(qb_data_file),
            "http://purl.org/linked-data/cube#",
            "QB",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
    )
    assert completed.returncode == 1, "subprocess exited incorrectly (failure expected)"


def test_definednamespace_creator_bad_ns():
    """
    Tests incorrect use of DefinedNamespace creator script -
    supplied namespace doesn't end in # or /
    """

    definednamespace_script = Path(__file__).parent.parent / "rdflib" / "tools" / "defined_namespace_creator.py"
    qb_data_file = Path(__file__).parent / "defined_namespaces" / "fake.xxx"
    print("\n")
    print(f"Using {definednamespace_script}...")
    print(f"Testing {qb_data_file}...(expected to fail - bad NS given)")
    completed = subprocess.run(
        [
            sys.executable,
            str(definednamespace_script),
            str(qb_data_file),
            "http://purl.org/linked-data/cube",
            "QB",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
    )
    assert completed.returncode == 1, "subprocess exited incorrectly (failure expected)"
