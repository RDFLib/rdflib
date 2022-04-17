import json
import subprocess
import sys
from pathlib import Path
from test.data import TEST_DATA_DIR

from rdflib import RDF, SKOS


def test_definednamespace_creator_qb():
    """
    Tests basic use of DefinedNamespace creator script using QB
    """

    definednamespace_script = (
        Path(__file__).parent.parent.parent
        / "rdflib"
        / "tools"
        / "defined_namespace_creator.py"
    )
    qb_data_file = Path(TEST_DATA_DIR) / "defined_namespaces" / "qb.ttl"
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
            if (
                'Attachable: URIRef  # Abstract superclass for everything that can have attributes and dimensions'
                in line
            ):
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

    definednamespace_script = (
        Path(__file__).parent.parent.parent
        / "rdflib"
        / "tools"
        / "defined_namespace_creator.py"
    )
    qb_data_file = Path(TEST_DATA_DIR) / "defined_namespaces" / "fake.xxx"
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

    definednamespace_script = (
        Path(__file__).parent.parent.parent
        / "rdflib"
        / "tools"
        / "defined_namespace_creator.py"
    )
    qb_data_file = Path(TEST_DATA_DIR) / "defined_namespaces" / "fake.xxx"
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


def test_definednamespace_dir():
    x = dir(RDF)

    values = [
        RDF.nil,
        RDF.direction,
        RDF.first,
        RDF.language,
        RDF.object,
        RDF.predicate,
        RDF.rest,
        RDF.subject,
        RDF.type,
        RDF.value,
        RDF.Alt,
        RDF.Bag,
        RDF.CompoundLiteral,
        RDF.List,
        RDF.Property,
        RDF.Seq,
        RDF.Statement,
        RDF.HTML,
        RDF.JSON,
        RDF.PlainLiteral,
        RDF.XMLLiteral,
        RDF.langString,
    ]

    assert len(values) == len(x)

    for value in values:
        assert value in x


def test_definednamespace_jsonld_context():
    expected = {
        "@context": {
            "skos": "http://www.w3.org/2004/02/skos/core#",
            "altLabel": "skos:altLabel",
            "broadMatch": "skos:broadMatch",
            "broader": "skos:broader",
            "broaderTransitive": "skos:broaderTransitive",
            "changeNote": "skos:changeNote",
            "closeMatch": "skos:closeMatch",
            "definition": "skos:definition",
            "editorialNote": "skos:editorialNote",
            "exactMatch": "skos:exactMatch",
            "example": "skos:example",
            "hasTopConcept": "skos:hasTopConcept",
            "hiddenLabel": "skos:hiddenLabel",
            "historyNote": "skos:historyNote",
            "inScheme": "skos:inScheme",
            "mappingRelation": "skos:mappingRelation",
            "member": "skos:member",
            "memberList": "skos:memberList",
            "narrowMatch": "skos:narrowMatch",
            "narrower": "skos:narrower",
            "narrowerTransitive": "skos:narrowerTransitive",
            "notation": "skos:notation",
            "note": "skos:note",
            "prefLabel": "skos:prefLabel",
            "related": "skos:related",
            "relatedMatch": "skos:relatedMatch",
            "scopeNote": "skos:scopeNote",
            "semanticRelation": "skos:semanticRelation",
            "topConceptOf": "skos:topConceptOf",
            "Collection": "skos:Collection",
            "Concept": "skos:Concept",
            "ConceptScheme": "skos:ConceptScheme",
            "OrderedCollection": "skos:OrderedCollection",
        }
    }
    actual = SKOS.as_jsonld_context("skos")

    assert actual == expected
