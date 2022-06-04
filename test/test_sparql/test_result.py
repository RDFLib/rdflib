import enum
import inspect
import itertools
import logging
import re
import sys
from contextlib import contextmanager
from dataclasses import dataclass
from io import BytesIO, StringIO
from pathlib import Path
from test.utils.result import ResultType
from typing import (
    IO,
    BinaryIO,
    Dict,
    Iterator,
    Mapping,
    Optional,
    Pattern,
    Sequence,
    Set,
    TextIO,
    Tuple,
    Type,
    Union,
)

import pytest
from _pytest.mark.structures import Mark, MarkDecorator, ParameterSet
from pyparsing import ParseException

from rdflib.graph import Graph
from rdflib.namespace import Namespace
from rdflib.query import Result, ResultRow
from rdflib.term import BNode, Identifier, Literal, Node, Variable

BindingsType = Sequence[Mapping[Variable, Identifier]]
ParseOutcomeType = Union[BindingsType, Type[Exception]]


@pytest.mark.parametrize(
    ("data", "format", "parse_outcome"),
    [
        pytest.param(
            "a\n1",
            "csv",
            [{Variable("a"): Literal("1")}],
            id="csv-okay-1c1r",
        ),
        pytest.param(
            '?a\n"1"',
            "tsv",
            [{Variable("a"): Literal("1")}],
            id="tsv-okay-1c1r",
        ),
        pytest.param(
            "1,2,3\nhttp://example.com",
            "tsv",
            ParseException,
            id="tsv-invalid",
        ),
    ],
)
def test_select_result_parse(
    data: str, format: str, parse_outcome: ParseOutcomeType
) -> None:
    """
    Parsing serialized SPARQL result produces expected bindings.
    """
    logging.debug("data = %s", data)

    if inspect.isclass(parse_outcome) and issubclass(parse_outcome, Exception):
        with pytest.raises(parse_outcome):
            parsed_result = Result.parse(StringIO(data), format=format)
    else:
        parsed_result = Result.parse(StringIO(data), format=format)
        assert parse_outcome == parsed_result.bindings


EGSCHEME = Namespace("example:")


@pytest.mark.parametrize(
    ("node", "format", "expected_result"),
    [
        (BNode(), "csv", re.compile(r"^_:.*$")),
        (BNode("a"), "csv", "_:a"),
        (Literal("x11"), "csv", "x11"),
    ],
)
def test_xsv_serialize(
    node: Identifier, format: str, expected_result: Union[Pattern[str], str]
) -> None:
    graph = Graph()
    graph.add((EGSCHEME.checkSubject, EGSCHEME.checkPredicate, node))
    result = graph.query(
        f"""
    PREFIX egscheme: <{EGSCHEME}>
    SELECT ?o {{
        egscheme:checkSubject egscheme:checkPredicate ?o
    }}
    """
    )
    assert len(result.bindings) == 1
    with BytesIO() as bio:
        result.serialize(bio, format=format)
        result_text = bio.getvalue().decode("utf-8")
    result_lines = result_text.splitlines()
    assert len(result_lines) == 2
    logging.debug("result_lines[1] = %r", result_lines[1])
    if isinstance(expected_result, str):
        assert expected_result == result_lines[1]
    else:
        assert expected_result.match(result_lines[1])


@pytest.fixture(scope="module")
def select_result(rdfs_graph: Graph) -> Result:
    query = """
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT ?subject ?predicate ?object WHERE {
        VALUES ?subject { rdfs:Resource }
        ?subject ?predicate ?object
    }
    ORDER BY ?subject ?predicate ?object
    """
    result = rdfs_graph.query(query)
    return result


def check_serialized(format: str, result: Result, data: str) -> None:
    if format == "txt":
        # This does somewhat of a smoke tests that data is the txt
        # serialization of the given result. This is by no means perfect but
        # better than nothing.
        txt_lines = data.splitlines()
        assert (len(txt_lines) - 2) == len(result)
        assert re.match(r"^[-]+$", txt_lines[1])
        header = txt_lines[0]
        assert result.vars is not None
        for var in result.vars:
            assert var in header
        for row_index, row in enumerate(result):
            txt_row = txt_lines[row_index + 2]
            value: Node
            assert isinstance(row, ResultRow)
            for key, value in row.asdict().items():
                assert f"{value}" in txt_row
    else:
        parsed_result = Result.parse(StringIO(data), format=format)
        assert result == parsed_result


class ResultFormatTrait(enum.Enum):
    HAS_SERIALIZER = enum.auto()
    HAS_PARSER = enum.auto()


@dataclass(frozen=True)
class ResultFormat:
    name: str
    supported_types: Set[ResultType]
    traits: Set[ResultFormatTrait]
    encodings: Set[str]


class ResultFormats(Dict[str, ResultFormat]):
    @classmethod
    def make(cls, *result_format: ResultFormat) -> "ResultFormats":
        result = cls()
        for item in result_format:
            result[item.name] = item
        return result


result_formats = ResultFormats.make(
    ResultFormat(
        "csv",
        {ResultType.SELECT},
        {
            ResultFormatTrait.HAS_PARSER,
            ResultFormatTrait.HAS_SERIALIZER,
        },
        {"utf-8", "utf-16"},
    ),
    ResultFormat(
        "txt",
        {ResultType.SELECT},
        {
            ResultFormatTrait.HAS_SERIALIZER,
        },
        {"utf-8"},
    ),
    ResultFormat(
        "json",
        {ResultType.SELECT},
        {
            ResultFormatTrait.HAS_PARSER,
            ResultFormatTrait.HAS_SERIALIZER,
        },
        {"utf-8", "utf-16"},
    ),
    ResultFormat(
        "xml",
        {ResultType.SELECT},
        {
            ResultFormatTrait.HAS_PARSER,
            ResultFormatTrait.HAS_SERIALIZER,
        },
        {"utf-8"},
    ),
    ResultFormat(
        "tsv",
        {ResultType.SELECT},
        {
            ResultFormatTrait.HAS_PARSER,
        },
        {"utf-8", "utf-16"},
    ),
)


class DestinationType(enum.Enum):
    TEXT_IO = enum.auto()
    BINARY_IO = enum.auto()
    STR_PATH = enum.auto()


class SourceType(enum.Enum):
    TEXT_IO = enum.auto()
    BINARY_IO = enum.auto()


@dataclass(frozen=True)
class DestRef:
    param: Union[str, IO[bytes], TextIO]
    path: Path


@contextmanager
def make_dest(
    tmp_path: Path, type: Optional[DestinationType]
) -> Iterator[Optional[DestRef]]:
    if type is None:
        yield None
        return
    path = tmp_path / f"file-{type}"
    if type is DestinationType.STR_PATH:
        yield DestRef(f"{path}", path)
    elif type is DestinationType.BINARY_IO:
        with path.open("wb") as bfh:
            yield DestRef(bfh, path)
    elif type is DestinationType.TEXT_IO:
        with path.open("w") as fh:
            yield DestRef(fh, path)
    else:
        raise ValueError(f"unsupported type {type}")


def make_select_result_serialize_parse_tests() -> Iterator[ParameterSet]:
    xfails: Dict[
        Tuple[str, Optional[DestinationType], str], Union[MarkDecorator, Mark]
    ] = {
        ("csv", DestinationType.TEXT_IO, "utf-8"): pytest.mark.xfail(raises=TypeError),
        ("csv", DestinationType.TEXT_IO, "utf-16"): pytest.mark.xfail(raises=TypeError),
        ("json", DestinationType.TEXT_IO, "utf-8"): pytest.mark.xfail(raises=TypeError),
        ("json", DestinationType.TEXT_IO, "utf-16"): pytest.mark.xfail(
            raises=TypeError
        ),
        ("txt", DestinationType.BINARY_IO, "utf-8"): pytest.mark.xfail(
            raises=TypeError
        ),
        ("txt", DestinationType.BINARY_IO, "utf-16"): pytest.mark.xfail(
            raises=TypeError
        ),
        ("txt", DestinationType.STR_PATH, "utf-8"): pytest.mark.xfail(raises=TypeError),
        ("txt", DestinationType.STR_PATH, "utf-16"): pytest.mark.xfail(
            raises=TypeError
        ),
    }
    if sys.platform == "win32":
        xfails[("csv", DestinationType.STR_PATH, "utf-8")] = pytest.mark.xfail(
            raises=FileNotFoundError,
            reason="string path handling does not work on windows",
        )
        xfails[("csv", DestinationType.STR_PATH, "utf-16")] = pytest.mark.xfail(
            raises=FileNotFoundError,
            reason="string path handling does not work on windows",
        )
        xfails[("json", DestinationType.STR_PATH, "utf-8")] = pytest.mark.xfail(
            raises=FileNotFoundError,
            reason="string path handling does not work on windows",
        )
        xfails[("json", DestinationType.STR_PATH, "utf-16")] = pytest.mark.xfail(
            raises=FileNotFoundError,
            reason="string path handling does not work on windows",
        )
        xfails[("xml", DestinationType.STR_PATH, "utf-8")] = pytest.mark.xfail(
            raises=FileNotFoundError,
            reason="string path handling does not work on windows",
        )
    formats = [
        format
        for format in result_formats.values()
        if ResultFormatTrait.HAS_SERIALIZER in format.traits
        and ResultType.SELECT in format.supported_types
    ]
    destination_types: Set[Optional[DestinationType]] = {None}
    destination_types.update(set(DestinationType))
    for format, destination_type in itertools.product(formats, destination_types):
        for encoding in format.encodings:
            xfail = xfails.get((format.name, destination_type, encoding))
            marks = (xfail,) if xfail is not None else ()
            yield pytest.param(
                (format, destination_type, encoding),
                id=f"{format.name}-{None if destination_type is None else destination_type.name}-{encoding}",
                marks=marks,
            )


@pytest.mark.parametrize(
    ["args"],
    make_select_result_serialize_parse_tests(),
)
def test_select_result_serialize_parse(
    tmp_path: Path,
    select_result: Result,
    args: Tuple[ResultFormat, Optional[DestinationType], str],
) -> None:
    """
    Round tripping of a select query through the serializer and parser of a
    specific format results in an equivalent result object.
    """
    format, destination_type, encoding = args
    with make_dest(tmp_path, destination_type) as dest_ref:
        destination = None if dest_ref is None else dest_ref.param
        serialize_result = select_result.serialize(
            destination=destination,
            format=format.name,
            encoding=encoding,
        )

    if dest_ref is None:
        assert isinstance(serialize_result, bytes)
        serialized_data = serialize_result.decode(encoding)
    else:
        assert serialize_result is None
        serialized_data = dest_ref.path.read_bytes().decode(encoding)

    logging.debug("serialized_data = %s", serialized_data)
    check_serialized(format.name, select_result, serialized_data)


def serialize_select(select_result: Result, format: str, encoding: str) -> bytes:
    if format == "tsv":
        # This is hardcoded as it is particularly diffficult to generate. If the result changes this will have to be adjusted by hand.
        return '''\
?subject	?predicate	?object
<http://www.w3.org/2000/01/rdf-schema#Resource>	<http://www.w3.org/1999/02/22-rdf-syntax-ns#type>	<http://www.w3.org/2000/01/rdf-schema#Class>
<http://www.w3.org/2000/01/rdf-schema#Resource>	<http://www.w3.org/2000/01/rdf-schema#comment>	"The class resource, everything."
<http://www.w3.org/2000/01/rdf-schema#Resource>	<http://www.w3.org/2000/01/rdf-schema#isDefinedBy>	<http://www.w3.org/2000/01/rdf-schema#>
<http://www.w3.org/2000/01/rdf-schema#Resource>	<http://www.w3.org/2000/01/rdf-schema#label>	"Resource"'''.encode(
            encoding
        )
    else:
        result = select_result.serialize(format=format)
        assert result is not None
        return result


def make_select_result_parse_serialized_tests() -> Iterator[ParameterSet]:
    xfails: Dict[Tuple[str, Optional[SourceType], str], Union[MarkDecorator, Mark]] = {}
    formats = [
        format
        for format in result_formats.values()
        if ResultFormatTrait.HAS_PARSER in format.traits
        and ResultType.SELECT in format.supported_types
    ]
    source_types = set(SourceType)
    for format, destination_type in itertools.product(formats, source_types):
        for encoding in {"utf-8"}:
            xfail = xfails.get((format.name, destination_type, encoding))
            marks = (xfail,) if xfail is not None else ()
            yield pytest.param(
                (format, destination_type, encoding),
                id=f"{format.name}-{None if destination_type is None else destination_type.name}-{encoding}",
                marks=marks,
            )


@pytest.mark.parametrize(
    ["args"],
    make_select_result_parse_serialized_tests(),
)
def test_select_result_parse_serialized(
    tmp_path: Path,
    select_result: Result,
    args: Tuple[ResultFormat, SourceType, str],
) -> None:
    """
    Parsing a serialized result produces the expected result object.
    """
    format, source_type, encoding = args

    serialized_data = serialize_select(select_result, format.name, encoding)

    logging.debug("serialized_data = %s", serialized_data.decode(encoding))

    source: Union[BinaryIO, TextIO]
    if source_type is SourceType.TEXT_IO:
        source = StringIO(serialized_data.decode(encoding))
    elif source_type is SourceType.BINARY_IO:
        source = BytesIO(serialized_data)
    else:
        raise ValueError(f"Invalid source_type {source_type}")

    parsed_result = Result.parse(source, format=format.name)

    assert select_result == parsed_result
