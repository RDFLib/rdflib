from __future__ import annotations

import enum
import itertools
import logging
import pathlib
import re
from contextlib import ExitStack, contextmanager
from dataclasses import dataclass
from io import BytesIO, StringIO, TextIOWrapper
from pathlib import Path
from typing import (  # Callable,
    IO,
    TYPE_CHECKING,
    BinaryIO,
    Collection,
    ContextManager,
    Generator,
    Generic,
    Iterable,
    Optional,
    TextIO,
    Tuple,
    Type,
    TypeVar,
    Union,
)

import pytest
from _pytest.mark.structures import ParameterSet

from rdflib.graph import Graph
from rdflib.parser import (
    BytesIOWrapper,
    FileInputSource,
    InputSource,
    StringInputSource,
    URLInputSource,
    create_input_source,
)
from test.utils import GraphHelper
from test.utils.httpfileserver import (
    HTTPFileInfo,
    HTTPFileServer,
    LocationType,
    ProtoFileResource,
    ProtoRedirectResource,
)
from test.utils.outcome import ExceptionChecker

from ..data import TEST_DATA_DIR


def test_empty_arguments():
    """create_input_source() function must receive exactly one argument."""
    with pytest.raises(ValueError):
        create_input_source()


def test_too_many_arguments():
    """create_input_source() function has a few conflicting arguments."""
    with pytest.raises(ValueError):
        create_input_source(source="a", location="b")


SourceParamType = Union[IO[bytes], TextIO, InputSource, str, bytes, pathlib.PurePath]
FileParamType = Union[BinaryIO, TextIO]
DataParamType = Union[str, bytes, dict]


class SourceParam(enum.Enum):
    """
    Indicates what kind of paramter should be passed as ``source`` to create_input_source().
    """

    BINARY_IO = enum.auto()
    TEXT_IO = enum.auto()
    INPUT_SOURCE = enum.auto()
    BYTES = enum.auto()
    PATH = enum.auto()
    PATH_STRING = enum.auto()
    FILE_URI = enum.auto()

    @contextmanager
    def from_path(self, path: Path) -> Generator[SourceParamType, None, None]:
        """
        Yields a value of the type indicated by the enum value which provides the data from the file at ``path``.


        :param path: Path to the file to read.
        :return: A context manager which yields a value of the type indicated by the enum value.
        """
        if self is SourceParam.BINARY_IO:
            yield path.open("rb")
        elif self is SourceParam.TEXT_IO:
            yield path.open("r", encoding="utf-8")
        elif self is SourceParam.INPUT_SOURCE:
            yield StringInputSource(path.read_bytes(), encoding="utf-8")
        elif self is SourceParam.BYTES:
            yield path.read_bytes()
        elif self is SourceParam.PATH:
            yield path
        elif self is SourceParam.PATH_STRING:
            yield f"{path}"
        elif self is SourceParam.FILE_URI:
            yield path.absolute().as_uri()
        else:
            raise ValueError(f"unsupported value self={self} self.value={self.value}")


class LocationParam(enum.Enum):
    """
    Indicates what kind of paramter should be passed as ``location`` to create_input_source().
    """

    FILE_URI = enum.auto()
    HTTP_URI = enum.auto()

    @contextmanager
    def from_path(
        self, path: Optional[Path], url: Optional[str]
    ) -> Generator[str, None, None]:
        """
        Yields a value of the type indicated by the enum value which provides the data from the file at ``path``.

        :param path: Path to the file to read.
        :return: A context manager which yields a value of the type indicated by the enum value.
        """
        if self is LocationParam.FILE_URI:
            assert path is not None
            yield path.absolute().as_uri()
        elif self is LocationParam.HTTP_URI:
            assert url is not None
            yield url
        else:
            raise ValueError(f"unsupported value self={self} self.value={self.value}")


class FileParam(enum.Enum):
    """
    Indicates what kind of paramter should be passed as ``file`` to create_input_source().
    """

    BINARY_IO = enum.auto()
    TEXT_IO = enum.auto()

    @contextmanager
    def from_path(self, path: Path) -> Generator[Union[BinaryIO, TextIO], None, None]:
        """
        Yields a value of the type indicated by the enum value which provides the data from the file at ``path``.

        :param path: Path to the file to read.
        :return: A context manager which yields a value of the type indicated by the enum value.
        """
        if self is FileParam.BINARY_IO:
            yield path.open("rb")
        elif self is FileParam.TEXT_IO:
            yield path.open("r", encoding="utf-8")
        else:
            raise ValueError(f"unsupported value self={self} self.value={self.value}")


class DataParam(enum.Enum):
    """
    Indicates what kind of paramter should be passed as ``data`` to create_input_source().
    """

    STRING = enum.auto()
    BYTES = enum.auto()
    # DICT = enum.auto()

    @contextmanager
    def from_path(self, path: Path) -> Generator[Union[bytes, str, dict], None, None]:
        """
        Yields a value of the type indicated by the enum value which provides the data from the file at ``path``.

        :param path: Path to the file to read.
        :return: A context manager which yields a value of the type indicated by the enum value.
        """
        if self is DataParam.STRING:
            yield path.read_text(encoding="utf-8")
        elif self is DataParam.BYTES:
            yield path.read_bytes()
        else:
            raise ValueError(f"unsupported value self={self} self.value={self.value}")


@contextmanager
def call_create_input_source(
    input: Union[HTTPFileInfo, Path],
    source_param: Optional[SourceParam] = None,
    # source_slot: SourceSlot,
    public_id: Optional[str] = None,
    location_param: Optional[LocationParam] = None,
    file_param: Optional[FileParam] = None,
    data_param: Optional[DataParam] = None,
    format: Optional[str] = None,
) -> Generator[InputSource, None, None]:
    """
    Calls create_input_source() with parameters of the specified types.
    """

    logging.debug(
        "source_param = %s, location_param = %s, file_param = %s, data_param = %s",
        source_param,
        location_param,
        file_param,
        data_param,
    )

    source: Optional[SourceParamType] = None
    location: Optional[str] = None
    file: Optional[FileParamType] = None
    data: Optional[DataParamType] = None

    input_url = None
    if isinstance(input, HTTPFileInfo):
        input_path = input.path
        input_url = input.request_url
    else:
        input_path = input

    with ExitStack() as xstack:
        if source_param is not None:
            source = xstack.enter_context(source_param.from_path(input_path))
        if location_param is not None:
            location = xstack.enter_context(
                location_param.from_path(input_path, input_url)
            )
        if file_param is not None:
            file = xstack.enter_context(file_param.from_path(input_path))
        if data_param is not None:
            data = xstack.enter_context(data_param.from_path(input_path))

        logging.debug(
            "source = %s/%r, location = %s/%r, file = %s/..., data = %s/...",
            type(source),
            source,
            type(location),
            location,
            type(file),
            type(data),
        )
        input_source = create_input_source(
            source=source,
            publicID=public_id,
            location=location,
            file=file,
            data=data,
            format=format,
        )
        yield input_source


AnyT = TypeVar("AnyT")


@dataclass
class Holder(Generic[AnyT]):
    value: AnyT


class StreamCheck(enum.Enum):
    BYTE = enum.auto()
    CHAR = enum.auto()
    GRAPH = enum.auto()


@dataclass
class InputSourceChecker:
    """
    Checker for input source objects.

    :param type: Expected type of input source.
    :param stream_check: What kind of stream check to perform.
    :param encoding: Expected encoding of input source. If ``None``, then the encoding is not checked. If it has a value (i.e. an instance of :class:`Holder`), then the encoding is expected to match ``encoding.value``.
    """

    type: Type[InputSource]
    stream_check: StreamCheck
    encoding: Optional[Holder[Optional[str]]]
    public_id: Optional[str]
    system_id: Optional[str]
    # extra_checks: List[Callable[[InputSource], None]] = field(factory=list)

    def check(
        self,
        params: CreateInputSourceTestParams,
        input_path: Path,
        input_source: InputSource,
    ) -> None:
        """
        Check that ``input_source`` matches expectations.
        """
        logging.debug(
            "input_source = %s / %s, self.type = %s",
            type(input_source),
            input_source,
            self.type,
        )
        assert isinstance(input_source, InputSource)
        if self.type is not None:
            assert isinstance(input_source, self.type)

        if self.stream_check is StreamCheck.BYTE:
            binary_io: BinaryIO = input_source.getByteStream()
            if params.data_param is DataParam.STRING:
                assert (
                    binary_io.read() == input_path.read_text(encoding="utf-8").encode()
                )
            else:
                assert binary_io.read() == input_path.read_bytes()
        elif self.stream_check is StreamCheck.CHAR:
            text_io: TextIO = input_source.getCharacterStream()
            assert text_io.read() == input_path.read_text(encoding="utf-8")
        elif self.stream_check is StreamCheck.GRAPH:
            graph = Graph()
            graph.parse(input_source, format=params.format)
            assert len(graph) > 0
            GraphHelper.assert_triple_sets_equals(BASE_GRAPH, graph)
        else:
            raise ValueError(f"unsupported stream_check value {self.stream_check}")

        if self.encoding is not None:
            assert self.encoding.value == input_source.getEncoding()

        logging.debug("input_source.getPublicId() = %r", input_source.getPublicId())
        logging.debug("self.public_id = %r", self.public_id)
        if self.public_id is not None and input_source.getPublicId() is not None:
            assert f"{self.public_id}" == f"{input_source.getPublicId()}"
        else:
            assert self.public_id == input_source.getPublicId()

        logging.debug("input_source.getSystemId() = %r", input_source.getSystemId())
        logging.debug("self.system_id = %r", self.system_id)
        if self.system_id is not None and input_source.getSystemId() is not None:
            assert f"{self.system_id}" == f"{input_source.getSystemId()}"
        else:
            assert self.system_id == input_source.getSystemId()

    @classmethod
    def type_from_param(
        cls, param: Union[SourceParam, FileParam, DataParam, LocationParam, enum.Enum]
    ) -> Type[InputSource]:
        """
        Return the type of input source that should be created for the given parameter.

        :param param: The parameter that will be passed to :func:`create_input_source`.
        :return: Type of input source that should be created for the given parameter.
        """
        if param in (
            SourceParam.PATH,
            SourceParam.PATH_STRING,
            SourceParam.FILE_URI,
            LocationParam.FILE_URI,
        ):
            return FileInputSource
        if param in (SourceParam.BINARY_IO, SourceParam.TEXT_IO):
            return InputSource
        if param in (*FileParam,):
            return FileInputSource
        if param in (SourceParam.BYTES, SourceParam.INPUT_SOURCE, *DataParam):
            return StringInputSource
        if param in (LocationParam.HTTP_URI,):
            return URLInputSource
        raise ValueError(f"unknown param {param}")


FileParamTypeCM = ContextManager[FileParamType]


CreateInputSourceTestParamsTuple = Tuple[
    Path,
    Optional[SourceParam],
    Optional[str],
    Optional[LocationParam],
    Optional[FileParam],
    Optional[DataParam],
    Optional[str],
    Union[ExceptionChecker, InputSourceChecker],
]
"""
Type alias for the tuple representation of :class:`CreateInputSourceTestParams`.
"""


@dataclass
class CreateInputSourceTestParams:
    """
    Parameters for :func:`create_input_source`.
    """

    input_path: Path
    source_param: Optional[SourceParam]
    public_id: Optional[str]
    location_param: Optional[LocationParam]
    file_param: Optional[FileParam]
    data_param: Optional[DataParam]
    format: Optional[str]
    expected_result: Union[ExceptionChecker, InputSourceChecker]

    def as_tuple(self) -> CreateInputSourceTestParamsTuple:
        return (
            self.input_path,
            self.source_param,
            self.public_id,
            self.location_param,
            self.file_param,
            self.data_param,
            self.format,
            self.expected_result,
        )

    @property
    def input_param(self) -> Union[SourceParam, LocationParam, FileParam, DataParam]:
        values = [
            param
            for param in (
                self.source_param,
                self.location_param,
                self.file_param,
                self.data_param,
            )
            if param is not None
        ]
        if len(values) != 1:
            raise ValueError(f"multiple input params: {values}")
        return values[0]

    @property
    def requires_http(self) -> bool:
        if self.location_param in (LocationParam.HTTP_URI,):
            return True
        return False

    def as_pytest_param(
        self,
        marks: Union[
            pytest.MarkDecorator, Collection[Union[pytest.MarkDecorator, pytest.Mark]]
        ] = (),
        id: Optional[str] = None,
    ) -> ParameterSet:
        if id is None:
            id = f"{self.input_path.as_posix()}:source_param={self.source_param}:public_id={self.public_id}:location_param={self.location_param}:file_param={self.file_param}:data_param={self.data_param}:format={self.format}:{self.expected_result}"
        return pytest.param(self, marks=marks, id=id)


VARIANTS_DIR = TEST_DATA_DIR.relative_to(Path.cwd()) / "variants"
BASE_GRAPH = Graph()
BASE_GRAPH.parse(VARIANTS_DIR / "simple_triple.nt", format="nt")


def generate_create_input_source_cases() -> Iterable[ParameterSet]:
    """
    Generate cases for :func:`test_create_input_source`.
    """
    default_format = "turtle"
    input_paths = {
        "turtle": VARIANTS_DIR / "simple_triple.ttl",
        "json-ld": VARIANTS_DIR / "simple_triple.jsonld",
        "xml": VARIANTS_DIR / "simple_triple.xml",
        "nt": VARIANTS_DIR / "simple_triple.nt",
        "hext": VARIANTS_DIR / "simple_triple.hext",
        None: VARIANTS_DIR / "simple_triple.ttl",
    }
    formats = set(input_paths.keys())

    for use_source, use_location, use_file, use_data in itertools.product(
        (True, False), (True, False), (True, False), (True, False)
    ):
        flags = (use_source, use_location, use_file, use_data)
        true_flags = sum([1 if flag is True else 0 for flag in flags])
        if true_flags <= 1:
            # Only process combinations with at least two flags set
            continue

        yield CreateInputSourceTestParams(
            input_paths[default_format],
            source_param=SourceParam.PATH if use_source else None,
            public_id=None,
            location_param=LocationParam.FILE_URI if use_location else None,
            file_param=FileParam.TEXT_IO if use_file else None,
            data_param=DataParam.STRING if use_data else None,
            format=default_format,
            expected_result=ExceptionChecker(
                ValueError,
                re.compile(
                    "exactly one of source, location, file or data must be given"
                ),
            ),
        ).as_pytest_param(
            id=f"bad_arg_combination-use_source={use_source}-use_location={use_location}-use_file={use_file}-use_data={use_data}"
        )

    def make_params(
        param: enum.Enum,
        stream_check: StreamCheck,
        expected_encoding: Optional[Holder[Optional[str]]],
        format: Optional[str] = default_format,
        id: Optional[str] = None,
        public_id: Optional[str] = None,
        marks: Union[
            pytest.MarkDecorator, Collection[Union[pytest.MarkDecorator, pytest.Mark]]
        ] = (),
    ) -> Iterable[ParameterSet]:
        yield CreateInputSourceTestParams(
            input_paths[format],
            source_param=param if isinstance(param, SourceParam) else None,
            public_id=public_id,
            location_param=param if isinstance(param, LocationParam) else None,
            file_param=param if isinstance(param, FileParam) else None,
            data_param=param if isinstance(param, DataParam) else None,
            format=format,
            expected_result=InputSourceChecker(
                InputSourceChecker.type_from_param(param),
                stream_check=stream_check,
                encoding=expected_encoding,
                public_id=public_id,
                system_id=None,
            ),
        ).as_pytest_param(marks, id)

    for param, stream_check, format in itertools.product(
        itertools.chain(SourceParam, LocationParam, FileParam, DataParam),
        StreamCheck,
        formats,
    ):
        # Generate cases for all supported source parameters. And create
        # variants of cases to perfom different stream checks on created input
        # sources.
        if stream_check is StreamCheck.CHAR and param in (
            SourceParam.BINARY_IO,
            SourceParam.PATH,
            SourceParam.PATH_STRING,
            SourceParam.FILE_URI,
            LocationParam.FILE_URI,
            LocationParam.HTTP_URI,
            FileParam.BINARY_IO,
        ):
            # These do not have working characther streams. Maybe they
            # should, but they don't.
            continue
        expected_encoding: Optional[Holder[Optional[str]]]
        if param in (
            SourceParam.PATH,
            SourceParam.PATH_STRING,
            SourceParam.FILE_URI,
            LocationParam.FILE_URI,
            LocationParam.HTTP_URI,
            SourceParam.BINARY_IO,
            FileParam.BINARY_IO,
        ):
            # This should maybe be ``None`` instead of ``Holder(None)``, but as
            # there is no ecoding supplied it is probably safe to assert that no
            # encoding is associated with it.
            expected_encoding = Holder(None)
        else:
            expected_encoding = Holder("utf-8")

        yield from make_params(param, stream_check, expected_encoding, format)

    for param in LocationParam:
        yield from make_params(
            param,
            StreamCheck.BYTE,
            Holder(None),
            public_id="https://example.com/explicit_public_id",
        )


@pytest.mark.parametrize(
    ["test_params"],
    generate_create_input_source_cases(),
)
def test_create_input_source(
    test_params: CreateInputSourceTestParams,
    http_file_server: HTTPFileServer,
) -> None:
    """
    A given set of parameters results in an input source matching specified
    invariants.

    :param test_params: The parameters to use for the test. This specifies what
        parameters should be passed to func:`create_input_source` and what
        invariants the resulting input source should match.
    :param http_file_server: The HTTP file server to use for the test.
    """
    logging.debug("test_params = %s", test_params)
    input_path = test_params.input_path
    input: Union[HTTPFileInfo, Path]
    if test_params.requires_http:
        http_file_info = http_file_server.add_file_with_caching(
            ProtoFileResource((), test_params.input_path),
            (ProtoRedirectResource((), 300, LocationType.URL),),
        )
        logging.debug("http_file_info = %s", http_file_info)
        input = http_file_info
    else:
        input = test_params.input_path

    if isinstance(test_params.expected_result, InputSourceChecker):
        expected_result = test_params.expected_result
        param = test_params.input_param
        if expected_result.public_id is None:
            if param in (
                SourceParam.PATH,
                SourceParam.PATH_STRING,
                SourceParam.FILE_URI,
                LocationParam.FILE_URI,
            ):
                expected_result.public_id = input_path.absolute().as_uri()
            elif param in (LocationParam.HTTP_URI,):
                expected_result.public_id = http_file_info.effective_url
            else:
                expected_result.public_id = ""

        if expected_result.system_id is None:
            if param in (
                SourceParam.BINARY_IO,
                SourceParam.TEXT_IO,
            ):
                expected_result.system_id = f"{input_path}"
            elif param in (
                SourceParam.INPUT_SOURCE,
                SourceParam.BYTES,
                DataParam.STRING,
                DataParam.BYTES,
            ):
                expected_result.system_id = None
            elif param in (
                SourceParam.PATH,
                SourceParam.PATH_STRING,
                SourceParam.FILE_URI,
                LocationParam.FILE_URI,
                FileParam.BINARY_IO,
                FileParam.TEXT_IO,
            ):
                expected_result.system_id = input_path.absolute().as_uri()
            elif param in (LocationParam.HTTP_URI,):
                expected_result.system_id = http_file_info.effective_url
            else:
                raise ValueError(
                    f"cannot determine expected_result.system_id for param={param!r}"
                )

    logging.info("expected_result = %s", test_params.expected_result)

    catcher: Optional[pytest.ExceptionInfo[Exception]] = None
    input_source: Optional[InputSource] = None
    with ExitStack() as xstack:
        if isinstance(test_params.expected_result, ExceptionChecker):
            catcher = xstack.enter_context(test_params.expected_result.context())

        input_source = xstack.enter_context(
            call_create_input_source(
                input,
                test_params.source_param,
                test_params.public_id,
                test_params.location_param,
                test_params.file_param,
                test_params.data_param,
                test_params.format,
            )
        )
        if not isinstance(test_params.expected_result, ExceptionChecker):
            assert input_source is not None
            test_params.expected_result.check(
                test_params, test_params.input_path, input_source
            )

    logging.debug("input_source = %s, catcher = %s", input_source, catcher)


def test_bytesio_wrapper():
    wrapper = BytesIOWrapper("hello world")
    assert wrapper.seekable()
    assert wrapper.read(1) == b"h"
    assert wrapper.read(1) == b"e"
    assert wrapper.seek(0) == 0
    assert wrapper.read() == b"hello world"
    wrapper.seek(0)
    ba = bytearray(7)
    assert wrapper.readinto(ba) == 7
    assert ba == b"hello w"
    assert not wrapper.closed
    wrapper.close()
    assert wrapper.closed

    text_stream = TextIOWrapper(BytesIO(b"hello world"))
    wrapper = BytesIOWrapper(text_stream)
    assert wrapper.seekable()
    assert wrapper.read(1) == b"h"
    assert wrapper.read(1) == b"e"
    assert wrapper.tell() == 2
    assert wrapper.seek(0) == 0
    assert wrapper.read() == b"hello world"
    ba = bytearray(7)
    assert wrapper.readinto(ba) == 0
    wrapper.seek(0)
    assert wrapper.readinto(ba) == 7
    assert ba == b"hello w"

    text_stream = StringIO("h∈llo world")
    wrapper = BytesIOWrapper(text_stream)
    assert wrapper.seekable()
    assert wrapper.read(1) == b"h"
    assert wrapper.read(1) == b"\xe2"
    assert wrapper.read(1) == b"\x88"
    assert wrapper.tell() == 3
    assert wrapper.read(2) == b"\x88l"
    assert wrapper.seek(0) == 0
    assert wrapper.read() == b"h\xe2\x88\x88llo world"
    ba = bytearray(7)
    assert wrapper.readinto(ba) == 0
    wrapper.seek(0)
    assert wrapper.readinto(ba) == 7
    assert ba == b"h\xe2\x88\x88llo"
    nquads_dir = TEST_DATA_DIR.relative_to(Path.cwd()) / "nquads.rdflib"

    with open(Path(nquads_dir / "test1.nquads"), "r") as f:
        # not binary file, opened as a TextIO
        if TYPE_CHECKING:
            assert isinstance(f, TextIOWrapper)
        wrapper = BytesIOWrapper(f)
        assert not wrapper.closed
        assert wrapper.name == str(nquads_dir / "test1.nquads")
        assert wrapper.seekable()
        assert wrapper.read(1) == b"<"
        assert wrapper.read(1) == b"h"
        assert wrapper.tell() == 2
        assert wrapper.seek(0) == 0
        assert wrapper.read(1) == b"<"
    assert wrapper.closed
