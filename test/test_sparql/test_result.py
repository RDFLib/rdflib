import enum
import inspect
import itertools
import logging
import re
import socket
from contextlib import ExitStack
from io import BytesIO, StringIO
from pathlib import Path, PosixPath, PurePath
from test.utils.destination import DestinationType, DestParmType
from test.utils.result import (
    ResultFormat,
    ResultFormatInfo,
    ResultFormatTrait,
    ResultType,
)
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
from urllib.parse import urlsplit, urlunsplit

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


class SourceType(enum.Enum):
    TEXT_IO = enum.auto()
    BINARY_IO = enum.auto()


DESTINATION_TYPES = {
    DestinationType.TEXT_IO,
    DestinationType.BINARY_IO,
    DestinationType.STR_PATH,
    DestinationType.FILE_URI,
    DestinationType.RETURN,
}

ResultDestParamType = Union[str, IO[bytes], TextIO]


def narrow_dest_param(param: DestParmType) -> ResultDestParamType:
    assert not isinstance(param, PurePath)
    return param


def make_select_result_serialize_parse_tests() -> Iterator[ParameterSet]:
    xfails: Dict[Tuple[str, DestinationType, str], Union[MarkDecorator, Mark]] = {
        ("csv", DestinationType.TEXT_IO, "utf-8"): pytest.mark.xfail(raises=TypeError),
        ("csv", DestinationType.TEXT_IO, "utf-16"): pytest.mark.xfail(raises=TypeError),
        ("json", DestinationType.TEXT_IO, "utf-8"): pytest.mark.xfail(raises=TypeError),
        ("json", DestinationType.TEXT_IO, "utf-16"): pytest.mark.xfail(
            raises=TypeError
        ),
        ("txt", DestinationType.BINARY_IO, "utf-8"): pytest.mark.xfail(
            raises=TypeError
        ),
        ("txt", DestinationType.STR_PATH, "utf-8"): pytest.mark.xfail(raises=TypeError),
        ("txt", DestinationType.FILE_URI, "utf-8"): pytest.mark.xfail(raises=TypeError),
    }
    format_infos = [
        format_info
        for format_info in ResultFormat.info_set()
        if ResultFormatTrait.HAS_SERIALIZER in format_info.traits
        and ResultType.SELECT in format_info.supported_types
    ]
    for format_info, destination_type in itertools.product(
        format_infos, DESTINATION_TYPES
    ):
        for encoding in format_info.encodings:
            xfail = xfails.get((format_info.name, destination_type, encoding))
            marks = (xfail,) if xfail is not None else ()
            yield pytest.param(
                (format_info, destination_type, encoding),
                id=f"{format_info.name}-{destination_type.name}-{encoding}",
                marks=marks,
            )


@pytest.mark.parametrize(
    ["test_args"],
    make_select_result_serialize_parse_tests(),
)
def test_select_result_serialize_parse(
    tmp_path: Path,
    select_result: Result,
    test_args: Tuple[ResultFormatInfo, DestinationType, str],
) -> None:
    """
    Round tripping of a select query through the serializer and parser of a
    specific format results in an equivalent result object.
    """
    format_info, destination_type, encoding = test_args
    with destination_type.make_ref(tmp_path, encoding) as dest_ref:
        destination = None if dest_ref is None else narrow_dest_param(dest_ref.param)
        serialize_result = select_result.serialize(
            destination=destination,
            format=format_info.name,
            encoding=encoding,
        )

    if dest_ref is None:
        assert isinstance(serialize_result, bytes)
        serialized_data = serialize_result.decode(encoding)
    else:
        assert serialize_result is None
        dest_bytes = dest_ref.path.read_bytes()
        serialized_data = dest_bytes.decode(encoding)

    logging.debug("serialized_data = %s", serialized_data)
    check_serialized(format_info.name, select_result, serialized_data)


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
        result = select_result.serialize(format=format, encoding=encoding)
        assert result is not None
        return result


def make_select_result_parse_serialized_tests() -> Iterator[ParameterSet]:
    xfails: Dict[Tuple[str, Optional[SourceType], str], Union[MarkDecorator, Mark]] = {}
    format_infos = [
        format_info
        for format_info in ResultFormat.info_set()
        if ResultFormatTrait.HAS_PARSER in format_info.traits
        and ResultType.SELECT in format_info.supported_types
    ]
    source_types = set(SourceType)
    xfails[("csv", SourceType.BINARY_IO, "utf-16")] = pytest.mark.xfail(
        raises=UnicodeDecodeError,
    )
    xfails[("json", SourceType.BINARY_IO, "utf-16")] = pytest.mark.xfail(
        raises=UnicodeDecodeError,
    )
    xfails[("tsv", SourceType.BINARY_IO, "utf-16")] = pytest.mark.xfail(
        raises=UnicodeDecodeError,
    )
    for format_info, destination_type in itertools.product(format_infos, source_types):
        for encoding in format_info.encodings:
            xfail = xfails.get((format_info.format, destination_type, encoding))
            marks = (xfail,) if xfail is not None else ()
            yield pytest.param(
                (format_info, destination_type, encoding),
                id=f"{format_info.name}-{None if destination_type is None else destination_type.name}-{encoding}",
                marks=marks,
            )


@pytest.mark.parametrize(
    ["test_args"],
    make_select_result_parse_serialized_tests(),
)
def test_select_result_parse_serialized(
    tmp_path: Path,
    select_result: Result,
    test_args: Tuple[ResultFormatInfo, SourceType, str],
) -> None:
    """
    Parsing a serialized result produces the expected result object.
    """
    format_info, source_type, encoding = test_args

    serialized_data = serialize_select(select_result, format_info.name, encoding)

    logging.debug("serialized_data = %s", serialized_data.decode(encoding))

    source: Union[BinaryIO, TextIO]
    if source_type is SourceType.TEXT_IO:
        source = StringIO(serialized_data.decode(encoding))
    elif source_type is SourceType.BINARY_IO:
        source = BytesIO(serialized_data)
    else:
        raise ValueError(f"Invalid source_type {source_type}")

    parsed_result = Result.parse(source, format=format_info.name)

    assert select_result == parsed_result


def make_test_serialize_to_strdest_tests() -> Iterator[ParameterSet]:
    destination_types: Set[DestinationType] = {
        DestinationType.FILE_URI,
        DestinationType.STR_PATH,
    }
    name_prefixes = [
        r"a_b-",
        r"a%b-",
        r"a%20b-",
        r"a b-",
        r"a b-",
        r"a@b",
        r"a$b",
        r"a!b",
    ]
    if isinstance(Path.cwd(), PosixPath):
        # not valid on windows https://docs.microsoft.com/en-us/windows/win32/fileio/naming-a-file#naming-conventions
        name_prefixes.extend(
            [
                r"a:b-",
                r"a|b",
            ]
        )
    for destination_type, name_prefix in itertools.product(
        destination_types, name_prefixes
    ):
        yield pytest.param(
            destination_type,
            name_prefix,
            id=f"{destination_type.name}-{name_prefix}",
        )


@pytest.mark.parametrize(
    ["destination_type", "name_prefix"],
    make_test_serialize_to_strdest_tests(),
)
def test_serialize_to_strdest(
    tmp_path: Path,
    select_result: Result,
    destination_type: DestinationType,
    name_prefix: str,
) -> None:
    """
    Various ways of specifying the destination argument of ``Result.serialize``
    as a string works correctly.
    """
    format_info = ResultFormat.JSON.info
    encoding = "utf-8"

    def path_factory(
        tmp_path: Path, type: DestinationType, encoding: Optional[str]
    ) -> Path:
        return tmp_path / f"{name_prefix}file-{type.name}-{encoding}"

    with destination_type.make_ref(
        tmp_path,
        encoding=encoding,
        path_factory=path_factory,
    ) as dest_ref:
        assert dest_ref is not None
        destination = narrow_dest_param(dest_ref.param)
        serialize_result = select_result.serialize(
            destination=destination,
            format=format_info.name,
            encoding=encoding,
        )

    assert serialize_result is None
    dest_bytes = dest_ref.path.read_bytes()
    serialized_data = dest_bytes.decode(encoding)

    logging.debug("serialized_data = %s", serialized_data)
    check_serialized(format_info.name, select_result, serialized_data)


@pytest.mark.parametrize(
    ["authority"],
    [
        ("localhost",),
        ("127.0.0.1",),
        ("example.com",),
        (socket.gethostname(),),
        (socket.getfqdn(),),
    ],
)
def test_serialize_to_fileuri_with_authortiy(
    tmp_path: Path,
    select_result: Result,
    authority: str,
) -> None:
    """
    Serializing to a file URI with authority raises an error.
    """
    destination_type = DestinationType.FILE_URI
    format_info = ResultFormat.JSON.info
    encoding = "utf-8"

    with ExitStack() as exit_stack:
        dest_ref = exit_stack.enter_context(
            destination_type.make_ref(
                tmp_path,
                encoding=encoding,
            )
        )
        assert dest_ref is not None
        assert isinstance(dest_ref.param, str)
        urlparts = urlsplit(dest_ref.param)._replace(netloc=authority)
        use_url = urlunsplit(urlparts)
        logging.debug("use_url = %s", use_url)
        catcher = exit_stack.enter_context(pytest.raises(ValueError))
        select_result.serialize(
            destination=use_url,
            format=format_info.name,
            encoding=encoding,
        )
        assert False  # this should never happen as serialize should always fail
    assert catcher.value is not None
