import inspect
import logging
import subprocess
import sys
import warnings
from contextlib import ExitStack
from dataclasses import dataclass
from pathlib import Path
from test.data import TEST_DATA_DIR
from typing import Optional, Type

import pytest

from rdflib import RDF, SKOS
from rdflib.namespace import DefinedNamespace, Namespace
from rdflib.term import URIRef


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
                "Attachable: URIRef  # Abstract superclass for everything that can have attributes and dimensions"
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


prefix = "http://example.com/"


class DFNSNoNS(DefinedNamespace):
    defined: URIRef
    _defined: URIRef


class DFNSDefaults(DefinedNamespace):
    _NS = Namespace(f"{prefix}DFNSDefaults#")
    defined: URIRef
    _defined: URIRef


class DFNSDefaultsEmpty(DefinedNamespace):
    _NS = Namespace(f"{prefix}DFNSDefaultsEmpty#")


class DFNSWarnFailEmpty(DefinedNamespace):
    _NS = Namespace(f"{prefix}DFNSWarnFailEmpty#")
    _warn = True
    _fail = True


class DFNSNoWarnNoFail(DefinedNamespace):
    _NS = Namespace(f"{prefix}DFNSNoWarnNoFail#")
    _warn = False
    _fail = False
    defined: URIRef
    _defined: URIRef


class DFNSNoWarnFail(DefinedNamespace):
    _NS = Namespace(f"{prefix}DFNSNoWarnFail#")
    _warn = False
    _fail = True
    defined: URIRef
    _defined: URIRef


class DFNSWarnNoFail(DefinedNamespace):
    _NS = Namespace(f"{prefix}DFNSWarnNoFail#")
    _warn = True
    _fail = False
    defined: URIRef
    _defined: URIRef


class DFNSWarnFail(DefinedNamespace):
    _NS = Namespace(f"{prefix}DFNSWarnFail#")
    _warn = True
    _fail = True
    defined: URIRef
    _defined: URIRef


@dataclass
class DFNSInfo:
    dfns: Type[DefinedNamespace]
    suffix: Optional[str]
    has_attrs: bool = True


dfns_infos = [
    DFNSInfo(DFNSNoNS, None),
    DFNSInfo(DFNSDefaults, "DFNSDefaults#"),
    DFNSInfo(DFNSNoWarnNoFail, "DFNSNoWarnNoFail#"),
    DFNSInfo(DFNSWarnFail, "DFNSWarnFail#"),
    DFNSInfo(DFNSNoWarnFail, "DFNSNoWarnFail#"),
    DFNSInfo(DFNSWarnNoFail, "DFNSWarnNoFail#"),
    DFNSInfo(DFNSDefaultsEmpty, "DFNSDefaultsEmpty#", False),
    DFNSInfo(DFNSWarnFailEmpty, "DFNSWarnFailEmpty#", False),
    DFNSInfo(DefinedNamespace, None, False),
]
dfns_list = [item.dfns for item in dfns_infos]


def get_dfns_info(dfns: Type[DefinedNamespace]) -> DFNSInfo:
    for dfns_info in dfns_infos:
        if dfns_info.dfns is dfns:
            return dfns_info
    raise ValueError("No DFNSInfo for the DefinedNamespace passed in ...")


@pytest.fixture(
    scope="module",
    params=[item.dfns for item in dfns_infos],
)
def dfns(request) -> DFNSInfo:
    assert issubclass(request.param, DefinedNamespace)
    return request.param


def test_repr(dfns: Type[DefinedNamespace]) -> None:
    dfns_info = get_dfns_info(dfns)
    ns_uri = f"{prefix}{dfns_info.suffix}"
    logging.debug("ns_uri = %s", ns_uri)

    repr_str: Optional[str] = None

    with ExitStack() as xstack:
        if dfns_info.suffix is None:
            xstack.enter_context(pytest.raises(AttributeError))
        repr_str = f"{dfns_info.dfns!r}"
    if dfns_info.suffix is None:
        assert repr_str is None
    else:
        assert repr_str is not None
        repro = eval(repr_str)
        assert ns_uri == f"{repro}"


def test_inspect(dfns: Type[DefinedNamespace]) -> None:
    """
    `inspect.signature` returns. This is here to check that this does not
    trigger infinite recursion.
    """
    inspect.signature(dfns, follow_wrapped=True)


@pytest.mark.parametrize(
    ["attr_name", "is_defined"],
    [
        ("defined", True),
        ("_defined", True),
        ("notdefined", False),
        ("_notdefined", False),
    ],
)
def test_value(dfns: Type[DefinedNamespace], attr_name: str, is_defined: bool) -> None:
    dfns_info = get_dfns_info(dfns)
    if dfns_info.has_attrs is False:
        is_defined = False
    resolved: Optional[str] = None
    with ExitStack() as xstack:
        warnings_record = xstack.enter_context(warnings.catch_warnings(record=True))
        if dfns_info.suffix is None or (not is_defined and dfns._fail is True):
            xstack.enter_context(pytest.raises(AttributeError))
        resolved = eval(f"dfns.{attr_name}")
    if dfns_info.suffix is not None:
        if is_defined or dfns._fail is False:
            assert f"{prefix}{dfns_info.suffix}{attr_name}" == f"{resolved}"
        else:
            assert resolved is None
        if dfns._warn is False:
            assert len(warnings_record) == 0
        elif not is_defined and resolved is not None:
            assert len(warnings_record) == 1
    else:
        assert resolved is None


@pytest.mark.parametrize(
    ["attr_name", "is_defined"],
    [
        ("defined", True),
        ("_defined", True),
        ("notdefined", False),
        ("_notdefined", False),
    ],
)
def test_contains(
    dfns: Type[DefinedNamespace], attr_name: str, is_defined: bool
) -> None:
    dfns_info = get_dfns_info(dfns)
    if dfns_info.suffix is not None:
        logging.debug("dfns_info = %s", dfns_info)
    if dfns_info.has_attrs is False:
        is_defined = False
    does_contain: Optional[bool] = None
    with ExitStack() as xstack:
        if dfns_info.suffix is None:
            xstack.enter_context(pytest.raises(AttributeError))
        does_contain = attr_name in dfns
    if dfns_info.suffix is not None:
        if is_defined:
            assert does_contain is True
        else:
            assert does_contain is False
    else:
        assert does_contain is None


@pytest.mark.parametrize(
    ["attr_name", "is_defined"],
    [
        ("defined", True),
        ("_defined", True),
        ("notdefined", False),
        ("_notdefined", False),
    ],
)
def test_hasattr(
    dfns: Type[DefinedNamespace], attr_name: str, is_defined: bool
) -> None:
    dfns_info = get_dfns_info(dfns)
    if dfns_info.suffix is not None:
        logging.debug("dfns_info = %s", dfns_info)
    if dfns_info.has_attrs is False:
        is_defined = False
    has_attr: Optional[bool] = None
    has_attr = hasattr(dfns, attr_name)
    if dfns_info.suffix is not None and (is_defined or dfns._fail is False):
        assert has_attr is True
    else:
        assert has_attr is False


def test_dir(dfns: Type[DefinedNamespace]) -> None:
    dfns_info = get_dfns_info(dfns)
    does_contain: Optional[bool] = None
    with ExitStack() as xstack:
        # dir should work for DefinedNamespace as this is called by sphinx to
        # document it.
        if dfns_info.suffix is None and dfns is not DefinedNamespace:
            xstack.enter_context(pytest.raises(AttributeError))
        attrs = list(dir(dfns))
    if dfns_info.suffix is not None:
        if dfns_info.has_attrs:
            assert set(attrs) == {
                URIRef(f"{prefix}{dfns_info.suffix}defined"),
                URIRef(f"{prefix}{dfns_info.suffix}_defined"),
            }
        else:
            assert list(attrs) == []
    else:
        assert does_contain is None
